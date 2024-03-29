# Scaffanweb deployment

Get the repository

```bash
git clone
```

Install requirements
 
```bash
sudo apt-get install redis
conda create -n scaffanweb -c conda-forge -c mjirik -c bioconda scaffan openslide-python django django-allauth google-auth pip redis-py
pip install django-q
```
 
Init authentification setup in database by copiing `db.sqlite3` and `secretkey.txt`


Or manually:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
```



Fill tables in admin

[Google login: 5 minutes tutorial](https://medium.com/@whizzoe/in-5-mins-set-up-google-login-to-sign-up-users-on-django-e71d5c38f5d5)



# Server preparation

Prepare static files

```bash
python manage.py collectstatic
```

## Nginx, gunicorn and supervisor

[Ngiinx, gunicorn, django tutorial](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/)

[Multiple django apps with nginx](http://michal.karzynski.pl/blog/2013/10/29/serving-multiple-django-applications-with-nginx-gunicorn-supervisor/)


Install

```bash
sudo apt-get install nginx supervisor
```

Prepare config files:

```

cp deploy/gunicorn_start /webapps/scaffanweb_django/bin/
cp deploy/scaffanweb.conf /etc/supervisor/conf.d/
cp deploy/scaffanweb_qcluster.conf /etc/supervisor/conf.d/
cp deploy/scaffanweb /etc/nginx/sites-available/scaffanweb
sudo ln -s /etc/nginx/sites-available/scaffanweb /etc/nginx/sites-enabled/scaffanweb
```

Update `supervisor`:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

Try:

```bash
sudo supervisorctl start scaffanweb
sudo supervisorctl start scaffanweb_qcluster
```

Create Nginx virtual servers:

```bash
sudo ln -s /etc/nginx/sites-available/scaffanweb /etc/nginx/sites-enabled/scaffanweb
sudo service nginx restart
```

## Q-cluster management

```bash
python manage.py qcluster
```
To monitor Q-cluster and check all statistics 

```bash
python manage.py qmonitor
python manage.py qinfo
```

## Google drive import

* Create `credentials.json` by downloading from [Google API Console](https://console.developers.google.com/)
* Copy `credentials.json` and `token.pickle` into project root dir (`token.pickle` can be created automatically)
* Change owner and permissions
  ```bash
  sudo chown scaffanweb /webapps/scaffanweb_django/scaffanweb/credentials_mjirik_gapps.json
  sudo chown scaffanweb /webapps/scaffanweb_django/scaffanweb/token.pickle
  ```
* Add records to `GDriveImport` and `Tasks` using fixture json (or manually)
  ```bash
  python manage.py loaddata gdrive_import
  ```
* Add/Check new record to `GDriveImport` in Admin (check paths)
* Add/Check new record to Django-Q Scheduled Tasks in Admin. (func: tasks.run_gdrive_import)

## Final touch

Sample data - upload new data and in admin you can select which data would 
be used as sample data.


# Usefull links

## Apache
We used apache before but now we moved our infrastructure to `nginx` and `gunicorn`.

sudo apt-get install libapache2-mod-wsgi-py3

[Conda virtual env with Apache](https://medium.com/faun/how-to-set-up-conda-virtual-environments-with-apache-mod-wsgi-flask-c2043711223e)


# Troubleshooting

## Restart everything

```bash
sudo supervisorctl restart all
sudo service nginx restart
```

## SocialApp matching query does not exist.

[set APP_ID=2](https://stackoverflow.com/questions/15409366/django-socialapp-matching-query-does-not-exist)

You can check your app ids from shell:

```bash
conda activate scaffan
python manage.py shell
```
```python
from django.contrib.sites.models import Site
sorted([(site.id,site.name) for site in Site.objects.all()])

```


