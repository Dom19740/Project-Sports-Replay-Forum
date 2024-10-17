from django.db import models

class Sport(models.Model):
    name = models.CharField(max_length=100)

class Event(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_time = models.DateTimeField()

class Result(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    score = models.IntegerField()
    finished_at = models.DateTimeField(null=True, blank=True)
