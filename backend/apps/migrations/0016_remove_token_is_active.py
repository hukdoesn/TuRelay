# Generated by Django 4.2.13 on 2024-11-29 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0015_token_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='is_active',
        ),
    ]
