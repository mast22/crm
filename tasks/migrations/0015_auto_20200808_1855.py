# Generated by Django 3.0.8 on 2020-08-08 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_auto_20200808_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Заметки'),
        ),
    ]
