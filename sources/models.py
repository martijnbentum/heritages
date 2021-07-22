from django.db import models
from django.db.models.fields.files import ImageField
from persons.models import Person
from utilities.models import SimpleModel
from utils.model_util import info
from utils.map_util import instance2related_locations, field2locations
from misc.models import Keyword, Language,Famine
from locations.models import Location
from utilities.models import instance2name, instance2color, instance2icon, instance2map_buttons
from utilities.models import instance2names
from partial_date import PartialDateField


def make_simple_model(name):
	'''make a simple model with only a name attribute.'''
	exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'MusicType,Collection,Rated,Commissioner'
names += ',FilmCompany,FilmType,TargetAudience,PublishingOutlet,Available,ImageType'
names += ',InfographicType,PictureStoryType,TextType,Publisher,Permission'
names += ',Institution,ProductionStudio,GameType,RecordedspeechType,BroadcastingStation'
names += ',MemorialType,ArtefactType'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Source(models.Model):
	'''abstract base class for source models for all non simple non relational models'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	famines = models.ManyToManyField(Famine, blank=True)
	title_original = models.CharField(max_length=1000,default='')
	title_english = models.CharField(max_length=1000,default='')
	collection = models.ForeignKey(Collection, **dargs)
	publishing_outlet = models.ForeignKey(PublishingOutlet,**dargs)
	available = models.ForeignKey(Available,**dargs)
	permission = models.ForeignKey(Permission,**dargs)
	rated = models.ForeignKey(Rated, **dargs)
	keywords= models.ManyToManyField(Keyword,blank=True)
	description = models.TextField(default='')
	comments = models.TextField(default='')
	date_created = PartialDateField(null=True,blank=True)
	date_released = PartialDateField(null=True,blank=True)
	commissioned_by = models.ForeignKey(Commissioner,**dargs)
	source_link = models.CharField(max_length=1000,default='')
	flag = models.BooleanField(default = False)
	thumbnail = models.ImageField(upload_to='thumbnail/',blank=True,null=True)
	setting = models.ManyToManyField(Location,blank=True)
	release_date_precedent = models.BooleanField(default=False)
	location_field = 'setting'

	class Meta:
		abstract = True

	def __str__(self):
		if self.title_original:
			return self.title_original
		else: return self.title_english

	@property
	def title(self):
		if self.title_original: return self.title_original
		return self.title_english

	@property
	def _pop_up(self):
		app_name, model_name = instance2names(self)
		m = ''
		if self.thumbnail.name:
			m += '<img src="'+self.thumbnail.url+'" width="200" style="border-radius:3%">'
		m += instance2icon(self)
		m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(self)+';">'
		m += self.title +'</p>'
		m += '<hr class="mt-1 mb-0" style="border:1px solid '+instance2color(self)+';">'
		m += '<p class="mt-2 mb-0">'+self.description+'</p>'

		if hasattr(self,'play_field'):
			link =  getattr(self,getattr(self,'play_field'))
			if link:
				m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href="'
				m += link
				m += '" role="button"><i class="fas fa-play"></i></a>'
		m += instance2map_buttons(self)
		return m

	@property
	def pop_up(self):
		'''can be overwritten by inherited classes to add to the _popup'''	
		return self._pop_up

	@property
	def related_locations(self):
		return instance2related_locations(self)	

	@property
	def latlng(self):
		location_field = self.location_field if self.location_field else 'setting'
		locations = field2locations(self,self.location_field)
		if locations:
			return [location.gps for location in locations]
		else: return None
	
	@property
	def setting_names(self):
		locations = self.setting.all() 
		if locations: return ', '.join([l.name for l in locations])
		else: return ''

	@property
	def famine_names(self):
		famines= self.famines.all() 
		if famines: return ', '.join([f.names_str for f in famines])
		else: return ''

	@property
	def keyword_names(self):
		keywords= self.keywords.all() 
		if keywords: return ', '.join([k.name for k in keywords])
		else: return ''

	@property
	def language_names(self):
		if hasattr(self,'languages_original'): l = getattr(self,'languages_original')
		elif hasattr(self,'languages'): l = getattr(self,'languages')
		else: return ''
		languages=  l.all()
		if languages:
			return ', '.join( [x.name for x in languages] )
		return ''

	@property
	def identifier(self):
		return self._meta.app_label + '_' + self._meta.model_name + '_' + str( self.pk )

	@property
	def edit_url(self):
		return self._meta.app_label + ':edit_' + self._meta.model_name 
		
	@property
	def date(self):
		if self.date_released and self.date_created and self.release_date_precedent:
			return self.date_released
		elif self.date_created: return self.date_created
		elif self.date_released: return self.date_released
		else: return ''

	@property
	def image_urls(self):
		'''returns a string of comma seperated urls to images.'''
		o = []
		for field in self._meta.fields:
			if type(field) == ImageField:
				x= getattr(self,field.name)
				if x.name:o.append(x.name)
		return ','.join(o)


class Music(Source,info):
	'''Meta data for songs related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	lyrics = models.TextField(default='')
	music_video_link = models.CharField(max_length=1000,default='')
	album = models.CharField(max_length=1000,default='')
	performing_artists = models.CharField(max_length=3000,default='')
	composers = models.ManyToManyField(Person,blank=True,related_name='music_composer_set')
	music_type = models.ForeignKey(MusicType,**dargs)
	languages = models.ManyToManyField(Language, blank=True)
	music_link = models.CharField(max_length=1000,default='')
	play_field = 'music_video_link'
	
	@property
	def icon(self):
		return 'fas fa-music'


	class Meta:
		unique_together = [['title_original','date_released']]


