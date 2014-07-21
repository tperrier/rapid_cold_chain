#!/usr/bin/python
from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):

	dict_ = request.GET.copy()

	dict_[field] = value

	return dict_.urlencode()

@register.simple_tag
def url_param_is(request,param,value):
	return request.GET.get(param,None) == value
