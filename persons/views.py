from django.shortcuts import render
from .forms import PersonForm,GenderForm,NationalityForm,OccupationForm
from .forms import AffiliationForm,LocationForm,KeywordForm
from utilities.views import edit_model, add_simple_model, list_view, delete_model



'''
def add_Gender(request):
	return add_simple_model(request,__name__,'Gender','persons','add gender')
'''

def create_simple_view(name):
	'''Create a simple view based on the Model name. 
	Assumes the form only has a name field.
	'''
	c = 'def add_'+name.lower()+'(request):\n'
	c += '\treturn add_simple_model(request,__name__,"'+name+'","persons","add '+name+'")'
	return exec(c,globals())

#create simple views for the following models
names = 'Gender,Nationality,Occupation,Affiliation,Location,Keyword'
for name in names.split(','):
	create_simple_view(name)



def edit_person(request,pk=None,focus='',view='complete'):
	return edit_model(request,__name__,'Person','persons',pk,focus=focus,view=view)


'''
def add_location(request):
	return add_simple_model(request,__name__,'Location','sources','add location')

def add_keyword(request):
	return add_simple_model(request,__name__,'Keyword','sources','add keyword')
'''

def delete(request, pk, model_name):
	return delete_model(request, __name__, model_name,'persons',pk)

# Create your views here.
