from .Email import email
from .Storage import CMOStore, tempStorage, emptyDirectory
from .HiddenPages import HiddenPages
from .Permissions import AUTHORITY, permissions


import re, uuid, hashlib
import pyramid.httpexceptions as exc

from ExpertWebtool.DatabaseHandler import DatabaseHandler as db

# Regular expressions for cross site things
EMAIL_REGEX = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

def pageVariables(request, additional=None) -> dict:

    alerts = request.session.get("alerts", [])
    request.session["alerts"] = []

    if additional is None:
        return {**request.session, "alerts":alerts}
    return {**request.session, **additional, "alerts":alerts}

def hashPassword(pwd, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    hashedPassword = hashlib.sha512((salt + pwd).encode("UTF-8")).hexdigest()
    return salt, hashedPassword

def recordModelMetrics(identifier: str, metrics = None) -> None:
	""" Handle the model output that comes from the expert repr """

	try:
		precision = metrics.precision
	except:
		precision = None

	try:
		accuracy = metrics.accuracy
	except:
		accuracy = None

	try:
		R2 = metrics.R2
	except:
		R2 = None

	try:
		L1 = metrics.L1_loss
	except:
		L1 = None

	db.execute("eModel_recordMetrics", [precision, accuracy, R2, L1, identifier]) # Record the model metrics

from .ProcessRunner import ProcessRunner