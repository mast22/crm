# Generated by Django 3.0.8 on 2020-07-31 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20200726_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskstatus',
            name='decision',
        ),
    ]
