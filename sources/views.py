from django.shortcuts import render
from django.http import HttpResponse
from utilities.views import edit_model, add_simple_model, list_view, delete_model
# from utilities.models import get_user_search
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
from .models import Image, Film, Music, Text, PictureStory, Memorialsite
from .models import Recordedspeech, Videogame, Artefact, Infographic
from utils import search_view_helper
from utils.model_util import get_random_image_urls
import time

def home(request):
    if not request.session or not request.session.session_key:
        print('pre save',  request.session, request.session.session_key)
        request.session.save()
        print('saved',  request.session, request.session.session_key)
    print('no saving',request.session.session_key)
    image_urls = get_random_image_urls(n=5,flagged=False)
    args = {'image_urls':image_urls}
    return render(request,'sources/home.html',args)

def make_fname(name):
    o = name[0]
    for c in name[1:]:
        if c.isupper(): o += '_' + c
        else: o += c
    return o.lower()

def detail_infographic_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Infographic.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    creators= instance.creators.all()
    languages= instance.languages.all().order_by('name') 
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    args = {'instance':instance, 'page_name':instance.title}
    args.update({'creators':creators, 'settings':settings,'famines':famines})
    args.update({'locations':locations, 'languages':languages,'us':us})
    return render(request,'sources/detail_infographic_view.html',args)

def detail_artefact_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Artefact.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    # us = get_user_search(request.session.session_key)
    us.set_current_instance(instance.identifier)
    creators= instance.creators.all()
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    args = {'instance':instance, 'page_name':instance.title}
    args.update({'creators':creators, 'settings':settings,'famines':famines})
    args.update({'locations':locations, 'us':us})
    return render(request,'sources/detail_artefact_view.html',args)

def detail_videogame_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Videogame.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    studios= instance.production_studio.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages_original.all().order_by('name') 
    subtitles= instance.languages_subtitle.all().order_by('name')
    args = {'instance':instance, 'page_name':instance.title,'studios':studios}
    args.update({'subtitles':subtitles, 'settings':settings,'famines':famines,'us':us})
    return render(request,'sources/detail_videogame_view.html',args)

def detail_image_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Image.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    creators = instance.creators.all()
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    args = {'instance':instance, 'page_name':instance.title,'creators':creators}
    args.update({'locations':locations, 'settings':settings,'famines':famines,'us':us})
    return render(request,'sources/detail_image_view.html',args)

def detail_memorialsite_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Memorialsite.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    creators = instance.creators.all()
    artists = instance.artists.all()
    donors = list(instance.donor_persons.all())
    temp= list(instance.donor_institutions.all())
    if temp:donors += temp
    commissioners= list(instance.commissioning_persons.all())
    temp= list(instance.commissioning_institutions.all())
    if temp:commissioners += temp
    languages= instance.languages.all().order_by('name') 
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    args = {'instance':instance, 'page_name':instance.title,'creators':creators}
    args.update({'donors':donors, 'commissioners':commissioners,'artists':artists})
    args.update({'locations':locations, 'settings':settings,'famines':famines,'us':us})
    args.update({'languages':languages})
    return render(request,'sources/detail_memorialsite_view.html',args)

def detail_music_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Music.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    composers= instance.composers.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages.all().order_by('name') 
    args = {'instance':instance, 'page_name':instance.title}
    args.update({'composers':composers})
    args.update({'settings':settings,'famines':famines,'languages':languages,'us':us})
    return render(request,'sources/detail_music_view.html',args)

def detail_recordedspeech_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Recordedspeech.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    creators= instance.creators.all()
    locations= instance.locations_recorded.all()
    speakers= instance.speakers.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages.all().order_by('name') 
    args = {'instance':instance, 'page_name':instance.title,}
    args.update({'settings':settings,'famines':famines,'languages':languages,'us':us})
    args.update({'creators':creators,'locations':locations})
    args.update({'speakers':speakers})
    return render(request,'sources/detail_recordedspeech_view.html',args)

def detail_picturestory_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = PictureStory.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    authors = instance.authors.all()
    artists= instance.authors.all()
    publishers = instance.publishers.all()
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages.all().order_by('name') 
    args = {'instance':instance, 'page_name':instance.title,}
    args.update({'settings':settings,'famines':famines,'languages':languages})
    args.update({'authors':authors,'publishers':publishers})
    args.update({'locations':locations,'artists':artists,'us':us})
    return render(request,'sources/detail_picturestory_view.html',args)

def detail_text_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Text.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    authors = list(instance.authors.all())
    temp= list(instance.institution_authors.all())
    if temp:authors += temp
    editors = instance.editors.all()
    translators= instance.translators.all()
    publishers = instance.publishers.all()
    locations= instance.locations.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages.all().order_by('name') 
    org_lang= instance.original_languages.all().order_by('name')
    args = {'instance':instance, 'page_name':instance.title,}
    args.update({'settings':settings,'famines':famines,'languages':languages})
    args.update({'org_lang':org_lang,'authors':authors})
    args.update({'editors':editors,'publishers':publishers})
    args.update({'locations':locations,'translators':translators,'us':us})
    return render(request,'sources/detail_text_view.html',args)

def detail_film_view(request,pk):
    print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    instance = Film.objects.get(pk = pk)
    us = search_view_helper.UserSearch(request)
    us.set_current_instance(instance.identifier)
    directors = instance.directors.all()
    writers= instance.writers.all()
    film_companies= instance.film_companies.all()
    creators = instance.creators.all()
    locations_shot= instance.locations_shot.all()
    settings= instance.setting.all()
    famines = instance.famines.all()
    languages= instance.languages_original.all().order_by('name')
    subtitles= instance.languages_subtitle.all().order_by('name')
    args = {'instance':instance, 'page_name':instance.title,'creators':creators}
    args.update({'loc_shot':locations_shot, 'settings':settings})
    args.update({'film_companies':film_companies})
    args.update({'famines':famines, 'writers':writers, 'directors':directors})
    args.update({'languages':languages, 'subtitles':subtitles, 'us':us})
    return render(request,'sources/detail_film_view.html',args)

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

