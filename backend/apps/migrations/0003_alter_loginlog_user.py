# Generated by Django 4.2.13 on 2024-07-29 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_loginlog_os_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginlog',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apps.user', verbose_name='用户'),
        ),
    ]