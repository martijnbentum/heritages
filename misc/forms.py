from django import forms
from django.forms import ModelForm, modelform_factory, inlineformset_factory
from .models import Famine,FamineName,CausalTrigger,Keyword, Language
from .models import KeywordRelation, License
from locations.models import Location
from .widgets import FamineNameWidget,FamineNamesWidget, FamineWidget, CausalTriggerWidget 
from .widgets import CausalTriggersWidget, CategoryKeywordWidget, KeywordsWidget
from locations.widgets import LocationsWidget
from utilities.forms import make_select2_attr

dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = make_select2_attr(input_length=0)
mft = {'fields':('name',),'widgets':{'name':forms.TextInput(dattr)}}


def create_simple_form(name):
    '''Create a simple model form based on the Model name. 
    Form is appended to model name
    Assumes the form only has a name field.
    '''
    exec(name + 'Form = modelform_factory('+name+',**mft)',globals())

#create simple forms for the following models
names = 'CausalTrigger,FamineName,Language'
for name in names.split(','):
    create_simple_form(name)

class FamineForm(ModelForm):
    names= forms.ModelMultipleChoiceField(
        queryset=FamineName.objects.all(),
        widget = FamineNamesWidget(**dselect2),
        required=False)
    locations= forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        widget = LocationsWidget(**make_select2_attr(input_length=2)),
        required=False)
    causal_triggers= forms.ModelMultipleChoiceField(
        queryset=CausalTrigger.objects.all(),
        widget = CausalTriggersWidget(**dselect2),
        required=False)
    estimated_excess_mortality= forms.IntegerField(required=False,widget=forms.NumberInput(**dattr))
    description= forms.CharField(**dtext)
    excess_mortality_description = forms.CharField(**dtext)
    comments = forms.CharField(**dtext)
    keywords = forms.ModelMultipleChoiceField(
        queryset=Keyword.objects.all(),
        widget=KeywordsWidget(**dselect2),
        required=False)
    filter_name = forms.CharField(**dchar_required)
    filter_location_name = forms.CharField(**dchar_required)

    class Meta:
        model = Famine
        fields = 'names,locations,estimated_excess_mortality,causal_triggers,description,comments,filter_name,filter_location_name'
        fields += ',keywords,excess_mortality_description'
        fields = fields.split(',')


class KeywordForm(ModelForm):
    name = forms.CharField(**dchar_required)
    description= forms.CharField(**dtext)
    comments = forms.CharField(**dtext)
    #this field is only here to ensure select is working on the formset
    locations= forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        widget = LocationsWidget(**make_select2_attr(input_length=2)),
        required=False)
    #this field is only here to ensure select is working on the formset


    class Meta:
        model = Keyword
        fields = 'name,description,comments'.split(',')

class KeywordRelationForm(ModelForm):
    container = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        widget=CategoryKeywordWidget(**dselect2))

    class Meta:
        model=KeywordRelation
        fields = 'container,contained'.split(',')

keywordkeyword_formset = inlineformset_factory(
    Keyword,KeywordRelation,fk_name = 'contained', 
    form = KeywordRelationForm, extra = 1)
    

class LicenseForm(ModelForm):
    name = forms.CharField(**dchar_required)
    description= forms.CharField(**dtext)
    comments = forms.CharField(**dtext)
    url = forms.CharField(**dchar)


    class Meta:
        model =License 
        fields = 'name,description,comments,url'.split(',')
    
