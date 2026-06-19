def build_notification(xp_result, new_badges):
    return {
        'xp': xp_result['xp'],
        'leveled_up': xp_result['leveled_up'],
        'new_level': xp_result['new_level'],
        'new_title': xp_result['new_title'],
        'badges': [{'name': b.name, 'icon': b.icon} for b in new_badges],
    }


def queue_notification(request, xp_result, new_badges):
    """Store a gamification notification in the session for display on next page load."""
    if xp_result['xp'] > 0 or new_badges:
        request.session['gamify_notification'] = build_notification(xp_result, new_badges)
