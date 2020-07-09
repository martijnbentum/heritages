from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Person,Gender,Nationality,Occupation,Affiliation,Location,Keyword
from .models import Location 

class SimpleBaseWidget(ModelSelect2Widget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class SimpleBasesWidget(ModelSelect2MultipleWidget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name


class LocationsWidget(SimpleBasesWidget):
	model = Location
	def get_queryset(self):
		return Location.objects.all().order_by('name')

class LocationWidget(SimpleBaseWidget):
	model = Location
	def get_queryset(self):
		return Location.objects.all().order_by('name')

class PersonWidget(SimpleBaseWidget):
	model = Person
	def get_queryset(self):
		return Person.objects.all().order_by('name')

class PersonsWidget(SimpleBasesWidget):
	model = Person
	def get_queryset(self):
		return Person.objects.all().order_by('name')

class KeywordsWidget(SimpleBasesWidget):
	model = Keyword
	def get_queryset(self):
		return Keyword.objects.all().order_by('name')

class GenderWidget(SimpleBaseWidget):
	model = Gender
	def get_queryset(self):
		return Gender.objects.all().order_by('name')

class NationalityWidget(SimpleBaseWidget):
	model = Nationality
	def get_queryset(self):
		return Nationality.objects.all().order_by('name')

class AffiliationWidget(SimpleBaseWidget):
	model = Affiliation
	def get_queryset(self):
		return Affiliation.objects.all().order_by('name')

class OccupationWidget(SimpleBaseWidget):
	model = Occupation
	def get_queryset(self):
		return Occupation.objects.all().order_by('name')


