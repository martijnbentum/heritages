'''
module to determine the country linked to an entry.
'''

from .export import Relations 
from .model_util import instance2name

def instance2countries(instance, field_name = '',all_location_fields = None):
	'''returns a comma separated string of countries.
	instance 		the db entry to get the linked country for
	field_name 		the field to get the country link from
	all_loc... 		get all country names for all linked locations
	'''
	if field_name: 
		field_names = [field_name]
		m ='all_location_fields is ignored because field_name is provided'
		if all_location_fields == True: print(m)
	else: field_names = get_all_location_field_names(instance)
		
	countries = []
	for field_name in field_names:
		countries.extend( _field_name2countries(field_name, instance) )
	return ','.join(sorted(list(set(countries))))


def get_all_location_field_names(instance):
	'''returns a list of field names that link to locations.'''
	relations = Relations(instance)
	field_names = []
	for field in relations.m2m_fields:
		if is_location_field(field): field_names.append(field.name)
	for field in relations.fk_fields:
		if is_location_field(field): field_names.append(field.name)
	return field_names


def _field_name2countries(field_name,instance): 
	'''returns a list of countries associated with a field name.'''
	if not hasattr(instance,field_name):
		raise ValueError(instance, 'does not have field', field_name)
	field_type = _fk_or_m2m(field_name,instance)
	locations = _field_name2locations(field_name,instance,field_type)
	countries = [l.country for l in locations if l and l.country]
	return countries
	
def _field_name2locations(field_name, instance,field_type = ''):
	'''returns locations linked to a field'''
	if not field_type: field_type = _fk_or_m2m(field_name, instance)
	attr = getattr(instance,field_name)
	if field_type == 'fk': return [attr]
	return attr.all()

def _location2country(location):
	'''returns the country associated with a locations.'''
	if hasattr(location,'location_type'):
		if location.location_type.name == 'country': 
			return location.name
	return location.country

def _field_name2field(field_name,instance):
	'''returns a field based on a field name.'''
	for field in instance._meta.get_fields():
		if field.name == field_name: return field
	m = field_name + ' not found for instance: ' + instance
	raise ValueError(m)

def _fk_or_m2m(field_name = '',instance = None, field = None):
	'''determines wether a field is fk or m2m relation.
	if the field is not relational it throws an error.
	'''
	if field_name:
		if not instance: raise ValueError('provide instance with field name')
		field = _field_name2field(field_name, instance)
	if not field: raise ValueError('provide field_name or field')
	if is_fk_field(field): return 'fk'
	if is_m2m_field(field): return 'm2m'
	m = field_name + ' is not a relation field ie fk or m2m ' + instance
	raise ValueError(m)

def is_fk_field(field):
	return 'ForeignKey' in field.__repr__()

def is_m2m_field(field):
	return 'ManyToManyField' in field.__repr__()

def is_location_field(field):
	_ = _fk_or_m2m(field = field) # check it is a relational field
	model = field.related_model
	model_name = instance2name(model)
	return model_name == 'Location'
