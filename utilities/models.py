from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info, instance2names,instance2name
from utils.model_util import identifier2instance
import json
import time
import os

class SimpleModel(models.Model):
    name = models.CharField(max_length=300,default='',unique=True)
    endnode = True

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name

    class Meta:
        abstract=True

class generic(models.Model):
    pass

class Protocol(models.Model, info):
    app_name = models.CharField(max_length=300,default='')
    model_name = models.CharField(max_length=300,default='')
    field_name = models.CharField(max_length=300,default='')
    explanation = models.TextField(default='')

    class Meta:
        unique_together = [['model_name','field_name']]

    def __str__(self):
        return self.app_name + ' ' + self.model_name + ' ' + self.field_name


class UserSearch(models.Model, info):
    '''
    stores state information for search queries. 
    linked to user via request.session.session_key (functional cookie)
    '''
    session_key = models.CharField(max_length = 60, default = '',unique = True) 
    user = models.OneToOneField(User, on_delete = models.CASCADE,
        blank=True,null=True)
    time = models.FloatField(null=True, blank=True)
    _active_ids = models.TextField(default = '')
    _filters = models.TextField(default = '')
    date_start = models.PositiveIntegerField(null=True,blank=True)
    date_end = models.PositiveIntegerField(null=True,blank=True)
    query = models.CharField(max_length = 300, default = '')
    sorting_direction = models.CharField(max_length = 100, default = '')
    sorting_category= models.CharField(max_length = 100, default = '')
    current_instance = models.CharField(max_length = 100, default = '')
    view_type= models.CharField(max_length = 100, default = '')
    _filter_active_dict = models.TextField(default = '')
    new_query = models.CharField(max_length = 30, default = '')
    keys = models.CharField(max_length = 300, default = '')

    def __repr__(self):
        m = 'session: ' + self.session_key + ' | '
        if self.user:
            m += 'user: ' + self.user.username+ ' | '
        m += 'nactive ids: ' + str(self.nactive_ids)+ ' | '
        m += 'delta time: ' + str(self.delta_time)+ ' | '
        m += 'useable: ' + str(self.useable)+ ' | '
        return m

    def __str__(self):
        m = 'session:'.ljust(15) + self.session_key + '\n'
        if self.user:
            m += 'user:'.ljust(15) + self.user.username+ '\n'
        m += 'nactive ids:'.ljust(15) + str(self.nactive_ids)+ '\n'
        m += 'delta time:'.ljust(15) + str(self.delta_time)+ '\n'
        m += 'useable:'.ljust(15) + str(self.useable)+ '\n'
        return m

    def update(self, request, json_string):
        '''update the state information with a json string that can be converted to
        dictionary.
        request object is used to check the session_key and optionally set the user
        (if user is logged in)
        '''
        if self.session_key != request.session.session_key:
            print(request.session.session_key,self.session_key,
                'different doing nothing')
            return
        try: d = json.loads(json_string)
        except json.JSONDecodeError:
            print(json_string, 'cannot be handled by json library, doing nothing')
            return
        self.time = time.time()
        self._set_user(request.user, save = False)
        self._update_search_state_information_with_dict(d, save = False)
        self.save() 

    @property
    def dict(self):
        if hasattr(self,'_dict'): return self._dict
        keys = self._get_json_value('keys')
        d = {}
        for key in keys:
            d[key] = getattr(self,key)
        d['index'] = self.index
        d['number'] = self.number
        d['nactive_ids'] = self.nactive_ids
        d['useable'] = self.useable
        self._dict = d
        return self._dict

    def to_json(self):
        '''create a json string of the dict with state information used by 
        search template
        javascript code to set used search parameters.
        '''
        return json.dumps(self.dict)

    def _update_search_state_information_with_dict(self, d, save = True):
        '''update the search parameters with current settings.
        update is done based on dictionary extracted from json string
        '''
        for name in d.keys():
            if name in 'time,index,number,nactive_ids,usable'.split(','):continue
            if name in 'active_ids,filters'.split(','):
                self._set_list(d[name], '_' + name,save = False)
            elif name == 'current_instance':
                self.set_current_instance(d['current_instance'], save = False)
            elif name == 'filter_active_dict':
                self._set_fad(d['filter_active_dict'], save = False)
            else: setattr(self,name,d[name])
        self._set_list(list(d.keys()),'keys', save = False)
        if save: self.save()

    def _set_user(self,user, save = True):
        '''if user is present set it.
        if another usersearch instance is linked to the user delete it
        only usersearch should exist per user and a new instance is made for
        each session key
        '''
        if not user or not user.username: return
        if user.usersearch != self: user.usersearch.delete()
        self.user = user
        if save: self.save()

    def set_current_instance(self, identifier, save = True):
        '''the current instance is shown in the detail view.
        it is possible to iterate over the set of active identifiers so current
        instance needs to be updatable
        '''
        if self.identifier_part_of_search_results(identifier):
            self.current_instance = identifier
            if save: self.save()
            print('current instance:',identifier)
        else:
            print(identifier,'not in active_ids doing nothing')

    def _set_fad(self,filter_active_dict, save = True):
        '''the filter active contains state information about the search filters.'''
        if not type(filter_active_dict) == dict:
            print(filter_active_dict,type(filter_active_dict), 
                'is not a dict, doing nothing')
            return
        self._filter_active_dict = json.dumps(filter_active_dict)
        if save: self.save()

    def _set_list(self,value,attr_name, save = True):
        '''general method to store a list (value) on a specific textfield (attr_name)
        the list is stored as a json string
        '''
        if not type(value) == list:
            print(value,type(value), 'is not a list, doing nothing')
            return
        setattr(self,attr_name,json.dumps(value))
        self.save()

    def _get_json_value(self, attr_name):
        '''retrieve an object stored as a json string in a text field as the correct
        object (e.g. list or dictionary)
        '''
        value = getattr(self,attr_name)
        if value: 
            try: output = json.loads(value)
            except json.JSONDecodeError:
                print(value, 'cannot be handled by json library, doing nothing')
                return
            else: return output
        return []

    def identifier_part_of_search_results(self,identifier):
        '''check whether the identifier is part of the list of active_ids.'''
        return hasattr(self,'current_instance') and identifier in self.active_ids

    @property
    def active_ids(self):
        return self._get_json_value('_active_ids')

    @property
    def filters(self):
        return self._get_json_value('_filters')

    @property
    def filter_active_dict(self):
        return self._get_json_value('_filter_active_dict')

    @property
    def index(self):
        if hasattr(self,'current_instance') and self.current_instance in self.active_ids:
            return self.active_ids.index(self.current_instance)
        else: return None

    @property
    def number(self):
        index = self.index
        if index: return index + 1
        return None

    @property
    def nactive_ids(self):
        return len(self.active_ids)

    @property
    def delta_time(self):
        if self.time: return time.time() - self.time
        return None

    @property
    def to_old(self):
        if not self.time: return True
        return self.delta_time > 3600 * 4
           
    @property
    def useable(self):
        d = self.filter_active_dict
        if not d or self.to_old or self.index == None: return False
        else: return True

    @property
    def instance(self):
        try: return identifier2instance(self.current_instance)
        except: return None


