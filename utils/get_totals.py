from django.apps import apps
from utils.model_util import get_all_models, get_all_instances
from utils.general import count_dict_to_percentage_dict

def get_totals(model_names = ''):
	o = {}
	models = get_all_models(model_names = model_names)
	print(models)
	for model in models:
		name = model._meta.model_name
		if name == 'memorialsite': name = 'memorial sites'
		elif name == 'picturestory': name = 'picture stories'
		elif name == 'recordedspeech': name = 'recorded speech'
		elif name == 'music': pass
		else: name += 's'
		print(name)
		o[name] = model.objects.all().count()
	return o


def _make_type_dict(model,skip_unknown = False):
	if skip_unknown: d = {}
	else: d = {'unknown':0}
	instances = model.objects.all()
	name = model._meta.model_name
	for instance in instances:
		if name == 'memorialsite':attr_name = 'memorial_type'
		elif name == 'picturestory':attr_name = 'picture_story_type'
		elif name == 'videogame':attr_name = 'game_type'
		else: attr_name = name + '_type'
		attr = getattr(instance,attr_name)
		if not attr: 
			if skip_unknown: continue
			d['unknown'] += 1
		elif attr.name not in d.keys(): d[attr.name] = 1
		else: d[attr.name] += 1
	d = count_dict_to_percentage_dict(d)
	return d
		

def get_types(model_names = ''):
	o = {}
	models = get_all_models(model_names = model_names)
	print(models)
	for model in models:
		name = model._meta.model_name
		if name == 'person':continue
		if name == 'memorialsite': name = 'memorial sites'
		elif name == 'picturestory': name = 'picture stories'
		elif name == 'recordedspeech': name = 'recorded speech'
		elif name == 'music': pass
		else: name += 's'
		o[name] = _make_type_dict(model)
	return o
	

def get_countries(model_names = ''):
	instances = get_all_instances(model_names)
	countries_dict = {'unknown':0}
	for instance in instances:
		countries = instance.country_field.split(',')
		for country in countries:
			if country == '': countries_dict['unknown'] += 1
			elif country not in countries_dict.keys():countries_dict[country] = 1
			else: countries_dict[country] += 1
	countries_dict = count_dict_to_percentage_dict(countries_dict)
	return countries_dict

def get_gender():
	gender_dict = {'female':0,'male':0,'unknown':0,'other':0}
	Person = apps.get_model('persons','Person')
	persons = Person.objects.all()
	npersons = persons.count()
	for person in persons:
		if not person.gender:gender_dict['unknown'] +=1
		elif person.gender.name not in gender_dict.keys():
			gender_dict[person.gender.name] = 1
		else: gender_dict[person.gender.name] +=1
	gender_dict = count_dict_to_percentage_dict(gender_dict,sort=False)
	return gender_dict
			
