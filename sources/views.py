from django.shortcuts import render
from django.http import HttpResponse
from utilities.views import edit_model, add_simple_model
from .forms import MusicForm, MusicTypeForm, FilmForm

def index(request):
	return HttpResponse('hello world')

def add_music_type(request):
	return add_simple_model(request,__name__,'MusicType','sources','add music type')

def add_film_type(request):
	return add_simple_model(request,__name__,'FilmType','sources','add film type')

def add_person(request):
	return add_simple_model(request,__name__,'Person','sources','add person')

def add_language(request):
	return add_simple_model(request,__name__,'Language','sources','add language')

def add_famine(request):
	return add_simple_model(request,__name__,'Famine','sources','add famine')

def add_keyword(request):
	return add_simple_model(request,__name__,'Keyword','sources','add keyword')

def add_collection(request):
	return add_simple_model(request,__name__,'Collection','sources','add collection')

def add_target_audience(request):
	return add_simple_model(request,__name__,'TargetAudience','sources','add target audience')

def music_list(request):
	return HttpResponse('hello music list')


def edit_music(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Music','sources',pk,focus=focus,view=view)

def edit_film(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Film','sources',pk,focus=focus,view=view)
# Create your views here.

def add_location(request):
	return add_simple_model(request,__name__,'Location','sources','add location')
