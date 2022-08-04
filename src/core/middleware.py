from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.urls import reverse


__all__ = [
    'is_restricted_internal_url',
    'login_required_middleware',
]


def is_restricted_internal_url(url):
    URL_PREFIXES_EXCLUDES = [
        # '/media/',
        '/__debug__/',
        '/login/',
        '/register/',
        '/logout/',
        '/password-',
        '/reset/',
        '/superadmin/',
    ]
    return not max([url.startswith(x) for x in URL_PREFIXES_EXCLUDES])


def login_required_middleware(get_response):
    def middleware(request):
        assert hasattr(request, 'user')
        if not request.user.is_authenticated:
            if is_restricted_internal_url(request.path_info):
                return HttpResponseRedirect(reverse('login'))

        response = get_response(request)
        return response
    return middleware
