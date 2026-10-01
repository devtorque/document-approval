import json

from submissions.constants import DEMO_USERS


class DemoUserMiddleware:
    """Resolve a demo identity from X-Demo-User for /api/ requests.

    This is a spoofable stand-in for authentication. The header selects a
    server-side record; the client cannot set its own role.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):
            user_id = request.headers.get("X-Demo-User", "").strip().lower()
            user = DEMO_USERS.get(user_id)
            if user is None:
                return json_error(
                    "Authentication credentials were not provided.",
                    status=401,
                )
            request.demo_user = user
        return self.get_response(request)


def json_error(detail, status):
    from django.http import HttpResponse

    payload = json.dumps({"detail": detail})
    return HttpResponse(
        payload,
        status=status,
        content_type="application/json",
    )
