from django.apps import apps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Location, LocationType, LocationRelation
from .forms import LocationForm, FastLocForm ,location_relation_formset 
from .forms import LocationRelationForm, LocationTypeForm,LocationStatusForm,LocationPrecisionForm
import json
from utils.view_util import make_tabs,FormsetFactoryManager
from utils.map_util import instance2related_locations,queryset2maplist
from utilities.views import getfocus, list_view, delete_model, edit_model, add_simple_model

from sources.models import Film, Music, Text, Image, PictureStory, Infographic
from persons.models import Person
from misc.models import Famine


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
	c = 'def add_'+make_fname(name)+'(request):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","locations","add '+name+'")'
	return exec(c,globals())

#create simple forms for the following models
names = 'LocationType,LocationPrecision,LocationStatus'
for name in names.split(','):
	create_simple_view(name)




def location_list(request):
	'''list view of locations.
	redirect to the utilities list view (nav bar directly calls the utilities list view)
	location view is slow to load because loading relation value (eg country) take
	2 ms for each, so for each location a country and region takes 4ms not easy to speed up
	'''
	return list_view(request, 'Location', 'locations',max_entries=50)


def map(request):
	# l,fn = instance2related_locations(f)
	maplist = queryset2maplist(get_querysets())
	args = {'page_name':'map','maplist':maplist}
	return render(request,'locations/map.html',args)

def show_links(request,app_name,model_name,pk):
	instance = apps.get_model(app_name,model_name).objects.get(pk=pk)
	l, fn= instance2related_locations(instance)
	roles = ['main']+[line[0] for line in l]
	link_list = queryset2maplist([instance] + [i[-1] for i in l],roles)
	args = {'page_name':'links','link_list':link_list}
	return render(request,'locations/map.html',args)
	


def edit_location(request, pk=None, focus = '', view='complete'):
	names = 'location_relation_formset'
	return edit_model(request, __name__,'Location','locations',pk, 
		formset_names=names,focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'locations',pk)


def get_querysets(names = None):
	'''load all queryset based on model names in names.
	names can be list or comma seprated string 
	each item should follow this format: app_name$model_name
	'''
	if not names: 
		names = 'Film,Image,Text,PictureStory,Infographic,Artefact,Memorialsite'
		names += ',Recordedspeech,Videogame'
		names = names.split(',')
		names = ['sources$'+name for name in names]
		# names.extend('persons$Person,misc$Famine'.split(','))
		#request to not show persons on the map #60
		names.extend('misc$Famine'.split(','))
	if type(names) == str: names = names.split(',')
	qs = []
	for name in names:
		app_name,model_name = name.split('$')
		model = apps.get_model(app_name,model_name)
		qs.extend(model.objects.all())
	return qs
		
