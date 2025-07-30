#!/usr/bin/env python3
"""
Reverse USB File Management Platform
A Flask-based web application for managing USB drives through a web interface.
"""

import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from utils.usb_manager import USBManager
from utils.file_operations import FileOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'

# Initialize extensions
csrf = CSRFProtect(app)

# Initialize managers
usb_manager = USBManager()
file_ops = FileOperations()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/usb/devices')
def get_usb_devices():
    """Get list of available USB devices."""
    try:
        devices = usb_manager.get_available_devices()
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        logger.error(f"Error getting USB devices: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/mount/<device>')
def mount_usb_device(device):
    """Mount a USB device."""
    try:
        # Decode the device name in case it's URL-encoded
        import urllib.parse
        original_device = device
        device = urllib.parse.unquote(device)
        
        logger.info(f"Mounting device: original='{original_device}', decoded='{device}'")
        
        mount_point = usb_manager.mount_device(device)
        return jsonify({
            'success': True,
            'mount_point': mount_point,
            'message': f'Device {device} mounted successfully'
        })
    except Exception as e:
        logger.error(f"Error mounting device {device}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/unmount', methods=['POST'])
def unmount_usb_device():
    """Unmount the currently mounted USB device."""
    try:
        usb_manager.unmount_device()
        return jsonify({
            'success': True,
            'message': 'USB device unmounted successfully'
        })
    except Exception as e:
        logger.error(f"Error unmounting device: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/files')
def get_usb_files():
    """Get list of files on the mounted USB drive."""
    try:
        path = request.args.get('path', '')
        files = file_ops.list_files(path)
        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/upload', methods=['POST'])
def upload_to_usb():
    """Upload file to USB drive."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file
        if not file_ops.is_valid_file(file):
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400

        # Upload file
        result = file_ops.upload_file(file)
        return jsonify({
            'success': True,
            'message': f'File {file.filename} uploaded successfully',
            'file_info': result
        })

    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large (max 100MB)'
        }), 413
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/files/<path:filename>', methods=['DELETE'])
def delete_usb_file(filename):
    """Delete a file from USB drive."""
    try:
        file_ops.delete_file(filename)
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/status')
def get_usb_status():
    """Get USB drive status and space information."""
    try:
        status = usb_manager.get_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting USB status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/folders', methods=['POST'])
def create_folder():
    """Create a new folder on USB drive."""
    try:
        data = request.get_json()
        folder_name = data.get('folder_name', '')
        parent_path = data.get('parent_path', '')
        
        if not folder_name:
            return jsonify({
                'success': False,
                'error': 'Folder name is required'
            }), 400

        result = file_ops.create_folder(folder_name, parent_path)
        return jsonify({
            'success': True,
            'message': f'Folder {folder_name} created successfully',
            'folder_info': result
        })
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/files/<path:filename>/rename', methods=['POST'])
def rename_file(filename):
    """Rename a file on USB drive."""
    try:
        data = request.get_json()
        new_name = data.get('new_name', '')
        
        if not new_name:
            return jsonify({
                'success': False,
                'error': 'New name is required'
            }), 400

        result = file_ops.rename_file(filename, new_name)
        return jsonify({
            'success': True,
            'message': f'File renamed to {new_name} successfully',
            'file_info': result
        })
    except Exception as e:
        logger.error(f"Error renaming file {filename}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usb/download/<path:filename>')
def download_file(filename):
    """Download a file from USB drive."""
    try:
        file_path = file_ops.get_file_path(filename)
        if not os.path.exists(file_path):
            abort(404)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 55005))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=False) 