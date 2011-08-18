from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
	(r'^flat/', include('django.contrib.flatpages.urls')),
    (r'^link/', include('wikilink.urls')),
)