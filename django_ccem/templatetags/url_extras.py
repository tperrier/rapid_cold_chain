#!/usr/bin/python
from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):

	params = request.GET.copy()

	params[field] = value
	
	return params.urlencode()
