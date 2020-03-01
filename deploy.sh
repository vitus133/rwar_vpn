#!/bin/bash

yum install epel-release -y
yum install wget python3 git openvpn iptables openssl ca-certificates -y

cd /usr/share
git clone https://github.com/vitus133/rwar_vpn.git
cd rwar_vpn
sleep 1
tar xzf bin/EasyRSA-nix-3.0.5.tgz
mv EasyRSA-3.0.5 /etc/openvpn/server/
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
public_ip=$(curl -4Ls "http://whatismyip.akamai.com/")
protocol="udp"
port="1194"
# Generate server.conf
echo "local $public_ip
port $port
proto $protocol
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh.pem
auth SHA512
tls-crypt tc.key
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt" > /etc/openvpn/server/server.conf
echo 'push "redirect-gateway def1 bypass-dhcp"' >> /etc/openvpn/server/server.conf
# DNS
echo 'push "dhcp-option DNS 1.1.1.1"' >> /etc/openvpn/server/server.conf
echo 'push "dhcp-option DNS 1.0.0.1"' >> /etc/openvpn/server/server.conf
echo "keepalive 10 120
cipher AES-256-CBC
user nobody
group nobody
persist-key
persist-tun
status openvpn-status.log
verb 3
crl-verify crl.pem" >> /etc/openvpn/server/server.conf
echo "explicit-exit-notify" >> /etc/openvpn/server/server.conf
# Enable net.ipv4.ip_forward for the system
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/30-openvpn-forward.conf
# Enable without waiting for a reboot or service restart
echo 1 > /proc/sys/net/ipv4/ip_forward
# Create a service to set up persistent iptables rules
echo "[Unit]
Before=network.target
[Service]
Type=oneshot
ExecStart=/sbin/iptables -t nat -A POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $public_ip
ExecStart=/sbin/iptables -I INPUT -p $protocol --dport $port -j ACCEPT
ExecStart=/sbin/iptables -I FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStart=/sbin/iptables -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
ExecStop=/sbin/iptables -t nat -D POSTROUTING -s 10.8.0.0/24 ! -d 10.8.0.0/24 -j SNAT --to $public_ip
ExecStop=/sbin/iptables -D INPUT -p $protocol --dport $port -j ACCEPT
ExecStop=/sbin/iptables -D FORWARD -s 10.8.0.0/24 -j ACCEPT
ExecStop=/sbin/iptables -D FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target" > /etc/systemd/system/openvpn-iptables.service
systemctl enable --now openvpn-iptables.service

# client-common.txt is created so we have a template to add further users later
echo "client
dev tun
proto $protocol
remote $public_ip $port
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
cipher AES-256-CBC
ignore-unknown-option block-outside-dns
block-outside-dns
verb 3" > /etc/openvpn/server/client-common.txt
# Enable and start the OpenVPN service
systemctl enable --now openvpn-server@server.service
new_client () {
	# Generates the custom client.ovpn
	{
	cat /etc/openvpn/server/client-common.txt
	echo "<ca>"
	cat /etc/openvpn/server/easy-rsa/pki/ca.crt
	echo "</ca>"
	echo "<cert>"
	sed -ne '/BEGIN CERTIFICATE/,$ p' /etc/openvpn/server/easy-rsa/pki/issued/"$1".crt
	echo "</cert>"
	echo "<key>"
	cat /etc/openvpn/server/easy-rsa/pki/private/"$1".key
	echo "</key>"
	echo "<tls-crypt>"
	sed -ne '/BEGIN OpenVPN Static key/,$ p' /etc/openvpn/server/tc.key
	echo "</tls-crypt>"
	} > ~/"$1".ovpn
}
new_client "client"

cd /usr/share/rwar_vpn
# Install and start web server
openssl req -batch -x509 -newkey rsa:4096 -nodes -out src/cert.pem -keyout src/key.pem -days 3650
python3 -m venv environment
source environment/bin/activate
pip install --upgrade pip
pip install -e .
cp service/rw_vpn.service /usr/lib/systemd/system/
pip install -r deploy_reqs.txt
systemctl daemon-reload
systemctl start rw_vpn.service
systemctl enable rw_vpn.service

# Create OpenVPN basic config