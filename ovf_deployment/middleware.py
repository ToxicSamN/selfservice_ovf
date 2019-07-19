
import re
from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')

        if not request.user.is_authenticated:
            if not any(url.match(request.path_info.lstrip('/')) for url in self.get_url_exclusions()):
                return redirect(settings.LOGIN_URL)

    def get_url_exclusions(self):
        exempt_urls = []
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

        return exempt_urls
