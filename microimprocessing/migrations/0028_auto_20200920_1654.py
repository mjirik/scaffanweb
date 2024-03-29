# Generated by Django 3.0.3 on 2020-09-20 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import microimprocessing.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('microimprocessing', '0027_auto_20200827_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdatafilename',
            name='annotationfile',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=microimprocessing.models.upload_to_unqiue_folder, verbose_name='Annotation File'),
        ),
        migrations.AlterField(
            model_name='serverdatafilename',
            name='imagefile',
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=microimprocessing.models.upload_to_unqiue_folder, verbose_name='Uploaded File'),
        ),
        migrations.AlterField(
            model_name='serverdatafilename',
            name='zip_file',
            field=models.ImageField(blank=True, null=True, upload_to='cellimage/'),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('files', models.ManyToManyField(to='microimprocessing.ServerDataFileName')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(default=microimprocessing.models.get_default_user_hash, max_length=50)),
                ('automatic_import', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
