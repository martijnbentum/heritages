from django.db import models
from locations.models import Location
from utilities.models import SimpleModel, expose_m2m
from utils.model_util import info
from utils.map_util import instance2related_locations, field2locations
from utilities.models import instance2name, instance2color 
from utilities.models import instance2icon, instance2map_buttons
from utils.instance2countries import instance2countries



def make_simple_model(name):
    exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'CausalTrigger,FamineName'
names = names.split(',')

for name in names:
    make_simple_model(name)

class License(models.Model, info):
    name = models.CharField(max_length=300,default='',unique=True)
    url= models.CharField(max_length=1000, default = '')
    description = models.TextField(default='')
    comments = models.TextField(default='')

    def __str__(self):
        return self.name

class Keyword(models.Model, info):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    name = models.CharField(max_length=300,default='',unique=True)
    description = models.TextField(default='')
    comments = models.TextField(default='')
    category = models.CharField(max_length=300,default='')
    category_relations= models.CharField(max_length=300,default='')

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        super(Keyword,self).save(*args,**kwargs)
        old_category = self.category
        self.category = self._category
        old_relations= self.category_relations
        self.category_relations= self._category_relations_str
        if old_category != self.category or old_relations != self.category_relations:
            super(Keyword,self).save(*args,**kwargs)
        

    @property
    def category_keyword(self):
        relations = self.container.all()
        return bool(relations)

    @property
    def _category(self):
        relations = self.container.all()
        if relations:return relations[0].container.name
        relations = self.contained.all()
        if relations:return relations[0].container.name
        return ''

    @property
    def category_relations_instances(self):
        relations = self.container.all()
        return [r.contained for r in relations]

    @property
    def _category_relations_str(self):
        return ' | '.join([x.name for x in self.category_relations_instances])

class Famine(models.Model, info):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    filter_name = models.CharField(max_length=1000,default='')
    filter_location_name = models.CharField(max_length=1000,default='')
    names = models.ManyToManyField(FamineName, blank=True)
    start_year= 1
    end_year= 1
    locations= models.ManyToManyField(Location,blank=True,
        related_name='famine_locations')
    estimated_excess_mortality = models.IntegerField(blank=True,null=True)
    excess_mortality_description = models.TextField(default='')
    causal_triggers = models.ManyToManyField(CausalTrigger, blank=True,
        related_name='famine_causal_triggers')
    description = models.TextField(default='')
    comments = models.TextField(default='')
    keywords= models.ManyToManyField(Keyword,blank=True)
    location_field = 'locations'
    thumbnail = models.ImageField(upload_to='media/',blank=True,null=True)
    country_field = models.CharField(max_length=1000,default='')
    loc_ids = models.CharField(max_length=1000,default='')

    def __str__(self):
        return self.names_str

    def save(self,*args,**kwargs):
        super(Famine,self).save(*args,**kwargs)
        old_country_field = self.country_field
        self.country_field = instance2countries(self)
        old_loc_ids = self.loc_ids
        self._set_gps()
        new_loc_ids = old_loc_ids != self.loc_ids
        new_country = old_country_field != self.country_field
        new = [new_loc_ids, new_country]
        if sum(new) > 0: 
            super(Famine,self).save(*args,**kwargs)

    def _set_gps(self):
        self.loc_ids = ''
        ids = [location.pk for location in self.locations.all()]
        if ids: self.loc_ids = ','.join(map(str,ids))
    

    def identifier(self):
        return self._meta.app_label+'_'+self._meta.model_name+'_'+str( self.pk )

    @property
    def names_str(self):
        return expose_m2m(self,'names','name').replace(',',', ')

    @property
    def locations_str(self):
        return expose_m2m(self,'locations','name')

    @property
    def location_list(self):
        return list(self.locations.all())

    @property
    def causal_trigger_list(self):
        return list(self.causal_triggers.all())

    @property
    def latlng(self):
        if self.location_field:
            locations = field2locations(self,self.location_field)
            return [location.gps for location in locations]
        else: return None

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name 

    @property
    def detail_url(self):
        return self._meta.app_label + ':detail_' + self._meta.model_name +'_view'

    @property
    def keyword_names(self):
        keywords= self.keywords.all().order_by('name') 
        if keywords: return ', '.join([k.name for k in keywords])
        else: return ''

    @property
    def pop_up(self):
        m = ''
        if self.thumbnail.name:
            m += '<img src="'+self.thumbnail.url
            m +='" width="200" style="border-radius:3%">'
        m += instance2icon(self)
        m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(self)+';">'
        m += self.names_str+'</p>'
        m += '<hr class="mt-1 mb-0" style="border:1px solid '
        m +=instance2color(self)+';">'
        m += '<p class="mt-2 mb-0">'+self.description+'</p>'

        m += instance2map_buttons(self)
        return m
        
class Language(models.Model, info):
    name = models.CharField(max_length=100, unique = True)
    iso = models.CharField(max_length=3,null=True,blank=True)
    endnode = True

    def __str__(self):
        return self.name
        
    

class KeywordRelation(models.Model, info):
    '''defines a hierarchy of keywords, e.g. women is a member of people.'''
    container = models.ForeignKey('Keyword', related_name='container',
                                    on_delete=models.CASCADE, default=None)
    contained = models.ForeignKey('Keyword', related_name='contained',
                                    on_delete=models.CASCADE, default=None)

    def __str__(self):
        '''deleting a Location can resultin an error due to the easy audit app.
        it needed the string representation of this model, 
        while the Location instance
        did not exist anymore '''
        try:
            m = self.contained.name + ' is a member of: ' + self.container.name
            return m
        except:return ''

    class Meta:
        unique_together = ('container','contained')


    def save(self,*args,**kwargs):
        super(KeywordRelation,self).save(*args,**kwargs)
        self.container.save()
        self.contained.save()
    
# Create your models here.
