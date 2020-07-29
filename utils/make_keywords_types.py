from django.apps import apps
from django import db
import pandas as pd
from misc.models import Keyword, KeywordRelation
from sources.models import Available, RequestUsePermission

def save_model(instance,saved,already_exists,error):
	ok = False
	try: instance.save()
	except db.IntegrityError: already_exists.append(instance)
	except: error.append(instance)
	else: 
		saved.append(instance)
		ok =True
	return ok
	


def show_results(model_name,saved,already_exists,error):
	print(model_name+':\n'+'-'*(len(model_name)+1))
	print('saved:',len(saved),'already exists:',len(already_exists),'error:',len(error))
	print()

d = pd.read_excel('data/keywords_and_types.xlsx',sheet_name=None)

def make_keywords():
	kw = d['Keywords']
	kw = [list(line) for line in kw.values[4:,1:3]]
	saved,already_exists,error = [],[],[]
	rsaved,ralready_exists,rerror = [],[],[]
	for category,name in kw:
		category_keyword = Keyword(name = category)
		name_keyword = Keyword(name = name)
		okck = save_model(category_keyword,saved,already_exists,error)
		oknk =save_model(name_keyword,saved,already_exists,error)
		if okck: ck = category_keyword
		else: ck = Keyword.objects.get(name =category)
		if oknk: nk = name_keyword
		else: nk = Keyword.objects.get(name= name)
		kr = KeywordRelation(container=ck,contained=nk)
		save_model(kr,rsaved,ralready_exists,rerror)

	show_results('Keyword',saved,already_exists,error)
	show_results('KeywordRelation',rsaved,ralready_exists,rerror)
			


def make_types():
	saved,already_exists,error = [],[],[]
	for key in d.keys():
		if not 'types' in key: continue
		model_name = key.split(' ')[0]+'Type'
		model = apps.get_model('sources',model_name)
		names = d[key].values
		for name in names:
			name = name[0]
			instance = model(name = name)
			save_model(instance,saved,already_exists,error)
		show_results(model_name,saved,already_exists,error)


def make_simple_model_instance(app_name,model_name,names):
	model = apps.get_model(app_name,model_name)
	o,saved,already_exists,error = [],[],[],[]
	for name in names.split(','):
		instance = model(name = name) 
		o.append(instance)
		save_model(instance,saved,already_exists,error)
	show_results(model_name,saved,already_exists,error)
	return o

def make_simple_models():
	available = 'sources','Available','available on site,available through link,unavailable'
	gender = 'persons','Gender','male,female,unknown,other'
	request_use_permission = 'sources','RequestUsePermission','yes,no'
	target_audience = 'sources','TargetAudience','national,international,both'
	rated = 'sources','Rated','general,<14,14+'
	o = []
	for sm in [available,gender,request_use_permission,target_audience,rated]:
		o.extend(make_simple_model_instance(*sm))
	return o
	

def make():
	make_keywords()
	make_types()
	make_simple_models()

