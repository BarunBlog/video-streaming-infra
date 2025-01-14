#!/bin/bash

# Update package list
sudo apt-get update -y

# Install Docker (if not already installed)
sudo apt-get install -y docker.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Give docker-compose executable permissions
sudo chmod +x /usr/local/bin/docker-compose

# Check the installation of docker-compose
docker-compose --version

# Start Docker and enable Docker on boot
sudo systemctl start docker
sudo systemctl enable docker

# Add the current user to the Docker group to run docker without sudo
sudo usermod -aG docker $USER

# Restart Docker
sudo systemctl restart docker
