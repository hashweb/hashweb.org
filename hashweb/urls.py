from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^(\w*)/users/(\w*)', 'stats.views.getUserInfo'),
    url(r'^(\w*)/getchattyusers', 'stats.views.getChattyUsers'),
    url(r'^(\w*)/getfullusercountweek', 'stats.views.getFullUserCountWeek'),
    url(r'^(\w*)/getfullusercounttoday', 'stats.views.getFullUserCountToday'),
    url(r'^(\w*)/getfullusercount', 'stats.views.getFullUserCount'),
    url(r'^(\w*)/', 'stats.views.index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

