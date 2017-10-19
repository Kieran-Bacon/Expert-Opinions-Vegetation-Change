from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from .DatabaseHandler import DatabaseHandler as db
import hashlib, uuid
import sqlite3


@view_config(route_name='blank', renderer="templates/base.html")
def blank(request):
	# Returns the base template page.
    return {"title":"Blank Page", "name":"Kieran"}

@view_defaults(route_name="login", renderer="templates/login.html")
class LoginHandler:

	def __init__(self, request):
		self.request = request

	@view_config(route_name="login")
	def loginGET(self):
		return {}

	@view_config(route_name="loggingIn", request_method='POST')
	def loginPOST(self):
		username = self.request.params.get('username', None)
		password = self.request.params.get('password', None)

		if username is None or password is None:
			return {"alert":"Invalid user information entered."}

		salt, storedPassword = db.execute("User_Password",[username])[0]

		password = hashlib.sha512((salt+password).encode("UTF-8")).hexdigest()

		if password == storedPassword:

			# Collect relevant user information
			user = db.execute("User_Info", [username])[0]

			# Store the information as session variables.
			self.request.session["status"] = 1
			self.request.session["username"] = username
			self.request.session["firstname"] = user["firstname"]
			self.request.session["lastname"] = user["lastname"]

			# Redirect the client to the new page
			raise exc.HTTPFound(self.request.route_url("blank"))

		return {"alert":"Invalid user information entered."}

@view_config(route_name="logout")
def logout(request):
	# Removed session information and

	# TODO: Remove session information is some form

	return exc.HTTPFound(request.route_url("login.html"))
