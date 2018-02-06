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
			password = self.request.params['password']
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
			raise exc.HTTPFound(self.request.route_url("index"))

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