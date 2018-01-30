from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from ExpertRep import ExpertModelAPI

from . import Helper
from .Helper import permissions
from .DatabaseHandler import DatabaseHandler as db
import hashlib, uuid
import sqlite3

@view_config(route_name='blank', renderer="templates/base.html")
def blank(request):
	permissions(request) # Validates user
	# Returns the base template page.
	return { **request.session, **{"title":"Blank Page"}}

@view_defaults(route_name="login", renderer="templates/login.html")
class LoginHandler:
	"""
	Class to aggregate the interactions of logging into a user account
	"""

	def __init__(self, request):
		self.request = request

	@view_config(route_name="login")
	def loginGET(self):
		return Helper.generatePageVariables(self.request)

	@view_config(route_name="loggingIn", request_method='POST')
	def loginPOST(self):

		# Collect the posted information from the login form
		username = self.request.params.get('username', None)
		password = self.request.params.get('password', None)

		# Ensure both pieces of information are present
		if username is None or password is None:
			self.request.session["alerts"] = [{"type":"error", "text":"The information provided is invalid.", "title":"Ow no, unable to log in!"}]
			return exc.HTTPFound(self.request.route_url("login"))

		# Collect from the database the salt and password for the user
		try:
			salt, storedPassword = db.executeOne("User_Password",[username])
		except:
			self.request.session["username"] = username
			self.request.session["alerts"] = [{"type":"error", "text":"The information provided is invalid.", "title":"Ow no, unable to log in!"}]
			return exc.HTTPFound(self.request.route_url("login"))

		password = hashlib.sha512((salt+password).encode("UTF-8")).hexdigest()
		if password == storedPassword:

			# Collect relevant user information
			user = db.executeOne("User_Info", [username])

			# Store the information as session variables.
			self.request.session["status"] = 1
			self.request.session["username"] = username
			self.request.session["firstname"] = user["firstname"]
			self.request.session["lastname"] = user["lastname"]
			self.request.session["avatar"] = user["avatar"]
			self.request.session["alerts"] = []

			# Redirect the client to the new page
			raise exc.HTTPFound(self.request.route_url("blank"))

		self.request.session["username"] = username
		self.request.session["alerts"] = [{"type":"error", "text":"The information provided is invalid.", "title":"Ow no, unable to log in!"}]
		return exc.HTTPFound(self.request.route_url("login"))

@view_config(route_name="logout")
def logout(request):
	# TODO: Delete the redundant session information
	request.session.invalidate()
	return exc.HTTPFound(request.route_url("login"))