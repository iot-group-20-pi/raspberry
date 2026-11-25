# RaspberryPi 5 for IoT project

## Note for later research

Maybe use Raspberry OS Lite (without desktop environment) for better efficiency, but will it effect something else?

## Initialization

### Update packages

```sh
sudo apt update
sudo apt upgrade
```

### Use ZSH

```sh
# zsh for better autocomplete
sudo apt install zsh

# omz as zsh plugins manager
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
omz plugin enable fast-syntax-highlighting zsh-syntax-highlighting zsh-autosuggestions

# (Optional) Add the following line to ~/.zshrc
# typeset -g ZSH_AUTOSUGGEST_STRATEGY=(completion)
```

### Setup remote development

```sh
# Tailscale for remote ssh
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key=tskey-auth-...
tailscale set --ssh
```

```sh
# Neovim for remote IDE
curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux-arm64.tar.gz
sudo rm -rf /opt/nvim-linux-arm64
sudo tar -C /opt -xzf nvim-linux-arm64.tar.gz

echo "export PATH=\"\$PATH:/opt/nvim-linux-arm64/bin\"" | tee -a ~/.zshrc

# LazyVim for neovim plugins
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
```

## Object Detection

### Useful documentations

<https://docs.ultralytics.com/guides/raspberry-pi>  
<https://docs.ultralytics.com/modes/predict>

### Export model to NCNN format

See [YOLO export usage](https://docs.ultralytics.com/modes/export) to optionally quantize the model.

```sh
# Export a YOLO26n PyTorch model to NCNN format
yolo export model=yolo26n.pt format=ncnn # creates 'yolo26n_ncnn_model'

# Run inference with the exported model
yolo predict model='yolo26n_ncnn_model' source='https://ultralytics.com/images/bus.jpg'
```

### Test the application

```sh
uv run src/app.py model/yolo26n_ncnn_model
```

## MQTT Setup

### Server

#### Setup Mosquitto

##### Local

See <https://mosquitto.org/download/>

##### EC2 (Amazon Linux 2023)

Copied from <https://aws.plainenglish.io/installing-mosquitto-on-amazon-linux-2023-114956dd79d1>

```sh
sudo su
yum update
yum install -y cmake openssl-devel libxslt
yum groupinstall -y "Development Tools"

git clone https://github.com/DaveGamble/cJSON.git
cd cJSON
cmake . && make && make install
cd ..

useradd -r -U mosquitto

wget https://mosquitto.org/files/source/mosquitto-2.0.21.tar.gz
tar -xvzf mosquitto-2.0.21.tar.gz && sudo rm mosquitto-2.0.21.tar.gz
cd mosquitto-2.0.21
cmake . && make && make install
```

#### Config

If no domain name is available, use pre-defined host like `mqtt.server` for the common name in certificate creation.
Also edit the `/etc/hosts` in raspberry pi to point to the EC2 instance IP address.

```txt
# /etc/hosts on raspberry pi or other client
# Change to the EC2 server IP address
1.1.1.1 mqtt.server
```

```sh
# Make sure to stay on root user permission

mkdir /etc/mosquitto
cd /etc/mosquitto

# Create username/password
mosquitto_passwd -c pwfile username

# SSL/TLS
## Certificate Authority (remember CA password)
mkdir ca_certificates
openssl req -new -x509 -days 30 -extensions v3_ca \
-keyout ca_certificates/ca.key \
-out ca_certificates/ca.crt

## Server Certificate (remember server password)
mkdir certs
openssl genrsa -aes256 -out certs/server.key 2048
openssl req -out server.csr -key certs/server.key -new
openssl x509 -req -in server.csr \
-CA ca_certificates/ca.crt -CAkey ca_certificates/ca.key \
-CAcreateserial -out certs/server.crt -days 15
```

Copy to `mosquitto.conf`

```conf
user mosquitto
listener 8883

cafile /etc/mosquitto/ca_certificates/ca.crt
require_certificate true

certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

per_listener_settings true

allow_anonymous false
password_file /etc/mosquitto/pwfile
```

#### Start Service

```sh
# Change owner permission to mosquitto user
chown -R mosquitto:mosquitto .

# Use the server password
mosquitto -c mosquitto.conf
```

To set it as system service so it starts automatically on reboot,  
Copy to `/etc/systemd/system/mosquitto.service`

```mosquitto.service
[Unit]
Description=Mosquitto service
Documentation=man:mosquitto(8)
Documentation=man:mosquitto.conf(5)
ConditionPathExists=/etc/mosquitto/mosquitto.conf
Requires=network.target

[Service]
ExecStart=/usr/local/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
ExecReload=/bin/kill -HUP $MAINPID
User=mosquitto
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

And run

```sh
# Remove PEM passphrase from the key to fix service hanging
openssl rsa -in certs/server.key -out certs/server.key

systemctl enable mosquitto.service
systemctl start mosquitto.service

systemctl status mosquitto.service
```

### Client

#### Config

```sh
# Copy the ca.crt and ca.key to mosquitto directory
## If generated on ec2 instance (or just cat it and copy)
## The following command may not work because of permission conflict
scp -i key.pem ec2-user@mqtt.server:/etc/mosquitto/ca_certificates/ca.crt ca.crt
scp -i key.pem ec2-user@mqtt.server:/etc/mosquitto/ca_certificates/ca.key ca.key

# Client Certificate (remember client password)
openssl genrsa -aes256 -out client.key 2048
openssl req -out client.csr -key client.key -new
openssl x509 -req -in client.csr \
-CA ca.crt -CAkey ca.key \
-CAcreateserial -out client.crt -days 15

# Test Connection (use client password)
mosquitto_sub -h mqtt.server -t test -u username -P password \
--cafile ca.crt --cert client.crt --key client.key

mosquitto_pub -m test -h mqtt.server -t test -u username -P password \
--cafile ca.crt --cert client.crt --key client.key
```

Update `.env`

```env
MQTT_HOSTNAME="mqtt.server"
MQTT_PORT="8883"
MQTT_USERNAME="username"
MQTT_PASSWORD="password"
MQTT_CACERTS="mosquitto/ca.crt"
MQTT_CERTFILE="mosquitto/client.crt"
MQTT_KEYFILE="mosquitto/client.key"
MQTT_KEYFILE_PASSWORD="client"
```

Test Application

```sh
uv run src/mqtt_subscribe.py
uv run src/mqtt_publish.py
```

## AWS S3 Setup

1. Create S3 bucket
2. Create a user with the S3 permission to `put object` (if directory bucket also S3 express `create session`)
3. Copy access key ID and secret access key to `.env`

```env
BUCKET_NAME="pi"

AWS_REGION_NAME="ap-southeast-1"
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
```
