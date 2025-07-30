# Reverse USB Platform Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    util-linux \
    mount \
    udev \
    usbutils \
    libmagic1 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -s /bin/bash app && \
    echo "app ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Create necessary directories
RUN mkdir -p /media/usb /app /tmp/uploads && \
    chown -R app:app /media/usb /app /tmp/uploads

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R app:app /app && \
    chmod +x /app/app.py

# Create mount points and set permissions
RUN mkdir -p /media/usb && \
    chmod 755 /media/usb && \
    chown app:app /media/usb

# Switch to app user
USER app

# Expose port
EXPOSE 55005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:55005/ || exit 1

# Run the application
CMD ["python", "app.py"] 