# Generated by Django 2.2.3 on 2020-02-23 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netBarSys', '0003_auto_20200222_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfos',
            name='onlinetimestr',
            field=models.CharField(default='0分钟', max_length=50),
        ),
    ]
