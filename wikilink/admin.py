from wikilink.models import Source,WPArticle,RSSFeed,UserProfile,Citation
from django.contrib import admin

class SourceAdmin(admin.ModelAdmin):
	list_display = ['title','url','getWPLinks']
	#exclude = ('wikiarticles',)

class RSSAdmin(admin.ModelAdmin):
	list_display = ['name','link']
	
admin.site.register(Source,SourceAdmin)
admin.site.register(WPArticle)
admin.site.register(RSSFeed,RSSAdmin)
admin.site.register(UserProfile)
admin.site.register(Citation)