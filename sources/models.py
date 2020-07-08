from django.db import models
from persons.models import Person
from utilities.models import SimpleModel


def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'MusicType,Language,Famine,Collection,Rated,Commissioner,Location,Keyword'
names += ',FilmCompany,FilmType,TargetAudience,PublishingOutlet,Available,ImageType'
names += ',InfographicType,PictureStoryType,TextType,Publisher,RequestUsePermission'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Source(models.Model):
	'''abstract base class for music,film,image,text,infographic,picturestory.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	famines = models.ManyToManyField(Famine, blank=True)
	title_english = models.CharField(max_length=1000,default='')
	title_original = models.CharField(max_length=1000,default='')
	collection = models.ForeignKey(Collection, **dargs)
	publishing_outlet = models.ForeignKey(PublishingOutlet,**dargs)
	available = models.ForeignKey(Available,**dargs)
	request_use_permission = models.ForeignKey(RequestUsePermission,**dargs)
	rated = models.ForeignKey(Rated, **dargs)
	keywords= models.ManyToManyField(Keyword,blank=True)
	description = models.TextField(default='')
	comments = models.TextField(default='')
	date_created = 1
	date_released = 1
	commissioned_by = models.ForeignKey(Commissioner,**dargs)
	source_link = models.CharField(max_length=1000,default='')

	class Meta:
		abstract = True

class Music(Source):
	'''Meta data for songs related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	lyrics = models.TextField(default='')
	music_video_link = models.CharField(max_length=1000,default='')
	performing_artists = models.CharField(max_length=3000,default='')
	composers = models.ManyToManyField(Person,blank=True,related_name='music_composer')
	music_type = models.ForeignKey(MusicType,**dargs)
	languages = models.ManyToManyField(Language, blank=True)
	music_file = models.FileField(upload_to='data/',blank=True,null=True)


class Film(Source):
	'''Meta data for movies related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	language_original = models.ForeignKey(Language,**dargs,related_name='film_language_original')
	language_subtitle = models.ForeignKey(Language,**dargs,related_name='film_language_subtitle')
	writers = models.ManyToManyField(Person,blank=True, related_name='film_writers')
	directors = models.ManyToManyField(Person,blank=True, related_name='film_directors')
	film_company = models.ForeignKey(FilmCompany,**dargs)
	locations_shot = models.ManyToManyField(Location,blank=True, related_name='film_location_shot')
	locations_released= models.ManyToManyField(Location,blank=True, related_name='film_location_released')
	target_audience = models.ForeignKey(TargetAudience,**dargs)
	film_type = models.ForeignKey(FilmType,**dargs)
	video_link = models.CharField(max_length=1000,default='')
	

class Image(Source):
	'''Meta data for Images related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	language_original = models.ForeignKey(Language,**dargs,related_name='image_language_original')
	image_type = models.ForeignKey(ImageType,**dargs)
	locations = models.ManyToManyField(Location,blank=True, related_name='image_locations')
	creators = models.ManyToManyField(Person,blank=True, related_name='image_creators')
	image_file = models.ImageField(upload_to='data/',blank=True,null=True)
	
class Infographic(Source):
	'''Meta data for infographics related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	infographic_type = models.ForeignKey(InfographicType,**dargs)
	creators = models.ManyToManyField(Person,blank=True, related_name='infographic_creators')
	image_file = models.ImageField(upload_to='data/',blank=True,null=True)

class PictureStory(Source):
	'''Meta data for picturestories (comics / graphic novels) related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	picture_story_type = models.ForeignKey(PictureStoryType,**dargs)
	authors = models.ManyToManyField(Person,blank=True, related_name='picture_story_author')
	artists = models.ManyToManyField(Person,blank=True, related_name='picture_story_artist')
	translators= models.ManyToManyField(Person,blank=True, related_name='picture_story_translator')
	publishers = models.ManyToManyField(Publisher,blank=True,related_name='picture_story_publisher')
	image_file = models.ImageField(upload_to='data/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='data/',blank=True,null=True)
	
class Text(Source):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	text_type = models.ForeignKey(TextType,**dargs)
	author = models.ForeignKey(Person,**dargs,related_name='text_author')
	editor = models.ForeignKey(Person,**dargs,related_name='text_editor')
	translator = models.ForeignKey(Person,**dargs,related_name='text_translator')
	publishers = models.ManyToManyField(Publisher,blank=True,related_name='text_publisher')
	text_file = models.FileField(upload_to='data/',blank=True,null=True)
	excerpt_file = models.FileField(upload_to='data/',blank=True,null=True)
	





