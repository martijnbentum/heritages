from django import forms
from django.forms import ModelForm, formset_factory
from django_select2.forms import ModelSelect2Widget
from .models import Protocol



def make_select2_attr(field_name = 'name', input_length = 2):
	attr= {'attrs':{'data-placeholder':'Select by '+field_name+' ...',
	'style':'width:100%','class':'searching','data-minimum-input-length':str(input_length)}}
	return attr



dattr = {'attrs':{'style':'width:95%'}}
dchar= {'widget':forms.TextInput(**dattr),'required':False}
dtext= {'widget':forms.Textarea(
	attrs={'style':'width:100%; font-size:80%','rows':6}),'required':False}

class ProtocolForm(ModelForm):
	model_name= forms.CharField(**dchar)
	field_name= forms.CharField(**dchar)
	explanation= forms.CharField(**dtext)

	class Meta:
		model = Protocol
		fields = ['field_name','explanation']

