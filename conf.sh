#!/bin/bash

echo "Installing Python and Dependencies..."
sudo apt-get install python3
sudo apt-get install python3-pip
echo "Process Complete."

echo "Installing Minicom..."
sudo apt install minicom
echo "Minicom Installed."

wget "https://assist.zoho.eu/api/v2/install_urs?type=2&encapiKey=yA6Kbntb7AT1xTlXFRJr05mC%2B4g4rvhv3inltijnLs10LoG12qFp0BdtdoS9IzfTjY6A460AOo8XJYi%2F6N1fKpE3MtZVKJTGTuv4P2uV48xhudyNcNsuhJyoA7EQEqNLcBIi&app=linux&version=arm64&isDebian=true" -O zohoassist_1.0.0.1.deb
sudo dpkg -i zohoassist_1.0.0.1.deb
echo "Zoho Assist Installed."

sudo apt-get update
sudo apt-get full-upgrade