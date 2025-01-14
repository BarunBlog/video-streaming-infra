#!/bin/bash

# Exit on any error
set -e

# Variables (Update these as per your requirements)
POSTGRES_VERSION="16"
POSTGRES_USER="BarunAdmin"
POSTGRES_PASSWORD="1B2A456"
POSTGRES_DB="videostream_db"
PORT="5432"

echo "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

echo "Installing PostgreSQL $POSTGRES_VERSION..."
# Add PostgreSQL APT repository and install
sudo sh -c "echo 'deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main' > /etc/apt/sources.list.d/pgdg.list"
wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update -y
sudo apt install -y "postgresql-$POSTGRES_VERSION" "postgresql-client-$POSTGRES_VERSION"

echo "Configuring PostgreSQL for public access..."
# Edit postgresql.conf for listening on all IPs
sudo sed -i "s/^#listen_addresses =.*/listen_addresses = '*'/" /etc/postgresql/$POSTGRES_VERSION/main/postgresql.conf

# Edit pg_hba.conf to allow connections from all IPs
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf
echo "host    all             all             ::/0                    md5" | sudo tee -a /etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf

echo "Restarting PostgreSQL service..."
sudo systemctl restart postgresql

echo "Enabling PostgreSQL service on boot..."
sudo systemctl enable postgresql@$POSTGRES_VERSION-main

echo "Creating PostgreSQL user and database..."
# Switch to the postgres user to execute SQL commands
sudo -u postgres psql <<EOF
CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOF

echo "Configuring UFW to allow PostgreSQL traffic on port $PORT..."
# Optional: Configure UFW (adjust security groups as needed)
sudo ufw allow $PORT
sudo ufw enable

echo "PostgreSQL setup complete!"
echo "Details:"
echo "  Public IP: <YOUR_PUBLIC_IP>"
echo "  Port: $PORT"
echo "  Database: $POSTGRES_DB"
echo "  Username: $POSTGRES_USER"
echo "  Password: $POSTGRES_PASSWORD"

echo "Remember to configure your EC2 security group to allow traffic to port $PORT from your public IP!"
