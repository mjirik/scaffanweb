  
[![Build Status](https://travis-ci.org/mjirik/scaffanweb.svg?branch=master)](https://travis-ci.org/mjirik/scaffanweb)
[![Coverage Status](https://coveralls.io/repos/github/mjirik/scaffanweb/badge.svg?branch=master)](https://coveralls.io/github/mjirik/scaffanweb?branch=master)
[![PyPI version](https://badge.fury.io/py/scaffanweb.svg)](http://badge.fury.io/py/scaffanweb)


scaffanweb

Web application for scaffold analysis from H&E stained images
# Install with docker-compose

```bash
cd scaffanweb
docker-compose up --build 
docker-compose exec web /opt/conda/bin/conda run -n scaffanweb python manage.py migrate --noinput
docker-compose exec web /opt/conda/bin/conda run -n scaffanweb python manage.py collectstatic --no-input --clear
```

get inside docker image
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


