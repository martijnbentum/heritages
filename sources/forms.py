from django import forms
from django.forms import ModelForm, modelform_factory
from .models import Source, SimpleModel, Videogame
from .models import Collection,PublishingOutlet,Available,Rated
from .models import Commissioner,MusicType,Music, Infographic,Recordedspeech
from .models import Permission, FilmCompany, FilmType, Film, Text, Image,Artefact
from .models import TargetAudience, TextType, InfographicType, ImageType,ArtefactType
from .models import Publisher, PictureStoryType, PictureStory, Institution
from .models import GameType, ProductionStudio,RecordedspeechType,BroadcastingStation
from .models import Memorialsite,MemorialType
from .widgets import CollectionWidget,PublishingOutletWidget,AvailableWidget, TextTypeWidget
from .widgets import RatedWidget,CommissionerWidget,MusicTypeWidget, FilmCompanyWidget
from .widgets import ImageTypeWidget, InfographicTypeWidget,FilmTypeWidget, PublisherWidget
from .widgets import PermissionWidget, PublishersWidget, ArtefactTypeWidget
from .widgets import TargetAudienceWidget, PictureStoryTypeWidget,FilmCompaniesWidget
from .widgets import TargetAudienceWidget,InstitutionsWidget
from .widgets import GameTypeWidget,ProductionStudiosWidget
from .widgets import RecordedspeechTypeWidget,BroadcastingStationWidget
from .widgets import MemorialTypeWidget
from locations.models import Location
from locations.widgets import LocationWidget, LocationsWidget
from misc.models import Famine, Language, Keyword, License
from misc.widgets import FaminesWidget, LanguagesWidget, KeywordsWidget
from misc.widgets import LicenseWidget
from persons.models import Person
from persons.widgets import PersonWidget, PersonsWidget
from utilities.forms import make_select2_attr


#setting default kwargs for to clean up form definition
dattr = {'attrs':{'style':'width:100%'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':False}
dselect2 = make_select2_attr(input_length = 0)
dselect2n2 = make_select2_attr(input_length = 2)
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
names += ',Keyword,PublishingOutlet,Institution,GameType,ProductionStudio,RecordedspeechType'
names += ',BroadcastingStation,MemorialType,ArtefactType'
for name in names.split(','):
	create_simple_form(name)
#----

# set the field names for the parent source form, these fields need to be
# set in the children forms Meta class as well (I think)
source_fields = 'famines,title_english,title_original,collection,publishing_outlet'
source_fields += ',available,permission,rated,keywords,description'
source_fields += ',comments,commissioned_by,source_link,flag,thumbnail'
source_fields += ',date_created,date_released,setting,release_date_precedent'
source_fields += ',license_image,license_thumbnail,reference'

class SourceForm(ModelForm):
	famines = forms.ModelMultipleChoiceField(
		queryset=Famine.objects.all(),
		widget=FaminesWidget(**dselect2),
		required=False)
	title_original = forms.CharField(**dchar_required)
	title_english = forms.CharField(**dchar_required)
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
	permission = forms.ModelChoiceField(
		queryset=Permission.objects.all(),
		widget= PermissionWidget(**dselect2),
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
	date_created= forms.CharField(**dchar)
	date_released= forms.CharField(**dchar)
	setting= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
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
		model = Source
		fields = source_fields.split(',')

class MusicForm(SourceForm):
	lyrics = forms.CharField(**dtext)
	music_video_link = forms.CharField(**dchar)
	album = forms.CharField(**dchar)
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
		fields += ',languages,album'
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
	creators= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	film_companies= forms.ModelMultipleChoiceField(
		queryset=FilmCompany.objects.all(),
		widget = FilmCompaniesWidget(**dselect2),
		required=False)
	locations_shot= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
		required=False)
	locations_released= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
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
	video_part_link = forms.CharField(**dchar)

	class Meta:
		model = Film
		fields = source_fields
		fields += ',languages_original,languages_subtitle,writers,directors,film_companies'
		fields += ',locations_shot,locations_released,target_audience,film_type,video_link'
		fields += ',video_part_link,creators'
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
	institution_authors= forms.ModelMultipleChoiceField(
		queryset=Institution.objects.all(),
		widget = InstitutionsWidget(**dselect2),
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
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget= LanguagesWidget(**dselect2),
		required=False)
	original_languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget= LanguagesWidget(**dselect2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget= LocationsWidget(**dselect2n2),
		required=False)
	
	class Meta:
		model = Text
		fields = source_fields
		fields += ',text_type,authors,editors,translators,publishers,text_file,excerpt_file'
		fields += ',languages,locations,original_languages,institution_authors'
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
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget= LanguagesWidget(**dselect2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget= LocationsWidget(**dselect2n2),
		required=False)
	
	class Meta:
		model = Infographic
		fields = source_fields
		fields += ',infographic_type,creators,image_file,languages,locations,image_filename'
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
		widget = LocationsWidget(**dselect2n2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget= LocationsWidget(**dselect2),
		required=False)
	
	class Meta:
		model = Image
		fields = source_fields
		fields += ',image_type,creators,image_file,locations,image_filename'
		fields = fields.split(',')

class ArtefactForm(SourceForm):
	artefact_type= forms.ModelChoiceField(
		queryset=ArtefactType.objects.all(),
		widget = ArtefactTypeWidget(**dselect2),
		required=False)
	creators = forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget= LocationsWidget(**dselect2),
		required=False)
	
	class Meta:
		model = Artefact
		fields = source_fields
		fields += ',artefact_type,creators,image_file,locations,image_filename'
		fields = fields.split(',')


class PictureStoryForm(SourceForm):
	picture_story_type= forms.ModelChoiceField(
		queryset=PictureStoryType.objects.all(),
		widget = PictureStoryTypeWidget(**dselect2),
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
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget= LanguagesWidget(**dselect2),
		required=False)
	locations = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget= LocationsWidget(**dselect2n2),
		required=False)
	
	class Meta:
		model = PictureStory
		fields = source_fields
		fields += ',picture_story_type,authors,artists,publishers,image_file,excerpt_file'
		fields += ',languages,locations,image_filename'
		fields = fields.split(',')




