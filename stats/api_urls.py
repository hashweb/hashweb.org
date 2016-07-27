from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from stats import views

urlpatterns = [
	url(r'^users/(.*)/addkarma$', views.addKarma),
    url(r'^users/(.*)$', views.userInfo)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)