from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_weekend_list, name='race_weekend_list'), # F1 events list
    # Add more paths as needed
]
