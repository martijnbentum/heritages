from django.db import models
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
	exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'MusicType,Collection,Rated,Commissioner'
names += ',FilmCompany,FilmType,TargetAudience,PublishingOutlet,Available,ImageType'
names += ',InfographicType,PictureStoryType,TextType,Publisher,RequestUsePermission'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Source(models.Model):
	'''abstract base class for music,film,image,text,infographic,picturestory.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	famines = models.ManyToManyField(Famine, blank=True)
	title_original = models.CharField(max_length=1000,default='')
	title_english = models.CharField(max_length=1000,default='')
	collection = models.ForeignKey(Collection, **dargs)
	publishing_outlet = models.ForeignKey(PublishingOutlet,**dargs)
	available = models.ForeignKey(Available,**dargs)
	request_use_permission = models.ForeignKey(RequestUsePermission,**dargs)
	rated = models.ForeignKey(Rated, **dargs)
	keywords= models.ManyToManyField(Keyword,blank=True)
	description = models.TextField(default='')
	comments = models.TextField(default='')
	date_created = PartialDateField(null=True,blank=True)
	date_released = PartialDateField(null=True,blank=True)
	commissioned_by = models.ForeignKey(Commissioner,**dargs)
	source_link = models.CharField(max_length=1000,default='')
	flag = models.BooleanField(default = False)
	thumbnail = models.ImageField(upload_to='media/',blank=True,null=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.title_english

	@property
	def _pop_up(self):
		app_name, model_name = instance2names(self)
		m = ''
		if self.thumbnail.name:
			m += '<img src="'+self.thumbnail.url+'" width="200" style="border-radius:3%">'
		m += instance2icon(self)
		m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(self)+';">'
		m += self.title_english +'</p>'
		m += '<hr class="mt-1 mb-0" style="border:1px solid '+instance2color(self)+';">'
		m += '<p class="mt-2 mb-0">'+self.description+'</p>'

		if hasattr(self,'play_field'):
			link =  getattr(self,getattr(self,'play_field'))
			if link:
				m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href='
				m += link
				m += 'role="button"><i class="fas fa-play"></i></a>'
		m += instance2map_buttons(self)
		return m

	@property
	def related_locations(self):
		return instance2related_locations(self)	

	@property
	def latlng(self):
		if self.location_field:
			locations = field2locations(self,self.location_field)
			return [location.gps for location in locations]
		else: return None

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
	music_file = models.FileField(upload_to='media/',blank=True,null=True)
	music_link = models.CharField(max_length=1000,default='')
	locations= models.ManyToManyField(Location,blank=True, related_name='music_locations')
	location_field = 'locations'
	play_field = 'music_video_link'

	@property
	def pop_up(self):
		m = self._pop_up
	
		return m


class Film(Source, info):
	'''Meta data for movies related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	language_original = models.ForeignKey(Language,**dargs,related_name='film_language_original')
	language_subtitle = models.ForeignKey(Language,**dargs,related_name='film_language_subtitle')
	writers = models.ManyToManyField(Person,blank=True, related_name='film_writers_set')
	directors = models.ManyToManyField(Person,blank=True, related_name='film_directors_set')
	film_company = models.ForeignKey(FilmCompany,**dargs)
	locations_shot = models.ManyToManyField(Location,blank=True, related_name='film_location_shot')
	locations_released= models.ManyToManyField(Location,blank=True, 
		related_name='film_location_released')
	target_audience = models.ForeignKey(TargetAudience,**dargs)
	film_type = models.ForeignKey(FilmType,**dargs)
	video_link = models.CharField(max_length=1000,default='')
	location_field = 'locations_shot'
	play_field = 'video_link'
	
	@property
	def pop_up(self):
		m = self._pop_up
		return m

	

class Image(Source, info):
	'''Meta data for Images related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	language_original = models.ForeignKey(Language,**dargs,related_name='image_language_original')
	image_type = models.ForeignKey(ImageType,**dargs)
	locations = models.ManyToManyField(Location,blank=True, related_name='image_locations')
	creators = models.ManyToManyField(Person,blank=True, related_name='image_creators_set')
	image_file = models.ImageField(upload_to='media/',blank=True,null=True)
	location_field = 'locations'

	@property
	def pop_up(self):
		m = self._pop_up
		if self.image_file.name:
			m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href='
			m += self.image_file.url
			m += 'role="button"><i class="fas fa-play"></i></a>'
		return m
	
class Infographic(Source,info):
	'''Meta data for infographics related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	infographic_type = models.ForeignKey(InfographicType,**dargs)
	creators = models.ManyToManyField(Person,blank=True, related_name='infographic_creators_set')
	image_file = models.ImageField(upload_to='media/',blank=True,null=True)
	languages = models.ManyToManyField(Language, blank=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='infographic_locations')
	location_field = 'locations'

	@property
	def pop_up(self):
		m = self._pop_up
		return m

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
	image_file = models.ImageField(upload_to='media/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='media/',blank=True,null=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='picture_story_locations')
	location_field = 'locations'

	@property
	def pop_up(self):
		m = self._pop_up
		return m
	
class Text(Source,info):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	text_type = models.ForeignKey(TextType,**dargs)
	author = models.ForeignKey(Person,**dargs,related_name='text_author_set')
	editor = models.ForeignKey(Person,**dargs,related_name='text_editor_set')
	translator = models.ForeignKey(Person,**dargs,related_name='text_translator_set')
	publishers = models.ManyToManyField(Publisher,blank=True,related_name='text_publisher')
	languages = models.ManyToManyField(Language, blank=True)
	text_file = models.FileField(upload_to='media/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='media/',blank=True,null=True)
	locations = models.ManyToManyField(Location,blank=True, related_name='text_locations')
	location_field = 'locations'
	
	@property
	def pop_up(self):
		m = self._pop_up
		return m





