from django.urls import path

from . import views

app_name = 'misc'
urlpatterns = [
	path('',views.edit_famine, name='index'),
	path('add_famine/',views.edit_famine, name='add_famine'),
	path('add_famine/<str:view>',views.edit_famine, name='add_famine'),
	path('edit_famine/<int:pk>/',views.edit_famine, name='edit_famine'),
	path('edit_famine/<int:pk>/<str:focus>/',views.edit_famine, name='edit_famine'),
	path('edit_keyword/<int:pk>/',views.edit_keyword, name='edit_keyword'),
	path('edit_keyword/<int:pk>/<str:focus>/',views.edit_keyword, name='edit_keyword'),
	path('add_faminename/',views.add_faminename, name='add_faminename'),
	path('add_faminename/<int:pk>',views.add_faminename, name='add_faminename'),
	path('add_causaltrigger/',views.add_causaltrigger, name='add_causaltrigger'),
	path('add_causaltrigger/<int:pk>',views.add_causaltrigger, name='add_causaltrigger'),
	path('add_famine_name/',views.add_faminename, name='add_famine_name'),
	path('add_famine_name/<int:pk>',views.add_faminename, name='add_famine_name'),
	path('add_causal_trigger/',views.add_causaltrigger, name='add_causal_trigger'),
	path('add_causal_trigger/<int:pk>',views.add_causaltrigger, name='add_causal_trigger'),
	path('add_language/',views.add_language, name='add_language'),
	path('add_language/<int:pk>',views.add_language, name='add_language'),
	path('add_keyword/',views.edit_keyword, name='add_keyword'),
	path('add_keyword/<str:view>',views.edit_keyword, name='add_keyword'),
	path('delete/<int:pk>/<str:model_name>',views.delete,name='delete'),
]

