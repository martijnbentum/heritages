from .model_util import make_models_image_file_dict
from django.apps import apps
from django.db.models import Q
from functools import reduce
from operator import __and__ as AND

import os


def get_all_instances_with_images():
	''' returns all instances from the database with a non empty image field '''
	# collect a dictionary with app_name, model_name as key and a list of imagefield names as value
	d = make_models_image_file_dict(only_image_fields = True)
	instances = []
	for app_name,model_name in d.keys():
		# retrieve model based on app and model name
		model = apps.get_model(app_name,model_name)
		#retrieve field names that correspond to and image field for that model
		field_names = d[app_name,model_name]
		#create a query for each image field
		qs = [Q(**{field_name:''}) for field_name in field_names]
		#the queries are combined with the AND operator
		qs = reduce(AND,qs)
		#we exclude all instances were all image fields are empty
		instances.extend(model.objects.exclude(qs))
	return instances


def get_size_of_thumbnail(instance):
    if not instance: return False
    if not hasattr(instance,'thumbnail'): return False
    if instance.thumbnail and instance.thumbnail.path:
        f = instance.thumbnail.path
    else: return False
    if not os.path.isfile(f): return False
    return round(os.path.getsize(f) / 1000_000,2)
    
        
		
			

		

	

