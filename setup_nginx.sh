#!/bin/bash

# Update and install Nginx
echo "Updating package list and installing Nginx..."
sudo apt update -y
sudo apt install nginx -y

# Enable Nginx to start on boot
echo "Enabling Nginx service to start on boot..."
sudo systemctl enable nginx

# Stop Nginx to replace the configuration
echo "Stopping Nginx service to update configuration..."
sudo systemctl stop nginx

# Copy the provided nginx.conf file
echo "Copying the provided Nginx configuration file..."
NGINX_CONF_SRC="./nginx.conf"  # Path to the local nginx.conf
NGINX_CONF_DEST="/etc/nginx/sites-available/django_load_balancer"
NGINX_LINK="/etc/nginx/sites-enabled/django_load_balancer"

if [ -f $NGINX_CONF_SRC ]; then
    sudo cp $NGINX_CONF_SRC $NGINX_CONF_DEST
else
    echo "Error: nginx.conf file not found at $NGINX_CONF_SRC"
    exit 1
fi

# Remove default symlink and create a new one
echo "Setting up the Nginx site configuration..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s $NGINX_CONF_DEST $NGINX_LINK

# Start Nginx service
echo "Starting Nginx service..."
sudo systemctl start nginx

# Restart Nginx to apply changes
echo "Restarting Nginx to apply changes..."
sudo systemctl restart nginx

# Display Nginx status
echo "Nginx setup completed. Displaying service status:"
sudo systemctl status nginx
