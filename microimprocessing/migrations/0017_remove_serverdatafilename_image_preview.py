# Generated by Django 3.0.7 on 2020-06-13 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0016_auto_20200613_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serverdatafilename',
            name='image_preview',
        ),
    ]
