from django.conf.urls.defaults import *
from django.views.generic import ListView,DetailView
from wikilink.models import Source

urlpatterns = patterns('wikilink.views',
    #(r'^$', 'index'),
    url(r'^$',ListView.as_view(model=Source),name="source_list"),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=Source),name="source_detail"),
)