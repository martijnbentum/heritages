from utilities.search import SearchAll
from utils.general import remove_keys_from_dict
import json
import copy

class SearchView:
	'''stores options for view template.'''
	def __init__(self, request = None,view_type = 'tile_view', query = ' ', 
		combine = ' ',exact = 'contains', direction = 'ascending', 
		sorting_option = 'title - name'):
		'''
		request 		django object
		view_type 		whether the results are shown in tile or row format
		query 			passing a query between view types, overwrites the
						query in the request
		'''
		self.request = request
		self.view_type = view_type
		self.query = query
		self.combine = combine
		self.exact = exact
		self.direction = direction
		self.sorting_option = sorting_option
		self.special_terms = [self.combine,self.exact]
		self.handle_request()
		self.make_search()
		self.handle_options()
		self.make_var()

	def make_search(self):
		self.search = SearchAll(self.request, query = self.query,
			direction = self.direction,special_terms = self.special_terms,
			sorting_option = self.sorting_option)
		self.instances= self.search.filter()
		self.identifiers = [x.identifier for x in self.instances]
		self.nentries = '# Entries: ' + str(len(self.instances))
		self.query = self.search.query if self.search.query else ' '

	def handle_request(self):
		if not self.request: return
		if 'HTTP_REFERER' not in self.request.META.keys(): self.query = None
		elif self.view_type in self.request.META['HTTP_REFERER']: self.query = None
		if self.query == ' ': self.query = None
		if 'combine' in self.request.GET.keys():
			self.combine = self.request.GET['combine']
		if 'sorting_option' in self.request.GET.keys():
			self.sorting_option = self.request.GET['sorting_option']
		if 'direction' in self.request.GET.keys():
			self.direction = self.request.GET['direction']
		if 'exact' in request.GET.keys():
			self.exact= self.request.GET['exact']

	def handle_options(self):
		if self.direction == 'ascending':self.sorting_icon = 'fas fa-sort-alpha-down'
		else:self.sorting_icon = 'fas fa-sort-alpha-up'
		self.d = {'title - name':'t','chronological':'c','famine':'f','category':'ca'}
		self.d.update({'location':'l'})
		if self.sorting_option in self.d.keys(): 
			self.select_sorting_option = self.d[self.sorting_option]
		else: self.select_sorting_option = 't'
		if self.view_type == 'tile_view':
			self.view_type_link = 'row_view'
			self.view_type_icon=  'fas fa-align-justify fa-lg'
		else:
			self.view_type_link = 'tile_view'
			self.view_type_icon=  'fas fa-th fa-lg'

	def make_var(self):
		self.var = {'page_name':self.view_type.replace('_',' '),
			'instances':self.instances,
			'query':self.query, 
			'nentries':self.nentries,
			'view_type_icon':self.view_type_icon,
			'vtl':self.view_type_link,
			'combine':self.combine,
			'direction':self.direction,
			'sorting_icon':self.sorting_icon,
			'exact':self.exact,
			'sorting_option':self.sorting_option,
			self.select_sorting_option:'selected',
			'country_counts':self.search.country_counts,
			'keyword_category_counts':self.search.keyword_category_counts,
			'model_counts':self.search.model_counts,
			'century_counts':self.search.century_counts,
			'famine_counts':self.search.famine_counts,
		}

class test:
	def __init__(self):
		self.a =1

def to_json(search_view_helper, filename = None):
	d = _prepare_search_view_helper_dict(search_view_helper)
	if filename: 
		with open(filename,'w') as fout:
			json.dump(d,fout)
	return json.dumps(d)
	

def _prepare_search_view_helper_dict(search_view_helper):
	remove_keys = ['search','instances']
	d = copy.copy(search_view_helper.__dict__)
	remove_keys_from_dict(d,remove_keys)
	var = copy.copy(d['var'])
	d['var'] = remove_keys_from_dict(var,['instances'])
	return d


	
