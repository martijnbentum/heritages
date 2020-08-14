from django.db import models
from utilities.models import SimpleModel
from utils.model_util import info
from misc.models import Keyword
from locations.models import Location
from utils.map_util import instance2related_locations, field2locations
from utilities.models import instance2name, instance2color, instance2map_buttons


def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'Gender,Nationality,Occupation,Affiliation'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Person(models.Model, info):
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	name = models.CharField(max_length=1000,default='')
	gender= models.ForeignKey(Gender,**dargs)
	nationality = models.ForeignKey(Nationality,**dargs)
	date_of_birth = 1
	date_of_death = 1
	location_of_birth = models.ForeignKey(Location, **dargs, related_name='person_location_of_birth')
	location_of_death = models.ForeignKey(Location, **dargs, related_name='person_location_of_death')
	occupation = models.ForeignKey(Occupation, **dargs)
	affiliation = models.ForeignKey(Affiliation, **dargs)
	biography_link = models.CharField(max_length=3000,default='')
	comments = models.TextField(default='')
	keywords= models.ManyToManyField(Keyword,blank=True)
	location_field = 'location_of_birth'

	def __str__(self):
		return self.name

	@property
	def latlng(self):
		if self.location_field:
			locations = field2locations(self,self.location_field)
			return [location.gps for location in locations]
		else: return None

	@property
	def pop_up(self):
		if self.gender and self.gender.name == 'female':
			m = '<i class="fa fa-female fa-lg" aria-hidden="true"></i>'
		else:
			m = '<i class="fa fa-male fa-lg" aria-hidden="true"></i>'
		m += '<p class="h6 mb-0" style="color:'+instance2color(self)+';">'+self.name+'</p>'
		m += '<hr class="mt-1 mb-0" style="border:1px solid '+instance2color(self)+';">'
		if self.occupation:
			m += '<p class="mt-2 mb-0">'+self.occupation.name+'</p>'
		m += instance2map_buttons(self)
		return m
		
