"""Site-wide access control middleware."""
from django.conf import settings
from django.contrib.auth.middleware import LoginRequiredMiddleware


class LoginRequiredIfEnabledMiddleware(LoginRequiredMiddleware):
    """Django's LoginRequiredMiddleware, but obeying the REQUIRE_LOGIN switch.

    REQUIRE_LOGIN is read per request (rather than at startup) so the setting
    can be flipped in config/settings/base.py, via the REQUIRE_LOGIN
    environment variable, or overridden in tests.

    When the requirement is on, views decorated with @login_not_required are
    still public -- see apps/linkhub/views.py for an example.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not getattr(settings, "REQUIRE_LOGIN", False):
            return None
        return super().process_view(request, view_func, view_args, view_kwargs)
