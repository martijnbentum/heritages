from collections import OrderedDict
from django.apps import apps
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.forms.models import model_to_dict
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from utils import view_util, help_util, image_util, map_util
from utils.view_util import Crud, Cruds, make_tabs, FormsetFactoryManager
from utils.model_util import copy_complete, get_all_instances 
from utils.model_util import get_instances_without_license_or_reference
from utils.get_totals import get_totals, get_countries, get_types
from utils.get_totals import get_gender
from utils.search_view_helper import SearchView, UserSearch
# from .models import copy_complete
from utilities.search import Search, SearchAll
from .models import Protocol
from .forms import ProtocolForm
from .forms import AddInfoForm
import os
import time

   


te = 'title_original,title_english'
field_names_dict = {
    'person':'name,pseudonyms,gender,location_of_birth',
    'music':te+',music_type','film':te+',film_type',
    'text':te+',text_type', 'infographic':te+',infographic_type',
    'image':te+',image_type','picturestory':te+',picture_story_type',
    'famine':'names_str$names,locations_str$locations',
    'location':'name,country,region,location_type$type',
    'keyword':'name,category,category_relations$relations',
    'videogame':te+',game_type','recordedspeech':te+',recordedspeech_type',
    'memorialsite':te+',memorial_type',
    'artefact':te+',artefact_type',
    'license':'name',
    }


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

def overview(request):
    totals = get_totals()
    countries = get_countries()
    gender = get_gender()
    types = get_types()
    print(totals)
    total = sum(totals.values())
    var = {'page_name':'overview','totals':totals,'total':total}
    var.update({'countries':countries,'types':types})
    var.update({'gender':gender})
    return render(request,'utilities/overview.html',var)

def sidebar(request):
    var = {'page_name':'sidebar'}
    return render(request,'utilities/sidebar.html',var)


@permission_required('utilities.view_generic')
def search_view(request, view_type = '', query = ' ', combine = ' ',
    exact = 'contains', direction = '', sorting_option = 'title - name'):
    if not request.session or not request.session.session_key:
        request.session.save()
    print(request.session, request.session.session_key)
    print('  search start\n','\033[91m'+time.strftime("%H:%M:%S"))
    print(str(time.time()).split('.')[-1]+' ' +'\033[0m')
    print(request.POST,request.FILES,'search view')
    s = SearchView(request, view_type, query, combine, exact, direction, 
        sorting_option)
    print(s.view_type)
    if s.view_type == 'tile_view':
        return render(request,'utilities/tile_view.html',s.var)
    elif s.view_type == 'map_view':
        d = map_util.get_all_location_ids_dict(instances = s.instances, 
            add_names_gps = True)
        s.var['d']=d
        return render(request,'utilities/map_view.html',s.var)
    else:
        return render(request,'utilities/row_view.html',s.var)

def get_user_search_requests(request):
    directory = 'user_search_requests/' + request.session.session_key+'/'
    if not os.path.isdir(directory): os.mkdir(directory)
    print('  user req received\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    o = list(request.FILES['file'].chunks())[0].decode('utf-8')
    with open(directory + 'search','w') as fout:
        fout.write(o)
    print('  file written\n','\033[91m'+time.strftime("%H:%M:%S")+' '+str(time.time()).split('.')[-1]+'\033[0m')
    with open(directory + 'ready', 'w') as fout:
        pass
    return HttpResponse('done', content_type='text/plain')

@permission_required('utilities.view_generic')
def list_view(request, model_name, app_name,html_name='',field_names = '',
    max_entries=200):
    '''list view of a model.'''
    print(max_entries, html_name,app_name)
    if field_names == '': field_names = field_names_dict[model_name.lower()]
    if html_name == '': html_name = 'utilities/general_list.html'
    if html_name == 'typemaster': 
        html_name = 'utilities/general_list.html'
        typemaster=True
    else: typemaster = False
    print(typemaster,'<---')
    s = Search(request,model_name,app_name,max_entries=max_entries)
    instances= s.filter()
    # removing double entries from search results, necessary??
    instances = list(set(instances))
    name = model_name.lower()
    field_dict = _handle_fieldnames(field_names) if field_names else {}
    var = {name +'_list':instances,'page_name':model_name,
        'order':s.order.order_by,'direction':s.order.direction,
        'query':s.query.query,'nentries':s.nentries, 'list':instances,'name':name,
        'type_name':name+'_type','app_name':app_name,'fields':field_dict.items(),
        'delete':app_name+':delete','edit':app_name+':edit_'+name,
        'typemaster':typemaster}
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
    print('focus',[focus])
    parameter_focus = focus
    start = time.time()
    names = formset_names
    model = apps.get_model(app_name,model_name)
    modelform = view_util.get_modelform(name_space,model_name+'Form')
    instance= model.objects.get(pk=instance_id) if instance_id else None
    thumbnail_size = image_util.get_size_of_thumbnail(instance)
    crud = Crud(instance) if instance and model_name != 'Location' else None
    ffm, form = None, None
    print(model,modelform,model_name,app_name,98765)
    if request.method == 'POST':
        focus, button = getfocus(request), getbutton(request)
        print('focus',[focus])
        if button in 'delete,cancel,confirm_delete': 
            return delete_model(request,name_space,model_name,app_name,instance_id)
        if button == 'saveas' and instance: instance = copy_complete(instance)
        if button == 'skip': return show_edit_screen(request)
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
                    if parameter_focus == 'add_info': return show_edit_screen(request)
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
        'helper':helper.get_dict(), 'thumbnail_size':thumbnail_size,
        'focus':focus}
    args.update(ffm.dict)
    return render(request,app_name+'/add_' + model_name.lower() + '.html',args)
        

