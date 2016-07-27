from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from stats import views

urlpatterns = patterns('',
    # Examples:
    url(r'^search', views.search),
    url(r'^logs/(\d*)', views.getConvoPartial),
    url(r'^users/(.*)', views.getUserInfo),
    url(r'^getchattyusers', views.getChattyUsers),
    url(r'^getkarmausers', views.getKarmaUsers),
    url(r'^getfullusercountweek', views.getFullUserCountWeek),
    url(r'^getfullusercounttoday', views.getFullUserCountToday),
    url(r'^getfullusercount', views.getFullUserCount),
    url(r'^getusertimeonline/(.*)$', views.getUserTimeOnline),
    url(r'^bans/$', views.showBansPage),
    url(r'^bans/update', views.reIndexBans),
    url(r'^bans/(\d*)', views.adjustBan),

    # Open API stuff
    url(r'^users/(.*)$', views.userInfo),


    url(r'^$', views.index),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


