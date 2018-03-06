
# Pyramid
from pyramid.view import view_config
import pyramid.httpexceptions as exc

# Python libraries
import os
import smtplib
from email.message import EmailMessage

# Package modules
from . import TEMPLATES
from . import Helper
from .Helper import EMAIL_REGEX
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name='personalSettings', renderer="templates/settings_personal.html")
def personalSettings(request):
	Helper.permissions(request)
	return Helper.pageVariables(request, {"title":"Personal Settings"})

@view_config(route_name='manageUsers', renderer="templates/settings_manageUsers.html")
def manageUsers(request):
	Helper.permissions(request)

	# Collect user information
	users_information = db.execute("Users&Permissions",[])

	return Helper.pageVariables(request, {"title":"Manage Users", "users_information": users_information})

@view_config(route_name='inviteUser', request_method='POST', renderer="json")
def inviteUser(request):
	Helper.permissions(request)

	try:
		title = request.params["title"]
		firstname = request.params["firstname"]
		lastname = request.params["lastname"]
		organisation = request.params["organisation"]
		email = request.params["email"]
	except:
		raise exc.HTTPBadRequest("Invalid request")

	if EMAIL_REGEX.match(email) is None: return exc.HTTPBadRequest(body="Not a valid e-mail address")

	# Create psuedo link
	link = Helper.HiddenPages.newAddress("/create_user/")
	link = os.path.join(request.host, link[1:]) # TODO: when the location is stable swap this line out.

	tempUsername = link[-10:]

	db.execute("User_addTemp",[tempUsername,email,None,None,0,title,firstname,lastname,organisation])
	Helper.email("Invitation to Expert Climate model webtool",email,"invite.email",[title, firstname, lastname, link])

@view_config(route_name='createUser',request_method='GET', renderer="templates/settings_createUser.html")
def createUser(request):

	if not Helper.HiddenPages.validate(request.path):
		return exc.HTTPNotFound()

	user = db.executeOne("User_Info",[request.path[-10:]])

	return {"title":"Create an account", "user":user}

@view_config(route_name='createUser',request_method='POST', renderer="json")
def confirmUser(request):

	if not Helper.HiddenPages.validate(request.path):
		return exc.HTTPNotFound() 

	try:
		username = request.params["username"]
		title = request.params["title"]
		firstname = request.params["firstname"]
		lastname = request.params["lastname"]
		organisation = request.params["organisation"]
		email = request.params["email"]
		password = request.params["password"]
	except:
		raise exc.HTTPBadRequest("Invalid request")

	# Check if username already exists
	if len(db.execute("User_Info",[username])):
		raise exc.HTTPBadRequest("Username Exists")

	salt, hashedPassword = Helper.hashPassword(password)
	db.execute("User_confirmTemp",[username,email,salt,hashedPassword,title,firstname,lastname,organisation,request.path[-10:]])

	Helper.HiddenPages.remove(request.path)