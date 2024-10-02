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
        ('practice', 'Practice Session'),
        ('qualifying', 'Qualifying'),
        ('race', 'Race'),
        ('sprint', 'Sprint Race'),
    ]
    
    race_weekend = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.event_type.capitalize()} - {self.race_weekend.name}"

class Rating(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    score = models.PositiveIntegerField()  # Rating score between 1 and 3

    def __str__(self):
        return f"{self.user.username} rated {self.event.event_type} - {self.score} stars"

    class Meta:
        unique_together = ('event', 'user')  # Ensure a user can only rate an event once

    # Validation to ensure the rating score is between 1 and 3
    def clean(self):
        
        if self.score < 1 or self.score > 3:
            raise ValidationError('Score must be between 1 and 3.')