class VideogameForm(SourceForm):
	game_type= forms.ModelChoiceField(
		queryset=GameType.objects.all(),
		widget = GameTypeWidget(**dselect2),
		required=False)
	production_studio = forms.ModelMultipleChoiceField(
		queryset=ProductionStudio.objects.all(),
		widget = ProductionStudiosWidget(**dselect2),
		required=False)
	languages_original = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	languages_subtitle = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	video_link = forms.CharField(**dchar)

	class Meta:
		model = Videogame
		fields = source_fields
		fields += ',game_type,languages_original,languages_subtitle,video_link'
		fields += ',production_studio'
		fields = fields.split(',')


class RecordedspeechForm(SourceForm):
	recordedspeech_type= forms.ModelChoiceField(
		queryset=RecordedspeechType.objects.all(),
		widget = RecordedspeechTypeWidget(**dselect2),
		required=False)
	creators= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	speakers= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	broadcasting_station= forms.ModelChoiceField(
		queryset=BroadcastingStation.objects.all(),
		widget = BroadcastingStationWidget(**dselect2),
		required=False)
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	locations_recorded= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
		required=False)
	audio_link = forms.CharField(**dchar)

	class Meta:
		model = Recordedspeech
		fields = source_fields
		fields += ',recordedspeech_type,creators,speakers,languages,audio_link'
		fields += ',broadcasting_station,locations_recorded'
		fields = fields.split(',')

class MemorialsiteForm(SourceForm):
	memorial_type= forms.ModelChoiceField(
		queryset=MemorialType.objects.all(),
		widget = MemorialTypeWidget(**dselect2),
		required=False)
	creators= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	artists= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	donor_persons= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	donor_institutions= forms.ModelMultipleChoiceField(
		queryset=Institution.objects.all(),
		widget = InstitutionsWidget(**dselect2),
		required=False)
	commissioning_persons= forms.ModelMultipleChoiceField(
		queryset=Person.objects.all(),
		widget = PersonsWidget(**dselect2),
		required=False)
	commissioning_institutions= forms.ModelMultipleChoiceField(
		queryset=Institution.objects.all(),
		widget = InstitutionsWidget(**dselect2),
		required=False)
	languages = forms.ModelMultipleChoiceField(
		queryset=Language.objects.all(),
		widget=LanguagesWidget(**dselect2),
		required=False)
	locations= forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget = LocationsWidget(**dselect2n2),
		required=False)
	video_link = forms.CharField(**dchar)

	class Meta:
		model = Memorialsite
		fields = source_fields
		fields += ',memorial_type,creators,artists,donor_persons,donor_institutions'
		fields += ',locations,image_file1,image_file2,image_file3,video_link'
		fields += ',commissioning_persons,commissioning_institutions,languages'
		fields = fields.split(',')


