# Generated by Django 2.1.1 on 2018-10-08 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsed_data', '0009_basicstatistic'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicstatistic',
            name='replies',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='basicstatistic',
            name='reply_user',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
