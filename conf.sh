#!/bin/bash

echo "Installing Python and Dependencies..."
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install rpi-connect-lite
pip install pymysql --break-system-packages
pip install Flask --break-system-packages
pip install flask-sqlalchemy --break-system-packages
pip install flask-script --break-system-packages
pip install DateTime --break-system-packages
pip install os-sys --break-system-packages
pip install requests --break-system-packages
pip install xmltodict --break-system-packages
pip install netifaces --break-system-packages
pip3 install pyserial --break-system-packages
rpi-connect on
echo "Process Complete."

echo "Installing Minicom..."
sudo apt install minicom
echo "Minicom Installed."

sudo apt-get update
sudo apt-get upgrade