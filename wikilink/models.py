from django.db import models
from wikilink.etc.linkfinder import getWikiLinks

# Create your models here.
class Source(models.Model):
	title = models.CharField(verbose_name="Title",max_length=300)
	author = models.CharField(verbose_name="Author",max_length=70)
	url = models.URLField(verbose_name="Source URL",verify_exists=True,max_length=500)
	content = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.url
	
	def has_content(self):
		return self.content == ""
	
	def getWPLinks(self):
		return getWikiLinks(self.content)
	
	def getWPTitles(self):
		return [l[0] for l in self.getWPLinks()]
	
	getWPLinks.short_description="Relevant Wikipedia Links"