class Film(Source, info):
	'''Meta data for movies related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	languages_original=models.ManyToManyField(Language,blank=True,related_name='film_language_original')
	languages_subtitle=models.ManyToManyField(Language,blank=True,related_name='film_language_subtitle')
	writers = models.ManyToManyField(Person,blank=True, related_name='film_writers_set')
	directors = models.ManyToManyField(Person,blank=True, related_name='film_directors_set')
	creators = models.ManyToManyField(Person,blank=True,related_name='film_creators_set')
	film_companies = models.ManyToManyField(FilmCompany,blank=True,related_name='film_film_company')
	locations_shot = models.ManyToManyField(Location,blank=True, related_name='film_location_shot')
	locations_released= models.ManyToManyField(Location,blank=True, 
		related_name='film_location_released')
	target_audience = models.ForeignKey(TargetAudience,**dargs)
	film_type = models.ForeignKey(FilmType,**dargs)
	video_link = models.CharField(max_length=1000,default='')
	video_part_link = models.CharField(max_length=1000,default='')
	play_field = 'video_link'

	@property
	def icon(self):
		return 'fa fa-film'
	

	class Meta:
		unique_together = [['title_original','date_released']]
	

class Artefact(Source, info):
	'''Meta data for material artefacts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	artefact_type = models.ForeignKey(ArtefactType,**dargs)
	locations = models.ManyToManyField(Location,blank=True, related_name='artefact_locations')
	creators = models.ManyToManyField(Person,blank=True, related_name='artefact_creators_set')
	image_file = models.ImageField(upload_to='artefact/',blank=True,null=True)
	location_field = 'locations'
	image_filename = models.CharField(max_length=500,default='',blank=True,null=True)


	@property
	def icon(self):
		return 'fas fa-utensil-spoon'

	class Meta:
		unique_together = [['title_original','date_created','image_filename']]


class Image(Source, info):
	'''Meta data for Images related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	image_type = models.ForeignKey(ImageType,**dargs)
	locations = models.ManyToManyField(Location,blank=True, related_name='image_locations')
	creators = models.ManyToManyField(Person,blank=True, related_name='image_creators_set')
	image_file = models.ImageField(upload_to='image/',blank=True,null=True)
	location_field = 'locations'
	image_filename = models.CharField(max_length=500,default='',blank=True,null=True)

	@property
	def icon(self):
		return 'fas fa-image'

	@property
	def pop_up(self):
		m = self._pop_up
		if self.image_file.name:
			m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href='
			m += self.image_file.url
			m += 'role="button"><i class="fas fa-play"></i></a>'
		return m

	class Meta:
		unique_together = [['title_original','image_filename']]

	
class Infographic(Source,info):
	'''Meta data for infographics related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	infographic_type = models.ForeignKey(InfographicType,**dargs)
	creators = models.ManyToManyField(Person,blank=True, related_name='infographic_creators_set')
	image_file = models.ImageField(upload_to='infographic/',blank=True,null=True)
	languages = models.ManyToManyField(Language, blank=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='infographic_locations')
	location_field = 'locations'
	image_filename = models.CharField(max_length=500,default='',blank=True,null=True)

	@property
	def icon(self):
		return 'fas fa-chart-area'

	class Meta:
		unique_together = [['title_original','image_filename']]


