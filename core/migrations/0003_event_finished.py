# Generated by Django 5.1.1 on 2024-10-12 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_competition_league'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
