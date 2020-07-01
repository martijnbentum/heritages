from django import forms
from django.forms import ModelForm, modelform_factory
from .models import Person,Gender,Nationality,Occupation,Affiliation,Location,Keyword
from .widgets import GenderWidget, LocationWidget, OccupationWidget 
from .widgets import AffiliationWidget, NationalityWidget, KeywordsWidget

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
names = 'Gender,Nationality,Occupation,Affiliation,Location,Keyword'
for name in names.split(','):
	create_simple_form(name)

class PersonForm(ModelForm):
	name= forms.CharField(**dchar)
	gender = forms.ModelChoiceField(
		queryset=Gender.objects.all(),
		widget = GenderWidget(**dselect2),
		required=False)
	nationality = forms.ModelChoiceField(
		queryset=Nationality.objects.all(),
		widget = NationalityWidget(**dselect2),
		required=False)
	location_of_birth= forms.ModelChoiceField(
		queryset=Location.objects.all(),
		widget = LocationWidget(**dselect2),
		required=False)
	location_of_death= forms.ModelChoiceField(
		queryset=Location.objects.all(),
		widget = LocationWidget(**dselect2),
		required=False)
	occupation = forms.ModelChoiceField(
		queryset=Occupation.objects.all(),
		widget = OccupationWidget(**dselect2),
		required=False)
	affiliation= forms.ModelChoiceField(
		queryset=Affiliation.objects.all(),
		widget = AffiliationWidget(**dselect2),
		required=False)
	biography_link = forms.CharField(**dchar)
	comments = forms.CharField(**dtext)
	keywords = forms.ModelMultipleChoiceField(
		queryset=Keyword.objects.all(),
		widget=KeywordsWidget(**dselect2),
		required=False)

	class Meta:
		model = Person
		fields = 'name,gender,nationality,location_of_birth,location_of_birth'
		fields += ',occupation,affiliation,biography_link,comments,keywords'
		#fields += ',date_of_birth,date_of_death'
		fields = fields.split(',')

