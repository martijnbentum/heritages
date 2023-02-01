from django.apps import apps
from .location_to_linked_instances import get_all_linked_instances
from .model_util import instance2name, instance2names, get_all_instances
from locations.models import Location
import random

def instance2related_locations(instance):
	'''returns all locations from related instances (foreign keys and m2m) 
	assumes related models have location_field <str> that specifies the fields with
	locations.
	'''
	locations = []
	field_names = instance2related_fieldnames(instance)
	for field_name, field_type in field_names:
		#field type is either fk or m2m for foreign keys / many to many relations
		ls =[]
		related_instance= getattr(instance,field_name)
		if not related_instance: continue
		if field_type == 'fk':
			# skip related instance with no location fielf (contains string holding the name of the
			# location field)
			if not hasattr(related_instance,'location_field'): continue
			ls = field2locations(related_instance,related_instance.location_field)
			model_name = instance2name(related_instance)
			if ls: # if there are locations set on the related instance add them to the output
				ls =[[field_name.replace('_set',''),model_name,l,related_instance] for l in ls]
				locations.extend(ls)
		if field_type == 'm2m':
			# handle m2m related instances
			for rl in related_instance.all():
				#for each m2m multiple instance can be related
				if not hasattr(rl,'location_field'): continue
				model_name = instance2name(rl)
				ls=field2locations(rl,rl.location_field)
				if ls: # if there are locations set on the related instance add them to the output
					ls =[[field_name.replace('_set',''),model_name,l,rl] for l in ls]
					locations.extend(ls)
	return locations,field_names
	

def field2locations(instance, field_name):
	'''return locations from a field (fk or m2m) on a model.'''
	if not hasattr(instance,field_name):return None
	x = getattr(instance,field_name)
	if type(x) == Location: return [x]
	if 'ManyRelatedManager' in str(type(x)): 
		return list(x.all())
	print('field:',field_name,'on:',instance,'is of unknown type:',type(x))
	return None

		
	
def instance2related_fieldnames(instance):
	'''returns a list of lists with fields names that are either fk or m2m (with type in str)
	[<field>,<str>field_type]
	extends this list with reversed relations (fields ending in _set)
	'''
	fn = []
	for field in instance._meta.__dict__['local_fields']:
		if 'Foreign Key' in field.description:
			fn.append([field.name,'fk'])
	for field in instance._meta.__dict__['local_many_to_many']:
		fn.append([field.name,'m2m'])
	fn.extend([[name,'m2m'] for name in dir(instance) if name.endswith('_set')])
	return fn

def queryset2maplist(qs,roles = [],perturbe= False,combine =False):
	'''Create a list of lists with information to create leaflet popups from a queryset.'''
	o = []
	for i,instance in enumerate(qs):
		if not instance.latlng: continue
		for latlng in instance.latlng:
			name = instance2name(instance).lower()
			popup = instance.pop_up
			markerid = name + str(instance.pk)
			if perturbe: latlng = perturbe_latlng(latlng)
			if roles:o.append([name,latlng,popup,markerid,roles[i].replace('_',' ')])
			else:o.append([name,latlng,popup,markerid])
	if combine:  o =combine_popups(o)
	return o

def combine_popups(o):
	'''Combines popup content of multiple instances into one popup content.'''
	no = []
	dublicate_locations = {}
	for line in o:
		if line[1] in dublicate_locations.keys(): dublicate_locations[line[1]].append(line)
		else: dublicate_locations[line[1]] = [line]
	for key, value in dublicate_locations.items():
		if len(value) > 1:
			popups = '<hr>'.join([x[2] for x in value])
			ids = ':'.join([x[3] for x in value])
			new_line = [value[0][0],key,popups,ids]
			no.append(new_line)
		else:
			no.append(value[0])
	return no

def perturbe_latlng(latlng):
	lat,lng = map(float,latlng.split(', '))
	lat+=(random.random() - 0.5) /50 
	lng+=(random.random() - 0.5) /50 
	return ','.join(map(str,[lat,lng]))


	
# from region map util
def _location_ids2location_instances(ids):
	'''load location instances based on a list of ids'''
	model = apps.get_model('locations','Location')
	return model.objects.filter(pk__in = ids)

def get_all_location_ids_dict(instances = None,add_names_gps = False):
	'''a dictionary with id numbers of location instances as values, 
    with as keys
	the modelnames of the instances they are linked to.
	'''
	if not instances: instances = get_all_instances()
	d = {}
	if add_names_gps: 
		locations = get_all_locs_linked_to_instances(instances=instances)
		location_dict = dict([[x.pk,x] for x in locations])
	for instance in instances:
		if not instance.loc_ids:continue
		ids = list(map(int,instance.loc_ids.split(',')))
		for i in ids:
			if i not in d.keys(): 
				d[i] = {'count':0,'model_names':[],'identifiers':[]}
				if add_names_gps:
					l = location_dict[i]
					d[i].update( {'name':l.name,'gps':l.gps, 'pk':l.pk} )
			app_name, model_name = instance2names(instance)
			name = app_name + '_' + model_name
			if name not in d[i].keys():d[i][name] = []
			d[i][name].append(instance.pk)
			d[i]['identifiers'].append(instance.identifier)
			d[i]['count'] += 1
			if model_name not in d[i]['model_names']:
				d[i]['model_names'].append(model_name)
	return d

def get_all_locs_linked_to_instances(ids = None, instances = None):
	'''get all location instances that are linked to an instance 
	(e.g. person or text)
	'''
	if not ids and not instances: instances = get_all_instances()
	if not ids:
		ids = ','.join([x.loc_ids for x in instances if x.loc_ids]).split(',')
		ids = list(set(ids))
	return _location_ids2location_instances(ids)

def location2linked_instances(location):
	return get_all_linked_instances(location)

def get_all_location_ids_dict(instances = None,add_names_gps = False):
	'''a dictionary with id numbers of location instances as values, 
    with as keys
	the modelnames of the instances they are linked to.
	'''
	if not instances: instances = get_all_instances()
	d = {}
	if add_names_gps: 
		locations = get_all_locs_linked_to_instances(instances=instances)
		location_dict = dict([[x.pk,x] for x in locations])
	for instance in instances:
		if not instance.loc_ids:continue
		ids = list(map(int,instance.loc_ids.split(',')))
		for i in ids:
			if i not in d.keys(): 
				d[i] = {'count':0,'model_names':[],'identifiers':[]}
				if add_names_gps:
					l = location_dict[i]
					d[i].update( {'name':l.name,'gps':l.gps, 'pk':l.pk} )
			app_name, model_name = instance2names(instance)
			name = app_name + '_' + model_name
			if name not in d[i].keys():d[i][name] = []
			d[i][name].append(instance.pk)
			d[i]['identifiers'].append(instance.identifier)
			d[i]['count'] += 1
			if model_name not in d[i]['model_names']:
				d[i]['model_names'].append(model_name)
	return d
	
		
