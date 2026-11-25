# MQTT

## Setup the certificate

Download the CA certificate (`ca.crt`) and key (`ca.key`) to this directory.

```sh
openssl genrsa -aes256 -out client.key 2048
openssl req -out client.csr -key client.key -new
sudo openssl x509 -req -in client.csr \
-CA ca.crt -CAkey ca.key \
-CAcreateserial -out client.crt -days 15
```

## Test connection

```sh
uv run src/mqtt_subscribe.py
uv run src/mqtt_publish.py
```
