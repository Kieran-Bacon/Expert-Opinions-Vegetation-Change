import os, uuid

import pyramid.httpexceptions as exc

from . import TEMPSTORAGE

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
