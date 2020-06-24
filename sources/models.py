from django.db import models

class SimpleModel(models.Model):
	name = models.CharField(max_length=300,default='')
	class Meta:
		abstract=True

class Person(SimpleModel):
	pass

class MusicType(SimpleModel):
	pass

class Language(SimpleModel):
	pass

class Famine(SimpleModel):
	pass

class Collection(SimpleModel):
	pass

class Rated(SimpleModel):
	pass

class Keyword(SimpleModel):
	pass

class Commissioner(SimpleModel):
	pass

class FilmCompany(SimpleModel):
	pass

class FilmType(SimpleModel):
	pass

class TargetAudience(SimpleModel):
	pass

class PublishingOutlet(SimpleModel):
	pass

class Location(SimpleModel):
	pass

class Available(SimpleModel):
	pass

class ImageType(SimpleModel):
	pass

class InfographicType(SimpleModel):
	pass

class PictureStoryType(SimpleModel):
	pass

class TextType(SimpleModel):
	pass

class Publisher(SimpleModel):
	pass

class RequestUsePermission(SimpleModel):
	pass

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
	keywords = models.ForeignKey(Keyword, **dargs)
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
	

class Image(Source):
	'''Meta data for Images related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	language_original = models.ForeignKey(Language,**dargs,related_name='image_language_original')
	image_type = models.ForeignKey(ImageType,**dargs)
	location = models.ForeignKey(Location,**dargs)
	creator = models.ForeignKey(Person,**dargs)
	
class Infographic(Source):
	'''Meta data for infographics related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	infographic_type = models.ForeignKey(InfographicType,**dargs)
	creator = models.ForeignKey(Person,**dargs)

class PictureStory(Source):
	'''Meta data for picturestories (comics / graphic novels) related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	picture_story_type = models.ForeignKey(PictureStoryType,**dargs)
	author = models.ForeignKey(Person,**dargs,related_name='picture_story_author')
	artist = models.ForeignKey(Person,**dargs,related_name='picture_story_artist')
	translator = models.ForeignKey(Person,**dargs,related_name='picture_story_translator')
	publisher = models.ForeignKey(Publisher,**dargs)
	text = models.TextField(default='')
	excerpt = models.CharField(max_length=3000,default='')
	
class Text(Source):
	'''Meta data for texts related to famines.'''
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	text_type = models.ForeignKey(TextType,**dargs)
	author = models.ForeignKey(Person,**dargs,related_name='text_author')
	editor = models.ForeignKey(Person,**dargs,related_name='text_editor')
	translator = models.ForeignKey(Person,**dargs,related_name='text_translator')
	text = models.TextField(default='')
	excerpt = models.CharField(max_length=3000,default='')
	





