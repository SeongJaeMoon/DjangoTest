# Generated by Django 2.1.1 on 2018-10-02 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsed_data', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imgdata',
            old_name='_list',
            new_name='_list_img',
        ),
        migrations.RenameField(
            model_name='videodata',
            old_name='_list',
            new_name='_list_video',
        ),
    ]
