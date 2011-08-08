from wikilink.models import Source
from django.contrib import admin

class SourceAdmin(admin.ModelAdmin):
	list_display = ['title','author','has_content']

admin.site.register(Source,SourceAdmin)