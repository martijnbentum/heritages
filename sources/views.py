from django.shortcuts import render
from django.http import HttpResponse
from utilities.views import edit_model, add_simple_model, list_view, delete_model
from .forms import MusicForm, MusicTypeForm, FilmTypeForm, FilmForm
from .forms import FilmCompanyForm, CollectionForm, TextForm, TextTypeForm
from .forms import InfographicForm, InfographicTypeForm, ImageForm, ImageTypeForm
from .forms import PictureStoryForm, PictureStoryTypeForm, PublisherForm
from .forms import LocationForm, LanguageForm, KeywordForm,InstitutionForm
from .forms import GameTypeForm, ProductionStudioForm, RecordedspeechTypeForm
from .forms import GameTypeForm, ProductionStudioForm, RecordedspeechTypeForm
from .forms import RecordedspeechForm, BroadcastingStationForm, MemorialTypeForm
from .forms import MemorialsiteForm, ArtefactForm, ArtefactTypeForm
from .forms import PublishingOutletForm, TargetAudienceForm,VideogameForm
from persons.forms import PersonForm
from .models import Image, Film, Music

def index(request):
	return HttpResponse('hello world')

def make_fname(name):
	o = name[0]
	for c in name[1:]:
		if c.isupper(): o += '_' + c
		else: o += c
	return o.lower()

def detail_image_view(request,pk):
	instance = Image.objects.get(pk = pk)
	creators = instance.creators.all()
	locations= instance.locations.all()
	settings= instance.setting.all()
	famines = instance.famines.all()
	args = {'instance':instance, 'page_name':instance.title,'creators':creators}
	args.update({'locations':locations, 'settings':settings,'famines':famines})
	return render(request,'sources/detail_image_view.html',args)

def detail_music_view(request,pk):
	instance = Music.objects.get(pk = pk)
	composers= instance.composers.all()
	settings= instance.setting.all()
	famines = instance.famines.all()
	languages= instance.languages.all()
	args = {'instance':instance, 'page_name':instance.title,}
	args.update({'settings':settings,'famines':famines,'languages':languages})
	return render(request,'sources/detail_music_view.html',args)

def detail_film_view(request,pk):
	instance = Film.objects.get(pk = pk)
	directors = instance.directors.all()
	writers= instance.writers.all()
	creators = instance.creators.all()
	locations_shot= instance.locations_shot.all()
	settings= instance.setting.all()
	famines = instance.famines.all()
	languages= instance.languages_original.all()
	subtitles= instance.languages_subtitle.all()
	args = {'instance':instance, 'page_name':instance.title,'creators':creators}
	args.update({'locations_shot':locations_shot, 'settings':settings})
	args.update({'famines':famines, 'writers':writers, 'directors':directors})
	args.update({'languages':languages, 'subtitles':subtitles})
	return render(request,'sources/detail_film_view.html',args)
	pass

def create_simple_view(name):
	'''Create a simple view based on the Model name. 
	Assumes the form only has a name field.
	'''
	c = 'def add_'+make_fname(name)+'(request,pk=None):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","sources","add '+name+'",pk=pk)'
	return exec(c,globals())

#create simple views for the following models
names = 'TextType,MusicType,ImageType,FilmType,InfographicType,PictureStoryType'
names += ',FilmCompany,Publisher,Collection,TargetAudience,PublishingOutlet,Institution'
names += ',ProductionStudio,GameType,RecordedspeechType,BroadcastingStation,MemorialType'
names += ',ArtefactType'
for name in names.split(','):
	create_simple_view(name)

def view_list(request,name):
	return list_view(request, name,'sources')


def edit_music(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Music','sources',pk,focus=focus,view=view)

def edit_film(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Film','sources',pk,focus=focus,view=view)

def edit_memorialsite(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Memorialsite','sources',pk,focus=focus,view=view)

def edit_videogame(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Videogame','sources',pk,focus=focus,view=view)

def edit_recordedspeech(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Recordedspeech','sources',pk,focus=focus,view=view)

def edit_text(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Text','sources',pk,focus=focus,view=view)

def edit_infographic(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Infographic','sources',pk,focus=focus,view=view)

def edit_image(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Image','sources',pk,focus=focus,view=view)

def edit_artefact(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Artefact','sources',pk,focus=focus,view=view)

def edit_picture_story(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'PictureStory','sources',pk,focus=focus,view=view)
# Create your views here.





def add_location(request):
	return add_simple_model(request,__name__,'Location','sources','add location')

def add_language(request):
	return add_simple_model(request,__name__,'Language','sources','add language')

def add_famine(request):
	return add_simple_model(request,__name__,'Famine','sources','add famine')

def add_keyword(request):
	return add_simple_model(request,__name__,'Keyword','sources','add keyword')


def delete(request, pk, model_name):
	return delete_model(request, __name__, model_name,'sources',pk)

