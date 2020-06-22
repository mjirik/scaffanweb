* git clone
* 



# with testserver

```bash
conda create -n scaffanweb -c conda-forge -c mjirik -c bioconda scaffan django django-allauth google-auth -y

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```


Fill tables in admin

[Tutorial](https://medium.com/@whizzoe/in-5-mins-set-up-google-login-to-sign-up-users-on-django-e71d5c38f5d5)


# Apache

[Tutorial](https://medium.com/faun/how-to-set-up-conda-virtual-environments-with-apache-mod-wsgi-flask-c2043711223e)

sudo apt-get install libapache2-mod-wsgi-py3



# Troubleshooting

# SocialApp matching query does not exist.

[set APP_ID=2](https://stackoverflow.com/questions/15409366/django-socialapp-matching-query-does-not-exist)

