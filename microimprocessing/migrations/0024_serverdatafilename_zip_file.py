# Generated by Django 3.0.7 on 2020-06-19 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0023_auto_20200618_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverdatafilename',
            name='zip_file',
            field=models.ImageField(blank=True, upload_to='cellimage/'),
        ),
    ]