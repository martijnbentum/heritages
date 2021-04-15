from collections import OrderedDict
from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from utils import view_util, help_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utils.model_util import copy_complete
# from .models import copy_complete
from utilities.search import Search
import time

te = 'title_original,title_english'
field_names_dict = {'person':'name,pseudonyms,gender,location_of_birth',
	'music':te+',music_type','film':te+',film_type',
	'text':te+',text_type', 'infographic':te+',infographic_type',
	'image':te+',image_type','picturestory':te+',picture_story_type',
	'famine':'names_str$names,locations_str$locations',
	'location':'name,country,region,location_type$type',
	'keyword':'name,category,category_relations$relations',
	'videogame':te+',game_type','recordedspeech':te+',recordedspeech_type',
	'memorialsite':te+',memorial_type'}


def _handle_fieldnames(field_names):
	fields = field_names.split(',')
	field_dict = OrderedDict()
	for f in fields:
		if '$' in f:
			name,hname = f.split('$')
			if not hname: hname = name
		else: name,hname = f,f.replace('_',' ')
		field_dict[name] = hname
	return field_dict
	

def row_view(request, model_name='', app_name='',html_name=''):
	'''list view of a model.'''
	if html_name == '': html_name = 'utilities/row_view.html'
	instance= apps.get_model('sources','Film').objects.get(title_original= '13 in de Oorlog: De Hongerwinter')
	name = model_name.lower()
	var = {name +'_row':instance,'page_name':model_name,
		'name':name,'app_name':app_name,'instance':instance}
	r =  render(request, html_name,var)
	return r
	

def list_view(request, model_name, app_name,html_name='',field_names = '',max_entries=200):
	'''list view of a model.'''
	print(max_entries)
	if field_names == '': field_names = field_names_dict[model_name.lower()]
	if html_name == '': html_name = 'utilities/general_list.html'
	s = Search(request,model_name,app_name,max_entries=max_entries)
	instances= s.filter()
	name = model_name.lower()
	field_dict = _handle_fieldnames(field_names) if field_names else {}
	var = {name +'_list':instances,'page_name':model_name,
		'order':s.order.order_by,'direction':s.order.direction,
		'query':s.query.query,'nentries':s.nentries, 'list':instances,'name':name,
		'type_name':name+'_type','app_name':app_name,'fields':field_dict.items(),
		'delete':app_name+':delete','edit':app_name+':edit_'+name}
	r =  render(request, html_name.replace('$','/'),var)
	return r

def timer(start):
	return time.time() -start

@permission_required('utilities.add_generic')
def edit_model(request, name_space, model_name, app_name, instance_id = None, 
	formset_names='', focus='', view ='complete'):
	'''edit view generalized over models.
	assumes a 'add_{{model_name}}.html template and edit_{{model_name}} function
	and {{model_name}}Form
	'''
	start = time.time()
	names = formset_names
	model = apps.get_model(app_name,model_name)
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	instance= model.objects.get(pk=instance_id) if instance_id else None
	crud = Crud(instance) if instance and model_name != 'Location' else None
	ffm, form = None, None
	print(model,modelform,model_name,app_name,98765)
	if request.method == 'POST':
		focus, button = getfocus(request), getbutton(request)
		if button in 'delete,cancel,confirm_delete': 
			return delete_model(request,name_space,model_name,app_name,instance_id)
		if button == 'saveas' and instance: instance = copy_complete(instance)
		form = modelform(request.POST, request.FILES, instance=instance)
		if form.is_valid():
			print('form is valid: ',form.cleaned_data,type(form))
			# print(form.cleaned_data['image_file'],str(form.cleaned_data['image_file']))
			instance = form.save()
			if view == 'complete':
				ffm = FormsetFactoryManager(name_space,names,request,instance)
				valid = ffm.save()
				if valid:
					show_messages(request,button, model_name)
					if button== 'add_another':
						return HttpResponseRedirect(reverse(app_name+':add_'+model_name.lower()))
					return HttpResponseRedirect(reverse(
						app_name+':edit_'+model_name.lower(), 
						kwargs={'pk':instance.pk,'focus':focus}))
				else: print('ERROR',ffm.errors)
			else: return HttpResponseRedirect('/utilities/close/')
		else:
			print(list(form.non_field_errors()))
			[show_messages(request,'error',l) for l in list(form.non_field_errors())]
	if not form: form = modelform(instance=instance)
	if not ffm: ffm = FormsetFactoryManager(name_space,names,instance=instance)
	tabs = make_tabs(model_name.lower(), focus_names = focus)
	page_name = 'Edit ' +model_name.lower() if instance_id else 'Add ' +model_name.lower()
	helper = help_util.Helper(model_name = model_name)
	args = {'form':form,'page_name':page_name,'crud':crud,
		'tabs':tabs, 'view':view,'app_name':app_name,'model_name':model_name,
		'helper':helper.get_dict()}
	args.update(ffm.dict)
	return render(request,app_name+'/add_' + model_name.lower() + '.html',args)
		

