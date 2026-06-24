def gamify_notification(request):
    notification = request.session.pop('gamify_notification', None)

    strip = None
    if request.user.is_authenticated:
        try:
            from .levels import level_info, level_colors, xp_gradient_color
            from .models import UserProfile, UserBadge
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            info = level_info(profile)
            bg, text = level_colors(info['level'])
            last_ub = (
                UserBadge.objects
                .filter(user=request.user)
                .select_related('badge')
                .order_by('-earned_at')
                .first()
            )
            strip = {
                'level':        info['level'],
                'title':        info['title'],
                'progress_pct': info['progress_pct'],
                'total_xp':     info['total_xp'],
                'xp_next':      info['xp_next'],
                'last_badge':   last_ub.badge if last_ub else None,
                'bg_color':     bg,
                'text_color':   text,
                'edge_color':   xp_gradient_color(info['progress_pct']),
            }
        except Exception:
            pass

    return {
        'gamify_notification': notification,
        'gamify_strip':        strip,
    }
