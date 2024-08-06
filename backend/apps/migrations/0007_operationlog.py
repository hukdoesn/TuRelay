# Generated by Django 4.2.13 on 2024-08-02 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0006_alter_token_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=150, verbose_name='操作模块')),
                ('request_interface', models.CharField(max_length=255, verbose_name='请求接口')),
                ('request_method', models.CharField(max_length=10, verbose_name='请求方式')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP地址')),
                ('before_change', models.TextField(blank=True, null=True, verbose_name='变更前')),
                ('after_change', models.TextField(blank=True, null=True, verbose_name='变更后')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.user', verbose_name='操作人员')),
            ],
            options={
                'db_table': 't_operation_log',
            },
        ),
    ]