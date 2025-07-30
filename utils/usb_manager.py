#!/usr/bin/env python3
"""
USB Device Manager
Handles USB device detection, mounting, unmounting, and status monitoring.
"""

import os
import json
import shutil
import subprocess
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pyudev

logger = logging.getLogger(__name__)

class USBManager:
    """Manages USB device operations."""
    
    def __init__(self):
        self.mount_point = None
        self.mounted_device = None
        self.mount_base = "/media/usb"
        
        # Ensure mount directory exists
        os.makedirs(self.mount_base, exist_ok=True)
    
    def get_available_devices(self) -> List[Dict]:
        """Get list of available USB storage devices."""
        devices = []
        
        try:
            # Use lsblk to get block devices with more details
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,LABEL,FSTYPE'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # First, find USB disks
                usb_disks = set()
                for device in data.get('blockdevices', []):
                    if device.get('type') == 'disk' and self._is_removable_disk(device):
                        usb_disks.add(device['name'])
                
                # Then find partitions of USB disks
                for device in data.get('blockdevices', []):
                    if device.get('type') == 'part' and self._is_usb_partition(device, usb_disks):
                        device_info = {
                            'name': device['name'],
                            'size': device.get('size', 'Unknown'),
                            'label': device.get('label', 'No Label'),
                            'mountpoint': device.get('mountpoint', ''),
                            'type': device.get('type', ''),
                            'fstype': device.get('fstype', '')
                        }
                        devices.append(device_info)
            
        except Exception as e:
            logger.error(f"Error getting USB devices: {e}")
            # Fallback method using /proc/partitions
            devices = self._get_devices_fallback()
        
        return devices
    
    def _is_removable_disk(self, device: Dict) -> bool:
        """Check if device is a removable disk."""
        try:
            device_name = device['name'].replace('/dev/', '')
            device_path = f"/sys/block/{device_name}"
            if os.path.exists(device_path):
                removable_path = os.path.join(device_path, 'removable')
                if os.path.exists(removable_path):
                    with open(removable_path, 'r') as f:
                        return f.read().strip() == '1'
        except:
            pass
        return False
    
    def _is_usb_partition(self, device: Dict, usb_disks: set) -> bool:
        """Check if partition belongs to a USB disk."""
        try:
            device_name = device['name']
            # Extract disk name from partition name (e.g., sda1 -> sda)
            if '/' in device_name:
                disk_name = device_name.split('/')[-1]
            else:
                disk_name = device_name
            
            # Remove partition number to get disk name
            for i in range(len(disk_name)):
                if disk_name[i].isdigit():
                    disk_name = disk_name[:i]
                    break
            
            # Check if this partition belongs to a USB disk
            return f"/dev/{disk_name}" in usb_disks
        except:
            pass
        return False
    
    def _is_usb_storage(self, device: Dict) -> bool:
        """Legacy method - kept for compatibility."""
        return self._is_removable_disk(device)
    
    def _get_devices_fallback(self) -> List[Dict]:
        """Fallback method to get USB devices."""
        devices = []
        
        try:
            # Check common USB device patterns
            usb_patterns = ['/dev/sd*', '/dev/usb*']
            
            for pattern in usb_patterns:
                for device_path in Path('/dev').glob(pattern.replace('/dev/', '')):
                    if device_path.is_block_device():
                        # Get device size
                        try:
                            size = subprocess.run(
                                ['lsblk', '-n', '-o', 'SIZE', str(device_path)],
                                capture_output=True, text=True, timeout=5
                            ).stdout.strip()
                        except:
                            size = 'Unknown'
                        
                        devices.append({
                            'name': str(device_path),
                            'size': size,
                            'label': 'USB Device',
                            'mountpoint': '',
                            'type': 'disk'
                        })
        except Exception as e:
            logger.error(f"Error in fallback device detection: {e}")
        
        return devices
    
    def mount_device(self, device_name: str) -> str:
        """Mount a USB device."""
        try:
            # Check if device exists
            if not os.path.exists(device_name):
                raise Exception(f"Device {device_name} does not exist")
            
            # Unmount any previously mounted device
            if self.mount_point:
                self.unmount_device()
            
            # Create unique mount point
            mount_point = os.path.join(self.mount_base, f"usb_{os.getpid()}")
            os.makedirs(mount_point, exist_ok=True)
            
            # Try to mount the device
            result = subprocess.run(
                ['sudo', 'mount', device_name, mount_point],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                # Try mounting with auto filesystem detection
                result = subprocess.run(
                    ['sudo', 'mount', '-t', 'auto', device_name, mount_point],
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode != 0:
                    raise Exception(f"Failed to mount device: {result.stderr}")
            
            # Verify mount was successful
            if not os.path.ismount(mount_point):
                raise Exception("Mount verification failed")
            
            self.mount_point = mount_point
            self.mounted_device = device_name
            
            logger.info(f"Successfully mounted {device_name} at {mount_point}")
            return mount_point
            
        except Exception as e:
            logger.error(f"Error mounting device {device_name}: {e}")
            raise
    
    def unmount_device(self) -> bool:
        """Unmount the currently mounted USB device."""
        if not self.mount_point:
            return True
        
        try:
            # Unmount the device
            result = subprocess.run(
                ['sudo', 'umount', self.mount_point],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Unmount warning: {result.stderr}")
            
            # Remove mount point directory
            try:
                os.rmdir(self.mount_point)
            except OSError:
                pass  # Directory might not be empty or already removed
            
            self.mount_point = None
            self.mounted_device = None
            
            logger.info("USB device unmounted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unmounting device: {e}")
            raise
    
    def get_status(self) -> Dict:
        """Get USB drive status and space information."""
        status = {
            'mounted': False,
            'device': None,
            'mount_point': None,
            'total_space': 0,
            'used_space': 0,
            'free_space': 0,
            'usage_percent': 0
        }
        
        if not self.mount_point or not os.path.ismount(self.mount_point):
            return status
        
        try:
            # Get disk usage
            usage = shutil.disk_usage(self.mount_point)
            
            status.update({
                'mounted': True,
                'device': self.mounted_device,
                'mount_point': self.mount_point,
                'total_space': usage.total,
                'used_space': usage.used,
                'free_space': usage.free,
                'usage_percent': round((usage.used / usage.total) * 100, 1)
            })
            
        except Exception as e:
            logger.error(f"Error getting USB status: {e}")
        
        return status
    
    def is_device_mounted(self) -> bool:
        """Check if a USB device is currently mounted."""
        return self.mount_point is not None and os.path.ismount(self.mount_point)
    
    def get_mount_point(self) -> Optional[str]:
        """Get the current mount point."""
        return self.mount_point if self.is_device_mounted() else None
    
    def get_mounted_device(self) -> Optional[str]:
        """Get the currently mounted device name."""
        return self.mounted_device if self.is_device_mounted() else None 