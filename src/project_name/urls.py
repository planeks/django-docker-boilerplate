from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings

admin.site.site_header = '{{project_name}} | Admin console'
admin.site.enable_nav_sidebar = False


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),
]
# For debug mode only
if settings.DEBUG:
    # Turn on debug toolbar
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    # Serve media files via Django
    import django.views.static
    urlpatterns += [
        re_path(r'media/(?P<path>.*)$',
            django.views.static.serve, {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True,
            }),
    ]
