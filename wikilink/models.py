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
		
	def url(self):
		underscored = self.title.replace(" ","_")
		return "http://en.wikipedia.org/wiki/{0}".format(underscored)

	

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	about = models.TextField(verbose_name="About Me",blank=True)

	def __unicode__(self):
		return self.user.get_full_name()


# Create your models here.
class Source(models.Model):
	title = models.CharField(verbose_name="Title",max_length=300)
	citationAuthor = models.CharField(verbose_name="Citation Author",max_length=70,blank=True)
	url = models.URLField(verbose_name="Source URL",verify_exists=True,max_length=500)
	content = models.TextField(blank=True)
	wikiarticles = models.ManyToManyField(WPArticle,blank=True,editable=False,related_name="relatedsources")
	
	dateAdded = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(UserProfile,verbose_name="Creator",related_name="mysources",blank=True)
	
	citations = models.ManyToManyField(WPArticle,editable=False,related_name="citedsources",through='Citation')
	watchers = models.ManyToManyField(UserProfile,verbose_name="Citation Watchlist",blank=True,related_name="watchlist")
	
	
	
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
		
	def allCitedArticles(self):
		citations = self.citations.all()
		citedarticles = [c for c in citations]
		return citedarticles
	
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
	lastUpdate = models.DateTimeField(editable=False)
	watchers = models.ManyToManyField(UserProfile,verbose_name="Watchers",blank=True,related_name="feeds")
	
	def __unicode__(self):
		return self.name
        
class Citation(models.Model):
	dateCited = models.DateTimeField(auto_now=True)
	source = models.ForeignKey(Source)
	article = models.ForeignKey(WPArticle)
	citer = models.ForeignKey(UserProfile)
	
	def __unicode__(self):
	 	return "{0} + {1} + {2}".format(self.source,self.article,self.citer)
		
def create_user_profile(sender, **kwargs):
	if kwargs['created'] and sender == User:
		u = UserProfile(user=kwargs['instance'])
		u.save()

post_save.connect(create_user_profile, sender=User)