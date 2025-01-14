#!/bin/bash

# Variables for customization
REDIS_USER="BarunAdmin"
REDIS_PASSWORD="Barun@1234"

# Update and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential tcl wget

# Download and extract Redis
REDIS_VERSION="6.2.6"
wget http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz

tar xzf redis-$REDIS_VERSION.tar.gz
cd redis-$REDIS_VERSION

# Build and install Redis
make
sudo make install

# Create directories and copy files
sudo mkdir -p /etc/redis /var/lib/redis
sudo cp redis.conf /etc/redis/

# Update Redis configuration to allow external connections
sudo sed -i "s/^bind 127.0.0.1 -::1/bind 0.0.0.0/" /etc/redis/redis.conf
sudo sed -i "s/^# requirepass .*/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf  # Optional: set a password
sudo sed -i "s/^protected-mode yes/protected-mode no/" /etc/redis/redis.conf
sudo sed -i "s@^dir ./@dir /var/lib/redis@" /etc/redis/redis.conf

# Create a systemd service file
cat <<EOF | sudo tee /etc/systemd/system/redis.service
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=$REDIS_USER
Group=$REDIS_USER
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create a Redis user and set permissions
sudo adduser --system --group --no-create-home $REDIS_USER
sudo chown $REDIS_USER:$REDIS_USER /var/lib/redis
sudo chmod 770 /var/lib/redis
sudo chown $REDIS_USER:$REDIS_USER /etc/redis/redis.conf

# Start and enable Redis service
sudo systemctl daemon-reload
sudo systemctl start redis
sudo systemctl enable redis

# Print Redis status
sudo systemctl status redis

echo "Redis has been installed and configured to accept external connections."
