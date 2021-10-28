from django.apps import apps
from django.db.models.functions import Lower
from django.db.models import Q
from utils.model_util import get_all_models, instance2names

class SearchAll:
	def __init__(self,request = None, models = [], query = None, 
		max_entries=False, special_terms = None):
		if not models: models = get_all_models()
		self.models = models
		self.searches = []
		for model in self.models:
			an, mn = instance2names(model)
			s = Search(request,mn,an,query,max_entries,do_ordering=True,
				special_terms = special_terms)
			self.searches.append(s)
		self.query = self.searches[0].query.query

	def filter(self):
		if hasattr(self,'_instances'): return self._instances
		self._instances = []
		for s in self.searches:
			s.n
			self._instances.extend(s.filter())
			s.n
		return self._instances


class Search:
	'''search a django model on all fields or a subset with Q objects'''
	def __init__(self,request=None, model_name='',app_name='',query=None, 
		max_entries=500, do_ordering= True, special_terms =None):
		'''search object to filter django models
		query 				search terms provided by user
		search_fields 		field set to restrict search (obsolete?)
		model_name 			name of the django model
		app_name 			name of the app of the model
		max_entries 		number of entries to return
							will not truncate entries if 0 or False
		do_ordering 		whether to order the results
		'''
		if query:
			self.query = Query(query=query, special_terms=special_terms)
			self.order = Order(order=get_foreign_keydict()[model_name.lower()])
		else:
			self.request = request
			self.query = Query(request,model_name,special_terms=special_terms)
			self.order = self.query.order
		self.do_ordering = do_ordering
		self.max_entries = max_entries
		self.model_name = model_name
		self.app_name = app_name
		self.model = apps.get_model(app_name,model_name)
		self.fields = get_fields(model_name,app_name)
		self.select_fields()
		self.notes = 'Search Fields: (' 
		self.notes += ','.join([f.name for f in self.fields if f.include]) + ')'

	def select_fields(self):
		if self.query.fields:
			for field in self.fields:
				if field.name in self.query.fields: field.include = True
				else: field.include = False

	def check_and_or(self, and_or):
		if and_or == '': 
			self.and_or = 'and' if 'and' in self.query.special_terms else 'or'
		if self.and_or == 'and': self.notes += '\nall fields should match query'
		else: self.notes += '\none or more fields should match query'

	def check_combine(self, combine):
		self.combine = self.query.combine if combine == None else combine
		if self.combine:
			self.notes += '\ncombined query term: ' + self.query.clean_query
		else: 
			self.notes += '\nseperate query terms: ' 
			self.notes += ', '.join(self.query.query_terms)

	def check_exact(self, exact):
		self.exact = self.query.exact if exact == None else exact
		if self.exact:
			self.notes += '\nsearching for the exact query term: '
			self.notes += self.query.clean_query
		else:
			self.notes += '\nsearching for fields that contain query term: '
			self.notes += self.query.clean_query
				

	def check_completeness_approval(self):
		if self.query.completeness != None: 
			self.result = self.result.filter(complete=self.query.completeness)
			self.notes += '\ncompleteness: ' + str(self.query.completeness)
		if self.query.approval != None: 
			self.result = self.result.filter(approved=self.query.approval)
			self.notes += '\napproval: ' + str(self.query.approval)

	def set_ordering_and_direction(self):
		self.result = self.result.order_by(Lower(self.order.order_by))
		self.notes += '\nordered on field: ' + self.order.order_by
		if self.order.direction == 'descending': 
			self.result= self.result.reverse()
		self.notes += '\nordered in ' + self.order.direction + ' order'

	def filter(self, option = 'icontains',and_or='',combine= None,exact = None):
		'''method to create q objects and filter instance from the database
		option 		search term for filtering, default capital insensitive search
		and_or 		whether q objects have an and/or relation
		combine 	whether the words in the query should be searched seperately
					or not
		'''
		self.check_and_or(and_or)
		self.check_combine(combine)
		self.check_exact(exact)
		if self.exact: option = 'iexact'
		self.qs = []
		for field in self.fields:
			if field.include: 
				if self.combine:
					term = self.query.clean_query
					self.qs.append(field.create_q(term=term,option=option))
				else:	
					for term in self.query.query_terms:
						self.qs.append(field.create_q(term=term,option=option))
		self.q = Q()
		for qobject in self.qs:
			if self.and_or == 'and': self.q &= qobject
			else: self.q |= qobject
			
		self.result = self.model.objects.filter(self.q)
		self.check_completeness_approval()
		if self.do_ordering:self.set_ordering_and_direction()
		self.nentries_found = self.result.count()
		self.nentries = '# Entries: ' + str(self.nentries_found) 
		if self.max_entries and self.nentries_found > self.max_entries:
			self.nentries += ' (truncated at ' + str(self.max_entries) 
			self.nentries += ' entries)'
			self.result[:self.max_entries]
		return self.result

	@property
	def n(self):
		print(self.notes)



