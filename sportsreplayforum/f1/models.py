from django.db import models
from django.core.exceptions import ValidationError

class Race(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    round = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.date}"

class Event(models.Model):
    EVENT_TYPES = [
        ('qualifying', 'Qualifying'),
        ('race', 'Race'),
        ('shootout', 'Sprint Shootout'),
        ('sprint', 'Sprint Race'),
    ]
    
    race_weekend = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.event_type.capitalize()} - {self.race_weekend.name}"

class Rating(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='rating')
    five_stars = models.IntegerField(default=0)
    four_stars = models.IntegerField(default=0)
    three_stars = models.IntegerField(default=0)
    two_stars = models.IntegerField(default=0)
    one_star = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)  

    def __str__(self):
        return f"{self.event.event_type} - {self.event.race_weekend.name}"