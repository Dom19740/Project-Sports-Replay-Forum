from django.db import migrations

BADGE = {
    'slug': 'beloved-tester',
    'name': 'Beloved Tester',
    'description': 'Thanks for your help, much appreciated.',
    'icon': 'fa-solid fa-heart',
    'rarity_threshold': 5,  # Legendary
}


def seed(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    Badge.objects.update_or_create(slug=BADGE['slug'], defaults=BADGE)


def unseed(apps, schema_editor):
    apps.get_model('gamify', 'Badge').objects.filter(slug=BADGE['slug']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gamify', '0004_seed_level_badges'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
