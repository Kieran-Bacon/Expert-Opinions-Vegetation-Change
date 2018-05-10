import os, re, uuid, threading

from datetime import datetime, timedelta

import smtplib
from email.message import EmailMessage

import pyramid.httpexceptions as exc
from os.path import abspath
TEMPSTORAGE = abspath("./ExpertWebtool/temp") + "/"
CMOSTORAGE = abspath("./ExpertWebtool/data/CMO") + "/" #TODO(KIERAN) Find out why these wernt importing from __init__
TEMPLATES = abspath("./ExpertWebtool/templates") + "/"


# Regular expressions for cross site things
EMAIL_REGEX = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

def email(subject: str, to: str, template: str, formatting: [str]):

	# Create email information
	email = EmailMessage()
	email["Subject"] = subject
	email["To"] = to
	email["From"] = "ExpertClimateWebtool@gmail.com"

	# Set e-mail contents
	with open(os.path.join(TEMPLATES, template)) as filehandler:
		email.set_content(filehandler.read().format(*formatting))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)  
	s.starttls()
	s.login("ExpertClimateWebtool@gmail.com", "Exeter1!")
	s.send_message(email)
	s.quit()

class Warehouse:
	# TODO :: Make this a thing 
	vault = {}
	pass

class HiddenPages:

	threadLock = threading.Lock()
	pages = {}

	def all():
		for content in HiddenPages.pages.items():
			yield content 

	def newAddress(leading: str, following="") -> str:
		""" Generate a random address at some point of the tree

		Params:
			lead - A string that will appear at the beginning of the path
			following - A string that will appear after the randomly generated segment

		Returns:
			str - The address of the new location
		"""

		location = leading + uuid.uuid4().hex.upper() + following
		while location in HiddenPages.pages:
			location = leading + uuid.uuid4().hex.upper() + following

		HiddenPages.threadLock.acquire()
		HiddenPages.pages[location] = datetime.now() + timedelta(days=1)
		HiddenPages.threadLock.release()

		return location

	def validate(address: str) -> bool:
		return address in HiddenPages.pages.keys()

	def remove(address: str) -> None:
		HiddenPages.threadLock.acquire()
		del HiddenPages.pages[address]
		HiddenPages.threadLock.release()

def pageVariables(request, additional=None) -> dict:

	alerts = request.session.get("alerts", [])
	request.session["alerts"] = []

	if additional is None:
		return {**request.session, "alerts":alerts}
	return {**request.session, **additional, "alerts":alerts}

def permissions(request) -> None:
	"""
	Takes a request object for an arbitary page and redirects the user if they
	do not have the correct permissions to access this page.

	Params:
		Request: Pyramid request object
	"""

	# Collect the status of the user from the sessions.
	status = request.session.get("status", None)

	# Determine fate based on status
	if status == 1: return None
	if status is None: raise exc.HTTPFound(request.route_url("login"))
	raise exc.HTTPFound(request.route_url("locked"))

def tempStorage(fileContents):

    filename = uuid.uuid4().hex.upper()
    while os.path.exists(os.path.join(TEMPSTORAGE, filename)):
        filename = uuid.uuid4().hex.upper()

    path = os.path.join(TEMPSTORAGE, filename)

    with open(path, "wb") as fileHandler:
        fileHandler.write(fileContents.read())

    return path
