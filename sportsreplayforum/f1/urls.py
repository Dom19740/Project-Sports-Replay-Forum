from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_list, name='race_list'), # F1 events list
    path('races/<int:race_id>/events/', views.race_weekend, name='race_weekend'),
]
