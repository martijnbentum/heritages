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

