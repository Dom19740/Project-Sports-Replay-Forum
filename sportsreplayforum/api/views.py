import requests
from .models import Sport, Event, Result
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Sport, Event, Result
from .serializers import SportSerializer, EventSerializer, ResultSerializer


@api_view(['GET'])
def get_sports(request):
    url = 'https://www.thesportsdb.com/api/v1/json/3/all_leagues.php'
    response = requests.get(url)
    if response.status_code == 200:
        sports_data = response.json()
        for sport in sports_data:
            Sport.objects.update_or_create(name=sport['name'])
        return Response(sports_data)
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_event_results(request, event_id):
    url = f'https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024'
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        for result in results:
            Event.objects.get(id=result['event_id']).result_set.create(
                score=result['score'],
                finished_at=result['finished_at']
            )
        return Response(results)
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SportsList(APIView):
    def get(self, request):
        sports = Sport.objects.all()
        serializer = SportSerializer(sports, many=True)
        return Response(serializer.data)

class EventsList(APIView):
    def get(self, request):
        events = Event.objects.filter(result__isnull=False)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class ResultsList(APIView):
    def get(self, request):
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
