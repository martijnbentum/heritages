from django.db import models
from utilities.models import SimpleModel
from utils.model_util import info
from misc.models import Keyword, Famine
from locations.models import Location
from utils.map_util import instance2related_locations, field2locations
from utilities.models import instance2name, instance2color, instance2map_buttons
from partial_date import PartialDateField


def make_simple_model(name):
	exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'Gender,Nationality,Occupation,Affiliation'
names = names.split(',')

for name in names:
	make_simple_model(name)

class Person(models.Model, info):
	dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
	name = models.CharField(max_length=1000,default='')
	pseudonyms = models.CharField(max_length=1000,default='')
	pseudonym_precedent= models.BooleanField(default = False)
	gender= models.ForeignKey(Gender,**dargs)
	nationality = models.ForeignKey(Nationality,**dargs)
	date_of_birth= PartialDateField(null=True,blank=True)
	date_of_death= PartialDateField(null=True,blank=True)
	location_of_birth = models.ForeignKey(Location, **dargs, 
		related_name='person_location_of_birth')
	location_of_death = models.ForeignKey(Location, **dargs, 
		related_name='person_location_of_death')
	occupation = models.ManyToManyField(Occupation, blank=True)
	affiliation = models.ForeignKey(Affiliation, **dargs)
	biography_link = models.CharField(max_length=3000,default='')
	comments = models.TextField(default='')
	description= models.TextField(default='')
	keywords= models.ManyToManyField(Keyword,blank=True)
	location_field = 'location_of_birth'
	flag = models.BooleanField(default = False)
	thumbnail = models.ImageField(upload_to='thumbnail/',blank=True,null=True)
	viaf = models.CharField(max_length=1000,default='')
	famines = models.ManyToManyField(Famine, blank=True)
	country_field = models.CharField(max_length=1000,default='')

	def __str__(self):
		return self.name

	@property
	def icon(self):
		return 'fas fa-user'

	@property
	def title(self): #helper property to display name in overviews
		if self.pseudonym_precedent and self.pseudonyms: return self.pseudonyms
		if not self.name and self.pseudonyms: return self.pseudonyms
		return self.name

	@property
	def occupations_str(self):
		return ', '.join([o.name for o in self.occupation.all()])

	@property
	def latlng(self):
		if self.location_field:
			locations = field2locations(self,self.location_field)
			if locations:return [location.gps for location in locations]
		return None

	@property
	def pop_up(self):
		if self.gender and self.gender.name == 'female':
			m = '<i class="fa fa-female fa-lg" aria-hidden="true"></i>'
		else:
			m = '<i class="fa fa-male fa-lg" aria-hidden="true"></i>'
		m += '<p class="h6 mb-0" style="color:'+instance2color(self)
		m += ';">'+self.name+'</p>'
		m += '<hr class="mt-1 mb-0" style="border:1px solid '
		m += instance2color(self)+';">'
		if self.occupation:
			m += '<p class="mt-2 mb-0">'+self.occupations_str+'</p>'
		m += instance2map_buttons(self)
		return m

	class Meta:
		unique_together = [['name','date_of_birth']]

	@property
	def edit_url(self):
		return self._meta.app_label + ':edit_' + self._meta.model_name 
	
	@property
	def identifier(self):
		m = self._meta.app_label + '_' + self._meta.model_name + '_'  
		m += str( self.pk )

	@property
	def age(self):
		try: 
			m=self.date_of_death.start_dt.year-self.date_of_birth.start_dt.year
			return m
		except:return ''

	@property
	def date(self):
		m = ''
		if self.date_of_birth:m += str(self.date_of_birth)
		if self.date_of_death:m += ' - ' + str(self.date_of_death)
		age = str(self.age)
		if age: m += ' (' + age + ')'
		return m
	
	@property
	def famine_names(self):
		famines= self.famines.all() 
		if famines: return ', '.join([f.names_str for f in famines])
		else: return ''
		
		
