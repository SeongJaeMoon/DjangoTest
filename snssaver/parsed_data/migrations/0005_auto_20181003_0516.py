# Generated by Django 2.1.1 on 2018-10-03 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsed_data', '0004_auto_20181002_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parsingdata',
            name='_profile_img',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uploaddata',
            name='_like',
            field=models.TextField(blank=True, null=True),
        ),
    ]
