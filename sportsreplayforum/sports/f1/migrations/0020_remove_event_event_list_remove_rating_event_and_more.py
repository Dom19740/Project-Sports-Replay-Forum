# Generated by Django 5.1.1 on 2024-10-09 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0019_rename_video_event_video_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_list',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='event',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='voters',
        ),
        migrations.DeleteModel(
            name='Competition',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
