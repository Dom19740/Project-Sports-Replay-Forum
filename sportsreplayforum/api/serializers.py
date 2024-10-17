from rest_framework import serializers
from .models import Sport, Event, Result

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name']

class EventSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'date_time', 'sport_name']

class ResultSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'score', 'finished_at', 'event_name']
