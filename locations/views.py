from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from .models import Location, LocationType, LocationRelation
from .forms import LocationForm, FastLocForm ,location_relation_formset 
from .forms import LocationRelationForm, LocationTypeForm,LocationStatusForm,LocationPrecisionForm
from django.forms import inlineformset_factory
import json
from utils.view_util import make_tabs,FormsetFactoryManager
from utilities.views import getfocus, list_view, delete_model, edit_model, add_simple_model


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
	'''list view of locations.'''
	return list_view(request, 'Location', 'locations')


def edit_location(request, pk=None, focus = '', view='complete'):
	print(view)
	return edit_model(request, __name__,'Location','locations',pk, 
		focus = focus, view=view)


def delete(request, pk, model_name):
	return delete_model(request, __name__,model_name,'locations',pk)

