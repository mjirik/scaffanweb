# Nginx setup


Generate ssl key:
```bash
sudo mkdir /etc/nginx/certificate/
openssl req -new -sha256 -nodes -newkey rsa:4096 -keyout scaffan.kky.zcu.cz.key -out scaffan.kky.zcu.cz.csr
```