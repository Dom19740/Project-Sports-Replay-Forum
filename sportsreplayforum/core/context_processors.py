from .views import sports

def sports_processor(request):
    return {'sports': sports}