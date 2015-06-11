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
    # Examples:
    url(r'^search', 'stats.views.search'),
    url(r'^logs/(\d*)', 'stats.views.getConvoPartial'),
    url(r'^users/(.*)', 'stats.views.getUserInfo'),
    url(r'^getchattyusers', 'stats.views.getChattyUsers'),
    url(r'^getfullusercountweek', 'stats.views.getFullUserCountWeek'),
    url(r'^getfullusercounttoday', 'stats.views.getFullUserCountToday'),
    url(r'^getfullusercount', 'stats.views.getFullUserCount'),
    url(r'^getusertimeonline/(.*)$', 'stats.views.getUserTimeOnline'),
    url(r'^bans$', 'stats.views.showBansPage'),
    url(r'^bans/(\d*)', 'stats.views.adjustBan'),

    # Open API stuff
    url(r'^users/(.*)$', 'stats.views.userInfo'),


    url(r'^$', 'stats.views.index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


