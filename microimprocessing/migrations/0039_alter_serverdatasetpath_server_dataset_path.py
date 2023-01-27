# Generated by Django 3.2.16 on 2023-01-27 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0038_serverdatafilename_last_task_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdatasetpath',
            name='server_dataset_path',
            field=models.FilePathField(allow_files=False, allow_folders=True, path='/root/data/medical/orig/Scaffan-analysis', verbose_name='Path to dataset on server'),
        ),
    ]
