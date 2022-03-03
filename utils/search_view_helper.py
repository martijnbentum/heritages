from utilities.search import SearchAll
from utils.general import remove_keys_from_dict
import copy
import json
import time
import os

class SearchView:
	'''stores options for view template.'''
	def __init__(self, request = None,view_type = 'tile_view', query = ' ', 
		combine = ' ',exact = 'contains', direction = 'ascending', 
		sorting_option = 'title - name', verbose = False):
		'''
		request 		django object
		view_type 		whether the results are shown in tile or row format
		query 			passing a query between view types, overwrites the
						query in the request
		'''
		self.start = time.time()
		self.request = request
		self.view_type = view_type
		self.query = query
		self.combine = combine
		self.exact = exact
		self.direction = direction
		self.sorting_option = sorting_option
		self.special_terms = [self.combine,self.exact]
		if verbose:print('start',delta(self.start))
		self.handle_request()
		if verbose:print('request',delta(self.start))
		self.make_search()
		if verbose:print('search',delta(self.start))
		self.handle_options()
		if verbose:print('options',delta(self.start))
		self.make_var()
		if verbose:print('var',delta(self.start))

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
		if 'exact' in self.request.GET.keys():
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
			'id_dict':self.id_dict,
			'filter_active_dict':self.filter_active_dict,
		}

	@property
	def id_dict(self):
		if hasattr(self,'_id_dict'): return self._id_dict
		self._id_dict = {
			'location':self.search._country_identifiers,
			'keyword':self.search._keyword_identifiers,
			'model':self.search._model_identifiers,
			'century':self.search._century_identifiers,
			'famine':self.search._famine_identifiers,
		}
		# all_ids = _get_all_non_dict_values_from_dict(self._id_dict)
		all_ids = [x.identifier for x in self.instances]
		for key in self._id_dict:
			all_ids_category = self._id_dict[key]['all']
			other_ids = list(set(all_ids) - set(all_ids_category))
			self._id_dict[key]['other'] = other_ids
		self._id_dict['all'] = all_ids
		return self._id_dict

	@property
	def filter_active_dict(self):
		o = {}
		for category_key, d in self.id_dict.items():
			if category_key == 'all': continue
			o[category_key] = 'active'
			for key in d.keys():
				if key == 'all' or key == 'other': continue
				o[category_key+','+key] = 'active'
		return o



class UserSearch:
	'''loads information about latest search by a user if available
	the information can be used to reload search view with all the settings
	corresponding to the search
	'''
	def __init__(self,request = None, user = ''):
		self.request = request
		if user: self.user = user
		if request: self.user = request.user.username
		self.directory = 'user_search_requests/' + self.user +'/'
		self.filename = self.directory + 'search'
		self.dict = None
		if os.path.isfile(self.filename): self.set_info()
		if not self.dict or self.to_old: self.useable = False
		else: self.useable = True

	def __repr__(self):
		m = 'UserSearch | '
		if self.dict:
			m += 'active ids: ' + str(self.nactive_ids) 
			m += ' | delta time: ' + str(self.delta_time)
			if self.query != ' ':m += ' | query: ' + str(self.query)
			m += ' | '
		m += 'useable: ' + str(self.useable)
		return m

	def set_info(self):
		self.dict = json.load(open(self.filename))
		for key,value in self.dict.items():
			setattr(self,key,value)
		self.nactive_ids = len(self.active_ids)

	@property
	def delta_time(self):
		return int(time.time() - self.time)

	@property
	def to_old(self):
		return self.delta_time > 3600 * 4

	
		

			
		

def to_json(search_view_helper, filename = None):
	d = _prepare_search_view_helper_dict(search_view_helper)
	if filename: 
		with open(filename,'w') as fout:
			json.dump(d,fout)
	return json.dumps(d)

def to_dict(search_view_helper):
	return _prepare_search_view_helper_dict(search_view_helper)
	

def _prepare_search_view_helper_dict(search_view_helper):
	remove_keys = ['search','instances','var','request']
	d = copy.copy(search_view_helper.__dict__)
	remove_keys_from_dict(d,remove_keys)
	return d

def delta(t):
	return time.time() -t

	
def _get_all_non_dict_values_from_dict(d, values = [], unique = True):
	for value in d.values():
		if type(value) == dict: 
			temp = _get_all_non_dict_values_from_dict(value)
		elif type(value) != list: temp = [value]
		else: temp = value
		values.extend(temp)
	if unique: values = list(set(values))
	return values




