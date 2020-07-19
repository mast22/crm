# Generated by Django 3.0.8 on 2020-07-19 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20200719_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='tasks.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='TaskFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-created_at']},
        ),
        migrations.DeleteModel(
            name='TaskFiles',
        ),
        migrations.AddField(
            model_name='taskfile',
            name='file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tasks.Task'),
        ),
        migrations.AddField(
            model_name='taskfile',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='tasks.Task'),
        ),
        migrations.AddField(
            model_name='commentfile',
            name='file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tasks.Task'),
        ),
    ]
