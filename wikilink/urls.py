from django.conf.urls.defaults import *
from django.views.generic import ListView,DetailView
from django.contrib.auth.views import login,logout
import wikilink.views as views
from wikilink.models import Source,RSSFeed
from django.db.models import Count

urlpatterns = patterns('wikilink.views',
    # (r'^$', 'index'),
    url(r'^$',views.SourceListView.as_view(),name="source_list"),
    url(r'^(uncited)/$',views.SourceListView.as_view(),name="uncited"),

    url(r'^(?P<pk>\d+)/$', views.source_detail,name="source_detail"),
    url(r'^(?P<pk>\d+)/update/$',views.source_update,name="source_update"),
    url(r'^(?P<pk>\d+)/(?P<action>cite|irrelevant|watch|delete|deleteconfirm)/$',views.source_action,name="source_action"),

	url(r'^recentcites/$',views.RecentlyCitedView.as_view(),name="recently_cited"),

    url(r'^newsource/$',views.new_source,name="new_source"),
    url(r'^newurl/$',views.new_source_from_url,name="new_url"),
    url(r'^rss/(?P<rssid>\d+)/$',views.SourceListView.as_view(),name="rss_detail"),
    url(r'^feeds/$',views.RSSListView.as_view(model=RSSFeed),name="feeds"),
    url(r'^rss/update/$',views.update_rss,name="update_rss"),
    url(r'^rss/watch/$',views.watch_rss,name="watch_rss"),
    url(r'^login/$',login,name="login"),
    url(r'^logout/$',logout,{'next_page':'/link'},name="logout"),
    url(r'^user/(?P<username>[A-Za-z0-9_\@\+\.\_]+)/$',views.user_profile,name="user_profile"),
    url(r'^workbench/$',views.workbench,name="workbench"),

   #Future  url(r'^users/(?P<username>[A-Za-z0-9_\@\+\.\_]+)/$',usercitations,name="user_citations")
)