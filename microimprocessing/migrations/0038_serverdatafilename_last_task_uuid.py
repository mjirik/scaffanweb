# Generated by Django 3.1.7 on 2022-06-23 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0037_serverdatafilename_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverdatafilename',
            name='last_task_uuid',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]