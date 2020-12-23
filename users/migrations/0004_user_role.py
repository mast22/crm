# Generated by Django 3.1 on 2020-12-11 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200913_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('manager', 'Менеджер'), ('performer', 'Исполнитель')], default='performer', max_length=15),
            preserve_default=False,
        ),
    ]
