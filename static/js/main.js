/**
 * Reverse USB Platform - Main JavaScript
 * Handles USB device management, file operations, and UI interactions
 */

class USBPlatform {
    constructor() {
        this.currentPath = '';
        this.currentView = 'grid';
        this.selectedFiles = new Set();
        this.contextMenu = null;
        this.toast = null;
        this.modal = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.loadUSBDevices();
        this.loadUSBStatus();
        this.loadFiles();
    }
    
    setupEventListeners() {
        // USB Device Management
        document.getElementById('refresh-devices-btn').addEventListener('click', () => {
            this.loadUSBDevices();
        });
        
        // File Browser
        document.getElementById('view-grid-btn').addEventListener('click', () => {
            this.setView('grid');
        });
        
        document.getElementById('view-list-btn').addEventListener('click', () => {
            this.setView('list');
        });
        
        document.getElementById('new-folder-btn').addEventListener('click', () => {
            this.showCreateFolderModal();
        });
        
        // File Search
        document.getElementById('file-search').addEventListener('input', (e) => {
            this.filterFiles(e.target.value);
        });
        
        // Upload Functionality
        this.setupUploadListeners();
        
        // Context Menu
        this.setupContextMenu();
        
        // Dark Mode Toggle
        document.getElementById('dark-mode-toggle').addEventListener('click', () => {
            this.toggleDarkMode();
        });
        
        // Refresh Button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshAll();
        });
        
        // Global Click Handler
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.context-menu')) {
                this.hideContextMenu();
            }
        });
    }
    
    initializeComponents() {
        // Initialize Bootstrap components
        this.toast = new bootstrap.Toast(document.getElementById('notification-toast'));
        this.modal = new bootstrap.Modal(document.getElementById('fileModal'));
        
        // Initialize context menu
        this.contextMenu = document.getElementById('context-menu');
    }
    
    setupUploadListeners() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        
        // Drag and Drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.uploadFiles(files);
        });
        
        // File Input
        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            this.uploadFiles(files);
        });
        
        // Click to browse
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    setupContextMenu() {
        // Context menu event listeners
        document.addEventListener('contextmenu', (e) => {
            const fileItem = e.target.closest('.file-item, .folder-item');
            if (fileItem) {
                e.preventDefault();
                this.showContextMenu(e, fileItem);
            }
        });
        
        // Context menu actions
        document.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const action = item.dataset.action;
                const targetFile = this.contextMenu.dataset.targetFile;
                this.handleContextMenuAction(action, targetFile);
                this.hideContextMenu();
            });
        });
    }
    
    async loadUSBDevices() {
        try {
            this.showLoading();
            const response = await fetch('/api/usb/devices');
            const data = await response.json();
            
            if (data.success) {
                this.renderUSBDevices(data.devices);
            } else {
                this.showNotification('Error loading USB devices', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to load USB devices', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    renderUSBDevices(devices) {
        const container = document.getElementById('usb-devices-list');
        
        if (devices.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-usb fa-2x mb-2"></i>
                    <p>No USB devices found</p>
                    <small>Connect a USB drive and click refresh</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = devices.map(device => `
            <div class="usb-device ${device.mountpoint ? 'mounted' : ''}" data-device="${device.name}">
                <div class="usb-device-info">
                    <div class="usb-device-icon">
                        <i class="fas fa-hdd"></i>
                    </div>
                    <div class="usb-device-details">
                        <h6>${device.label || 'USB Device'}</h6>
                        <small>${device.name} • ${device.size}</small>
                    </div>
                </div>
                <div class="d-flex gap-2">
                    ${device.mountpoint ? 
                        `<button class="btn btn-sm btn-outline-danger" onclick="usbPlatform.unmountDevice()">
                            <i class="fas fa-eject me-1"></i>Unmount
                        </button>` :
                        `<button class="btn btn-sm btn-outline-success" onclick="usbPlatform.mountDevice('${device.name}')">
                            <i class="fas fa-plug me-1"></i>Mount
                        </button>`
                    }
                </div>
            </div>
        `).join('');
    }
    
    async mountDevice(deviceName) {
        try {
            this.showLoading();
            const response = await fetch(`/api/usb/mount/${deviceName}`);
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Success', `Device ${deviceName} mounted successfully`, 'success');
                this.loadUSBDevices();
                this.loadUSBStatus();
                this.loadFiles();
            } else {
                this.showNotification('Error', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to mount device', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async unmountDevice() {
        try {
            this.showLoading();
            const response = await fetch('/api/usb/unmount', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Success', 'USB device unmounted successfully', 'success');
                this.loadUSBDevices();
                this.loadUSBStatus();
                this.loadFiles();
            } else {
                this.showNotification('Error', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to unmount device', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async loadUSBStatus() {
        try {
            const response = await fetch('/api/usb/status');
            const data = await response.json();
            
            if (data.success) {
                this.renderUSBStatus(data.status);
            }
        } catch (error) {
            console.error('Error loading USB status:', error);
        }
    }
    
    renderUSBStatus(status) {
        const container = document.getElementById('usb-status');
        
        if (!status.mounted) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <div class="status-indicator disconnected"></div>
                    <span>No device mounted</span>
                </div>
            `;
            return;
        }
        
        const usagePercent = status.usage_percent;
        const usageClass = usagePercent > 90 ? 'danger' : usagePercent > 75 ? 'warning' : '';
        
        container.innerHTML = `
            <div class="mb-2">
                <div class="status-indicator connected"></div>
                <span>Device mounted</span>
            </div>
            <div class="space-usage">
                <div class="d-flex justify-content-between mb-1">
                    <small>Storage Usage</small>
                    <small>${usagePercent}%</small>
                </div>
                <div class="space-bar">
                    <div class="space-used ${usageClass}" style="width: ${usagePercent}%"></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                    <small>${this.formatBytes(status.used_space)} used</small>
                    <small>${this.formatBytes(status.free_space)} free</small>
                </div>
            </div>
        `;
    }
    
    async loadFiles() {
        try {
            const response = await fetch(`/api/usb/files?path=${this.currentPath}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderFiles(data.files);
                this.updateBreadcrumb();
            } else {
                this.renderNoFiles(data.error);
            }
        } catch (error) {
            this.renderNoFiles('Failed to load files');
        }
    }
    
    renderFiles(files) {
        const container = document.getElementById('files-container');
        
        if (files.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-folder-open fa-3x mb-3"></i>
                    <h5>No files found</h5>
                    <p>This folder is empty</p>
                </div>
            `;
            return;
        }
        
        const filesHtml = files.map(file => this.renderFileItem(file)).join('');
        container.innerHTML = `<div class="files-${this.currentView}">${filesHtml}</div>`;
        
        // Add event listeners to file items
        container.querySelectorAll('.file-item, .folder-item').forEach(item => {
            this.addFileItemListeners(item);
        });
    }
    
    renderFileItem(file) {
        const iconClass = this.getFileIconClass(file.icon);
        const template = file.is_directory ? 'folder-template' : 'file-template';
        const templateElement = document.getElementById(template);
        const clone = templateElement.content.cloneNode(true);
        
        const item = clone.querySelector(file.is_directory ? '.folder-item' : '.file-item');
        item.dataset.filePath = file.path;
        item.dataset.fileName = file.name;
        
        const iconElement = item.querySelector('.file-icon i, .folder-icon i');
        iconElement.className = iconClass;
        
        const nameElement = item.querySelector('.file-name, .folder-name');
        nameElement.textContent = file.name;
        
        const metaElement = item.querySelector('.file-meta, .folder-meta');
        if (file.is_directory) {
            metaElement.innerHTML = `<span>Folder</span>`;
        } else {
            metaElement.innerHTML = `
                <span>${file.human_size}</span>
                <span>•</span>
                <span>${new Date(file.modified).toLocaleDateString()}</span>
            `;
        }
        
        return item.outerHTML;
    }
    
    getFileIconClass(iconType) {
        const iconMap = {
            'folder': 'fas fa-folder',
            'image': 'fas fa-file-image',
            'pdf': 'fas fa-file-pdf',
            'word': 'fas fa-file-word',
            'excel': 'fas fa-file-excel',
            'powerpoint': 'fas fa-file-powerpoint',
            'video': 'fas fa-file-video',
            'audio': 'fas fa-file-audio',
            'archive': 'fas fa-file-archive',
            'code': 'fas fa-file-code',
            'text': 'fas fa-file-text',
            'file': 'fas fa-file'
        };
        
        return iconMap[iconType] || 'fas fa-file';
    }
    
    addFileItemListeners(item) {
        // Click to open/download
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.file-actions, .folder-actions')) {
                const path = item.dataset.filePath;
                const isDirectory = item.classList.contains('folder-item');
                
                if (isDirectory) {
                    this.navigateToFolder(path);
                } else {
                    this.downloadFile(path);
                }
            }
        });
        
        // Action buttons
        const actionButtons = item.querySelectorAll('.file-action-btn, .folder-action-btn');
        actionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.title.toLowerCase();
                const path = item.dataset.filePath;
                this.handleFileAction(action, path);
            });
        });
    }
    
    async handleFileAction(action, filePath) {
        switch (action) {
            case 'download':
                this.downloadFile(filePath);
                break;
            case 'rename':
                this.showRenameModal(filePath);
                break;
            case 'delete':
                this.showDeleteModal(filePath);
                break;
        }
    }
    
    downloadFile(filePath) {
        window.open(`/api/usb/download/${encodeURIComponent(filePath)}`, '_blank');
    }
    
    navigateToFolder(folderPath) {
        this.currentPath = folderPath;
        this.loadFiles();
    }
    
    updateBreadcrumb() {
        const breadcrumb = document.getElementById('file-breadcrumb');
        const paths = this.currentPath.split('/').filter(p => p);
        
        let html = `
            <li class="breadcrumb-item">
                <a href="#" data-path="" class="breadcrumb-link">
                    <i class="fas fa-home"></i> Root
                </a>
            </li>
        `;
        
        let currentPath = '';
        paths.forEach((path, index) => {
            currentPath += (currentPath ? '/' : '') + path;
            html += `
                <li class="breadcrumb-item">
                    <a href="#" data-path="${currentPath}" class="breadcrumb-link">${path}</a>
                </li>
            `;
        });
        
        breadcrumb.innerHTML = html;
        
        // Add click listeners
        breadcrumb.querySelectorAll('.breadcrumb-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const path = link.dataset.path;
                this.currentPath = path;
                this.loadFiles();
            });
        });
    }
    
    setView(view) {
        this.currentView = view;
        
        // Update button states
        document.getElementById('view-grid-btn').classList.toggle('active', view === 'grid');
        document.getElementById('view-list-btn').classList.toggle('active', view === 'list');
        
        // Reload files with new view
        this.loadFiles();
    }
    
    filterFiles(query) {
        const items = document.querySelectorAll('.file-item, .folder-item');
        const searchTerm = query.toLowerCase();
        
        items.forEach(item => {
            const fileName = item.dataset.fileName.toLowerCase();
            const isVisible = fileName.includes(searchTerm);
            item.style.display = isVisible ? '' : 'none';
        });
    }
    
    async uploadFiles(files) {
        if (files.length === 0) return;
        
        const uploadProgress = document.getElementById('upload-progress');
        const uploadArea = document.getElementById('upload-area');
        const progressBar = uploadProgress.querySelector('.progress-bar');
        
        uploadArea.classList.add('d-none');
        uploadProgress.classList.remove('d-none');
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const progress = ((i + 1) / files.length) * 100;
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/usb/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Success', `${file.name} uploaded successfully`, 'success');
                } else {
                    this.showNotification('Error', `Failed to upload ${file.name}: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showNotification('Error', `Failed to upload ${file.name}`, 'error');
            }
            
            progressBar.style.width = `${progress}%`;
        }
        
        // Reset upload area
        uploadArea.classList.remove('d-none');
        uploadProgress.classList.add('d-none');
        progressBar.style.width = '0%';
        
        // Reload files
        this.loadFiles();
    }
    
    showContextMenu(e, targetElement) {
        const rect = targetElement.getBoundingClientRect();
        this.contextMenu.style.display = 'block';
        this.contextMenu.style.left = e.pageX + 'px';
        this.contextMenu.style.top = e.pageY + 'px';
        this.contextMenu.dataset.targetFile = targetElement.dataset.filePath;
    }
    
    hideContextMenu() {
        this.contextMenu.style.display = 'none';
    }
    
    async handleContextMenuAction(action, filePath) {
        switch (action) {
            case 'open':
                this.navigateToFolder(filePath);
                break;
            case 'download':
                this.downloadFile(filePath);
                break;
            case 'rename':
                this.showRenameModal(filePath);
                break;
            case 'delete':
                this.showDeleteModal(filePath);
                break;
        }
    }
    
    showCreateFolderModal() {
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const confirmBtn = document.getElementById('modalConfirmBtn');
        
        modalTitle.textContent = 'Create New Folder';
        modalBody.innerHTML = `
            <div class="mb-3">
                <label for="folder-name" class="form-label">Folder Name</label>
                <input type="text" class="form-control" id="folder-name" placeholder="Enter folder name">
            </div>
        `;
        
        confirmBtn.onclick = () => this.createFolder();
        this.modal.show();
    }
    
    async createFolder() {
        const folderName = document.getElementById('folder-name').value.trim();
        
        if (!folderName) {
            this.showNotification('Error', 'Please enter a folder name', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/usb/folders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    folder_name: folderName,
                    parent_path: this.currentPath
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Success', `Folder "${folderName}" created successfully`, 'success');
                this.modal.hide();
                this.loadFiles();
            } else {
                this.showNotification('Error', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to create folder', 'error');
        }
    }
    
    showRenameModal(filePath) {
        const fileName = filePath.split('/').pop();
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const confirmBtn = document.getElementById('modalConfirmBtn');
        
        modalTitle.textContent = 'Rename File';
        modalBody.innerHTML = `
            <div class="mb-3">
                <label for="new-name" class="form-label">New Name</label>
                <input type="text" class="form-control" id="new-name" value="${fileName}">
            </div>
        `;
        
        confirmBtn.onclick = () => this.renameFile(filePath);
        this.modal.show();
    }
    
    async renameFile(oldPath) {
        const newName = document.getElementById('new-name').value.trim();
        
        if (!newName) {
            this.showNotification('Error', 'Please enter a new name', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/usb/files/${encodeURIComponent(oldPath)}/rename`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    new_name: newName
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Success', 'File renamed successfully', 'success');
                this.modal.hide();
                this.loadFiles();
            } else {
                this.showNotification('Error', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to rename file', 'error');
        }
    }
    
    showDeleteModal(filePath) {
        const fileName = filePath.split('/').pop();
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const confirmBtn = document.getElementById('modalConfirmBtn');
        
        modalTitle.textContent = 'Delete File';
        modalBody.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Are you sure you want to delete "${fileName}"?
                <br><small class="text-muted">This action cannot be undone.</small>
            </div>
        `;
        
        confirmBtn.onclick = () => this.deleteFile(filePath);
        this.modal.show();
    }
    
    async deleteFile(filePath) {
        try {
            const response = await fetch(`/api/usb/files/${encodeURIComponent(filePath)}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Success', 'File deleted successfully', 'success');
                this.modal.hide();
                this.loadFiles();
            } else {
                this.showNotification('Error', data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error', 'Failed to delete file', 'error');
        }
    }
    
    renderNoFiles(message) {
        const container = document.getElementById('files-container');
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <h5>Unable to load files</h5>
                <p>${message}</p>
            </div>
        `;
    }
    
    showNotification(title, message, type = 'info') {
        const toastTitle = document.getElementById('toast-title');
        const toastMessage = document.getElementById('toast-message');
        
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        
        const toastElement = document.getElementById('notification-toast');
        toastElement.className = `toast ${type === 'error' ? 'bg-danger text-white' : ''}`;
        
        this.toast.show();
    }
    
    showLoading() {
        document.getElementById('loading-overlay').classList.remove('d-none');
    }
    
    hideLoading() {
        document.getElementById('loading-overlay').classList.add('d-none');
    }
    
    toggleDarkMode() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.showNotification('Theme Changed', `${newTheme.charAt(0).toUpperCase() + newTheme.slice(1)} mode enabled`, 'success');
    }
    
    refreshAll() {
        this.loadUSBDevices();
        this.loadUSBStatus();
        this.loadFiles();
        this.showNotification('Refreshed', 'All data has been refreshed', 'success');
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
    
    // Initialize the platform
    window.usbPlatform = new USBPlatform();
}); 