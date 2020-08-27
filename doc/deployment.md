# Scaffanweb deployment

* git clone
* 



# with testserver

```bash
conda create -n scaffanweb -c conda-forge -c mjirik -c bioconda scaffan django django-allauth google-auth pip redis-y
pip install django-q

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```


Fill tables in admin

[Googl login: 5 minutes tutorial](https://medium.com/@whizzoe/in-5-mins-set-up-google-login-to-sign-up-users-on-django-e71d5c38f5d5)


# Auth

[SocialApps Tutorial](https://medium.com/faun/how-to-set-up-conda-virtual-environments-with-apache-mod-wsgi-flask-c2043711223e)

# Deploy

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
cp deploy/scaffanweb /etc/nginx/sites-enabled/scaffanweb
```

Update `supervisor`:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

Try:

```bash
sudo supervisorctl start scaffanweb
```

Create Nginx virtual servers:

```bash
sudo ln -s /etc/nginx/sites-available/scaffanweb /etc/nginx/sites-enabled/scaffanweb
sudo service nginx restart
```


## Apache
We used apache before but now we moved our infrastructure to `nginx` and `gunicorn`.

sudo apt-get install libapache2-mod-wsgi-py3


# Final touch

Sample data - uplad new data and in admin you can select which data would 
be used as sample data.



# Troubleshooting

# SocialApp matching query does not exist.

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

