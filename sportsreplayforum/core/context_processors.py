from .models import Sport

def sports(request):
    return {'sports': Sport.objects.all()}