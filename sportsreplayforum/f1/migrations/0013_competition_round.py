# Generated by Django 5.1.1 on 2024-10-04 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0012_remove_competition_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='round',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
