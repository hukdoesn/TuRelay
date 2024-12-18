# Generated by Django 4.2.13 on 2024-12-18 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0018_alerthistorylog_alert_host_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alerthistorylog',
            options={'ordering': ['-create_time']},
        ),
        migrations.RemoveField(
            model_name='alerthistorylog',
            name='alert_contacts',
        ),
        migrations.RemoveField(
            model_name='alerthistorylog',
            name='alert_host',
        ),
        migrations.RemoveField(
            model_name='alerthistorylog',
            name='alert_name',
        ),
        migrations.RemoveField(
            model_name='alerthistorylog',
            name='alert_time',
        ),
        migrations.AddField(
            model_name='alerthistorylog',
            name='command',
            field=models.TextField(blank=True, null=True, verbose_name='执行命令'),
        ),
        migrations.AddField(
            model_name='alerthistorylog',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='alerthistorylog',
            name='hostname',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='执行主机'),
        ),
        migrations.AddField(
            model_name='alerthistorylog',
            name='match_type',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='匹配类型'),
        ),
        migrations.AddField(
            model_name='alerthistorylog',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='执行用户'),
        ),
        migrations.AlterField(
            model_name='alerthistorylog',
            name='alert_rule',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='触发规则'),
        ),
        migrations.AlterField(
            model_name='alerthistorylog',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='编号'),
        ),
    ]
