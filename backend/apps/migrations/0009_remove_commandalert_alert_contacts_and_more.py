# Generated by Django 4.2.13 on 2024-10-21 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0008_remove_commandalert_alert_contact_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commandalert',
            name='alert_contacts',
        ),
        migrations.RemoveField(
            model_name='commandalert',
            name='hosts',
        ),
        migrations.AddField(
            model_name='commandalert',
            name='alert_contacts',
            field=models.TextField(blank=True, null=True, verbose_name='告警联系人'),
        ),
        migrations.AddField(
            model_name='commandalert',
            name='hosts',
            field=models.TextField(blank=True, null=True, verbose_name='关联主机'),
        ),
    ]