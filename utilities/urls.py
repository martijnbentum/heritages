from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
search_path_complete ='search_view/<str:view_type>/'
search_path_complete +='<str:query>/<str:combine>/<str:exact>/<str:direction>/'
search_path_complete +='<str:sorting_option>/'

urlpatterns = [
	path('close/',views.close,name='close'),
    path('add_info/',views.add_info,name='add_info'),
	path('list_view/<str:model_name>/<str:app_name>/',
		views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<int:max_entries>/',
		views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<str:html_name>/',
		views.list_view,name='list_view'),
	path('list_view_general/<str:model_name>/<str:app_name>/<str:field_names>/',
		views.list_view,name='list_view_general'),
	path('sidebar/',views.sidebar,name='sidebar'),
	path('search_view',views.search_view,name='search_view'),
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
	path('overview/',views.overview,name='overview'),
	path('get_user_search_requests/',views.get_user_search_requests,
		name='get_user_search_requests'),
]
