from wikilink.models import Source,WPArticle
from wikilink.forms import SourceForm,URLForm,IrrelevantLinkForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect,Http404
from wikilink.etc.linkfinder import getTextFromURL
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# Create your views here.

class SourceListView(ListView):
	# See https://docs.djangoproject.com/en/dev/topics/class-based-views/#adding-extra-context
	model = Source
	
	def get_context_data(self,**kwargs):
		context = super(ListView,self).get_context_data(**kwargs)
		context['form'] = URLForm()
		context['action'] = reverse('new_url')
		
		return context

@login_required
def mycitations(request):
	u = request.user
	mycites = u.get_profile().myCitations.all()
	
	return render_to_response('wikilink/source_list.html',{'object_list':mycites},context_instance=RequestContext(request))

def irrelevant(request):
	if request.method == 'POST':
		form = IrrelevantLinkForm(request.POST)
		if form.is_valid():
			wikipageid = form.cleaned_data['wikipageid']
			sourceid = form.cleaned_data['sourceid']
			undo = form.cleaned_data['undo']
			
			s = get_object_or_404(Source,pk=sourceid)
			wp = get_object_or_404(WPArticle,pk=wikipageid)
			
			if not undo:
				s.wikiarticles.remove(wp)
				message = "Wikipedia page <em>{0}</em> marked as irrelevant.".format(wp)
				undoform = IrrelevantLinkForm({'wikipageid':wikipageid,'sourceid':sourceid,'undo':True})
				return render_to_response('wikilink/source_detail.html',{'object': s,'message':message,'undoform':undoform},context_instance=RequestContext(request))
			else:
				s.wikiarticles.add(wp)
				return HttpResponseRedirect(reverse('source_detail',args=[s.id]))
		else:
			raise Http404
	else:
		return HttpResponseRedirect(reverse('source_list'))
			

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
				s = Source(url=url,title=title,content=text)
				s.save()
				return HttpResponseRedirect(reverse('source_detail',args=[s.id])) # Redirect after POST
			else:
				message = "Error obtaining text from URL.  Please use the manual text entry form or try a different URL."
	else:
		form = URLForm()
	
	actionurl = reverse('new_url')
	return render_to_response('wikilink/newsource.html',{'form':form,'action':actionurl,'message':message,},context_instance=RequestContext(request))
# 	
# def login(request):
# 	if request.method == 'POST':
# 		username = request.POST['username']
# 		password = request.POST['password']
# 		user = authenticate(username=username, password=password)
# 		if user is not None:
# 			if user.is_active:
# 				login(request, user)
# 				# Redirect to a success page.
# 			else:
# 				pass
# 				# Return a 'disabled account' error message
# 		else:
# 			pass
# 		# Return an 'invalid login' error message.
# 	else:
# 		return render_to_response('wikilink/login.html')