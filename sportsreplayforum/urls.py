from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from users.views import registration_view
from .sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap

import os

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('users/', include('users.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('home.urls')),
]

# Serve the static HTML
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urlpatterns += [
    re_path(r'^site/(?P<path>.*)$', serve,
        {'document_root': os.path.join(BASE_DIR, 'site'),
         'show_indexes': True},
        name='site_path'
        ),
]

# Serve the favicon - Keep for later
urlpatterns += [
    path('favicon.ico', serve, {
            'path': 'favicon.ico',
            'document_root': os.path.join(BASE_DIR, 'home/static'),
        }
    ),
]