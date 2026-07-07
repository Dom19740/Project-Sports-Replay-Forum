from django.db import migrations

# slug -> (new description, new level number for the description text)
LEVEL_BADGE_UPDATES = {
    'level-5':  ('Reached Level 3 — you\'re a real fan.', 3),
    'level-9':  ('Reached Level 6 — a regular on the site.', 6),
    'level-12': ('Reached Level 10 — a serious contender.', 10),
    'level-16': ('Reached Level 14 — you\'re an All-Star.', 14),
    'level-19': ('Reached Level 18 — a true Champion.', 18),
    'level-23': ('Reached Level 22 — a living Legend.', 22),
}

OLD_DESCRIPTIONS = {
    'level-5':  'Reached Level 5 — you\'re a real fan.',
    'level-9':  'Reached Level 9 — a regular on the site.',
    'level-12': 'Reached Level 12 — a serious contender.',
    'level-16': 'Reached Level 16 — you\'re an All-Star.',
    'level-19': 'Reached Level 19 — a true Champion.',
    'level-23': 'Reached Level 23 — a living Legend.',
}


def update_descriptions(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    for slug, (description, _level) in LEVEL_BADGE_UPDATES.items():
        Badge.objects.filter(slug=slug).update(description=description)


def revert_descriptions(apps, schema_editor):
    Badge = apps.get_model('gamify', 'Badge')
    for slug, description in OLD_DESCRIPTIONS.items():
        Badge.objects.filter(slug=slug).update(description=description)


class Migration(migrations.Migration):

    dependencies = [
        ('gamify', '0005_seed_beloved_tester'),
    ]

    operations = [
        migrations.RunPython(update_descriptions, revert_descriptions),
    ]
