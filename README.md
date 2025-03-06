Surveillance Guardian

Install Guide

sudo apt-get git

git clone https://github.com/CraigEM8/SurveillanceGuardian.git

Run AutoConf.sh, add permissions if needed.

sudo raspi-config

sudo cp /home/surveillance_guardian_***/SurveillanceGuardian/clipper /etc/ppp/clipper

sudo pon clipper

