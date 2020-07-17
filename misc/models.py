from django.db import models
from locations.models import Location
from utilities.models import SimpleModel, expose_m2m
from utils.model_util import info



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

	@property
	def names_str(self):
		return expose_m2m(self,'names','name')

	@property
	def locations_str(self):
		return expose_m2m(self,'locations','name')


		
class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)

	def __str__(self):
		return self.name
		
	
	
# Create your models here.
