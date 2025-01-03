# Generated by Django 4.2.13 on 2024-10-18 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_alertcontact_alter_token_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertcontact',
            name='name',
            field=models.CharField(max_length=150, unique=True, verbose_name='告警联系人名称'),
        ),
        migrations.CreateModel(
            name='CommandAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='告警名称')),
                ('command_rule', models.TextField(verbose_name='命令规则')),
                ('hosts', models.TextField(verbose_name='关联主机')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否告警')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('alert_contacts', models.ManyToManyField(to='apps.alertcontact', verbose_name='告警联系人')),
            ],
            options={
                'db_table': 't_command_alert',
            },
        ),
    ]
