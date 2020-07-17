from django.apps import apps
import pandas as pd
from misc.models import Keyword, KeywordRelation

d = pd.read_excel('data/keywords_and_types.xlsx',sheet_name=None)

def make_keywords():
	kw = d['Keywords']
	kw = [list(line) for line in kw.values[4:,1:3]]
	for category,name in kw:
		new_name_keyword = False
		try:
			category_keyword = Keyword(name = category)
			category_keyword.save()
			ck = category_keyword
			print('category:',category,'saved')
		except: print('category:',category,'already exists')
		try:
			name_keyword = Keyword(name = name)
			name_keyword.save()
			new_name_keyword = True
			print('category:',category,'name:',name,'saved')
		except: print('category:',category,'name:',name,'already exists')
		if new_name_keyword:
			try:
				kr = KeywordRelation(container=ck,contained=name_keyword)
				kr.save()
				print(kr,'saved')
			except: print('relation already exists:',category,name)
			


def make_types():
	for key in d.keys():
		if not 'types' in key: continue
		model_name = key.split(' ')[0]+'Type'
		model = apps.get_model('sources',model_name)
		names = d[key].values
		for name in names:
			name = name[0]
			try:
				instance = model(name = name)
				instance.save()
				print(model_name,name,'saved')
			except:
				print(model_name,name,'alread exists')

def make():
	make_keywords()
	make_types()

