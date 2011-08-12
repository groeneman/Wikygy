from django.forms import ModelForm
from django import forms
from wikilink.models import Source

class SourceForm(ModelForm):
	class Meta:
		model = Source

class URLForm(forms.Form):
	url = forms.URLField(label='URL',widget=forms.TextInput(attrs={'size':100}))
	
class SourceArticleLinkForm(forms.Form):
	sourceid = forms.IntegerField(widget=forms.HiddenInput)
	articleid = forms.IntegerField(widget=forms.HiddenInput)
	undo = forms.BooleanField(widget=forms.HiddenInput,required=False)