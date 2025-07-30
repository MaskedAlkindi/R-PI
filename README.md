# Reverse USB File Management Platform

A modern Flask-based web application that provides a comprehensive reverse USB file management system. This platform allows users to browse, upload, download, and manage files on USB drives through an intuitive web interface.

## 🚀 Features

### Core Functionality
- **USB Device Detection**: Automatically detect and list available USB storage devices
- **File Browser**: Browse USB files with size, date, and type information
- **Upload Interface**: Drag-and-drop or file picker for uploading to USB
- **File Operations**: Delete, rename, and organize files on USB
- **Real-time Monitoring**: Show USB drive status and available space

### Advanced Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Mode**: Toggle between light and dark themes
- **File Search**: Search and filter files by name
- **Context Menu**: Right-click context menu for file operations
- **Progress Indicators**: Real-time upload progress and operation status
- **File Type Icons**: Visual file type identification
- **Breadcrumb Navigation**: Easy folder navigation
- **Grid/List Views**: Toggle between different file view modes

### Security Features
- **File Type Validation**: Secure file upload with type checking
- **Size Limits**: Configurable file size limits (default: 100MB)
- **CSRF Protection**: Built-in CSRF protection
- **Input Sanitization**: Secure filename handling

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **File Operations**: Python subprocess for USB mounting
- **Containerization**: Docker & Docker Compose
- **File Type Detection**: python-magic
- **Image Processing**: Pillow

## 📋 Requirements

### System Requirements
- Linux system with USB support
- Python 3.11 or higher
- Docker (for containerized deployment)
- USB storage devices

### Python Dependencies
- Flask 2.3.3
- Flask-WTF 1.1.1
- psutil 5.9.5
- pyudev 0.24.1
- Pillow 10.0.1
- python-magic 0.4.27

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reverse-usb-platform
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser and navigate to `http://localhost:55005`
   - The application will be available on port 55005

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reverse-usb-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:55005`

## 📁 Project Structure

```
reverse-usb-platform/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── README.md            # Project documentation
├── static/
│   ├── css/
│   │   └── style.css     # Modern responsive CSS
│   └── js/
│       └── main.js       # File operations and UI logic
├── templates/
│   ├── base.html         # Base template
│   └── dashboard.html    # Main interface
└── utils/
    ├── __init__.py       # Package initialization
    ├── usb_manager.py    # USB device management
    └── file_operations.py # File handling utilities
```

## 🔌 API Endpoints

### USB Device Management
- `GET /api/usb/devices` - List available USB devices
- `GET /api/usb/mount/{device}` - Mount USB device
- `POST /api/usb/unmount` - Unmount USB device
- `GET /api/usb/status` - Get USB drive status and space

### File Operations
- `GET /api/usb/files` - List files on mounted USB
- `POST /api/usb/upload` - Upload file to USB
- `DELETE /api/usb/files/{filename}` - Delete file from USB
- `GET /api/usb/download/{filename}` - Download file from USB
- `POST /api/usb/files/{filename}/rename` - Rename file
- `POST /api/usb/folders` - Create new folder

## 🎯 Usage Guide

### Connecting USB Devices

1. **Insert USB Drive**: Connect your USB storage device to the system
2. **Refresh Devices**: Click the "Refresh Devices" button in the USB Devices panel
3. **Mount Device**: Click "Mount" on the desired USB device
4. **Access Files**: Once mounted, files will appear in the file browser

### File Management

#### Uploading Files
- **Drag & Drop**: Drag files directly onto the upload area
- **Browse Files**: Click "Browse Files" to select files from your computer
- **Progress Tracking**: Monitor upload progress in real-time

#### File Operations
- **Download**: Click on a file to download it
- **Rename**: Use the edit button or right-click context menu
- **Delete**: Use the delete button or right-click context menu
- **Navigate**: Click on folders to navigate into them

#### Folder Management
- **Create Folders**: Click "New Folder" to create directories
- **Breadcrumb Navigation**: Use the breadcrumb trail to navigate back
- **Search**: Use the search box to find specific files

### Interface Features

#### View Modes
- **Grid View**: Card-based layout for visual browsing
- **List View**: Compact list layout for detailed information

#### Dark Mode
- **Toggle Theme**: Use the settings menu to switch between light and dark themes
- **Persistent**: Theme preference is saved in browser storage

#### Status Monitoring
- **USB Status**: Real-time connection status indicator
- **Storage Usage**: Visual progress bar showing disk usage
- **Space Information**: Detailed storage space breakdown

## 🔧 Configuration

### Environment Variables

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production

# File Upload Settings
MAX_CONTENT_LENGTH=104857600  # 100MB in bytes
UPLOAD_FOLDER=/tmp/uploads

# USB Mount Settings
USB_MOUNT_BASE=/media/usb
```

