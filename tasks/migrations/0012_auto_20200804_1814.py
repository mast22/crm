# Generated by Django 3.0.8 on 2020-08-04 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20200804_1812'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taskstatus',
            old_name='created_at',
            new_name='last_modified',
        ),
    ]
