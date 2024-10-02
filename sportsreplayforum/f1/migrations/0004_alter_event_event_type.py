# Generated by Django 5.1.1 on 2024-10-02 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0003_race_round'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(choices=[('qualifying', 'Qualifying'), ('race', 'Race'), ('Shootout', 'Sprint Shootout'), ('sprint', 'Sprint Race')], max_length=10),
        ),
    ]
