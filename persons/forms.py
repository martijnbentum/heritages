from django import forms
from django.forms import ModelForm, modelform_factory
from .models import Person,Gender,Nationality,Occupation,Affiliation
from .widgets import GenderWidget, OccupationWidget,OccupationsWidget 
from .widgets import AffiliationWidget, NationalityWidget 
from locations.models import Location
from locations.widgets import LocationWidget, LocationsWidget
from misc.models import Famine, Language, Keyword, License
from misc.widgets import FaminesWidget, LanguagesWidget, KeywordsWidget
from misc.widgets import LicenseWidget
from utilities.forms import make_select2_attr

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = make_select2_attr(input_length = 0)
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
    pseudonyms= forms.CharField(**dchar)
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
    occupation = forms.ModelMultipleChoiceField(
        queryset=Occupation.objects.all(),
        widget = OccupationsWidget(**dselect2),
        required=False)
    affiliation= forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        widget = AffiliationWidget(**dselect2),
        required=False)
    biography_link = forms.CharField(**dchar)
    comments = forms.CharField(**dtext)
    description = forms.CharField(**dtext)
    keywords = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.all(),
        widget=KeywordsWidget(**dselect2),
        required=False)
    date_of_birth= forms.CharField(**dchar)
    date_of_death= forms.CharField(**dchar)
    viaf = forms.CharField(**dchar)
    famines = forms.ModelMultipleChoiceField(
        queryset=Famine.objects.all(),
        widget=FaminesWidget(**dselect2),
        required=False)
    license_image= forms.ModelChoiceField(
        queryset=License.objects.all(),
        widget = LicenseWidget(**dselect2),
        required=False)
    license_thumbnail= forms.ModelChoiceField(
        queryset=License.objects.all(),
        widget = LicenseWidget(**dselect2),
        required=False)
    reference= forms.CharField(**dtext)

    class Meta:
        model = Person
        fields = 'name,gender,nationality,location_of_birth,location_of_death'
        fields += ',occupation,affiliation,biography_link,comments,keywords'
        fields += ',date_of_birth,date_of_death,description,flag,thumbnail,pseudonyms'
        fields += ',pseudonym_precedent,viaf,famines,reference,license_image'
        fields += ',license_thumbnail'
        fields = fields.split(',')

