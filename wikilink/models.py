from django.db import models
from wikilink.etc.linkfinder import getWikiLinks
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import feedparser
import datetime

class WPArticle(models.Model):
	pageid = models.IntegerField(verbose_name="Page ID",primary_key=True)
	title = models.CharField(verbose_name="Title",max_length=255)
	
	def __unicode__(self):
		return self.title
		
	def url(self):
		underscored = self.title.replace(" ","_")
		return "http://en.wikipedia.org/wiki/"+underscored

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	about = models.TextField(verbose_name="About Me",blank=True)

	def __unicode__(self):
		return self.user.get_full_name()

# Create your models here.
class Source(models.Model):
	title = models.CharField(verbose_name="Title",max_length=300)
	url = models.URLField(verbose_name="Source URL",verify_exists=True,unique=True,max_length=500)
	content = models.TextField(blank=True)
	published = models.DateTimeField(blank=True,null=True)
	wikiarticles = models.ManyToManyField(WPArticle,blank=True,editable=False,related_name="relatedsources")
	
	dateAdded = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(UserProfile,verbose_name="Creator",related_name="my_sources")
	
	citations = models.ManyToManyField(WPArticle,editable=False,related_name="cited_sources",through='Citation')
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
		
	def numCitiations(self):
		return Count(self.citations)
	
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
	url = models.URLField(verbose_name="Feed URL",unique=True)
	link = models.URLField(verbose_name="Feed Link",blank=True)
	sources = models.ManyToManyField(Source,editable=False,blank=True)
	lastUpdate = models.DateTimeField(editable=False,blank=True,null=True)
	watchers = models.ManyToManyField(UserProfile,verbose_name="Watchers",blank=True,related_name="feeds")
	
	def __unicode__(self):
		return self.name
	
	def save(self,*args,**kwargs):
		super(RSSFeed,self).save(*args,**kwargs)
		self.update()
	
	def save_no_update(self,*args,**kwargs):
		super(RSSFeed,self).save(*args,**kwargs)
	
	def update(self):
		parsed = feedparser.parse(self.url)
		self.name = unicode(parsed.feed.title)
		self.link = parsed.feed.link
		self.save_no_update()
		
		rssUser = User.objects.get(username="RSS").get_profile()
		
		for s in parsed.entries:
			title = unicode(s.title).encode("UTF-8")
			published = datetime.datetime(*s.updated_parsed[:6])
			url = s.link
			
			try:
				source=Source.objects.get(url=url)
			except Source.DoesNotExist:
				source = Source(title=title,url=url,published=published,creator=rssUser)
				source.save()
				self.sources.add(source)
			else:
				print source.title ,"already exists in DB."
				self.sources.add(source)
        
class Citation(models.Model):
	dateCited = models.DateTimeField(auto_now=True)
	source = models.ForeignKey(Source)
	article = models.ForeignKey(WPArticle,related_name="citations")
	citer = models.ForeignKey(UserProfile,related_name="my_citations")
	
	def __unicode__(self):
	 	return "{0} + {1} + {2}".format(self.source,self.article,self.citer)

# Signal to mandate the creation of a user profie

def create_user_profile(sender, **kwargs):
	if kwargs['created'] and sender == User:
		u = UserProfile(user=kwargs['instance'])
		u.save()

post_save.connect(create_user_profile, sender=User)