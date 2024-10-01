from django.db import models

class RaceWeekend(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.date}"

class Event(models.Model):
    EVENT_TYPES = [
        ('practice', 'Practice Session'),
        ('qualifying', 'Qualifying'),
        ('race', 'Race'),
        ('sprint', 'Sprint Race'),
    ]
    
    race_weekend = models.ForeignKey(RaceWeekend, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.event_type.capitalize()} - {self.race_weekend.name}"

class Rating(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Assuming you're using Django's built-in user model
    score = models.PositiveIntegerField()  # Assuming a score out of 3

    def __str__(self):
        return f"{self.user.username} rated {self.event.event_type} - {self.score} stars"
