from wikilink.models import Source,WPArticle,Citation,RSSFeed
from wikilink.forms import SourceForm,URLForm,SourceArticleLinkForm,RSSUpdateForm,SourceIDForm,MyRSSForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect,Http404,HttpResponseServerError
from wikilink.etc.linkfinder import getTextFromURL
from django.core.urlresolvers import reverse
from django.views.generic import ListView,DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from collections import namedtuple
import feedparser
from django.db.models import Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages

# Create your views here.

class SourceListView(ListView):
	# See https://docs.djangoproject.com/en/dev/topics/class-based-views/#adding-extra-context
	model = Source
	paginate_by = 10
	
	def get_context_data(self,**kwargs):
		context = super(SourceListView,self).get_context_data(**kwargs)
		context['form'] = URLForm()
		context['action'] = reverse('new_url')
		context['heading'] = "Sources"
		
		if "rssid" in self.kwargs.keys():
			rssid =self.kwargs['rssid']
			context['feed'] = RSSFeed.objects.get(pk=rssid)
			context['feed'].updateForm = RSSUpdateForm({"action":"update","rssid":context['feed'].id})
			context['feed'].addToMy = MyRSSForm({'rssid':rssid})
			context['heading'] = "Stories from "+ context['feed'].name
		elif "uncited" in self.args:
			context['heading'] = "Uncited Sources"
			
		return context
		
	def get_queryset(self):
		if "rssid" in self.kwargs.keys():
			feed = get_object_or_404(RSSFeed,pk=self.kwargs['rssid'])
			return Source.objects.filter(feeds=feed)
		elif "uncited" in self.args:
			return Source.objects.annotate(cite_count=Count('citations')).filter(cite_count__eq=0)
		else:
			return Source.objects.all()

class RecentlyCitedView(SourceListView):
	template_name = "wikilink/recent_cite_list.html"
	def get_queryset(self):
		cites = Citation.objects.order_by('-dateCited')[:50]
		return cites
	
	def get_context_data(self,**kwargs):
		context = super(SourceListView,self).get_context_data(**kwargs)
		context['heading'] = "Recently Cited"
		return context
		
class RSSListView(ListView):
	model = RSSFeed
	
	def get_context_data(self,**kwargs):
		context = super(RSSListView,self).get_context_data(**kwargs)
		context['form'] = URLForm(initial={'source_type':'RSS'})
		return context

@require_POST
def update_rss(request):
	if 'action' in request.POST.keys() and request.POST['action'] == 'update':
		print "Start"
		feed = RSSFeed.objects.get(pk=request.POST['rssid'])
		feed.update()
		print "Done!"
		return HttpResponseRedirect(reverse('rss_detail', args=(feed.id,)))

def generateArticleContainers(request,articles,source):
	article_containers = []
	
	ArticleContainer = namedtuple('ArticleContainer',['meta','irr_cited_form','citation','citation_undo'])
	
	for a in articles:
		citation_undo = None
		try:
			c= Citation.objects.get(article=a,source=source)
		except Citation.DoesNotExist:
			c=None
		else:
			if request.user.is_authenticated() and request.user.get_profile() == c.citer:
				citation_undo = SourceArticleLinkForm({'articleid':a.pageid,'sourceid':source.id,'undo':True})
		finally:
			if request.user.is_authenticated():
				form = SourceArticleLinkForm({'articleid':a.pageid,'sourceid':source.id})
			else:
				form = None
			
			article_containers.append(ArticleContainer(a,form,c,citation_undo))
			
	return article_containers
			
def handleCite(request):
	message,undoform = None,None
	source,wp,undo = parseSourceArticleLinkForm(request)
	
	if not undo:
		try:
			c = Citation.objects.get(source=source,article=wp,citer=request.user.get_profile())
		except Citation.DoesNotExist:
			c = Citation(source=source,article=wp,citer=request.user.get_profile())
			c.save()
		messages.info(request,"Source marked as cited on Wikipedia page <em>{0}</em> by {1}.".format(wp,request.user.get_full_name()))
		undoform = SourceArticleLinkForm({'articleid':wp.pageid,'sourceid':source.id,'undo':True})
	else:
		Citation.objects.get(source=source,article=wp,citer=request.user.get_profile()).delete()
	
	return undoform
	
def handleIrrelevant(request):
	message, undoform = None,None
	source,wp,undo = parseSourceArticleLinkForm(request)
	
	if not undo:
		source.wikiarticles.remove(wp)
		messages.info(request,"Wikipedia page <em>{0}</em> marked as irrelevant.".format(wp))
		undoform = SourceArticleLinkForm({'articleid':wp.pageid,'sourceid':source.id,'undo':True})
	else:
		source.wikiarticles.add(wp)
		
	return undoform

def parseSourceArticleLinkForm(request):
	form = SourceArticleLinkForm(request.POST)
	if form.is_valid():
		sourceid = form.cleaned_data['sourceid']
		undo = form.cleaned_data['undo']
		articleid = form.cleaned_data['articleid']
		source = get_object_or_404(Source,pk=sourceid)
		article = get_object_or_404(WPArticle,pk=articleid)
	else:
		raise HttpResponseServerError
		
	return source,article,undo

@login_required
@require_POST
def source_action(request,pk,action):
	source = get_object_or_404(Source,pk=pk)
	
	print "in!"
	
	if action == 'irrelevant':
		undoform = handleIrrelevant(request)
	elif action == 'cite':
		undoform = handleCite(request)
	elif action == 'watch':
		print "Marked as watch"
		undoform = handleWatch(request)
	elif action == 'delete':
		messages.info(request,"Are you sure you want to delete \"{0}\"?  This cannot be undone: <a href='{1}'>Yes</a> <a href='{2}'>No</a>".\
			format(source,'javascript:document.delete_confirm.submit()',reverse('source_detail',args=[source.id])))
	elif action == 'deleteconfirm':
		source.delete()
		messages.info(request,"Source \"{0}\" permanently deleted".format(source))
		return HttpResponseRedirec(reverse('source_list'))
	return HttpResponseRedirect(reverse('source_detail',args=[source.id]))

