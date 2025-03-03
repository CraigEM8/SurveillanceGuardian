#!/bin/bash

echo "Installing Python and Dependencies..."
sudo apt-get install python3
pip install pymysql --break-system-packages
pip install Flask==3.1.0 --break-system-packages
pip install flask-sqlalchemy==3.0.0 --break-system-packages
pip install flask-script==2.0.6 --break-system-packages
pip install DateTime==5.5 --break-system-packages
pip install os-sys==2.1.4 --break-system-packages
pip install requests==2.32.3 --break-system-packages
pip install xmltodict==0.14.2 --break-system-packages
pip install netifaces --break-system-packages
echo "Process Complete."

echo "Installing Minicom..."
sudo apt install minicom
echo "Minicom Installed."

sudo apt-get update
sudo apt-get upgrade