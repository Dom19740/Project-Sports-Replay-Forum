from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import uuid

class Competition(models.Model):
    league = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=255)
    date = models.DateField()
    banner = models.CharField(max_length=255, default="")
    badge = models.CharField(max_length=255, default="", null=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    event_list = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    idEvent = models.CharField(max_length=255, default="")
    video_id = models.CharField(max_length=255, null=True, default="")
    is_finished = models.BooleanField(default=False, null=True)
    poster = models.CharField(max_length=255, default="")
    ai_review = models.TextField(null=True, default="")
    ai_rating = models.CharField(max_length=255, default="")

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
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    @property
    def average_stars(self):
        total = self.five_stars + self.four_stars + self.three_stars + self.two_stars + self.one_star
        if total == 0:
            return 0
        return round((5 * self.five_stars + 4 * self.four_stars + 3 * self.three_stars + 2 * self.two_stars + self.one_star) / total)

    @property
    def star_label(self):
        avg = self.average_stars
        if avg >= 4:
            return 'Hot'
        elif avg >= 2:
            return 'Mid'
        return 'Not'

    def __str__(self):
        return f"{self.event.event_type} - {self.event.event_list.name}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    body = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : {self.body[:30]}' 
        except:
            return f'no author : {self.body[:30]}'
        
    class Meta:
        ordering = ['-created']
        
class CommentVote(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    VOTE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ['user', 'comment']

    def __str__(self):
        return f'{self.user.username} {self.vote}d {self.comment.id}'


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='replies')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    body = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : {self.body[:30]}' 
        except:
            return f'no author : {self.body[:30]}'
        
    class Meta:
        ordering = ['-created']