from utilities.search import SearchAll
from utilities.forms import NewsearchForm
# from utilities.models import UserSearch, get_user_search
from utils.general import remove_keys_from_dict
from utils.model_util import identifier2instance
from utils import query_hints
import copy
import json
import time
import os

class SearchView:
    '''stores options for view template.'''
    def __init__(self, request = None,view_type = '', query = ' ', 
        combine = ' ',exact = 'contains', direction = '', 
        sorting_option = 'title - name', verbose = False):
        '''
        request         django object
        view_type       whether the results are shown in tile or row format
        query           passing a query between view types, overwrites the
                        query in the request
        '''
        self.start = time.time()
        self.query = query
        self.request = request
        # self.user_search = get_user_search(request.session.session_key)
        self.user_search = UserSearch(request)
        self.make_new_search_form(request)
        self.view_type = view_type
        self.combine = combine
        self.exact = exact
        self.direction = direction
        self.sorting_option = sorting_option
        self.special_terms = [self.combine,self.exact]
        if verbose:print('start',delta(self.start))
        self.handle_request()
        if verbose:print('request',delta(self.start))
        self.make_search()
        self.get_date_range()
        if verbose:print('search',delta(self.start))
        self.handle_options()
        if verbose:print('options',delta(self.start))
        self.make_var()
        if verbose:print('var',delta(self.start))

    def make_new_search_form(self,request):
        '''Create a form to handle user query and query hints.'''
        if request.method == 'POST':
            self.new_search_form = NewsearchForm(request.POST)
        else:
            if hasattr(self.user_search,'query'): 
                if self.user_search.query == ' ':
                    self.user_search.query = ''
                initial = {'query': self.user_search.query}
            else:
                initial = {'query': ''}
            print(initial,'initial')
            self.new_search_form = NewsearchForm(initial = initial)

    def make_search(self):
        self.search = SearchAll(self.request, query = self.user_search.query,
            direction = self.direction,special_terms = self.special_terms,
            sorting_option = self.sorting_option)
        self.instances= self.search.filter()
        self.identifiers = [x.identifier for x in self.instances]
        self.nentries = '# Entries: ' + str(len(self.instances))
        self.query = self.search.query if self.search.query else ' '

    def handle_request(self):
        if not self.request: return
        usu = self.user_search.useable
        if 'HTTP_REFERER' not in self.request.META.keys(): self.query = None
        elif self.view_type in self.request.META['HTTP_REFERER']: self.query = None
        if self.query == ' ': self.query = None
        if not self.query and hasattr(self.user_search, 'query') and usu:
            # if self.user_search.new_query == 'false':
            self.query = self.user_search.query
        if hasattr(self.user_search, 'sorting_category') and usu:
            self.sorting_option = self.user_search.sorting_category
        has_sorting_d = hasattr(self.user_search, 'sorting_direction')
        if not self.direction and has_sorting_d and usu: 
            self.direction = self.user_search.sorting_direction
        else: self.direction = 'ascending'
        if not self.view_type and hasattr(self.user_search,'view_type') and usu: 
            self.view_type = self.user_search.view_type
        else: self.view_type = 'tile_view'

    def handle_options(self):
        if self.direction == 'ascending':
            self.sorting_icon = 'fas fa-sort-alpha-down'
        else:self.sorting_icon = 'fas fa-sort-alpha-up'
        self.d = {'title - name':'t','chronological':'c','famine':'f'}
        self.d.update({'location':'l','category':'ca'})
        if self.sorting_option in self.d.keys(): 
            self.select_sorting_option = self.d[self.sorting_option]
        else: self.select_sorting_option = 't'

    def get_date_range(self):
        years = [x.year for x in self.instances]
        years = [x for x in years if x]
        if years:
            earliest_date = min(years)
            latest_date = max(years)
        else: earliest_date,latest_date = '',''
        self.earliest_date, self.latest_date = earliest_date, latest_date
        self.date_range = {'earliest_date':earliest_date,'latest_date':latest_date}

    def make_var(self):
        if self.query == ' ': self.query = ''
        self.var = {'page_name':self.view_type.replace('_',' '),
            'view_type':self.view_type,
            'instances':self.instances,
            'query':self.query, 
            'nentries':self.nentries,
            'combine':self.combine,
            'direction':self.direction,
            'sorting_icon':self.sorting_icon,
            'exact':self.exact,
            'sorting_option':self.sorting_option,
            self.select_sorting_option:'selected',
            'rating_counts':self.search.rating_counts,
            'country_counts':self.search.country_counts,
            'keyword_category_counts':self.search.keyword_category_counts,
            'model_counts':self.search.model_counts,
            'century_counts':self.search.century_counts,
            'famine_counts':self.search.famine_counts,
            'famine_name_to_detail_view':self.search.famine_name_to_detail_view,
            'id_dict':self.id_dict,
            'filter_active_dict':self.filter_active_dict,
            'us':self.user_search,
            'date_range':self.date_range,
            'earliest_date':self.earliest_date,
            'latest_date':self.latest_date,
            'id_year_range_dict':self.id_year_range_dict,
            'query_terms':query_hints.get_queryterms(),
            'new_search_form':self.new_search_form,
        }

    @property
    def id_dict(self):
        if hasattr(self,'_id_dict'): return self._id_dict
        self._id_dict = {
            'rating':self.search._rating_identifiers,
            'location':self.search._country_identifiers,
            'keyword':self.search._keyword_identifiers,
            'model':self.search._model_identifiers,
            'century':self.search._century_identifiers,
            'famine':self.search._famine_identifiers,
        }
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

    @property
    def id_year_range_dict(self):
        if hasattr(self,'_id_year_range_dict'): return self._id_year_range_dict
        self._id_year_range_dict = {}
        for instance in self.instances:
            year_range =instance.year,instance.year
            self._id_year_range_dict[instance.identifier] = year_range
        return self._id_year_range_dict
        



