from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

import debug_toolbar
admin.autodiscover()


urlpatterns = patterns('')
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

urlpatterns += patterns('',
    url(r'^users/(.*)$', 'stats.views.userInfo')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


