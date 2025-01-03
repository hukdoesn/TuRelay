# Generated by Django 4.2.13 on 2024-10-13 23:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommandLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, verbose_name='用户名')),
                ('command', models.TextField(verbose_name='执行的命令')),
                ('hosts', models.CharField(max_length=255, verbose_name='执行主机')),
                ('credential', models.CharField(max_length=150, verbose_name='使用的凭据')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
            ],
            options={
                'db_table': 't_command_log',
            },
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='apps.user', verbose_name='用��'),
        ),
    ]
