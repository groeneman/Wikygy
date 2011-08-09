from wikilink.models import Source
from django.contrib import admin


class SourceAdmin(admin.ModelAdmin):
	list_display = ['title','author','getWPLinks']

admin.site.register(Source,SourceAdmin)