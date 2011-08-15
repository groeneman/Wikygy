from wikilink.models import Source,WPArticle,Citation
from wikilink.forms import SourceForm,URLForm,SourceArticleLinkForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect,Http404
from wikilink.etc.linkfinder import getTextFromURL
from django.core.urlresolvers import reverse
from django.views.generic import ListView,DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from collections import namedtuple

# Create your views here.

class SourceListView(ListView):
	# See https://docs.djangoproject.com/en/dev/topics/class-based-views/#adding-extra-context
	model = Source	
	def get_context_data(self,**kwargs):
		context = super(ListView,self).get_context_data(**kwargs)
		context['form'] = URLForm()
		context['action'] = reverse('new_url')
		
		return context

def generateArticleContainers(request,articles,source):
	article_containers = []
	
	ArticleContainer = namedtuple('ArticleContainer',['meta','irr_cited_form','citation','citation_undo'])
	
	for a in articles:
		citation_undo = None
		try:
			c= Citation.objects.get(article=a,source=source)
		except Citation.DoesNotExist:
			c=(None)
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
			
def handleCite(request,undo,source,wp):
	message,undoform = None,None	
	
	if not undo:
		try:
			c = Citation.objects.get(source=source,article=wp,citer=request.user.get_profile())
		except Citation.DoesNotExist:
			c = Citation(source=source,article=wp,citer=request.user.get_profile())
			c.save()
		message = "Source marked as cited on Wikipedia page <em>{0}</em> by {1}.".format(wp,request.user.get_full_name())
		undoform = SourceArticleLinkForm({'articleid':wp.pageid,'sourceid':source.id,'undo':True})
	else:
		Citation.objects.get(source=source,article=wp,citer=request.user).delete()
	
	return message, undoform
	
def handleIrrelevant(undo,source,wp):
	message, undoform = None,None
	if not undo:
		source.wikiarticles.remove(wp)
		message = "Wikipedia page <em>{0}</em> marked as irrelevant.".format(wp)
		undoform = SourceArticleLinkForm({'articleid':wp.pageid,'sourceid':source.id,'undo':True})
	else:
		source.wikiarticles.add(wp)
		
	return message,undoform

def source_detail(request,pk,action=None):
	source = get_object_or_404(Source,pk=pk)
	message, undoform = None, None
	
	if request.method=='POST':
		form = SourceArticleLinkForm(request.POST)
		if form.is_valid():
			articleid = form.cleaned_data['articleid']
			sourceid = form.cleaned_data['sourceid']
			undo = form.cleaned_data['undo']
			wp = get_object_or_404(WPArticle,pk=articleid)
			
			if action == 'irrelevant':
				message,undoform = handleIrrelevant(undo,source,wp)
			elif action == 'cite':
				message,undoform = handleCite(request,undo,source,wp)
			else:
				raise Http404
		else:
			raise Http404
	
	articles = source.wikiarticles.all()
	article_containers = generateArticleContainers(request,articles,source)
	
	return render_to_response('wikilink/source_detail.html',{'source':source,'articles':article_containers,'message':message,'undoform':undoform},\
								context_instance=RequestContext(request))
	
@login_required
def workbench(request):
	u = request.user
	
	myWatchlist = u.get_profile().watchlist.all()
	myCitations = u.get_profile().my_citations.all()
	myCitations = set([citation.source for citation in myCitations])
	mySources = u.get_profile().my_sources.all()
	myRSSFeeds = u.get_profile().feeds.all()
		
	form = URLForm()
	action = reverse('new_url')
	
	return render_to_response('wikilink/workbench.html',\
		{'myWatchlist':myWatchlist,'mySources':mySources,'myCitations':myCitations,'myRSSFeeds':myRSSFeeds,'form':form,'action':action},context_instance=RequestContext(request))

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
	
	return render_to_response('wikilink/newsource.html', {
		'form': form,'action':actionurl}, context_instance=RequestContext(request))
		
def new_source_from_url(request):
	message = None
	if request.method == 'POST':
		form = URLForm(request.POST)
		if form.is_valid():
			url = form.cleaned_data['url']
			title,text = getTextFromURL(url)
			if text is not None and title is not None:
				s = Source(creator=request.user.get_profile(),url=url,title=title,content=text)
				s.save()
				return HttpResponseRedirect(reverse('source_detail',args=[s.id])) # Redirect after POST
			else:
				message = "Error obtaining text from URL.  Please use the manual text entry form or try a different URL."
	else:
		form = URLForm()
	
	actionurl = reverse('new_url')
	return render_to_response('wikilink/newsource.html',{'form':form,'action':actionurl,'message':message,},context_instance=RequestContext(request))
	
def new_rss(request):
	message = None
	if request.method == 'POST':
		form = URLForm(request.POST)
		if form.is_valid():
			feedurl= form.cleaned_data['url']
			