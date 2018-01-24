from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from .Helper import permissions
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name='personalSettings', renderer="templates/base.html")
def personalSettings(request):
	permissions(request) # Validates user
	# Returns the base template page.
	return { **request.session, **{"title":"Personal Settings"}}

@view_config(route_name='manageUsers', renderer="templates/settings_manageUsers.html")
def manageUsers(request):
	permissions(request) # Validates user
	# Returns the base template page.
	return { **request.session, **{"title":"Manage Users"}}