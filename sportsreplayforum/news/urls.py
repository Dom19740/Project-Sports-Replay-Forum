from django.urls import path
from .views import news_sidebar

urlpatterns = [
    path('news/', news_sidebar, name='news_sidebar'),
]
