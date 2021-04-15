from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
urlpatterns = [
	path('close/',views.close,name='close'),
	path('list_view/<str:model_name>/<str:app_name>/',views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<int:max_entries>/',views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<str:html_name>/',views.list_view,name='list_view'),
	path('list_view_general/<str:model_name>/<str:app_name>/<str:field_names>/',views.list_view,name='list_view_general'),
	path('row_view/<str:model_name>/<str:app_name>/',views.row_view,name='row_view'),
]
