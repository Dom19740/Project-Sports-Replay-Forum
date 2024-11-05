from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Competition(models.Model):
    league = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=255)
    date = models.DateField()
    banner = models.CharField(max_length=255, default="")
    badge = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name

class Event(models.Model):
    event_list = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    idEvent = models.CharField(max_length=255, default="")
    video_id = models.CharField(max_length=255, null=True, default="")
    is_finished = models.BooleanField(default=False)
    poster = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"{self.event_type} for {self.event_list.name} on {self.date_time}"

class Rating(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='rating')
    five_stars = models.IntegerField(default=0)
    four_stars = models.IntegerField(default=0)
    three_stars = models.IntegerField(default=0)
    two_stars = models.IntegerField(default=0)
    one_star = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    voters = models.ManyToManyField(User, related_name='rated_events')

    def __str__(self):
        return f"{self.event.event_type} - {self.event.event_list.name}"
    
class Result_f1(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='results')
    position = models.IntegerField()
    driver = models.CharField(max_length=255)
    team = models.CharField(max_length=255)
    time = models.CharField(max_length=255, null=True)    

    def __str__(self):
        return f"{self.player} - {self.event.event_type} - {self.position}"