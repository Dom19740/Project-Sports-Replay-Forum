# Generated by Django 5.1.1 on 2024-10-05 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0015_remove_competition_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='idEvent',
            field=models.CharField(default='', max_length=255),
        ),
    ]
