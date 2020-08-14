from django.db import models
from locations.models import Location
from utilities.models import SimpleModel, expose_m2m
from utils.model_util import info
from utils.map_util import instance2related_locations, field2locations
from utilities.models import instance2name, instance2color, instance2icon, instance2map_buttons



def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'CausalTrigger,FamineName,Keyword'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Famine(models.Model, info):
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	names = models.ManyToManyField(FamineName, blank=True)
	start_year= 1
	end_year= 1
	locations= models.ManyToManyField(Location,blank=True,related_name='famine_locations')
	estimated_excess_mortality = models.IntegerField(blank=True,null=True)
	causal_triggers = models.ManyToManyField(CausalTrigger, blank=True,
		related_name='famine_causal_triggers')
	description = models.TextField(default='')
	comments = models.TextField(default='')
	keywords= models.ManyToManyField(Keyword,blank=True)
	location_field = 'locations'
	thumbnail = models.ImageField(upload_to='media/',blank=True,null=True)

	def __str__(self):
		return self.names_str

	@property
	def names_str(self):
		return expose_m2m(self,'names','name')

	@property
	def locations_str(self):
		return expose_m2m(self,'locations','name')

	@property
	def latlng(self):
		if self.location_field:
			locations = field2locations(self,self.location_field)
			return [location.gps for location in locations]
		else: return None


	@property
	def pop_up(self):
		m = ''
		if self.thumbnail.name:
			m += '<img src="'+self.thumbnail.url+'" width="200" style="border-radius:3%">'
		m += instance2icon(self)
		m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(self)+';">'
		m += self.names_str+'</p>'
		m += '<hr class="mt-1 mb-0" style="border:1px solid '+instance2color(self)+';">'
		m += '<p class="mt-2 mb-0">'+self.description+'</p>'

		m += instance2map_buttons(self)
		return m
		
class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)

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
		it needed the string representation of this model, while the Location instance
		did not exist anymore '''
		try:return self.contained.name + ' is a member of: ' + self.container.name
		except:return ''

	class Meta:
		unique_together = ('container','contained')
	
# Create your models here.