class PictureStory(Source,info):
	'''Meta data for picturestories (comics / graphic novels) related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	picture_story_type = models.ForeignKey(PictureStoryType,**dargs)
	authors = models.ManyToManyField(Person,blank=True, related_name='picture_story_author_set')
	artists = models.ManyToManyField(Person,blank=True, related_name='picture_story_artist_set')
	translators= models.ManyToManyField(Person,blank=True, 
		related_name='picture_story_translator_set')
	publishers = models.ManyToManyField(Publisher,blank=True,
		related_name='picture_story_publisher_set')
	languages = models.ManyToManyField(Language, blank=True)
	image_file = models.ImageField(upload_to='picturestory/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='picturestory/',blank=True,null=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='picture_story_locations')
	location_field = 'locations'
	image_filename = models.CharField(max_length=500,default='',blank=True,null=True)

	@property
	def icon(self):
		return 'fas fa-book-open'

	class Meta:
		unique_together = [['title_original','image_filename']]

	
class Text(Source,info):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	text_type = models.ForeignKey(TextType,**dargs)
	authors = models.ManyToManyField(Person,blank=True,related_name='text_author_set')
	institution_authors= models.ManyToManyField(Institution,blank=True,related_name='text_author_set')
	editors = models.ManyToManyField(Person,blank=True,related_name='text_editor_set')
	translators = models.ManyToManyField(Person,blank=True,related_name='text_translator_set')
	publishers = models.ManyToManyField(Publisher,blank=True,related_name='text_publisher')
	languages = models.ManyToManyField(Language, blank=True)
	original_languages= models.ManyToManyField(Language, blank=True,
		related_name='text_original_languages')
	text_file = models.FileField(upload_to='text/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='text/',blank=True,null=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='text_locations')
	location_field = 'locations'

	@property
	def icon(self):
		return 'fas fa-file-alt'
	
	class Meta:
		unique_together = [['title_original','date_released']]



class Videogame(Source,info):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	game_type = models.ForeignKey(GameType,**dargs)
	production_studio= models.ManyToManyField(ProductionStudio,blank=True,
		related_name='videogame_productionstudio_set')
	languages_original=models.ManyToManyField(Language,blank=True,
		related_name='videogame_language_original')
	languages_subtitle=models.ManyToManyField(Language,blank=True,
		related_name='videogame_language_subtitle')
	video_link = models.CharField(max_length=1000,default='')
	
	@property
	def icon(self):
		return 'fas fa-gamepad'

	class Meta:
		unique_together = [['title_original','date_released']]


class Recordedspeech(Source,info):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	recordedspeech_type= models.ForeignKey(RecordedspeechType,**dargs)
	creators = models.ManyToManyField(Person,blank=True,related_name='recordedspeech_creators_set')
	speakers = models.ManyToManyField(Person,blank=True,related_name='recordedspeech_speakers_set')
	broadcasting_station= models.ForeignKey(BroadcastingStation,**dargs)
	languages=models.ManyToManyField(Language,blank=True,
		related_name='recordedspeech_language')
	audio_link = models.CharField(max_length=1000,default='')
	locations_recorded= models.ManyToManyField(Location,blank=True, 
		related_name='recordedspeech_location_recorded')

	@property
	def icon(self):
		return 'far fa-comments'

	class Meta:
		unique_together = [['title_original','date_released']]
	

class Memorialsite(Source,info):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	memorial_type= models.ForeignKey(MemorialType,**dargs)
	creators = models.ManyToManyField(Person,blank=True,related_name='memorialsite_creators_set')
	artists= models.ManyToManyField(Person,blank=True,related_name='memorialsite_artists_set')
	image_file1 = models.ImageField(upload_to='memorialsite/',blank=True,null=True)
	image_file2 = models.ImageField(upload_to='memorialsite/',blank=True,null=True)
	image_file3 = models.ImageField(upload_to='memorialsite/',blank=True,null=True)
	donor_persons= models.ManyToManyField(Person,blank=True,
		related_name='memorialsite_person_donors_set')
	donor_institutions= models.ManyToManyField(Institution,blank=True,
		related_name='memorialsite_institution_donors_set')
	commissioning_persons= models.ManyToManyField(Person,blank=True,
		related_name='memorialsite_person_commissioning_set')
	commissioning_institutions= models.ManyToManyField(Institution,blank=True,
		related_name='memorialsite_institution_commissioning_set')
	languages=models.ManyToManyField(Language,blank=True,
		related_name='memorialsite_language')
	locations= models.ManyToManyField(Location,blank=True, 
		related_name='memorialsite_location_recorded')
	video_link = models.CharField(max_length=1000,default='')
	location_field = 'locations'

	@property
	def icon(self):
		return 'fas fa-monument'
	
	class Meta:
		unique_together = [['title_original','date_released']]
