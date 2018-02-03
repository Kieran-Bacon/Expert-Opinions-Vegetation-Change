
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

	# Collect the address passed
	userAddress = request.params.get("address", None)

	# Validate the address is valid
	if userAddress is None: return exc.HTTPBadRequest(body="Address not provided")
	if EMAIL_REGEX.match(userAddress) is None: return exc.HTTPBadRequest(body="Not a valid e-mail address")

	# Create psuedo link
	link = Helper.HiddenPages.newAddress("/create_user/")
	link = os.path.join(request.host, link[1:]) # TODO: when the location is stable swap this line out.

	# Create email information
	email = EmailMessage()
	email["Subject"] = "Invitation to Expert Climate model webtool"
	email["To"] = userAddress
	email["From"] = "noreply@expert.com"

	# Set e-mail contents
	with open( os.path.join(TEMPLATES, "invite.email")) as template:
		email.set_content(template.read().format(link))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)  
	s.starttls()
	s.login("kieran.bacon.personal@gmail.com", "***")
	s.send_message(email)
	s.quit()

@view_config(route_name='createUser', renderer="templates/settings_createUser.html")
def createUser(request):

	if not Helper.HiddenPages.validate(request.current_route_path()):
		# Not a vaid link 
		# TODO: make the system sleep before responding as to reduce effectiveness of brute forcing.
		return exc.HTTPNotFound()

	return {"title":"Create an account"}