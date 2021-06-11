from django import forms
from django.forms import ModelForm, inlineformset_factory
from django_select2.forms import ModelSelect2Widget
from .models import Protocol



def make_select2_attr(field_name = 'name', input_length = 2):
	attr= {'attrs':{'data-placeholder':'Select by '+field_name+' ...',
	'style':'width:100%','class':'searching','data-minimum-input-length':str(input_length)}}
	return attr



'''
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext_required = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),'required':True}
class ProtocolForm(ModelForm):
	model_name= forms.CharField(**dchar_required)
	field_name= forms.CharField(**dchar_required)
	explanation= forms.CharField(**dtext_required)

	class Meta:
		model = Protocol
		fields = ['field_name','explanation']
'''
