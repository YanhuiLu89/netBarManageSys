# Generated by Django 2.2.3 on 2020-02-22 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netBarSys', '0002_auto_20200222_1102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfos',
            old_name='lastLogouttime',
            new_name='lastlogouttime',
        ),
    ]