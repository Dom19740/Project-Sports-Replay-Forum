# news/views.py

from django.shortcuts import render
from .services import fetch_news

def news_sidebar(request):
    news_articles = fetch_news()
    return render(request, 'news/sidebar.html', {'news_articles': news_articles})
