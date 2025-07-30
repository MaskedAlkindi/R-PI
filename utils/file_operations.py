#!/usr/bin/env python3
"""
File Operations Manager
Handles file operations on USB drives including listing, upload, download, delete, and rename.
"""

import os
import shutil
import mimetypes
import magic
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename
from PIL import Image
import io

logger = logging.getLogger(__name__)

class FileOperations:
    """Handle file operations on USB drives."""
    
    def __init__(self, usb_manager=None):
        """Initialize FileOperations with optional USB manager instance."""
        self.usb_manager = usb_manager
        self.allowed_extensions = {
            '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.doc', '.docx',
            '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.mp3', '.mp4',
            '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.csv', '.json',
            '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.c',
            '.h', '.hpp', '.md', '.log', '.ini', '.cfg', '.conf', '.yml',
            '.yaml', '.toml', '.sql', '.db', '.sqlite', '.bak', '.tmp'
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        
    def _get_usb_manager(self):
        """Get USB manager instance, creating one if not provided."""
        if self.usb_manager is None:
            from .usb_manager import USBManager
            self.usb_manager = USBManager()
        return self.usb_manager
    
    def list_files(self, path: str = '') -> List[Dict]:
        """List files in the specified path on USB drive."""
        try:
            # Get mount point from USB manager
            usb_manager = self._get_usb_manager()
            mount_point = usb_manager.get_mount_point()
            
            if not mount_point:
                raise Exception("No USB device mounted")
            
            full_path = os.path.join(mount_point, path)
            
            if not os.path.exists(full_path):
                raise Exception(f"Path does not exist: {path}")
            
            files = []
            
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                relative_path = os.path.join(path, item) if path else item
                
                try:
                    stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    file_info = {
                        'name': item,
                        'path': relative_path,
                        'is_directory': is_dir,
                        'size': stat.st_size if not is_dir else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'permissions': oct(stat.st_mode)[-3:],
                        'type': self._get_file_type(item, is_dir),
                        'icon': self._get_file_icon(item, is_dir),
                        'human_size': self._format_size(stat.st_size) if not is_dir else '--'
                    }
                    
                    files.append(file_info)
                    
                except OSError as e:
                    logger.warning(f"Error accessing {item}: {e}")
                    continue
            
            # Sort: directories first, then files alphabetically
            files.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files in {path}: {e}")
            raise
    
    def upload_file(self, file) -> Dict:
        """Upload a file to USB drive."""
        try:
            # Get mount point
            usb_manager = self._get_usb_manager()
            mount_point = usb_manager.get_mount_point()
            
            if not mount_point:
                raise Exception("No USB device mounted")
            
            # Secure filename
            filename = secure_filename(file.filename)
            if not filename:
                raise Exception("Invalid filename")
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:  # Use max_file_size from __init__
                raise Exception("File too large (max 100MB)")
            
            # Save file to USB
            file_path = os.path.join(mount_point, filename)
            
            # Check if file already exists
            counter = 1
            original_filename = filename
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                file_path = os.path.join(mount_point, filename)
                counter += 1
            
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file, f)
            
            # Get file info
            stat = os.stat(file_path)
            file_info = {
                'name': filename,
                'path': filename,
                'size': stat.st_size,
                'human_size': self._format_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': self._get_file_type(filename, False),
                'icon': self._get_file_icon(filename, False)
            }
            
            logger.info(f"File uploaded successfully: {filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def delete_file(self, filename: str) -> bool:
        """Delete a file from USB drive."""
        try:
            # Get mount point
            usb_manager = self._get_usb_manager()
            mount_point = usb_manager.get_mount_point()
            
            if not mount_point:
                raise Exception("No USB device mounted")
            
            file_path = os.path.join(mount_point, filename)
            
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {filename}")
            
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            
            logger.info(f"File deleted successfully: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            raise
    
    def rename_file(self, old_name: str, new_name: str) -> Dict:
        """Rename a file on USB drive."""
        try:
            # Get mount point
            usb_manager = self._get_usb_manager()
            mount_point = usb_manager.get_mount_point()
            
            if not mount_point:
                raise Exception("No USB device mounted")
            
            old_path = os.path.join(mount_point, old_name)
            new_path = os.path.join(mount_point, new_name)
            
            if not os.path.exists(old_path):
                raise Exception(f"File not found: {old_name}")
            
            if os.path.exists(new_path):
                raise Exception(f"File already exists: {new_name}")
            
            os.rename(old_path, new_path)
            
            # Get updated file info
            stat = os.stat(new_path)
            file_info = {
                'name': new_name,
                'path': new_name,
                'size': stat.st_size,
                'human_size': self._format_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': self._get_file_type(new_name, os.path.isdir(new_path)),
                'icon': self._get_file_icon(new_name, os.path.isdir(new_path))
            }
            
            logger.info(f"File renamed successfully: {old_name} -> {new_name}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error renaming file {old_name}: {e}")
            raise
    
    def create_folder(self, folder_name: str, parent_path: str = '') -> Dict:
        """Create a new folder on USB drive."""
        try:
            # Get mount point
            usb_manager = self._get_usb_manager()
            mount_point = usb_manager.get_mount_point()
            
            if not mount_point:
                raise Exception("No USB device mounted")
            
            # Secure folder name
            folder_name = secure_filename(folder_name)
            if not folder_name:
                raise Exception("Invalid folder name")
            
            # Create full path
            if parent_path:
                full_path = os.path.join(mount_point, parent_path, folder_name)
            else:
                full_path = os.path.join(mount_point, folder_name)
            
            if os.path.exists(full_path):
                raise Exception(f"Folder already exists: {folder_name}")
            
            os.makedirs(full_path, exist_ok=True)
            
            # Get folder info
            stat = os.stat(full_path)
            folder_info = {
                'name': folder_name,
                'path': os.path.join(parent_path, folder_name) if parent_path else folder_name,
                'size': 0,
                'human_size': '--',
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': 'folder',
                'icon': 'folder'
            }
            
            logger.info(f"Folder created successfully: {folder_name}")
            return folder_info
            
        except Exception as e:
            logger.error(f"Error creating folder {folder_name}: {e}")
            raise
    
    def get_file_path(self, filename: str) -> str:
        """Get the full path of a file on USB drive."""
        usb_manager = self._get_usb_manager()
        mount_point = usb_manager.get_mount_point()
        
        if not mount_point:
            raise Exception("No USB device mounted")
        
        return os.path.join(mount_point, filename)
    
    def is_valid_file(self, file) -> bool:
        """Check if uploaded file is valid."""
        try:
            # Check file extension
            filename = file.filename.lower()
            if not filename:
                return False
            
            # Get file extension
            ext = os.path.splitext(filename)[1]
            
            # Check if extension is allowed
            if ext not in self.allowed_extensions:
                return False
            
            # Check file content type (basic check)
            file.seek(0)
            content = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset position
            
            # Use python-magic to check file type
            try:
                file_type = magic.from_buffer(content, mime=True)
                # Basic validation - could be enhanced
                return True
            except:
                # Fallback to extension check
                return ext in self.allowed_extensions
                
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False
    
    def _get_file_type(self, filename: str, is_directory: bool) -> str:
        """Get file type based on extension."""
        if is_directory:
            return 'folder'
        
        ext = os.path.splitext(filename.lower())[1]
        
        # This part of the logic needs to be updated to use the allowed_extensions set
        # For now, it will return 'unknown' for any extension not in the set
        return 'unknown'
    
    def _get_file_icon(self, filename: str, is_directory: bool) -> str:
        """Get appropriate icon for file type."""
        if is_directory:
            return 'folder'
        
        ext = os.path.splitext(filename.lower())[1]
        
        # Map extensions to icons
        icon_map = {
            # Images
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.bmp': 'image', '.tiff': 'image', '.webp': 'image',
            
            # Documents
            '.pdf': 'pdf', '.doc': 'word', '.docx': 'word', '.txt': 'text',
            '.rtf': 'text', '.odt': 'text',
            
            # Spreadsheets
            '.xls': 'excel', '.xlsx': 'excel', '.csv': 'table', '.ods': 'table',
            
            # Presentations
            '.ppt': 'powerpoint', '.pptx': 'powerpoint', '.odp': 'presentation',
            
            # Archives
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive',
            '.tar': 'archive', '.gz': 'archive',
            
            # Videos
            '.mp4': 'video', '.avi': 'video', '.mkv': 'video', '.mov': 'video',
            '.wmv': 'video', '.flv': 'video',
            
            # Audio
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.aac': 'audio',
            '.ogg': 'audio',
            
            # Code
            '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code',
            '.json': 'code', '.xml': 'code', '.sql': 'code'
        }
        
        return icon_map.get(ext, 'file')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}" 