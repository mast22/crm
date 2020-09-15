# Generated by Django 3.1 on 2020-09-14 20:21

import django.contrib.postgres.indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_taskstatus_last_modified'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='task',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created_at'], name='tasks_task_created_7a389d_brin'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['name', 'text'], name='tasks_task_name_3aca2c_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['work_type'], name='tasks_task_work_ty_60c992_idx'),
        ),
    ]