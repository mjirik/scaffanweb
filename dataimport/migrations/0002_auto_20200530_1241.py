# Generated by Django 3.0.3 on 2020-05-30 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataimport', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdatafilename',
            name='server_dataset_path',
            field=models.FilePathField(verbose_name='File Path on server'),
        ),
    ]
