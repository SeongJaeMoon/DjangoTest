# Generated by Django 2.1.1 on 2018-10-08 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsed_data', '0008_auto_20181007_1725'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ids', models.TextField()),
                ('place', models.TextField(blank=True, null=True)),
                ('users', models.TextField(blank=True, null=True)),
                ('hashtag', models.TextField(blank=True, null=True)),
                ('wording', models.TextField(blank=True, null=True)),
                ('time_days', models.TextField(blank=True, null=True)),
                ('time_hours', models.TextField(blank=True, null=True)),
                ('likes', models.TextField(blank=True, null=True)),
                ('moving_avg', models.TextField(blank=True, null=True)),
            ],
        ),
    ]