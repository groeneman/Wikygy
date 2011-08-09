from django.conf.urls.defaults import *
from django.views.generic import ListView
from wikilink.models import Source

urlpatterns = patterns('wikilink.views',
    #(r'^$', 'index'),
    (r'^sources/',ListView.as_view(model=Source,)),

   # (r'^(?P<source_id>\d+)/$', 'detail'),
)