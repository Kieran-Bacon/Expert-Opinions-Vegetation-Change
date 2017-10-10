from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='blank', renderer="templates/base.html")
def blank(request):
	# Returns the base template page.
    return {"title":"Blank Page", "name":"Kieran"}
