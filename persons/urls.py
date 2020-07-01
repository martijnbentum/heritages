from django.urls import path

from . import views

app_name = 'persons'
urlpatterns = [
	path('',views.edit_person, name='index'),
	path('add_person/',views.edit_person, name='add_person'),
	path('add_gender/',views.add_gender, name='add_gender'),
	path('add_nationality/',views.add_nationality, name='add_nationality'),
	path('add_occupation/',views.add_occupation, name='add_occupation'),
	path('add_affiliation/',views.add_affiliation, name='add_affiliation'),
]
