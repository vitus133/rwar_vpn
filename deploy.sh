#!/bin/bash

yum install epel-release -y
yum install wget python3 git openvpn iptables openssl ca-certificates -y

cd /usr/share
git clone https://github.com/vitus133/rwar_vpn.git
cd rwar_vpn
tar xzf bin/EasyRSA-nix-3.0.5.tgz -C ~/
mv ~/EasyRSA-3.0.5/ /etc/openvpn/server/
mv /etc/openvpn/server/EasyRSA-3.0.5/ /etc/openvpn/server/easy-rsa/
chown -R root:root /etc/openvpn/server/easy-rsa/
cd /etc/openvpn/server/easy-rsa/
# Create the PKI, set up the CA and the server and client certificates
./easyrsa init-pki
./easyrsa --batch build-ca nopass
EASYRSA_CERT_EXPIRE=3650 ./easyrsa build-server-full server nopass
EASYRSA_CERT_EXPIRE=3650 ./easyrsa build-client-full client nopass
EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
# Move the stuff we need
cp pki/ca.crt pki/private/ca.key pki/issued/server.crt pki/private/server.key pki/crl.pem /etc/openvpn/server
# CRL is read with each client connection, when OpenVPN is dropped to nobody
chown nobody:nobody /etc/openvpn/server/crl.pem
# Generate key for tls-crypt
openvpn --genkey --secret /etc/openvpn/server/tc.key
# Create the DH parameters file using the predefined ffdhe2048 group

openssl dhparam -out /etc/openvpn/server/dh.pem 2048


cd /usr/share/rwar_vpn
# Install and start web server
openssl req -batch -x509 -newkey rsa:4096 -nodes -out src/cert.pem -keyout src/key.pem -days 3650
python3 -m venv environment
source environment/bin/activate
pip install --upgrade pip
cp service/rw_vpn.service /usr/lib/systemd/system/
pip install -r deploy_reqs.txt
systemctl daemon-reload
systemctl start rw_vpn.service
systemctl enable rw_vpn.service

# Create OpenVPN basic config