# Generated by Django 3.0.7 on 2020-06-13 10:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('microimprocessing', '0013_auto_20200613_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdatafilename',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
