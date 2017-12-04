from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

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
		return {}

	@view_config(route_name="loggingIn", request_method='POST')
	def loginPOST(self):

		# Collect the posted information from the login form
		username = self.request.params.get('username', None)
		password = self.request.params.get('password', None)

		# Ensure both pieces of information are present
		if username is None or password is None:
			return {"alert":"Invalid user information entered."}

		# Collect from the database the salt and password for the user
		try:
			salt, storedPassword = db.executeOne("User_Password",[username])
		except:
			return {"alert":"Invalid user information entered."}

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

			# Redirect the client to the new page
			raise exc.HTTPFound(self.request.route_url("blank"))

		return {"alert":"Invalid user information entered."}

@view_config(route_name="logout")
def logout(request):
	# TODO: Delete the redundant session information
	request.session["status"] = None
	return exc.HTTPFound(request.route_url("login.html"))

@view_config(route_name="createQuestion", renderer="json")
def createQuestion(request):
    """ Add a parsed question text into the database if it is from a authorised
	user """
    permissions(request)

    questionText = request.params.get("text", None)

    # TODO: Parse/edit the question text
    # Remove starting and trailing white space
    # Remove unnecessary white space
    # Ensure last character is question mark

    if questionText is None or len(db.execute_literal("SELECT * FROM questions WHERE text = ?", [questionText])) > 0:
        request.response.status = 400
        return {"error": "Question already exists"}

    qid = db.executeID("insertQuestion",[questionText])

    return {"qid": qid}

@view_config(route_name="deleteQuestion", renderer="json")
def deleteQuestion(request):
    """ Delete a question from the data base if the request is authorised """
    permissions(request)

    qid = request.params.get("qid", None)

    if qid is None:
        request.response.status = 400
        return {"error": "qid is not supplied"}

    db.execute("deleteQuestion", [qid])

    return {}