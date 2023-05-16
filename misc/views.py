from django.shortcuts import render
from .forms import FamineForm,FamineNameForm,LanguageForm,LicenseForm
from .forms import CausalTriggerForm,KeywordForm, keywordkeyword_formset
from .models import Famine
from utilities.views import edit_model, add_simple_model, list_view, delete_model
from utils import search_view_helper
import time


def create_simple_view(name):
	'''Create a simple view based on the Model name. 
	Assumes the form only has a name field.
	'''
	c = 'def add_'+name.lower()+'(request,pk=None):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","misc","add_'+name+'",pk=pk)'
	return exec(c,globals())

#create simple views for the following models
names = 'CausalTrigger,FamineName,Location,Language'
for name in names.split(','):
	create_simple_view(name)

def edit_license(request,pk=None,focus='',view='complete'):
	print(pk,focus,view,123456,request)
	return edit_model(request,__name__,'License','misc',pk,focus=focus,view=view)
		

def edit_keyword(request,pk=None,focus='',view='complete'):
	names = 'keywordkeyword_formset'
	print(pk,focus,view,123456,request)
	return edit_model(request,__name__,'Keyword','misc',pk,
		formset_names=names,focus=focus,view=view)


def edit_famine(request,pk=None,focus='',view='complete'):
	print(pk,focus,view,123456,request)
	return edit_model(request,__name__,'Famine','misc',pk,focus=focus,view=view)


'''
def add_location(request):
	return add_simple_model(request,__name__,'Location','sources','add location')

def add_keyword(request):
	return add_simple_model(request,__name__,'Keyword','sources','add keyword')
'''

def delete(request, pk, model_name):
	return delete_model(request, __name__, model_name,'misc',pk)

def detail_famine_view(request,pk):
	print('  detail view start\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
	instance = Famine.objects.get(pk = pk)
	us = search_view_helper.UserSearch(request)
	us.set_current_instance(instance.identifier)
	args = {'instance':instance, 'page_name':instance.names_str,'us':us}
	return render(request,'misc/detail_famine_view.html',args)

