# Generated by Django 3.1 on 2020-09-06 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20200830_0026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='address',
        ),
        migrations.RemoveField(
            model_name='task',
            name='company',
        ),
        migrations.AddField(
            model_name='task',
            name='groups',
            field=models.CharField(blank=True, max_length=300, verbose_name='ВУЗ, Кафедра, Группа'),
        ),
        migrations.AlterField(
            model_name='task',
            name='teacher_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ФИО руководителя'),
        ),
    ]