def get_user_search(session_key):
    try: return UserSearch.objects.get(session_key = session_key)
    except UserSearch.DoesNotExist:
        us = UserSearch(session_key = session_key)
        us.save()
        return us

def expose_m2m(instance, field_name,attr):
    ''' return a comma seperated string of attr from m2m linked model. '''
    n = []
    m2m= getattr(instance,field_name)
    for item in m2m.all():
        n.append(getattr(item,attr))
    return ','.join(n)


def instance2color(instance):
    name = instance2name(instance).lower()
    if name in color_dict.keys(): return color_dict[name]
    else: return 'black'

def instance2icon(instance):
    '''
    name = instance2name(instance).lower()
    if name in icon_dict.keys(): 
        return icon_dict[name]
    return 'not found'
    '''
    if not hasattr(instance,'icon'):return ''
    return '<i class="'+instance.icon+' fa-lg mt-2" aria-hidden="true"></i>' 

def instance2map_buttons(instance):
    app_name,model_name= instance2names(instance)
    m = ''
    m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
    m += '/'+app_name+'/edit_' + model_name.lower()+'/' + str(instance.pk) +'/'
    m += ' role="button"><i class="far fa-edit"></i></a>'
    m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
    m += '/locations/show_links/'+app_name+'/'+ model_name.lower()+'/' + str(instance.pk) +'/'
    m += ' role="button"><i class="fas fa-project-diagram"></i></a>'
    return m


names = 'text,picturestory,dot,image,infographic,famine,film,artefact,memorialsite,recordedspeech,videogame'.split(',');
colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817,#eb4034,#ebbd34'.split(',')
#names = 'text,picturestory,dot,image,infographic,famine,film,music,person'.split(',');
#colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817'.split(',')
# icons ='fa fa-book,fa fa-star,fa fa-circle,fa fa-picture-o'
# icons +=',fa fa-bar-chart,fas fa-exclamation,fa fa-video-camera,fa fa-music,fa fa-male'
# icons = ['<i class="'+icon+' fa-lg mt-2" aria-hidden="true"></i>' for icon in icons.split(',')]
color_dict={}
for i,name in enumerate(names):
    color_dict[name] = colors[i]

