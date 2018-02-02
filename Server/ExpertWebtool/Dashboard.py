from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from . import Helper
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="index", renderer="templates/dashboard_main.html")
@view_config(route_name="dashboardMain", renderer="templates/dashboard_main.html")
def dashboardMain(request):
	return Helper.generatePageVariables(request, {"title":"Dashboard"})

@view_config(route_name="userProfile", renderer="templates/dashboard_profile.html")
def userProfile(request):
    Helper.permissions(request)
    return Helper.generatePageVariables(request, {"title":"Profile"})