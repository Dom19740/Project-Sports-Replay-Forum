from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import Competition, Event


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return ['home', 'about', 'replay_platforms']

    def location(self, item):
        return reverse(item)


class SportScheduleSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return ['FIFA World Cup', 'Formula 1', 'MotoGP']

    def location(self, item):
        return reverse('core:competition_schedule', kwargs={'league': item})


class CompetitionSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Competition.objects.all().order_by('-date')[:200]

    def location(self, obj):
        return reverse('core:event_list', kwargs={'competition_id': obj.pk})

    def lastmod(self, obj):
        return obj.date


class EventSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return Event.objects.select_related('event_list').order_by('-date_time')[:500]

    def location(self, obj):
        return reverse('core:event', kwargs={'event_id': obj.pk})

    def lastmod(self, obj):
        return obj.date_time
