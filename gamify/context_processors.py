def gamify_notification(request):
    """
    Pop any pending gamification notification from the session and expose it
    to all templates as `gamify_notification`. The pop ensures it shows once.
    """
    notification = request.session.pop('gamify_notification', None)
    return {'gamify_notification': notification}