@permission_required('utilities.add_generic')
def add_simple_model(request, name_space,model_name,app_name, page_name, pk= None):
    '''Function to add simple models with only a form could be extended.
    request     django object
    name_space  the name space of the module calling this function (to load forms / models)
    model_name  name of the model
    app_name    name of the app
    page_name   name of the page
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

def ajax_instance_info(request,identifier,fields = 'all'):
    app_name, model_name, pk = identifier.split('_')
    model = apps.get_model(app_name,model_name)
    print(model,identifier, fields,app_name,model_name,pk)
    instance = model.objects.get(pk=int(pk))
    print(instance,1234)
    if fields == 'all': 
        fields = instance.__dict__.keys()
    if ',' in fields: fields = fields.split(',')
    else: fields = [fields]
    d = {}
    for field in fields:
        if hasattr(instance,field):
            attr = str(getattr(instance,field))
            if attr == 'None': attr = ''
            d[field] = attr
        else: d[field] = ''
    return JsonResponse(d)

def edit_protocol(request, app_name, model_name, field_name = None):
    print(app_name,model_name,field_name,1111,222)
    app_name, model_name = app_name.lower(), model_name.lower()
    ProtocolFormSet = modelformset_factory(Protocol, ProtocolForm,
        fields=('field_name','explanation'),extra=1,can_delete=True)
    queryset=Protocol.objects.filter(app_name = app_name,model_name=model_name)
    formset = []
    if request.method == 'POST':
        formset = ProtocolFormSet(request.POST,queryset=queryset)
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                need_save = False
                if not instance.app_name or instance.model_name: need_save = True
                if not instance.app_name: instance.app_name = app_name
                if not instance.model_name: instance.model_name = model_name
                if need_save: instance.save()
            print('save is a success')
            # if not field_name: return render(request,'utilities/close.html')
            # return HttpResponseRedirect('/'+app_name+'/add_'+ model_name+'/')
            return render(request,'utilities/close.html')
        else: print('not valid',formset.errors,app_name,model_name)
    if not formset: formset = ProtocolFormSet(queryset=queryset)
    note = 'changes to the protocol text will be visible after refreshing the page'
    page_name = 'Protocol ' + model_name
    var = {'formset':formset,'page_name':page_name,'note':note}
    return render(request, 'utilities/add_protocol.html',var)

def show_edit_screen(request):
    d = request.session.get('add_info_form')
    index = request.session.get('add_info_index')
    incomplete_instances = get_instances_without_license_or_reference(
        add_info_form = d)
    if index >= len(incomplete_instances): return add_info(request)
    instance = incomplete_instances[index]
    request.session['add_info_index'] = index + 1
    var = {'pk':instance.pk, 'focus':'add_info'}
    url = reverse(instance.edit_url, kwargs = var)
    print('url',url)
    return HttpResponseRedirect(url)

def add_info(request):
    n_all_instances = len(get_all_instances())
    n_incomplete_instances = len(get_instances_without_license_or_reference())
    form = None
    if request.method == 'POST':
        form = AddInfoForm(request.POST)
        if form.is_valid(): 
            request.session['add_info_form'] = form.cleaned_data
            request.session['add_info_index'] = 0
            print(form.cleaned_data)
            # return handle_add_info_instances(request,form.cleaned_data)
            return show_edit_screen(request)
    if not form: form = AddInfoForm()
    var = {'form':form,'n_all_instances':n_all_instances,
        'n_incomplete_instances':n_incomplete_instances}
    return render(request, 'utilities/add_info.html', var)

