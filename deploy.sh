#!/bin/bash

yum install epel-release -y
yum install wget python3 git openvpn iptables openssl ca-certificates -y

cd /usr/share
git clone https://github.com/vitus133/rwar_vpn.git
cd rwar_vpn
openssl req -batch -x509 -newkey rsa:4096 -nodes -out src/cert.pem -keyout src/key.pem -days 3650
python3 -m venv environment
source environment/bin/activate
pip install --upgrade pip
cp service/rw-vpn.service /usr/lib/systemd/system/
cd src
pip install -r requirements.txt
systemctl daemon-reload
systemctl start rw-vpn.service
systemctl enable rw-vpn.service
