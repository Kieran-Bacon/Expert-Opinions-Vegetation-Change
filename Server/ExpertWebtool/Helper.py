import os, uuid
import re

import pyramid.httpexceptions as exc

from . import TEMPSTORAGE

# Regular expressions for cross site things
EMAIL_REGEX = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

class HiddenPages:

	pages = set()

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

		HiddenPages.pages.add(location)

		return location

	def validate(address: str) -> bool:
		return address in HiddenPages.pages

	def remove(address: str) -> None:
		HiddenPages.pages.remove(address)

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