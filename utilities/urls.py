from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
search_path_complete ='search_view/<str:view_type>/'
search_path_complete +='<str:query>/<str:combine>/<str:exact>/<str:direction>/'

urlpatterns = [
	path('close/',views.close,name='close'),
	path('list_view/<str:model_name>/<str:app_name>/',
		views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<int:max_entries>/',
		views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<str:html_name>/',
		views.list_view,name='list_view'),
	path('list_view_general/<str:model_name>/<str:app_name>/<str:field_names>/',
		views.list_view,name='list_view_general'),
	path('sidebar/',views.sidebar,name='sidebar'),
	path('row_view/',views.row_view,name='row_view'),
	path('row_view/<str:query>',views.row_view,name='row_view'),
	path('tile_view/',views.tile_view,name='tile_view'),
	path('tile_view/<str:query>',views.tile_view,name='tile_view'),
	path('search_view/<str:view_type>/',
		views.search_view,name='search_view'),
	path('search_view/<str:view_type>/<str:query>/',
		views.search_view,name='search_view'),
	path(search_path_complete,views.search_view,name='search_view'),
	path('ajax_instance_info/<str:identifier>/',views.ajax_instance_info, 
		name='ajax_instance_info'),
	path('ajax_instance_info/<str:identifier>/<str:fields>/',
		views.ajax_instance_info, name='ajax_instance_info'),
	path('add_protocol/<str:app_name>/<str:model_name>',
		views.edit_protocol,name='add_protocol'),
]
