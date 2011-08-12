from django.db import models
from wikilink.etc.linkfinder import getWikiLinks
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class WPArticle(models.Model):
	pageid = models.IntegerField(verbose_name="Page ID",primary_key=True)
	title = models.CharField(verbose_name="Title",max_length=255)
	
	def __unicode__(self):
		return self.title

# Create your models here.
class Source(models.Model):
	title = models.CharField(verbose_name="Title",max_length=300)
	author = models.CharField(verbose_name="Author",max_length=70,blank=True)
	dateAdded = models.DateTimeField(auto_now_add=True)
	url = models.URLField(verbose_name="Source URL",verify_exists=True,max_length=500)
	content = models.TextField(blank=True)
	wikiarticles = models.ManyToManyField(WPArticle,blank=True,editable=False,related_name="relatedsources")
	cited = models.ManyToManyField(WPArticle,blank=True,editable=False,related_name="citedsources")
	
	def __unicode__(self):
		return self.title
	
	def has_content(self):
		return self.content == ""
	
	def genWPLinks(self):
		return getWikiLinks(self.url,self.content)
	
	def getWPLinks(self):
		return [article.title for article in self.wikiarticles.all()]
	
	def getWPTitles(self):
		return [l[2] for l in self.getWPLinks()]
	
	def save(self,*args,**kwargs):
		super(Source,self).save(*args,**kwargs)
		links = self.genWPLinks()
		
		for link in links:
			try:
				article = WPArticle.objects.get(pageid=link[0])
			except WPArticle.DoesNotExist:
				article = WPArticle(pageid=link[1],title=link[2])
				article.save()
				self.wikiarticles.add(article)
			else:
				self.wikiarticles.add(article)
		
	getWPLinks.short_description="Relevant Wikipedia Links"

class RSSFeed(models.Model):
	name = models.CharField(max_length=200,verbose_name="Name",blank=True)
	url = models.URLField(verbose_name="Feed URL")
	citations = models.ManyToManyField(Source,editable=False,blank=True)

	def __unicode__(self):
		return self.name
        


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	about = models.TextField(verbose_name="About Me",blank=True)
	rssfeeds = models.ManyToManyField(RSSFeed,verbose_name="RSS Feeds",blank=True)
	myCitations = models.ManyToManyField(Source,verbose_name="Citations",related_name="owners",blank=True)
	citationWatchlist = models.ManyToManyField(Source,verbose_name="Citation Watchlist",blank=True,related_name="watchers")
	
	def __unicode__(self):
		return "Profile for {0}".format(self.user.username)

def create_user_profile(sender, **kwargs):
	if kwargs['created'] and sender == User:
		u = UserProfile(user=kwargs['instance'])
		u.save()

post_save.connect(create_user_profile, sender=User)