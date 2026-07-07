from django.db import migrations

# Mirrors gamify.levels.xp_for_level's new banded curve as of this migration.
_CUMULATIVE_XP = (
    0, 25, 50, 75, 100,
    130, 160, 195, 230, 270,
    315, 360, 410, 460, 515,
    575, 635, 700, 765, 835,
    910, 985, 1065, 1145, 1230,
)
_OLD_CUMULATIVE_XP = tuple(int(9 * (n ** 1.5)) if n > 1 else 0 for n in range(1, 26))
MAX_LEVEL = 25


def _compute_level(total_xp, cumulative_xp):
    level = 1
    while level < MAX_LEVEL and total_xp >= cumulative_xp[level]:
        level += 1
    return level


def recompute_new(apps, schema_editor):
    UserProfile = apps.get_model('gamify', 'UserProfile')
    for profile in UserProfile.objects.all():
        new_level = _compute_level(profile.total_xp, _CUMULATIVE_XP)
        if new_level != profile.current_level:
            profile.current_level = new_level
            profile.save(update_fields=['current_level'])


def recompute_old(apps, schema_editor):
    UserProfile = apps.get_model('gamify', 'UserProfile')
    for profile in UserProfile.objects.all():
        old_level = _compute_level(profile.total_xp, _OLD_CUMULATIVE_XP)
        if old_level != profile.current_level:
            profile.current_level = old_level
            profile.save(update_fields=['current_level'])


class Migration(migrations.Migration):

    dependencies = [
        ('gamify', '0006_update_level_badge_thresholds'),
    ]

    operations = [
        migrations.RunPython(recompute_new, recompute_old),
    ]
