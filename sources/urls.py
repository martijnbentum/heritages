from django.urls import path

from . import views

app_name = 'sources'
urlpatterns = [
	path('',views.index, name='index'),
	path('add_film/',views.edit_film, name='add_film'),
	path('add_film_type/',views.add_film_type, name='add_film_type'),
	path('add_film_company/',views.add_film_type, name='add_film_company'),
	path('add_location/',views.add_location, name='add_location'),
	path('add_music/',views.edit_music, name='add_music'),
	path('add_music_type/',views.add_music_type, name='add_music_type'),
	path('add_person/',views.add_person, name='add_person'),
	path('add_target_audience/',views.add_target_audience, name='add_target_audience'),
	path('add_language/',views.add_language, name='add_language'),
	path('add_famine/',views.add_famine, name='add_famine'),
	path('add_keyword/',views.add_keyword, name='add_keyword'),
	path('add_collection/',views.add_collection, name='add_collection'),
	path('music_list/',views.music_list, name='music_list'),
]
