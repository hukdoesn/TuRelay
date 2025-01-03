# Generated by Django 4.2.13 on 2024-12-18 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0017_alerthistorylog'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerthistorylog',
            name='alert_host',
            field=models.TextField(blank=True, null=True, verbose_name='告警主机'),
        ),
        migrations.AlterField(
            model_name='alerthistorylog',
            name='alert_contacts',
            field=models.TextField(blank=True, null=True, verbose_name='告警联系人'),
        ),
        migrations.AlterField(
            model_name='alerthistorylog',
            name='alert_rule',
            field=models.TextField(blank=True, null=True, verbose_name='告警规则'),
        ),
    ]
