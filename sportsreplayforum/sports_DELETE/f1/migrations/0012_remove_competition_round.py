# Generated by Django 5.1.1 on 2024-10-04 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0011_rename_race_competition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='round',
        ),
    ]