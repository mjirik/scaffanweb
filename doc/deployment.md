* git clone
* 

```bash
conda create -n scaffanweb -c conda-forge -c mjirik -c bioconda scaffan django django-allauth google-auth -y

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

