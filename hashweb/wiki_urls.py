from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from wiki.urls import get_pattern as get_wiki_pattern
from django_notify.urls import get_pattern as get_notify_pattern


urlpatterns = patterns('',
	url(r'^notify/', get_notify_pattern()),
    url(r'', get_wiki_pattern()),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)