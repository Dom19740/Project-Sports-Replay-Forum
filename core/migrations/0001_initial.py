# Generated by Django 5.1.5 on 2025-03-12 20:32

import django.db.models.deletion
import uuid
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
                ('league', models.CharField(default='', max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('banner', models.CharField(default='', max_length=255)),
                ('badge', models.CharField(default='', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=50)),
                ('date_time', models.DateTimeField()),
                ('idEvent', models.CharField(default='', max_length=255)),
                ('video_id', models.CharField(default='', max_length=255, null=True)),
                ('is_finished', models.BooleanField(default=False, null=True)),
                ('poster', models.CharField(default='', max_length=255)),
                ('ai_review', models.TextField(default='', null=True)),
                ('ai_rating', models.CharField(default='', max_length=255)),
                ('event_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.competition')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('body', models.CharField(max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.event')),
            ],
            options={
                'ordering': ['-created'],
            },
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
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='core.event')),
                ('voters', models.ManyToManyField(related_name='rated_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('body', models.CharField(max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.comment')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
