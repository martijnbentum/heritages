from django.apps import apps
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.conf import settings

from easyaudit.models import CRUDEvent

from misc.models import Famine
from sources.models import Film,Text,Image,PictureStory,Music,Infographic
from persons.models import Person

from .backup_util import put_file, isfile

import sys
import os

def catch_m2m(instance, action, pk_set, model_name,field_name):
	'''Adds a changed field dict to changed_fields attr of easyaudit event object
	in case of m2m changes.
	functions is called by django m2m_changed signal.
	this needs a receiver per m2m field per model, these are made by the 
	model2m2m receiver.
	'''
	z = False
	field = getattr(instance,field_name)
	if action == 'pre_remove':
		before = field.all()
		after = [n for n in field.all() if n.pk not in pk_set]
		z = True
	elif action == 'post_add':
		after= field.all()
		before= [n for n in field.all() if n.pk not in pk_set]
		z = True
	if z:
		# the event object stores changes in the changed_fields as a dict
		# easyaudit does not catch m2m changes, here we update the attr with m2m changes
		event = CRUDEvent.objects.filter(content_type__model = model_name,object_id= instance.pk)
		if event: 
			event = event[0]
			v = {field_name:[','.join([str(n) for n in before]),','.join([str(n) for n in after])]}
			if type(event.changed_fields) != dict: event.changed_fields = v
			else: 
				event.changed_fields.update(v)
			event.save()
		# print(model_name,field_name, 'before:',','.join([str(n) for n in before]))
		# print(model_name,field_name,'after:',','.join([str(n) for n in after]))
	

def make_m2mreceiver(sender,model_name,field_name):
	'''creates a receiver for a given m2m field of a model.'''
	m = '@receiver(m2m_changed, sender='+sender+')\n'
	m+= 'def '+sender.replace('.','__').lower() +'(sender,instance,action,**kwargs):\n'
	m+= '\tpk_set = kwargs["pk_set"]\n'
	m+= '\tcatch_m2m(instance,action,pk_set,"'+model_name+'","'+field_name+'")'
	exec(m,globals())

def model2m2mreceiver(model_name,app_name):
	'''creates m2m reciever for each m2m field of a model.'''
	model = apps.get_model(app_name,model_name)
	m2m_fieldnames = model._meta.__dict__['local_many_to_many']
	for f in m2m_fieldnames:
		field_name = f.attname
		sender = model_name+'.'+field_name+'.through'
		make_m2mreceiver(sender,model_name.lower(),field_name)


#list of models with m2m models that need to be tracked by easyaudit.'''
names = 'Famine$misc,Film$sources,Text$sources,Image$sources,PictureStory$sources'
names += ',Music$sources,Infographic$sources,Person$persons'
for name in names.split(','):
	model_name, app_name = name.split('$')
	model2m2mreceiver(model_name,app_name)


#example of a receiver function to cat m2m_changed singals.
'''
@receiver(m2m_changed,sender=Famine.names.through)
def bla(sender, instance,action,**kwargs):
	pk_set = kwargs['pk_set']
	catch_m2m(instance,action,pk_set,'famine','names')
'''

@receiver(post_save, sender = Image)
def print_filename(sender, instance, **kwargs):
	if instance.image_file:
		local_path, remote_path, filename=  extract_filename_and_path(instance.image_file.name)
		print(local_path,remote_path,filename)
		if not isfile(remote_path + filename):
			print('file not yet backed up, saving to remote folder')
			put_file(local_path,remote_path,filename)
		else: print('backup file already exists, doing nothing')

def make_file_backup_postsave_receiver(app_name,model_name):
	m = '@receiver(post_save, sender = '
	m += model_name + ')\n'
	m += 'def save_file_backup(sender, instance, **kwargs):\n'
	m += '\tapp_name, model_name = instance2names(instance)\n'
	#work in progress, need to get the fields from make_models_image_file_dict and loop them
	m += '\to = extract_filename_and_path(instance.image_file.name)\n'
	m += '\tprint(o)\n'
	m += '\tif not isfile(remote_path + filename):\n'
	m += '\t\tprint("file not yet backed up, saving to remote folder")\n'
	m += '\t\tput_file(local_path,remote_path,filename)\n'
	m += '\telse: print("backup file already exists, doing nothing")\n'

def model2file_backup_postsave_receiver(app_name,model_name):
	pass


'''
for k in make_models_image_file_dict:
	model2file_backup_postsave_receiver(*k)
'''
		

def extract_filename_and_path(name):
	media_dir = settings.MEDIA_ROOT
	media_remote_dir = media_dir.split('/')[-1]
	if not media_dir.endswith('/'): media_dir += '/'
	if not media_remote_dir.endswith('/'): media_remote_dir += '/'
	if '/' not in name: filename, remote_path = name, ''
	else: filename, remote_path = name.split('/')[-1], '/'.join(name.split('/')[:-1])
	remote_path += '/'
	local_path = media_dir + remote_path
	name = local_path + '/' + filename
	remote_path = media_remote_dir + remote_path
	if not os.path.isdir(local_path):print(path,'not an existing directory') 
	if not os.path.isfile(name):print(name,'not an existing file')
	return local_path, remote_path, filename

		
