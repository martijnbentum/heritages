from django import forms
from django.forms import ModelForm, modelform_factory
from .models import Famine,FamineName,CausalTrigger,Keyword, Language
from locations.models import Location
from .widgets import FamineNameWidget,FamineNamesWidget, FamineWidget, CausalTriggerWidget 
from .widgets import CausalTriggersWidget, KeywordsWidget
from locations.widgets import LocationsWidget

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = {'attrs':{'data-placeholder':'Select by name...','style':'width:100%',
	'class':'searching'}}
mft = {'fields':('name',),'widgets':{'name':forms.TextInput(dattr)}}


def create_simple_form(name):
	'''Create a simple model form based on the Model name. 
	Form is appended to model name
	Assumes the form only has a name field.
	'''
	exec(name + 'Form = modelform_factory('+name+',**mft)',globals())

#create simple forms for the following models
names = 'CausalTrigger,FamineName,Keyword,Language'
for name in names.split(','):
	create_simple_form(name)

class FamineForm(ModelForm):
	names= forms.ModelMultipleChoiceField(
		queryset=FamineName.objects.all(),
		widget = FamineNamesWidget(**dselect2),
		required=False)
	locations= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2),
		required=False)
	causal_triggers= forms.ModelMultipleChoiceField(
		queryset=CausalTrigger.objects.all(),
		widget = CausalTriggersWidget(**dselect2),
		required=False)
	estimated_excess_mortality= forms.IntegerField(required=False,widget=forms.NumberInput(**dattr))
	description= forms.CharField(**dtext)
	comments = forms.CharField(**dtext)
	keywords = forms.ModelMultipleChoiceField(
		queryset=Keyword.objects.all(),
		widget=KeywordsWidget(**dselect2),
		required=False)

	class Meta:
		model = Famine
		fields = 'names,locations,estimated_excess_mortality,causal_triggers,description,comments'
		fields = fields.split(',')

