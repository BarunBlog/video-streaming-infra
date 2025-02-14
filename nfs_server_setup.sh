#!/bin/bash

# Install NFS server
sudo apt update && sudo apt install -y nfs-kernel-server

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
