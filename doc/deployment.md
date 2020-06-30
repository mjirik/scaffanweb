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

[Tutorial](https://medium.com/@whizzoe/in-5-mins-set-up-google-login-to-sign-up-users-on-django-e71d5c38f5d5)


# Auth

[SocialApps Tutorial](https://medium.com/faun/how-to-set-up-conda-virtual-environments-with-apache-mod-wsgi-flask-c2043711223e)

# Apache

sudo apt-get install libapache2-mod-wsgi-py3



# Troubleshooting

# SocialApp matching query does not exist.

[set APP_ID=2](https://stackoverflow.com/questions/15409366/django-socialapp-matching-query-does-not-exist)

You can check your app ids from shell:

```bash
conda activate scaffan
python manage.py shell
```
from django.contrib.sites.models import Site
sorted([(site.id,site.name) for site in Site.objects.all()])
```python

```

