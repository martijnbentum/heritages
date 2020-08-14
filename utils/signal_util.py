from django.apps import apps
import sys
from easyaudit.models import CRUDEvent
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from misc.models import Famine
from sources.models import Film,Text,Image,PictureStory,Music,Infographic
from persons.models import Person

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
