from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from hashweb import views

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/stats/', include('stats.api_urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    # url(r'^stats', 'stats.views.index'),
    url(r'^$', views.index)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

