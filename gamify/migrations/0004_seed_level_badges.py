from django.db import migrations

LEVEL_BADGES = [
    {
        'slug': 'level-5',
        'name': 'Fan',
        'description': 'Reached Level 5 — you\'re a real fan.',
        'icon': 'fa-solid fa-user-check',
        'rarity_threshold': 1,  # Common
    },
    {
        'slug': 'level-9',
        'name': 'Regular',
        'description': 'Reached Level 9 — a regular on the site.',
        'icon': 'fa-solid fa-repeat',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'level-12',
        'name': 'Contender',
        'description': 'Reached Level 12 — a serious contender.',
        'icon': 'fa-solid fa-dumbbell',
        'rarity_threshold': 2,  # Uncommon
    },
    {
        'slug': 'level-16',
        'name': 'All-Star',
        'description': 'Reached Level 16 — you\'re an All-Star.',
        'icon': 'fa-solid fa-star',
        'rarity_threshold': 3,  # Rare
    },
    {
        'slug': 'level-19',
        'name': 'Champion',
        'description': 'Reached Level 19 — a true Champion.',
        'icon': 'fa-solid fa-crown',
        'rarity_threshold': 4,  # Epic
    },
    {
        'slug': 'level-23',
        'name': 'Legend',
        'description': 'Reached Level 23 — a living Legend.',
        'icon': 'fa-solid fa-gem',
        'rarity_threshold': 5,  # Legendary
    },
]


def seed_level_badges(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    for data in LEVEL_BADGES:
        Badge.objects.update_or_create(slug=data['slug'], defaults=data)


def remove_level_badges(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    Badge.objects.filter(slug__in=[b['slug'] for b in LEVEL_BADGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gamify', '0003_seed_badges'),
    ]

    operations = [
        migrations.RunPython(seed_level_badges, remove_level_badges),
    ]
