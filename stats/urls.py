from django.conf import settings
from django.conf.urls import     include, url
from django.conf.urls.static import static
from django.contrib import admin

from stats import views
import stats

urlpatterns = [
    # Examples:
    url(r'^search', views.search),
    url(r'^logs/(\d*)', views.getConvoPartial, name='stats_convopartial'),
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
    url(r'^users/(.*)$', views.userInfo, name='stats_userinfo'),


    url(r'^$', stats.views.index, name="stats_home"),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


