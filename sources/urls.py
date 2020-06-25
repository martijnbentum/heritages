from django.urls import path

from . import views

app_name = 'sources'
urlpatterns = [
	path('',views.index, name='index'),
	path('add_film/',views.edit_film, name='add_film'),
	path('add_text/',views.edit_text, name='add_text'),
	path('add_music/',views.edit_music, name='add_music'),
	path('add_infographic/',views.edit_infographic, name='add_infographic'),
	path('add_image/',views.edit_image, name='add_image'),
	path('add_picture_story/',views.edit_picture_story, name='add_picture_story'),
	path('add_picture_story_type/',views.add_picture_story_type, name='add_picture_story_type'),
	path('add_image_type/',views.add_image_type, name='add_image_type'),
	path('add_text_type/',views.add_text_type, name='add_text_type'),
	path('add_music_type/',views.add_music_type, name='add_music_type'),
	path('add_film_type/',views.add_film_type, name='add_film_type'),
	path('add_infographic_type/',views.add_infographic_type, name='add_infographic_type'),
	path('add_film_company/',views.add_film_company, name='add_film_company'),
	path('add_publisher/',views.add_publisher, name='add_publisher'),
	path('add_location/',views.add_location, name='add_location'),
	path('add_person/',views.add_person, name='add_person'),
	path('add_target_audience/',views.add_target_audience, name='add_target_audience'),
	path('add_language/',views.add_language, name='add_language'),
	path('add_famine/',views.add_famine, name='add_famine'),
	path('add_keyword/',views.add_keyword, name='add_keyword'),
	path('add_collection/',views.add_collection, name='add_collection'),
	path('music_list/',views.music_list, name='music_list'),
]
