from django import forms
from django.forms import ModelForm, modelform_factory
from .models import Source, SimpleModel
from .models import Famine,Collection,PublishingOutlet,Available,Rated
from .models import Keyword,Commissioner,MusicType,Language,Music, Infographic
from .models import RequestUsePermission, FilmCompany, FilmType, Film, Text, Image
from .models import Location, TargetAudience, TextType, InfographicType, ImageType
from .models import Publisher, PictureStoryType, PictureStory
from .widgets import CollectionWidget,PublishingOutletWidget,AvailableWidget, TextTypeWidget
from .widgets import RatedWidget,CommissionerWidget,MusicTypeWidget, FilmCompanyWidget
from .widgets import ImageTypeWidget, InfographicTypeWidget,FilmTypeWidget, PublisherWidget
from .widgets import RequestUsePermissionWidget, PublishersWidget
from .widgets import FaminesWidget
from .widgets import LanguagesWidget
from .widgets import KeywordsWidget
from .widgets import LocationsWidget
from .widgets import TargetAudienceWidget
from persons.models import Person
from persons.widgets import PersonWidget, PersonsWidget

#setting default kwargs for to clean up form definition
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
names = 'TextType,ImageType,MusicType,PictureStoryType,FilmType,InfographicType'
names += ',FilmCompany,TargetAudience,Collection,Publisher,Location,Language'
names += ',Keyword'
for name in names.split(','):
	create_simple_form(name)
#----

# set the field names for the parent source form, these fields need to be
# set in the children forms Meta class as well (I think)
source_fields = 'famines,title_english,title_original,collection,publishing_outlet'
source_fields += ',available,request_use_permission,rated,keywords,description'
source_fields += ',comments,commissioned_by,source_link'

class SourceForm(ModelForm):
	famines = forms.ModelMultipleChoiceField(
		queryset=Famine.objects.all(),
		widget=FaminesWidget(**dselect2),
		required=False)
	title_english = forms.CharField(**dchar_required)
	title_original = forms.CharField(**dchar)
	collection = forms.ModelChoiceField(
		queryset=Collection.objects.all(),
		widget= CollectionWidget(**dselect2),
		required=False)
	publishing_outlet = forms.ModelChoiceField(
		queryset=PublishingOutlet.objects.all(),
		widget= PublishingOutletWidget(**dselect2),
		required=False)
	available = forms.ModelChoiceField(
		queryset=Available.objects.all(),
		widget= AvailableWidget(**dselect2),
		required=False)
	request_use_permission = forms.ModelChoiceField(
		queryset=RequestUsePermission.objects.all(),
		widget= RequestUsePermissionWidget(**dselect2),
		required=False)
	rated = forms.ModelChoiceField(
		queryset=Rated.objects.all(),
		widget= RatedWidget(**dselect2),
		required=False)
	keywords = forms.ModelMultipleChoiceField(
		queryset=Keyword.objects.all(),
		widget=KeywordsWidget(**dselect2),
		required=False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)
	commissioned_by = forms.ModelChoiceField(
		queryset=Commissioner.objects.all(),
		widget= CommissionerWidget(**dselect2),
		required=False)
	source_link = forms.CharField(**dchar)
	#date_created
	#date_released

	class Meta:
		model = Source
		#fields += ',date_created,date_released'
		fields = source_fields.split(',')

class MusicForm(SourceForm):
	lyrics = forms.CharField(**dtext)
	music_video_link = forms.CharField(**dchar)
	performing_artists = forms.CharField(**dchar)
	composers = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	music_type = forms.ModelChoiceField(
		queryset=MusicType.objects.all(),
		widget= MusicTypeWidget(**dselect2),
		required=False)
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget= LanguagesWidget(**dselect2),
		required=False)

	class Meta:
		model = Music
		fields = source_fields
		fields += ',lyrics,music_video_link,performing_artists,composers,music_type'
		fields += ',languages'
		#fields += ',date_created,date_released'
		fields = fields.split(',')


class FilmForm(SourceForm):
	languages_original = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	languages_subtitle = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	writers= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	directors= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	film_company= forms.ModelChoiceField(
		queryset=FilmCompany.objects.all(),
		widget = FilmCompanyWidget(**dselect2),
		required=False)
	locations_shot= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2),
		required=False)
	locations_released= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2),
		required=False)
	target_audience= forms.ModelChoiceField(
		queryset=TargetAudience.objects.all(),
		widget = TargetAudienceWidget(**dselect2),
		required=False)
	film_type= forms.ModelChoiceField(
		queryset=FilmType.objects.all(),
		widget = FilmTypeWidget(**dselect2),
		required=False)
	video_link = forms.CharField(**dchar)

	class Meta:
		model = Film
		fields = source_fields
		fields += ',languages_original,languages_subtitle,writers,directors,film_company'
		fields += ',locations_shot,locations_released,target_audience,film_type'
		#fields += ',date_created,date_released'
		fields = fields.split(',')


class TextForm(SourceForm):
	text_type= forms.ModelChoiceField(
		queryset=TextType.objects.all(),
		widget = TextTypeWidget(**dselect2),
		required=False)
	authors= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	editors= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	translators= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	publishers= forms.ModelMultipleChoiceField(
		queryset=Publisher.objects.all(),
		widget = PublishersWidget(**dselect2),
		required=False)
	
	class Meta:
		model = Text
		fields = source_fields
		fields += ',text_type,authors,editors,translators,publishers,text_file,excerpt_file'
		fields = fields.split(',')
	
class InfographicForm(SourceForm):
	infographic_type= forms.ModelChoiceField(
		queryset=InfographicType.objects.all(),
		widget = InfographicTypeWidget(**dselect2),
		required=False)
	creators = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	
	class Meta:
		model = Infographic
		fields = source_fields
		fields += ',infographic_type,creators,image_file'
		fields = fields.split(',')


class ImageForm(SourceForm):
	image_type= forms.ModelChoiceField(
		queryset=ImageType.objects.all(),
		widget = ImageTypeWidget(**dselect2),
		required=False)
	creators = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2),
		required=False)
	
	class Meta:
		model = Image
		fields = source_fields
		fields += ',image_type,creators,image_file'
		fields = fields.split(',')


class PictureStoryForm(SourceForm):
	picture_story_type= forms.ModelChoiceField(
		queryset=ImageType.objects.all(),
		widget = ImageTypeWidget(**dselect2),
		required=False)
	authors = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	artists = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	publishers= forms.ModelMultipleChoiceField(
		queryset=Publisher.objects.all(),
		widget = PublishersWidget(**dselect2),
		required=False)
	
	class Meta:
		model = PictureStory
		fields = source_fields
		fields += ',picture_story_type,authors,artists,publishers,image_file,excerpt_file'
		fields = fields.split(',')










