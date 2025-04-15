#!/bin/bash

# Update package lists and fix missing packages
sudo apt update --fix-missing && sudo apt install -y nfs-kernel-server

# Verify if nfs-kernel-server is installed
if ! command -v exportfs &> /dev/null; then
    echo "Error: nfs-kernel-server installation failed."
    exit 1
fi

# Create a directory to store videos
sudo mkdir -p /mnt/shared_storage
sudo chown -R nobody:nogroup /mnt/shared_storage
sudo chmod 777 /mnt/shared_storage

# Configure NFS exports
echo "/mnt/shared_storage 10.0.0.0/16(rw,sync,no_root_squash,no_subtree_check)" | sudo tee -a /etc/exports

# Restart and enable NFS server on boot
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server

echo "NFS server setup completed successfully!"
