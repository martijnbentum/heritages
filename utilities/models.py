from django.apps import apps
from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info, instance2names,instance2name

class SimpleModel(models.Model):
    name = models.CharField(max_length=300,default='',unique=True)
    endnode = True

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name

    class Meta:
        abstract=True

class generic(models.Model):
    pass

class Protocol(models.Model, info):
    app_name = models.CharField(max_length=300,default='')
    model_name = models.CharField(max_length=300,default='')
    field_name = models.CharField(max_length=300,default='')
    explanation = models.TextField(default='')

    class Meta:
        unique_together = [['model_name','field_name']]

    def __str__(self):
        return self.app_name + ' ' + self.model_name + ' ' + self.field_name

class SearchViewHelper(models.Model, info):
    '''
    self.start = time.time()
    self.request = request
    self.user_search = UserSearch(request)
    self.view_type = view_type
    self.query = query
    self.combine = combine
    self.exact = exact
    self.direction = direction
    self.sorting_option = sorting_option
    self.special_terms = [self.combine,self.exact]
    '''

class UserSearch(models.Model, info):
    session_key = models.CharField(max_length = 60, default = '',unique = True) 
    time = models.FloatField(null=True, blank=True)
    active_ids = models.TextField(default = '')
    filters = models.TextField(default = '')
    date_start = models.PositiveIntegerField(null=True,blank=True)
    date_end = models.PositiveIntegerField(null=True,blank=True)
    query = models.CharField(max_length = 300, default = '')
    sorting_direction = models.CharField(max_length = 100, default = '')
    sorting_category= models.CharField(max_length = 100, default = '')
    current_instance = models.CharField(max_length = 100, default = '')
    view_type= models.CharField(max_length = 100, default = '')
    filter_active_dict = models.TextField(default = '')
    new_query = models.BooleanField(default=False)
    index = models.PositiveIntegerField(null = True, blank = True)
    number = models.PositiveIntegerField(null = True, blank = True)
    nactive_ids= models.PositiveIntegerField(null = True, blank = True)
    usable= models.BooleanField(default=False)

    def update(self, request):
        if self.session_key != request.session.session_key:
            print(request.session.session_key, self.session_key,'different!')
            return
        self.time = time.time()
        active_ids = 1

    def set_current_instance(self, identifier):
        if self.identifier_part_of_search_results(identifier):
            self.current_instance = identifier
            self.save()
            print('current instance:',identifier, 'saved to file:',self.filename)
        else:
            print(identifier,'not in active_ids doing nothing')

    def set_active_ids(self, active_ids):
        self.active_ids = ','.join(active_ids)
        self.save()

    @property
    def get_active_ids(self):
        if active_ids: return active_ids.split(',')
        return []

           
    '''
    self.request = request
    self.wait_for_ready = False
    if request and 'HTTP_REFERER' in self.request.META.keys(): 
        if 'search_view' in request.META['HTTP_REFERER']: self.wait_for_ready
    self.time_out = False
    if user: self.user = user
    if request: self.user = request.user.username
    self.directory = 'user_search_requests/' + self.user +'/'
    self.filename = self.directory + 'search'
    self.dict = None
    self.start = time.time()
    self.wait_attemps = 0
    if self.wait_for_ready: self.wait_for_data()
    if os.path.isfile(self.filename): self.set_info()
    if not self.dict or self.to_old or self.index == None: self.useable = False
    else: self.useable = True
    if self.dict is not None: self.dict['useable'] = self.useable
    if not self.useable or self.nactive_ids == 1 or self.index == None:
        self.iterating_possible = False
    else: self.iterating_possible = True
    '''




def expose_m2m(instance, field_name,attr):
    ''' return a comma seperated string of attr from m2m linked model. '''
    n = []
    m2m= getattr(instance,field_name)
    for item in m2m.all():
        n.append(getattr(item,attr))
    return ','.join(n)


def instance2color(instance):
    name = instance2name(instance).lower()
    if name in color_dict.keys(): return color_dict[name]
    else: return 'black'

def instance2icon(instance):
    '''
    name = instance2name(instance).lower()
    if name in icon_dict.keys(): 
        return icon_dict[name]
    return 'not found'
    '''
    if not hasattr(instance,'icon'):return ''
    return '<i class="'+instance.icon+' fa-lg mt-2" aria-hidden="true"></i>' 

def instance2map_buttons(instance):
    app_name,model_name= instance2names(instance)
    m = ''
    m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
    m += '/'+app_name+'/edit_' + model_name.lower()+'/' + str(instance.pk) +'/'
    m += ' role="button"><i class="far fa-edit"></i></a>'
    m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href='
    m += '/locations/show_links/'+app_name+'/'+ model_name.lower()+'/' + str(instance.pk) +'/'
    m += ' role="button"><i class="fas fa-project-diagram"></i></a>'
    return m


names = 'text,picturestory,dot,image,infographic,famine,film,artefact,memorialsite,recordedspeech,videogame'.split(',');
colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817,#eb4034,#ebbd34'.split(',')
#names = 'text,picturestory,dot,image,infographic,famine,film,music,person'.split(',');
#colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817'.split(',')
# icons ='fa fa-book,fa fa-star,fa fa-circle,fa fa-picture-o'
# icons +=',fa fa-bar-chart,fas fa-exclamation,fa fa-video-camera,fa fa-music,fa fa-male'
# icons = ['<i class="'+icon+' fa-lg mt-2" aria-hidden="true"></i>' for icon in icons.split(',')]
color_dict={}
for i,name in enumerate(names):
    color_dict[name] = colors[i]

