from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import Famine, FamineName, CausalTrigger, Keyword
from .models import Language, License

class SimpleBaseWidget(ModelSelect2Widget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name

class SimpleBasesWidget(ModelSelect2MultipleWidget):
	search_fields = ['name__icontains']
	def label_from_instance(self,obj):
		return obj.name


class LicenseWidget(SimpleBaseWidget):
	model = License
	def get_queryset(self):
		return License.objects.all().order_by('name')

class FamineWidget(SimpleBaseWidget):
	model = Famine
	def get_queryset(self):
		return Famine.objects.all().order_by('name')

class FaminesWidget(SimpleBasesWidget):
	model = Famine
	search_fields = ['names__name__icontains']

	def label_from_instance(self,obj):
		#return ', '.join([n.name for n in obj.names.all()])
		return obj.names_str

	def get_queryset(self):
		return Famine.objects.all()


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


class KeywordWidget(SimpleBaseWidget):
	model = Keyword
	
	def label_from_instance(self,obj):
		relations = obj.contained.all()
		if relations:
			return obj.name + ' | ' + ', '.join([r.container.name for r in relations])
		else: return obj.name

	def get_queryset(self):
		return Keyword.objects.all().order_by('name')


class KeywordsWidget(SimpleBasesWidget):
	model = Keyword
	
	def label_from_instance(self,obj):
		relations = obj.contained.all()
		if relations:
			return obj.name + ' | ' + ', '.join([r.container.name for r in relations])
		else: return obj.name

	def get_queryset(self):
		return Keyword.objects.all().order_by('name')


class CategoryKeywordWidget(SimpleBaseWidget):
	model = Keyword
	
	def label_from_instance(self,obj):
		relations = obj.container.all().order_by('contained__name')
		if relations:
			return obj.name + ' | ' + ', '.join([r.contained.name for r in relations[:3]]) + ', ...'
		else: return obj.name

	def get_queryset(self):
		return Keyword.objects.filter(contained__isnull=True).order_by('name')


class LanguagesWidget(SimpleBasesWidget):
	model = Language
	def get_queryset(self):
		return Language.objects.all().order_by('name')