@permission_required('utilities.add_generic')
def add_simple_model(request, name_space,model_name,app_name, page_name, pk= None):
	'''Function to add simple models with only a form could be extended.
	request 	django object
	name_space 	the name space of the module calling this function (to load forms / models)
	model_name 	name of the model
	app_name 	name of the app
	page_name 	name of the page
	The form name should be of format <model_name>Form
	'''
	model = apps.get_model(app_name,model_name)
	modelform = view_util.get_modelform(name_space,model_name+'Form')
	instance= model.objects.get(pk=pk) if pk else None
	form = None
	if request.method == 'POST':
		form = modelform(request.POST,instance=instance)
		button = getbutton(request)
		print(button,'12345667889999')
		if button in 'delete,confirm_delete': 
			print('deleting simple model')
			return delete_model(request,name_space,model_name,app_name,pk,True)
		if form.is_valid():
			form.save()
			messages.success(request, model_name + ' saved')
			return HttpResponseRedirect('/utilities/close/')
	if not form: form = modelform(instance=instance)
	instances = model.objects.all().order_by('name')
	page_name = 'Edit ' +model_name.lower() if pk else 'Add ' +model_name.lower()
	url = '/'.join(request.path.split('/')[:-1])+'/' if pk else request.path
	var = {'form':form, 'page_name':page_name, 'instances':instances,'url':url}
	return render(request, 'utilities/add_simple_model.html',var)

@permission_required('utilities.delete_generic')
def delete_model(request, name_space, model_name, app_name, pk, close = False):
	model = apps.get_model(app_name,model_name)
	instance= get_object_or_404(model,id =pk)
	focus, button = getfocus(request), getbutton(request)
	print(request.POST.keys())
	print(99,instance.view(),instance,888)
	print(button)
	if request.method == 'POST':
		if button == 'cancel': 
			show_messages(request,button, model_name)
			return HttpResponseRedirect(reverse(
				app_name+':edit_'+model_name.lower(), 
				kwargs={'pk':instance.pk,'focus':focus}))
		if button == 'confirm_delete':
			instance.delete()
			show_messages(request,button, model_name)
			if close: return HttpResponseRedirect('/utilities/close/')
			return HttpResponseRedirect('/utilities/list_view/'+model_name.lower()+'/'+app_name+'/')
	info = instance.info
	print(1,info,instance,pk)
	var = {'info':info,'page_name':'Delete '+model_name.lower()}
	print(2)
	return render(request, 'utilities/delete_model.html',var)
	

def getfocus(request):
	'''extracts focus variable from the request object to correctly set the active tabs.'''
	if 'focus' in request.POST.keys():
		return request.POST['focus']
	else: return 'default'
# Create your views here.
def getbutton(request):
	if 'save' in request.POST.keys():
		return request.POST['save']
	else: return 'default'

def show_messages(request,button,model_name):
	'''provide user feedback on submitting a form.'''
	if button == 'saveas':messages.warning(request,
		'saved a copy of '+model_name+'. Use "save" button to store edits to this copy')
	elif button == 'confirm_delete':messages.success(request, model_name + ' deleted')
	elif button == 'cancel':messages.warning(request,'delete aborted')
	elif button == 'error':messages.warning(request,model_name)
	else: messages.success(request, model_name + ' saved')

def close(request):
	'''page that closes itself for on the fly creation of model instances (loaded in a new tab).'''
	return render(request,'utilities/close.html')
