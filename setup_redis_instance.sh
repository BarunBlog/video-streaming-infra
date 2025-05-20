#!/bin/bash

set -e

REDIS_PORT=6379
REDIS_CLUSTER_CONFIG_FILE="nodes.conf"
REDIS_CLUSTER_LOG="/var/log/redis.log"
REDIS_CONF="/etc/redis/redis.conf"

echo "==== Installing Redis ===="
sudo apt update
sudo apt install -y redis-server

echo "==== Backing up original config ===="
sudo cp $REDIS_CONF ${REDIS_CONF}.backup

echo "==== Editing redis.conf for cluster ===="

sudo sed -i "s/^bind 127.0.0.1 -::1/bind 0.0.0.0/" $REDIS_CONF
sudo sed -i "s/^protected-mode .*/protected-mode no/" $REDIS_CONF
#sudo sed -i "s/^port 6379/port $REDIS_PORT/" $REDIS_CONF

# Enable cluster mode
sudo sed -i "s/^#* *cluster-enabled .*/cluster-enabled yes/" $REDIS_CONF
sudo sed -i "s/^#* *cluster-config-file .*/cluster-config-file $REDIS_CLUSTER_CONFIG_FILE/" $REDIS_CONF
sudo sed -i "s/^#* *cluster-node-timeout .*/cluster-node-timeout 5000/" $REDIS_CONF

# Enable appendonly
sudo sed -i "s/^#* *appendonly .*/appendonly yes/" $REDIS_CONF

# Set logfile
#sudo sed -i "s|^#* *logfile .*|logfile \"$REDIS_CLUSTER_LOG\"|" $REDIS_CONF

# Remove daemonize line if present (systemd needs it non-daemonized)
#sudo sed -i "/^daemonize /d" $REDIS_CONF

echo "==== Creating cluster config file ===="
sudo touch /etc/redis/$REDIS_CLUSTER_CONFIG_FILE
sudo chown redis:redis /etc/redis/$REDIS_CLUSTER_CONFIG_FILE

echo "==== Restarting Redis via systemd ===="
sudo systemctl restart redis-server
sudo systemctl enable redis-server

echo "==== Opening necessary ports ===="
sudo ufw allow $REDIS_PORT
sudo ufw allow $((REDIS_PORT+10000))  # Cluster bus port

echo "==== DONE! Redis is running and ready for clustering ===="
