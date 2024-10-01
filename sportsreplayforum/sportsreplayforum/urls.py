from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('login/', core_views.login_view, name='login_view'),
    path('register/', core_views.register_view, name='register_view'),
    path('logout/', core_views.logout_view, name='logout_view'),
    path('f1/', include('f1.urls')),
]
