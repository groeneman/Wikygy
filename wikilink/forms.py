from django.forms import ModelForm
from django import forms
from wikilink.models import Source

class SourceForm(ModelForm):
	class Meta:
		model = Source

class URLForm(forms.Form):
	url = forms.URLField(label='URL',widget=forms.TextInput(attrs={'size':100}))
	source_type = forms.ChoiceField((('HTML','Web Link'),('RSS','RSS Feed')))
	
class RSSUpdateForm(forms.Form):
	rssid = forms.IntegerField(widget=forms.HiddenInput)
	action = forms.CharField(widget=forms.HiddenInput)

class SourceArticleLinkForm(forms.Form):
	sourceid = forms.IntegerField(widget=forms.HiddenInput)
	articleid = forms.IntegerField(widget=forms.HiddenInput)
	undo = forms.BooleanField(widget=forms.HiddenInput,required=False)
	
class SourceIDForm(forms.Form):
	sourceid = forms.IntegerField(widget=forms.HiddenInput)
	
class MyRSSForm(forms.Form):
	rssid = forms.IntegerField(widget=forms.HiddenInput)