class Query:
	'''class to parse a http request extract query and extract relevant 
	information.'''
	def __init__(self,request=None, model_name='',query='', special_terms = None):
		'''individual words and special terms are extracted from the query.
		a clean version of the query (without special terms) is constructed.
		$ 	symbol prepended to field names
		* 	symbol prepended to special terms such as and/or
		'''
		self.request = request
		if 'query' in self.request.GET.keys():
			tquery = self.request.GET['query']
		else: tquery = ''
		if query: self.query = query
		else: self.query = tquery
		self.order = Order(request,model_name)
		self.query_words = self.query.split(' ')
		self.words = self.query_words
		self.query_terms = [w for w in self.words if w and w[0] not in ['*','$']]
		self.clean_query = ' '.join(self.query_terms)
		self.extract_field_names()
		self.extract_special_terms(special_terms)

	def extract_field_names(self):
		temp= [w[1:] for w in self.words if len(w) > 1 and w[0] == '$']
		self.field_term, self.fields= [],[]
		for term in temp:
			if ':' in term:self.field_term.append(term.split(':'))
			else: self.fields.append(term.lower())

	def extract_special_terms(self, special_terms):
		if 'combine' in self.request.GET.keys():
			combine = self.request.GET['combine']
		else: combine = ''
		if 'exact' in self.request.GET.keys():
			exact= self.request.GET['exact']
		else: exact= ''
		st = [w[1:].lower() for w in self.words if len(w) > 1 and w[0] == '*']
		self.special_terms = st
		if combine: self.special_terms.append(combine)
		if exact: self.special_terms.append(exact)
		if special_terms: self.special_terms.extend(special_terms)
		if 'complete' in self.special_terms: self.completeness = True
		elif 'incomplete' in self.special_terms: self.completeness = False
		else: self.completeness = None
		if 'approved' in self.special_terms: self.approval = True
		elif 'unapproved' in self.special_terms: self.approval = False
		else: self.approval = None
		self.combine = 'True' if 'combine' in self.special_terms else False
		self.exact = 'True' if 'exact' in self.special_terms else False
		print(self.special_terms,'<9--------')



class Order:
	def __init__(self,request=None, model_name=None,order=''):
		self.request = request
		self.model_name = model_name
		if order: self.order_by = order
		else:self.order_by = get_foreign_keydict()[self.model_name.lower()]
		self.direction = 'ascending'
		self.set_values()


	def set_values(self):
		if self.request:
			if 'direction' in self.request.GET.keys():
				temp = self.request.GET['direction']
				if temp in ['descending','ascending']: self.direction = temp

	def __repr__(self):
		return self.order_by + ', ' + self.direction
			
	
			
class Field:
	def __init__(self,name,description,model):
		self.model = model
		self.name = name
		self.description = description
		self.set_field_type()
		self.set_include()
		self.check_relation()

	def __repr__(self):
		return self.name

	def set_include(self, value = None):
		self.include = True 
		if self.name == 'id' or self.bool or self.file or self.image: 
			self.include = False 
		if value != None and value in [True,False]: self.include = value


	def set_field_type(self):
		'''sets booleans for field types (see field_typedict).'''
		ftd = get_field_typesdict()
		for name in ftd.keys():
			v= True if name in self.description else False
			setattr(self,ftd[name],v)

	def check_relation(self):
		'''checks whether a field is a foreign key or m2m and creates the full 
		name
		variable to end up with a field to be filtered on 
		(whether it is a relational field or not.'''
		self.relation = True if self.fk or self.m2m else False
		fkd = get_foreign_keydict()
		if self.relation:
			if self.name in fkd.keys(): 
				self.related_name = fkd[self.name]
				self.full_name = self.name +'__' + self.related_name
			elif self.name in link2name():
				self.full_name = self.name + '__name'
			else: 
				print('could not find related name of relational field',
					self.name,self.description)
				self.include =False
		else: self.full_name = self.name

	def create_q(self, term, option='icontains'):
		'''creates django q object for filtering'''
		self.q = Q(**{'__'.join([self.full_name,option]):term})
		return self.q
		



def get_fields(model_name,app_name):
	'''Get field names from a model (for now ignore many to one relations. 
	For example persontextrelation field is ignored on Text.
	'''
	model = apps.get_model(app_name,model_name)
	o = []
	for f in model._meta.get_fields():
		if hasattr(f,'description'): # skips ManyToOneRel
			o.append(Field(f.name,f.description,model))
	return o


def make_dict(s):
	return dict([i.split(':') for i in s.split(',')])

def get_field_typesdict():
	m = 'Foreign Key:fk,Many-to-many:m2m,Boolean:bool,Integer:int,String:str'
	m += ',File:file,Image:image,PartialDateField:partial_date'
	return make_dict(m)
	

def get_foreign_keydict():
	m = 'film:title_english,music:title_english,image:title_english'
	m += ',text:title_english'
	m += ',infographic:title_english,picturestory:title_english,person:name'
	m += ',famine:names,famines:names__name'
	m += ',location:name,keyword:name,videogame:title_english'
	m += ',recordedspeech:title_english'
	m += ',memorialsite:title_english,artefact:title_english'
	return make_dict(m)

def link2name():
	m = 'writers,directors,film_companies,locations_shot,locations_released'
	m += ',languages_subtitle,languages_original,setting,keyword,film_type'
	m += ',publishing_outlet,collection,commissioned_by,image_type,locations'
	m += ',creators,infographic_type,languages,music_type,composers'
	m += ',picture_story_type,authors,translators,publishers,artists'
	m += ',institution_authors,production_studio,game_type,text_type'
	m += ',recordedspeech_type,speakers,locations_recorded,setting'
	m += ',broadcasting_station,commissioning_persons,commissioning_institutions'
	m += ',donor_persons,donor_institutions,memorial_type,artefact_type'
	m += ',keywords,target_audience,available,permission,rated,editors'
	m += ',original_languages,names,causal_triggers,gender,nationality'
	m += ',location_of_birth,location_of_death,affiliation,occupation'
	return m.split(',')



'''
	publications = Publication.objects.filter(
		Q(title__icontains=query) | eval('Q(form__name__icontains=query)') |
		Q(publisher__name__icontains=query) | Q(location__name__icontains=query)).order_by(Lower(order_by))
'''
