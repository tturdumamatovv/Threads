# Generated by Django 4.2.4 on 2023-08-15 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_followingsystem_approved_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='followingsystem',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='followingsystem',
            name='request_sent',
        ),
    ]