def source_detail(request,pk,action=None):
	source = get_object_or_404(Source,pk=pk)
	toggleWatchList = SourceIDForm({'sourceid':source.id})

	articles = source.wikiarticles.all()
	article_containers = generateArticleContainers(request,articles,source)
	
	if request.user.is_authenticated() and source.creator == request.user.get_profile():
		deleteSourceForm = SourceIDForm({'sourceid':source.id})
	else:
		deleteSourceForm = None
	
	return render_to_response('wikilink/source_detail.html',\
			{'source':source,'articles':article_containers,'toggleWatchList':toggleWatchList,'deleteSourceForm':deleteSourceForm},\
			context_instance=RequestContext(request))

@login_required
@require_POST
def handleWatch(request):
	u = request.user.get_profile()
	form = SourceIDForm(request.POST)
	if form.is_valid():
		sourceid = form.cleaned_data['sourceid']
		s = get_object_or_404(Source,pk=sourceid)
		
		if s in u.watchlist.all():
			u.watchlist.remove(s)
			messages.info(request,"Source \"{0}\" removed from watchlist.".format(s))
		else:
			u.watchlist.add(s)
			messages.info(request,message = "Source \"{0}\" added to watchlist.".format(s))
			
		undoform = SourceIDForm({'sourceid':s.id})
		return undoform
	else:
		return HttpResponseRedirect(reverse('source_detail',args=[s.id]))
			
@login_required
def workbench(request):
	return HttpResponseRedirect(reverse('user_profile',args=[request.user.username]))
	
def new_source(request):
	if request.method == 'POST': # If the form has been submitted...
		form = SourceForm(request.POST) # A form bound to the POST data
		if form.is_valid():
			s = form.save(commit = False)
			s.save()
			return HttpResponseRedirect(reverse('source_detail',args=[s.id])) # Redirect after POST
	else:
		form = SourceForm() # An unbound form

	actionurl = reverse('new_source')
	
	return render_to_response('wikilink/newsource.html',\
	 		{'form': form,'action':actionurl}, context_instance=RequestContext(request))
		
def new_source_from_url(request):
	message = None
	if request.method == 'POST':
		form = URLForm(request.POST)
		if form.is_valid():
			url = form.cleaned_data['url']
			source_type = form.cleaned_data['source_type']
			
			if source_type == "HTML":
				title,text = getTextFromURL(url)
				if text is not None and title is not None:
					s = Source(creator=request.user.get_profile(),url=url,title=title,content=text)
					s.save()
					return HttpResponseRedirect(reverse('source_detail',args=[s.id])) # Redirect after POST
				else:
					message = "Error obtaining text from URL.  Please use the manual text entry form or try a different URL."
			elif source_type=='RSS':
				f = RSSFeed(url=url)
				f.save()
				f.watchers.add(request.user.get_profile())
				return HttpResponseRedirect(reverse('rss_detail',args=[f.id]))
	else:
		form = URLForm()
	
	actionurl = reverse('new_url')
	return render_to_response('wikilink/newsource.html',{'form':form,'action':actionurl,'message':message,},context_instance=RequestContext(request))
	
def source_update(request,pk):
	s = Source.objects.get(pk=pk)
	s.update()
	return HttpResponseRedirect(reverse('source_detail',args=[s.id])) # Redirect after POST

@login_required
@require_POST
def watch_rss(request):
	message,undoform = None,None
	
	u = request.user.get_profile()
	form = MyRSSForm(request.POST)
	if form.is_valid():
		rssid = form.cleaned_data['rssid']
		f = get_object_or_404(RSSFeed,pk=rssid)
		
		if f in u.feeds.all():
			u.feeds.remove(f)
			messages.info(request, "Feed \"{0}\" removed from My RSS Feeds.".format(f))
		else:
			u.feeds.add(f)
			messages.info(request, "Feed \"{0}\" added to My RSS Feeds.".format(f))
		
		return HttpResponseRedirect(reverse('rss_detail',args=[f.id]))
	else:
		return HttpResponseRedirect(reverse('feeds'))

@login_required
def delete(request,pk,confirm=False):
	s = Source.objects.get(pk=pk)
	
	if not confirm:
		message.info("Are you sure you want to delete {0}.  This cannot be undone: <a href='{1}'>Yes</a> <a href='{2}'>No</a>").\
			format(source,reverse('source_detail',args=[source.id]),reverse('source_detail',args=[source.id]))
		return HttpResponseRedirect(reverse('source_detail',args=[s.id]))

def user_profile(request,username):
	u = User.objects.get(username=username)
	profile = u.get_profile()
	
	myWatchlist = profile.watchlist.all()
	myCitations = profile.my_citations.all()
	myCitations = set([citation.source for citation in myCitations])
	mySources = profile.my_sources.all()
	myRSSFeeds = profile.feeds.all()
	
	if u == request.user:
		addSource = URLForm()
		name = "My"
	else:
		addSource= None
		name = u.first_name+"'s"
	
	return render_to_response('wikilink/workbench.html',\
			{'myWatchlist':myWatchlist,'mySources':mySources,'myCitations':myCitations,'myRSSFeeds':myRSSFeeds,'form':addSource,'name':name},\
			context_instance=RequestContext(request))