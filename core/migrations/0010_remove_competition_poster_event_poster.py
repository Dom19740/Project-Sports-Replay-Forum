# Generated by Django 5.1.1 on 2024-11-05 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_competition_badge_competition_banner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='poster',
        ),
        migrations.AddField(
            model_name='event',
            name='poster',
            field=models.CharField(default='', max_length=255),
        ),
    ]
