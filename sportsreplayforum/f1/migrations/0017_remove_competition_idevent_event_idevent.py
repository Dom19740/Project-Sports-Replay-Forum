# Generated by Django 5.1.1 on 2024-10-05 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0016_competition_idevent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='idEvent',
        ),
        migrations.AddField(
            model_name='event',
            name='idEvent',
            field=models.CharField(default='', max_length=255),
        ),
    ]