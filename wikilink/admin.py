from wikilink.models import Source,WPArticle,RSSFeed,UserProfile,Citation
from django.contrib import admin

class SourceAdmin(admin.ModelAdmin):
	list_display = ['title','citationAuthor','getWPLinks']
	#exclude = ('wikiarticles',)

admin.site.register(Source,SourceAdmin)
admin.site.register(WPArticle)
admin.site.register(RSSFeed)
admin.site.register(UserProfile)
admin.site.register(Citation)