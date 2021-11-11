from django.apps import apps
from utils.model_util import get_all_models, get_all_instances

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

def get_countries(model_names = ''):
	instances = get_all_instances(model_names)
	countries_dict = {}
	for instance in instances:
		countries = instance.country_field.split(',')
		for country in countries:
			if country == '': continue
			if country not in countries_dict.keys():countries_dict[country] = 1
			else: countries_dict[country] += 1
	total = sum(countries_dict.values())
	temp = []
	for key, val in countries_dict.items():
		temp.append([key, round(val /total * 100,2)])
	temp = sorted(temp, key=lambda x: x[1],reverse = True)
	countries_dict = dict(temp)
	return countries_dict

			
