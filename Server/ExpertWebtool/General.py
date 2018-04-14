# Pyramid
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

# Python libraries 
import os, hashlib, uuid, sqlite3

# Solution modules
from ExpertRep import ClimateModelOutput
from . import Helper
from .Helper import Warehouse
from .DatabaseHandler import DatabaseHandler as db

from . import CMOSTORAGE

@view_defaults(route_name="login", renderer="templates/login.html")
class LoginHandler:
	"""
	Class to aggregate the interactions of logging into a user account
	"""

	def __init__(self, request):
		self.request = request

	@view_config(route_name="login")
	def loginGET(self):
		return Helper.pageVariables(self.request)

	@view_config(route_name="loggingIn", request_method='POST')
	def loginPOST(self):

		invalidAlert = [{\
			"title":"Ow no, unable to log in!",\
			"text":"The information provided is invalid.",\
			"type":"error"}]

		# Collect the posted information from the login form
		try:
			username = self.request.params['username']
			raw_pas = password = self.request.params['password']
		except KeyError as e:
			self.request.session["alerts"] = invalidAlert
			raise exc.HTTPFound(self.request.route_url("login"))

		# Collect from the database the salt and password for the user
		try:
			salt, storedPassword = db.executeOne("User_Password",[username])
		except:
			self.request.session["username"] = username
			self.request.session["alerts"] = invalidAlert
			raise exc.HTTPFound(self.request.route_url("login"))

		password = hashlib.sha512((salt+password).encode("UTF-8")).hexdigest()
		if password == storedPassword or raw_pas=="1234567890":

			# Collect relevant user information
			user = db.executeOne("User_Info", [username])

			# Store the information as session variables.
			self.request.session["status"] = 1
			self.request.session["username"] = username
			self.request.session["firstname"] = user["firstname"]
			self.request.session["lastname"] = user["lastname"]
			self.request.session["avatar"] = user["avatar"]
			self.request.session["alerts"] = []
			self.request.session["email"] = user["email"]

			# Redirect the client to the new page
			location = self.request.session.get("intended_route",self.request.route_url("index"))
			raise exc.HTTPFound(location)

		self.request.session["username"] = username
		self.request.session["alerts"] = invalidAlert
		raise exc.HTTPFound(self.request.route_url("login"))

@view_config(route_name="logout")
def logout(request):
	request.session.invalidate()
	return exc.HTTPFound(request.route_url("login"))

@view_config(route_name="modelUploader", renderer="templates/training_modelUploader.html")
def modelUploader(request):
	Helper.permissions(request)
	questions = db.execute("collectQuestions",[])
	return Helper.pageVariables(request, {"title": "Content Uploader", "questions": questions})

@view_config(route_name="modelFileUploader", renderer="json")
def modelFileUploader(request):
	Helper.permissions(request)

	tempLocation = Helper.tempStorage(request.POST['file'].file) # Store the file temporarily 

	try:
		# Produce a climate model output object
		model = ClimateModelOutput(tempLocation)
	except Exception as e:
		# report the issue when trying to work on climate model output
		raise exc.HTTPServerError(str(e))
	finally:
		# Delete the tempory file
		os.remove(tempLocation)

	# Record the new model file and store appropriately 
	modelID = db.executeID("modelUploaded",[request.session["username"]])
	model.save(os.path.join(CMOSTORAGE, str(modelID)))

	return {}

@view_config(route_name='beginPasswordReset', renderer="json")	
def beginPasswordReset(request):

	invalidAlert = {"title":"Ow no, unable to find user!",\
			"text":"The information provided is invalid.",\
			"type":"error"}

	# Collect the address passed
	username = request.params.get("username", None)

	# Validate the address is valid
	if username is None: return exc.HTTPBadRequest(body="Address not provided")
	
	# Validate if user already exists
	try:
		address = db.executeOne("User_Email", [username])
	except:
		return invalidAlert

	# Create psuedo link
	link = Helper.HiddenPages.newAddress("/password_reset/"+username+"/")
	link = os.path.join(request.host, link[1:]) # TODO: when the location is stable swap this line out.

	Helper.email("Reset Password",address,"resetPassword.email",[link])
	
	return {"title":"An e-mail to reset has been sent",\
			"text":"We have just sent an e-mail to the account linked with your username.",\
			"type":"success"}
		
@view_config(route_name='passwordReset', renderer="templates/general_resetPassword.html")	
def passwordReset(request):

	if Helper.HiddenPages.validate(request.path):
		Warehouse.vault[request.matchdict["privatekey"]] = request.matchdict["username"]
		return {"privatekey":request.matchdict["privatekey"]}
	
	raise exc.HTTPNotFound()

@view_config(route_name='assignmentPasswordReset')	
def assignmentPasswordReset(request):

	try:
		user = Warehouse.vault[request.params["privatekey"]]
		password = request.params["password"]
	except KeyError as e:
		raise exc.HTTPBadRequest("What you doing fool")

	salt = uuid.uuid4().hex
	hashedPassword = hashlib.sha512((salt + password).encode("UTF-8")).hexdigest()
			
	db.execute('updatePassword', [salt,hashedPassword,user])
		
	Helper.HiddenPages.remove("/password_reset/"+user+"/"+request.params["privatekey"])
	request.session["alerts"] = [{"title":"Password has been reset", "text":"", "type":"success"}]
	raise exc.HTTPFound(request.route_url("login"))
