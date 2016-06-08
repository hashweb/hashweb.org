from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/stats/', include('stats.api_urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'^eurostats$', 'hashweb.views.euro_stats'),
    # url(r'^stats', 'stats.views.index'),
    url(r'^$', 'hashweb.views.index')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

