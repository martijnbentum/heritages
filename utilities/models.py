from django.apps import apps
from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info

class SimpleModel(models.Model):
	name = models.CharField(max_length=300,default='',unique=True)

	def __str__(self):
		return self.name

	class Meta:
		abstract=True

class generic(models.Model):
	pass


def copy_complete(instance, commit = True):
	#copy a model instance completely with all relations.
	copy = simple_copy(instance, commit)
	app_name, model_name = instance2names(instance)
	for f in copy._meta.get_fields():
		if f.one_to_many:
			for r in list(getattr(instance,f.name+'_set').all()):
				rcopy = simple_copy(r,False)
				setattr(rcopy,model_name.lower(), copy)
				rcopy.save()
		if f.many_to_many:
			getattr(copy,f.name).set(getattr(instance,f.name).all())
	return copy


def simple_copy(instance, commit = True):
	#Copy a model instance and save it to the database.
	#m2m and relations are not saved.
	#
	app_name, model_name = instance2names(instance)
	model = apps.get_model(app_name,model_name)
	copy = model.objects.get(pk=instance.pk)
	copy.pk = None
	if commit:
		copy.save()
	return copy

def instance2names(instance):
	s = str(type(instance)).split("'")[-2]
	app_name,_,model_name = s.split('.')
	return app_name, model_name

def instance2name(instance):
	model_name = instance.__class__.__name__
	return model_name


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
	name = instance2name(instance).lower()
	if name in icon_dict.keys(): 
		return icon_dict[name]
	return 'not found'

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


names = 'text,picturestory,dot,image,infographic,famine,film,music,person'.split(',');
colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817'.split(',')
icons ='fa fa-book,fa fa-star,fa fa-circle,fa fa-picture-o'
icons +=',fa fa-bar-chart,fas fa-exclamation,fa fa-video-camera,fa fa-music,fa fa-male'
icons = ['<i class="'+icon+' fa-lg mt-2" aria-hidden="true"></i>' for icon in icons.split(',')]
color_dict,icon_dict ={}, {}
for i,name in enumerate(names):
	color_dict[name] = colors[i]
	icon_dict[name] = icons[i]

