from django import forms
from django.forms import ModelForm
from .models import Source, SimpleModel
from .models import Famine,Collection,PublishingOutlet,Available,Rated
from .models import Keyword,Commissioner,Person,MusicType,Language,Music
from .models import RequestUsePermission, FilmCompany, FilmType, Film
from .models import Location, TargetAudience
from .widgets import CollectionWidget,PublishingOutletWidget,AvailableWidget
from .widgets import RatedWidget,CommissionerWidget,MusicTypeWidget, FilmCompanyWidget
from .widgets import FilmTypeWidget
from .widgets import RequestUsePermissionWidget
from .widgets import FaminesWidget
from .widgets import PersonsWidget
from .widgets import LanguagesWidget
from .widgets import KeywordsWidget
from .widgets import LocationsWidget
from .widgets import TargetAudienceWidget


dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr)}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3})}
dselect2 = {'attrs':{'data-placeholder':'Select by name...','style':'width:100%',
	'class':'searching'}}

class SimpleForm(ModelForm):
	name = forms.CharField(**dchar)
	class Meta:
		model = SimpleModel
		fields = ['name']


class SourceForm(ModelForm):
	famines = forms.ModelMultipleChoiceField(
		queryset=Famine.objects.all(),
		widget=FaminesWidget(**dselect2),
		required=False)
	title_english = forms.CharField(**dchar)
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
	keywords = forms.ModelChoiceField(
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
		fields = 'famines,title_english,title_original,collection,publishing_outlet'
		fields += ',available,request_use_permission,rated,keywords,description'
		fields += ',comments,commissioned_by,source_link'
		#fields += ',date_created,date_released'
		fields = fields.split(',')

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
		fields = 'lyrics,music_video_link,performing_artists,composers,music_type'
		fields += ',languages'
		#fields += ',date_created,date_released'
		fields = fields.split(',')

class MusicTypeForm(SimpleForm):
	class Meta:
		model = MusicType
		fields = ['name']


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

	class Meta:
		model = Film
		fields = 'languages_original,languages_subtitle,writers,directors,film_company'
		fields += ',locations_shot,locations_released,target_audience,film_type'
		#fields += ',date_created,date_released'
		fields = fields.split(',')








