# Generated by Django 5.1.1 on 2024-10-09 16:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=50)),
                ('date_time', models.DateTimeField()),
                ('idEvent', models.CharField(default='', max_length=255)),
                ('video_id', models.CharField(default='', max_length=255)),
                ('event_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.competition')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('five_stars', models.IntegerField(default=0)),
                ('four_stars', models.IntegerField(default=0)),
                ('three_stars', models.IntegerField(default=0)),
                ('two_stars', models.IntegerField(default=0)),
                ('one_star', models.IntegerField(default=0)),
                ('percentage', models.FloatField(default=0.0)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='core.event')),
                ('voters', models.ManyToManyField(related_name='rated_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]