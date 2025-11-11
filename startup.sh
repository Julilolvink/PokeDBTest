#!/usr/bin/env bash
set -e

# Install ODBC Driver 18 so pyodbc can talk to Azure SQL
apt-get update
apt-get install -y curl apt-transport-https gnupg ca-certificates
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# Debian 12 base for App Service Python images. If it changes, adjust the line below.
echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# Ensure deps are installed (App Service caches but this is safe)
pip install --upgrade pip
pip install -r requirements.txt

# Start Gunicorn (App Service sets $PORT)
exec gunicorn --bind=0.0.0.0:${PORT:-8000} run:app
