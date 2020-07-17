from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Famine, FamineName, CausalTrigger, Keyword
from .models import Language

class SimpleBaseWidget(ModelSelect2Widget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class SimpleBasesWidget(ModelSelect2MultipleWidget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name


class FamineWidget(SimpleBaseWidget):
	model = Famine
	def get_queryset(self):
		return Famine.objects.all().order_by('name')

class FaminesWidget(ModelSelect2MultipleWidget):
	model = Famine
	search_fields = ['name__icontains']

	def label_from_instance(self,obj):
		return obj.name

	def get_queryset(self):
		return Famine.objects.all().order_by('names')


class FamineNameWidget(SimpleBaseWidget):
	model = FamineName
	def get_queryset(self):
		return FamineName.objects.all().order_by('name')

class FamineNamesWidget(SimpleBasesWidget):
	model = FamineName
	def get_queryset(self):
		return FamineName.objects.all().order_by('name')

class CausalTriggerWidget(SimpleBaseWidget):
	model = CausalTrigger
	def get_queryset(self):
		return CausalTrigger.objects.all().order_by('name')

class CausalTriggersWidget(SimpleBasesWidget):
	model = CausalTrigger
	def get_queryset(self):
		return CausalTrigger.objects.all().order_by('name')

class KeywordsWidget(SimpleBasesWidget):
	model = Keyword
	def get_queryset(self):
		return Keyword.objects.all().order_by('name')

class LanguagesWidget(SimpleBasesWidget):
	model = Language
	def get_queryset(self):
		return Language.objects.all().order_by('name')
