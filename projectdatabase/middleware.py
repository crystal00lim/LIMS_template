# projectdatabase/middleware.py
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone

class KickOtherDevicesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Safely register the signal on startup
        user_logged_in.connect(kick_other_devices)

    def __call__(self, request):
        # Simply passes the request along without restricting any IP addresses
        return self.get_response(request)


# The Signal Receiver that handles single-session enforcement
def kick_other_devices(sender, request, user, **kwargs):
    # Fetch all unexpired sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    
    for session in sessions:
        data = session.get_decoded()
        # If the session belongs to you, but it's on a different device/browser, delete it
        if data.get('_auth_user_id') == str(user.id) and session.session_key != request.session.session_key:
            session.delete()