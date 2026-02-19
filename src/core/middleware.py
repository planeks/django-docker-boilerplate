from django.http import HttpResponseRedirect
from django.urls import reverse

__all__ = [
    "is_restricted_internal_url",
    "login_required_middleware",
]


def is_restricted_internal_url(url):
    url_prefixes_excludes = [
        # '/media/',
        "/__debug__/",
        "/login/",
        "/register/",
        "/logout/",
        "/password-",
        "/reset/",
        "/superadmin/",
    ]
    return not any(url.startswith(x) for x in url_prefixes_excludes)


def login_required_middleware(get_response):
    def middleware(request):
        assert hasattr(request, "user")
        if not request.user.is_authenticated and is_restricted_internal_url(request.path_info):
            return HttpResponseRedirect(reverse("login"))

        return get_response(request)

    return middleware
