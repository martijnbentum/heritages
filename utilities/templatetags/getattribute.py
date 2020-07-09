from django import template
from django.conf import settings

register = template.Library()

def getattribute(instance, attr_name):
	if hasattr(instance, attr_name):
		return getattr(instance, attr_name)
	return settings.TEMPLATE_STRING_IF_INVALID

register.filter('getattribute',getattribute)
