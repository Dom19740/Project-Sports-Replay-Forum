# Generated by Django 5.1.1 on 2024-10-02 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1', '0002_race_alter_rating_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='round',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
