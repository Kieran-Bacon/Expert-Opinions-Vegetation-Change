# Pyramid
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

# Python libraries 
import os, hashlib, uuid, sqlite3

# Solution modules
from ExpertRep import ClimateModelOutput
from . import Helper
from .DatabaseHandler import DatabaseHandler as db

from . import CMOSTORAGE



def forgotPost(self):

	invalidAlert = [{\
			"title":"Ow no, unable to find user!",\
			"text":"The information provided is invalid.",\
			"type":"error"}]

	# Collect the address passed
	userAddress = request.params.get("address", None)

	# Validate the address is valid
	if userAddress is None: return exc.HTTPBadRequest(body="Address not provided")
	if EMAIL_REGEX.match(userAddress) is None: return exc.HTTPBadRequest(body="Not a valid e-mail address")
	
	# Validate if user already exists
	try:
		address = db.executeOne("User_Email", [userAddress])
	except:
		self.request.session["alerts"] = invalidAlert
		raise exc.HTTPFound(self.request.route_url("login"))

	# Create psuedo link
	link = Helper.HiddenPages.newAddress("/reset/")
	link = os.path.join(request.host, link[1:]) # TODO: when the location is stable swap this line out.

	# Create email information
	email = EmailMessage()
	email["Subject"] = "Password to Expert Climate model webtool"
	email["To"] = userAddress
	email["From"] = "noreply@expert.com"

	# Set e-mail contents
	with open( os.path.join(TEMPLATES, "forgot.email")) as template:
		email.set_content(template.read().format(link))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)  
	s.starttls()
	s.login("kieran.bacon.personal@gmail.com", "***")
	s.send_message(email)
	s.quit()
	
	
def resetPassword(self):
	invalidAlert = [{\
			"title":"Ow no, passwords don't match!",\
			"text":"The passwords provided do not match.",\
			"type":"error"}]
	
	#check the entered passwords are the same
	if self.request.params['password'] == self.request.params['passwordCheck']:
		password = self.request.params['password']
		salt = uuid.uuid4().hex
		hashedPassword = hashlib.sha512((salt + password).encode("UTF-8")).hexdigest()
		
		
		db.execute('updatePassword', [password, salt])
		
		raise exc.HTTPFound(self.request.route_url("login"))
		
	else:
		self.request.session["alerts"] = invalidAlert
		raise exc.HTTPFound(self.request.route_url("reset"))
		
	
	
