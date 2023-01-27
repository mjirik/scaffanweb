  
[![Build Status](https://travis-ci.org/mjirik/scaffanweb.svg?branch=master)](https://travis-ci.org/mjirik/scaffanweb)
[![Coverage Status](https://coveralls.io/repos/github/mjirik/scaffanweb/badge.svg?branch=master)](https://coveralls.io/github/mjirik/scaffanweb?branch=master)
[![PyPI version](https://badge.fury.io/py/scaffanweb.svg)](http://badge.fury.io/py/scaffanweb)


scaffanweb

Web application for scaffold analysis from H&E stained images

# Install with docker-compose

```bash
git clone git@github.com:mjirik/scaffan.git
git clone git@github.com:mjirik/scaffanweb.git
cd scaffanweb
```

 * in `nginx/nginx.conf` comment the server listening on 443
 * copy database file 
 * copy file with secrets
 * copy google drive key
 * copy google spreadsheet key

Create certifiace by:
```bash
docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d scaffan.kky.zcu.cz
```

* in `nginx/nginx.conf` uncomment the server listening on 443

Make migrations and get static files
```bash
docker-compose up --build 
docker-compose exec web /opt/conda/bin/conda run -n scaffanweb python manage.py makemigrations
docker-compose exec web /opt/conda/bin/conda run -n scaffanweb python manage.py migrate
docker-compose exec web /opt/conda/bin/conda run -n scaffanweb python manage.py collectstatic --no-input --clear
```

Get inside docker image
```bash
docker-compose exec web bash
```

# Install with docker

```bash

cd scaffanweb
docker build -t scaffan:0.1 .
```

You might want to copy secret keys and database:

* `scaffanweb/db.sqlite3`
* `scaffanweb/scaffanweb/piglegsurgery-creds.json`
* `scaffanweb/scaffanweb/secreetkey.json`
* `scaffanweb/scaffanweb/settings_local.json`
* `scaffanweb/scaffanweb/piglegsurgery-creds.json`
* `scaffanweb/media`

```bash
docker run -d -v "C:/Users/Jirik/projects/scaffanweb:/webapps/scaffanweb_django/scaffanweb/" -v "C:/Users/Jirik/projects/scaffan:/webapps/scaffanweb_django/scaffan/" -p 8080:80 -p 8000:8000  --name scaffan scaffan:0.1
```

```bash
docker run -d -v "/home/mjirik/projects/scaffanweb:/webapps/scaffanweb_django/scaffanweb/" -v "/home/mjirik/projects/scaffan:/webapps/scaffanweb_django/scaffan/" -p 8080:8080 -p 80:8000  --name scaffan scaffan:0.1
```


