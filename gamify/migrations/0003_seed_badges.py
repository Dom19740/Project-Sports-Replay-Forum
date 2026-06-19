from django.db import migrations

BADGES = [
    {
        'slug': 'first-rating',
        'name': 'First Rating',
        'description': 'Submitted your very first event rating.',
        'icon': 'fa-solid fa-star',
        'rarity_threshold': 1,  # Common
    },
    {
        'slug': 'quick-take',
        'name': 'Quick Take',
        'description': 'Rated an event within 1 hour of it finishing.',
        'icon': 'fa-solid fa-bolt',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'hot-streak-7',
        'name': 'Hot Streak 7',
        'description': 'Engaged on the site for 7 consecutive days.',
        'icon': 'fa-solid fa-fire',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'hot-streak-30',
        'name': 'Hot Streak 30',
        'description': 'Maintained an activity streak for 30 days in a row.',
        'icon': 'fa-solid fa-fire-flame-curved',
        'rarity_threshold': 4,  # Epic
    },
    {
        'slug': 'multi-sport-fan',
        'name': 'Multi-Sport Fan',
        'description': 'Rated events across 3 or more different competitions.',
        'icon': 'fa-solid fa-globe',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'full-weekend',
        'name': 'Full Weekend',
        'description': 'Rated every session of a single GP or race weekend.',
        'icon': 'fa-solid fa-calendar-check',
        'rarity_threshold': 3,  # Rare
    },
    {
        'slug': 'tournament-completionist',
        'name': 'Tournament Completionist',
        'description': 'Rated every match in a round of a World Cup or Champions League.',
        'icon': 'fa-solid fa-trophy',
        'rarity_threshold': 4,  # Epic
    },
    {
        'slug': 'crowd-pleaser',
        'name': 'Crowd Pleaser',
        'description': 'Received 50 or more likes across all your event ratings.',
        'icon': 'fa-solid fa-heart',
        'rarity_threshold': 3,  # Rare
    },
    {
        'slug': 'commentator',
        'name': 'Commentator',
        'description': 'Posted 25 or more comments.',
        'icon': 'fa-solid fa-comments',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'trusted-voice',
        'name': 'Trusted Voice',
        'description': 'Gave ratings within 10% of community consensus at least 10 times.',
        'icon': 'fa-solid fa-check-double',
        'rarity_threshold': 3,  # Rare
    },
    {
        'slug': 'contrarian',
        'name': 'Contrarian',
        'description': 'Earned 10+ likes on a rating that went against the majority.',
        'icon': 'fa-solid fa-arrows-left-right',
        'rarity_threshold': 4,  # Epic
    },
]


def seed_badges(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    for data in BADGES:
        Badge.objects.update_or_create(slug=data['slug'], defaults=data)


def remove_badges(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    Badge.objects.filter(slug__in=[b['slug'] for b in BADGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gamify', '0002_update_xpevent_action_types'),
    ]

    operations = [
        migrations.RunPython(seed_badges, remove_badges),
    ]
