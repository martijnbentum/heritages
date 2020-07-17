from django.db import models
from utilities.models import SimpleModel
from utils.model_util import info


def make_simple_model(name):
	exec('class '+name + '(SimpleModel):\n\tpass',globals())

names = 'Gender,Nationality,Occupation,Affiliation,Location,Keyword'
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
