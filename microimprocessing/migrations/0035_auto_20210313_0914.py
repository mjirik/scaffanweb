# Generated by Django 3.1.2 on 2021-03-13 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microimprocessing', '0034_auto_20210221_2147'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverallMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='serverdatafilename',
            name='score_area',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serverdatafilename',
            name='score_branch_number',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serverdatafilename',
            name='score_dead_ends_number',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serverdatafilename',
            name='score_skeleton_length',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
