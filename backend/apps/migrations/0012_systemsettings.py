# Generated by Django 4.2.13 on 2024-11-13 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0011_user_mfa_level_user_otp_secret_key_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watermark_enabled', models.BooleanField(default=True, verbose_name='水印启用状态')),
                ('ip_whitelist', models.TextField(blank=True, null=True, verbose_name='IP白名单')),
                ('ip_blacklist', models.TextField(blank=True, null=True, verbose_name='IP黑名单')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 't_system_settings',
            },
        ),
    ]