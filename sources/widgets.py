from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Collection,PublishingOutlet,Available,Rated
from .models import Commissioner,MusicType,Language,Music
from .models import Film,Image,PictureStory,Text,Infographic,Publisher
from .models import InfographicType, TextType, FilmType,PictureStoryType,ImageType
from .models import GameType,ProductionStudio
from .models import Permission, FilmCompany
from .models import TargetAudience, Institution
from .models import RecordedspeechType,BroadcastingStation 
from .models import MemorialType, Artefact, ArtefactType

class SimpleBaseWidget(ModelSelect2Widget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class SimpleBasesWidget(ModelSelect2MultipleWidget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class BaseWidget(ModelSelect2Widget):
	search_fields = ['title_english__icontains']
	def label_from_instance(self,obj):
		return obj.title_english

# Main model widgets

class MusicWidget(BaseWidget):
	model = Music
	def get_queryset(self):
		return Music.objects.all().order_by('title_english')

class FilmWidget(BaseWidget):
	model = Film
	def get_queryset(self):
		return Film.objects.all().order_by('title_english')

class ImageWidget(BaseWidget):
	model = Image 
	def get_queryset(self):
		return Image.objects.all().order_by('title_english')

class ArtefactWidget(BaseWidget):
	model = Artefact
	def get_queryset(self):
		return Artefact.objects.all().order_by('title_english')

class PictureStoryWidget(BaseWidget):
	model = PictureStory
	def get_queryset(self):
		return PictureStory.objects.all().order_by('title_english')

class TextWidget(BaseWidget):
	model = Text 
	def get_queryset(self):
		return Text.objects.all().order_by('title_english')

class InfographicWidget(BaseWidget):
	model = Infographic
	def get_queryset(self):
		return Infographic.objects.all().order_by('title_english')


#helper widgets

class TargetAudienceWidget(SimpleBaseWidget):
	model = TargetAudience
	def get_queryset(self):
		return TargetAudience.objects.all().order_by('name')


class InfographicTypeWidget(SimpleBaseWidget):
	model = InfographicType
	def get_queryset(self):
		return InfographicType.objects.all().order_by('name')

class MusicTypeWidget(SimpleBaseWidget):
	model = MusicType
	def get_queryset(self):
		return MusicType.objects.all().order_by('name')

class TextTypeWidget(SimpleBaseWidget):
	model = TextType
	def get_queryset(self):
		return TextType.objects.all().order_by('name')

class FilmTypeWidget(SimpleBaseWidget):
	model = FilmType
	def get_queryset(self):
		return FilmType.objects.all().order_by('name')

class GameTypeWidget(SimpleBaseWidget):
	model = GameType
	def get_queryset(self):
		return GameType.objects.all().order_by('name')

class MemorialTypeWidget(SimpleBaseWidget):
	model = MemorialType
	def get_queryset(self):
		return MemorialType.objects.all().order_by('name')

class RecordedspeechTypeWidget(SimpleBaseWidget):
	model = RecordedspeechType
	def get_queryset(self):
		return RecordedspeechType.objects.all().order_by('name')

class BroadcastingStationWidget(SimpleBaseWidget):
	model =BroadcastingStation
	def get_queryset(self):
		return BroadcastingStation.objects.all().order_by('name')

class PictureStoryTypeWidget(SimpleBaseWidget):
	model = PictureStoryType
	def get_queryset(self):
		return PictureStoryType.objects.all().order_by('name')

class ImageTypeWidget(SimpleBaseWidget):
	model = ImageType
	def get_queryset(self):
		return ImageType.objects.all().order_by('name')

class ArtefactTypeWidget(SimpleBaseWidget):
	model = ArtefactType
	def get_queryset(self):
		return ArtefactType.objects.all().order_by('name')

class AvailableWidget(SimpleBaseWidget):
	model = Available
	def get_queryset(self):
		return Available.objects.all().order_by('name')

class PermissionWidget(SimpleBaseWidget):
	model = Permission
	def get_queryset(self):
		return Permission.objects.all().order_by('name')

class RatedWidget(SimpleBaseWidget):
	model = Rated
	def get_queryset(self):
		return Rated.objects.all().order_by('name')

class CommissionerWidget(SimpleBaseWidget):
	model = Commissioner
	def get_queryset(self):
		return Commissioner.objects.all().order_by('name')

class CollectionWidget(SimpleBaseWidget):
	model = Collection
	def get_queryset(self):
		return Collection.objects.all().order_by('name')

class PublisherWidget(SimpleBaseWidget):
	model = Publisher 
	def get_queryset(self):
		return Publisher.objects.all().order_by('name')

class PublishersWidget(SimpleBasesWidget):
	model = Publisher 
	def get_queryset(self):
		return Publisher.objects.all().order_by('name')

class PublishingOutletWidget(SimpleBaseWidget):
	model = PublishingOutlet
	def get_queryset(self):
		return PublishingOutlet.objects.all().order_by('name')

class FilmCompanyWidget(SimpleBaseWidget):
	model =FilmCompany 
	def get_queryset(self):
		return FilmCompany.objects.all().order_by('name')

class FilmCompaniesWidget(SimpleBasesWidget):
	model =FilmCompany 
	def get_queryset(self):
		return FilmCompany.objects.all().order_by('name')

class ProductionStudiosWidget(SimpleBasesWidget):
	model =ProductionStudio
	def get_queryset(self):
		return ProductionStudio.objects.all().order_by('name')

class InstitutionsWidget(SimpleBasesWidget):
	model =Institution
	def get_queryset(self):
		return Institution.objects.all().order_by('name')



