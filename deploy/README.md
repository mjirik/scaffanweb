# Nginx setup


Generate ssl key:
```bash
sudo mkdir /etc/nginx/certificate/
openssl req -new -x509 -sha256 -newkey rsa:2048 -nodes -keyout scaffan.kky.zcu.cz.key.pem -out scaffan.kky.zcu.cz.cert.pem
```