### Docker Configuration

The `docker-compose.yml` file includes:
- **Privileged Mode**: Required for USB device access
- **Device Mounting**: Access to `/dev` for USB detection
- **System Mounts**: Access to `/sys`, `/proc` for device information
- **Volume Mounts**: Persistent storage for uploads and USB mounting

## 🛡️ Security Considerations

### File Upload Security
- **File Type Validation**: Only allowed file types can be uploaded
- **Size Limits**: Configurable maximum file size
- **Filename Sanitization**: Secure filename handling
- **Content Validation**: File content type verification

### USB Device Security
- **Mount Permissions**: Proper mount point permissions
- **Device Isolation**: USB devices are isolated in container
- **Error Handling**: Graceful handling of device disconnections

### Web Security
- **CSRF Protection**: Built-in CSRF token protection
- **Input Validation**: All user inputs are validated
- **Error Messages**: Secure error handling without information disclosure

## 🐛 Troubleshooting

### Common Issues

#### USB Device Not Detected
1. **Check Device Connection**: Ensure USB device is properly connected
2. **Refresh Devices**: Click "Refresh Devices" button
3. **Check Permissions**: Ensure proper USB device permissions
4. **Docker Permissions**: If using Docker, ensure privileged mode is enabled

#### Mount Permission Errors
1. **Sudo Access**: Ensure the application has sudo access for mounting
2. **Mount Point**: Check if `/media/usb` directory exists and has proper permissions
3. **Device Busy**: Ensure device is not already mounted elsewhere

#### File Upload Issues
1. **File Size**: Check if file exceeds maximum size limit (100MB)
2. **File Type**: Ensure file type is in allowed extensions list
3. **Disk Space**: Check available space on USB device
4. **Network**: Ensure stable network connection for large uploads

#### Docker Issues
1. **Privileged Mode**: Ensure container runs with `--privileged` flag
2. **Device Access**: Check if `/dev` is properly mounted
3. **Port Binding**: Verify port 55005 is not already in use

### Debug Mode

To enable debug mode for development:

```bash
# Set environment variable
export FLASK_ENV=development

# Or modify app.py
app.run(host='0.0.0.0', port=55005, debug=True)
```

## 🔄 Development

### Adding New Features

1. **Backend Changes**: Modify `app.py` and utility modules
2. **Frontend Changes**: Update templates and static files
3. **API Extensions**: Add new endpoints in `app.py`
4. **Styling**: Modify `static/css/style.css`

### Testing

```bash
# Run basic tests
python -m pytest

# Test USB functionality
python -c "from utils.usb_manager import USBManager; print(USBManager().get_available_devices())"

# Test file operations
python -c "from utils.file_operations import FileOperations; print(FileOperations().allowed_extensions)"
```

## 📈 Performance Optimization

### File Upload Optimization
- **Chunked Uploads**: Large files are uploaded in chunks
- **Progress Tracking**: Real-time upload progress
- **Background Processing**: Non-blocking file operations

### Memory Management
- **Streaming**: File operations use streaming for large files
- **Cleanup**: Temporary files are automatically cleaned up
- **Caching**: File metadata is cached for better performance

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes**: Add new functionality or fix bugs
4. **Test thoroughly**: Ensure all features work correctly
5. **Submit pull request**: Create a detailed pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Flask Community**: For the excellent web framework
- **Bootstrap Team**: For the responsive UI framework
- **Font Awesome**: For the comprehensive icon library
- **Docker Community**: For containerization tools

## 📞 Support

For support and questions:
- **Issues**: Create an issue on GitHub
- **Documentation**: Check this README and inline code comments
- **Community**: Join our community discussions

---

**Note**: This application requires root/sudo access for USB device mounting operations. Ensure proper security measures are in place when deploying in production environments. 