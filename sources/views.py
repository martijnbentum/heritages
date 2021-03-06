from django.shortcuts import render
from django.http import HttpResponse
from utilities.views import edit_model, add_simple_model, list_view, delete_model
from .forms import MusicForm, MusicTypeForm, FilmTypeForm, FilmForm, TargetAudienceForm
from .forms import FilmCompanyForm, CollectionForm, TextForm, TextTypeForm
from .forms import InfographicForm, InfographicTypeForm, ImageForm, ImageTypeForm
from .forms import PictureStoryForm, PictureStoryTypeForm, PublisherForm, PublishingOutletForm
from .forms import LocationForm, LanguageForm, KeywordForm,InstitutionForm
from persons.forms import PersonForm

def index(request):
	return HttpResponse('hello world')

def make_fname(name):
	o = name[0]
	for c in name[1:]:
		if c.isupper(): o += '_' + c
		else: o += c
	return o.lower()

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
for name in names.split(','):
	create_simple_view(name)

def view_list(request,name):
	return list_view(request, name,'sources')




def edit_music(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Music','sources',pk,focus=focus,view=view)

def edit_film(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Film','sources',pk,focus=focus,view=view)

def edit_text(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Text','sources',pk,focus=focus,view=view)

def edit_infographic(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Infographic','sources',pk,focus=focus,view=view)

def edit_image(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Image','sources',pk,focus=focus,view=view)

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

