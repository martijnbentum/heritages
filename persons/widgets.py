from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Person,Gender,Nationality,Occupation,Affiliation

class SimpleBaseWidget(ModelSelect2Widget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class SimpleBasesWidget(ModelSelect2MultipleWidget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name



class PersonWidget(SimpleBaseWidget):
	search_fields = ['name__icontains','pseudonyms__icontains']
	model = Person

	def label_from_instance(self,obj):
		m = obj.name
		if obj.pseudonyms:
			m += ' | ' + obj.pseudonyms
		return m

	def get_queryset(self):
		return Person.objects.all().order_by('name')

class PersonsWidget(SimpleBasesWidget):
	search_fields = ['name__icontains','pseudonyms__icontains']
	model = Person

	def label_from_instance(self,obj):
		m = obj.name
		if obj.pseudonyms:
			m += ' | ' + obj.pseudonyms
		return m

	def get_queryset(self):
		return Person.objects.all().order_by('name')


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

class OccupationsWidget(SimpleBasesWidget):
	model = Occupation
	def get_queryset(self):
		return Occupation.objects.all().order_by('name')



