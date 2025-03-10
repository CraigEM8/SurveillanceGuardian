#!/bin/bash

echo "Installing Python and Dependencies..."
sudo apt-get install python3
sudo apt-get install python3-pip
echo "Process Complete."

echo "Installing Minicom..."
sudo apt install minicom
echo "Minicom Installed."

sudo apt-get update
sudo apt-get full-upgrade