class UserSearch:
    '''loads information about latest search by a user if available
    the information can be used to reload search view with all the settings
    corresponding to the search
    '''
    def __init__(self,request = None, user = ''):
        self.query = ' '
        self.request = request
        self.wait_for_ready = False
        if request and 'HTTP_REFERER' in self.request.META.keys(): 
            if 'search_view' in request.META['HTTP_REFERER']: 
                self.wait_for_ready = True
        self.time_out = False
        if user: self.user = user
        if request: self.user = request.user.username
        self.directory = 'user_search_requests/' + request.session.session_key+'/'
        self.filename = self.directory + 'search'
        self.dict = None
        self.start = time.time()
        self.wait_attemps = 0
        if self.wait_for_ready: self.wait_for_data()
        if os.path.isfile(self.filename): self.set_info()
        if not self.dict or self.to_old: self.useable = False
        else: self.useable = True
        if self.dict is not None: self.dict['useable'] = self.useable
        if not self.useable or self.nactive_ids == 1 or self.index == None:
            self.iterating_possible = False
        else: self.iterating_possible = True
        print(self)

    def __repr__(self):
        m = 'UserSearch'
        if self.dict:
            m += ' | active ids: ' + str(self.nactive_ids) 
            m += ' | delta time: ' + str(self.delta_time)
            if self.query != ' ':m += ' | query: ' + str(self.query)
            if self.index: m + ' | index: ' + str(self.index)
            m += ' | wait ' + str(self.wait_for_ready)
            if self.wait_for_ready:
                m += ' | attemps ' + str(self.wait_attemps)
                m += ' | time out ' + str(self.time_out)
        m += ' | useable: ' + str(self.useable)
        return m

    def _load_json_search_data(self):
        try: self.dict = json.load(open(self.filename))
        except json.decoder.JSONDecodeError: self.dict = None
        if type(self.dict) != dict:self.dict = None
            

    def set_info(self):
        self._load_json_search_data()
        if not self.dict: return
        for key,value in self.dict.items():
            if key in ['index','number']:continue
            setattr(self,key,value)
        self.nactive_ids = len(self.active_ids)
        self.dict['index'] = self.index
        self.dict['number'] = self.number
        self.dict['nactive_ids'] = self.nactive_ids
        

    def wait_for_data(self):
        if self.ready: 
            os.remove(self.directory + 'ready')
            print('wait attemps:',self.wait_attemps)
        elif time.time() - self.start > 0.9: 
            self.time_out = True
            print('timed out waiting for user search request data')
        else:
            time.sleep(0.05)
            self.wait_attemps += 1
            self.wait_for_data()
        
    @property
    def ready(self):
        return os.path.isfile(self.directory + 'ready')

    @property
    def delta_time(self):
        return int(time.time() - self.time)

    @property
    def to_old(self):
        return self.delta_time > 3600 * 4

    @property
    def index(self):
        if hasattr(self,'current_instance') and self.current_instance in self.active_ids:
            return self.active_ids.index(self.current_instance)
        else: return None

    @property
    def number(self):
        index = self.index
        if index: return index + 1
        return None

    def save(self):
        self.dict['index'] = self.index
        self.dict['number'] = self.number
        self.dict['nactive_ids'] = self.nactive_ids
        with open(self.filename,'w') as fout:
            json.dump(self.dict,fout)

    def set_current_instance(self, identifier):
        if self.identifier_part_of_search_results(identifier):
            self.current_instance = identifier
            self.dict['current_instance'] = identifier
            self.save()
            print('current instance:',identifier, 'saved to file:',self.filename)
        else:
            print(identifier,'not in active_ids doing nothing')

    def identifier_part_of_search_results(self,identifier):
        return hasattr(self,'current_instance') and identifier in self.active_ids

    @property
    def next_instance(self):
        if not self.iterating_possible: return None
        if self.index == self.nactive_ids -1: identifier = self.active_ids[0]
        else: identifier = self.active_ids[self.index+1]
        return identifier2instance(identifier)

    @property
    def previous_instance(self):
        if not self.iterating_possible: return None
        identifier = self.active_ids[self.index-1]
        return identifier2instance(identifier)
        

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

class dummy:
    '''empty dummy object'''
    pass

def make_dummy_request_for_user_search(session_key = '',username = 'mb'):
    '''create a dummy request object for UserSearch to load user search data.'''
    r = dummy()
    r.session = dummy()
    r.user= dummy()
    r.user.username = username
    r.session.session_key = session_key
    r.method = ''
    r.GET = {}
    r.META = {}
    return r


