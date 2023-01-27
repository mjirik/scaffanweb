# Generated by Django 3.0.3 on 2020-08-27 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0026_exampledata'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverdatafilename',
            name='process_started',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='serverdatasetpath',
            name='server_dataset_path',
            field=models.FilePathField(allow_files=False, allow_folders=True, path='/webapps/scaffanweb_django/data/medical/orig/Scaffan-analysis', verbose_name='Path to dataset on server'),
        ),
    ]
