import os
import dcl
from django.apps import apps
from .model_util import make_models_image_file_dict, id_generator

def rename_file(instance,file_fieldname,new_name, overwrite = False):
	file_field = getattr(instance,file_fieldname)
	old_path = file_field.path
	base_dir = old_path.replace(file_field.name,'')
	new_path = base_dir + new_name
	if not overwrite and os.path.isfile(new_path): new_path = _fix(new_path)
	os.rename(old_path,new_path)
	setattr(instance,file_fieldname,new_name)
	instance.save()

def remove_diacritics_filename_existing_file(instance,file_fieldname):
	file_field = getattr(instance,file_fieldname)
	if not dcl.has_diacritics(file_field.name):return
	new_name = dcl.clean_diacritics(file_field.name)
	rename_file(instance,file_fieldname,new_name)
	print(instance, new_name, 'updated filename\n')

def rename_all_dicritic_illustration_filenames():
	from catalogue.models import Illustration
	i = Illustration.objects.all()
	for x in i:
		if not x.upload: continue
		remove_diacritics_filename_existing_file(x,'upload')

def remove_diacritics_filename(filename):
	return dcl.clean_diacritics(filename)


def _handle_instance(instance,field_names):
	for field_name in field_names:
		file_field= getattr(instance,field_name)
		if file_field: remove_diacritics_filename_existing_file(instance,field_name)

def rename_all_dicritic_filenames():
	d = make_models_image_file_dict()
	for app_model_name, field_names in d.items():
		model = apps.get_model(*app_model_name)
		instances = model.objects.all()
		for instance in instances:
			_handle_instance(instance,field_names)

def _fix(filename):
	temp = filename.split('.')
	if len(temp) == 1: return temp[0] + '_django-' + id_generator()
	extension = temp[-1]
	path = '-'.join(temp[:-1])
	path += '_django-' + id_generator()
	return path + '.' + extension


