# Pyramid
from pyramid.view import view_config
import pyramid.httpexceptions as exc

# Python libraries
import os
import concurrent.futures

# Package modules
from . import TEMPLATES, CMOSTORAGE
from . import Helper
from .DatabaseHandler import DatabaseHandler as db
from .Training import ProcessRunner, fit_model_and_write_db

import ExpertRep
from ExpertRep import ExpertModelAPI, ClimateModelOutput


@view_config(route_name='personalSettings', renderer="templates/settings_personal.html")
def personalSettings(request):
    Helper.permissions(request)

    UserModelSpec = db.execute_literal(
        "SELECT modelSpec FROM users WHERE username = ?", [request.session["username"]])[0]["modelSpec"]
    models = ExpertRep.available_models()  # Get a list of available models

    return Helper.pageVariables(request,
                                {"title": "Personal Settings", "selectedModel": UserModelSpec, "models": models})


@view_config(route_name='updatePersonal', renderer="json")
def updatePersonal(request):
    Helper.permissions(request)

    try:
        modelSpec = request.params["model_spec"]
    except:
        raise exc.HTTPBadRequest("Information missing")

    user = db.executeOne("User_Info", [request.session["username"]])

    if True:
        # Change all the models currently implemented and re train
        expertsModels = db.execute_literal(
            "SELECT * FROM expertModels WHERE username = ?", [user["username"]])

        # Update users Model Specification
        db.execute_literal("UPDATE users SET modelSpec = ? WHERE username = ?", [modelSpec, user["username"]])

        for model in expertsModels:
            # Replace the old model with the new model in the database
            identifier = ExpertModelAPI().create_model(model_type=modelSpec)
            db.execute_literal("UPDATE expertModels SET identifier = ? WHERE identifier = ?", [
                identifier, model["identifier"]])
            trainingData = db.execute("collectModelLabels", [user["username"], model["qid"]])
            CMOs, scores = [], []
            for datapoint in trainingData:
                CMOs.append(ClimateModelOutput.load(os.path.join(CMOSTORAGE, str(datapoint["cmoid"]))))
                scores.append(datapoint["score"])
            ProcessRunner().add_process(fit_model_and_write_db, identifier, user["username"], model["qid"], CMOs,
                                        scores)
            # Delete old model
            ExpertModelAPI().delete_model(model_id=model["identifier"])


@view_config(route_name='manageUsers', renderer="templates/settings_manageUsers.html")
def manageUsers(request):
    Helper.permissions(request)

    # Collect user information

    return Helper.pageVariables(request, {"title": "Manage Users", "authorities": Helper.AUTHORITY,
                                          "users_information": users_information})


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

    if Helper.EMAIL_REGEX.match(email) is None: return exc.HTTPBadRequest(body="Not a valid e-mail address")

    # Create psuedo link
    link = Helper.HiddenPages.newAddress("/create_user/")
    link = os.path.join(request.host, link[1:])  # TODO: when the location is stable swap this line out.

    tempUsername = link[-10:]

    db.execute("User_addTemp", [tempUsername, email, None, None, 0, title, firstname, lastname, organisation])
    Helper.email("Invitation to Expert Climate model webtool", email, "invite.email",
                 [title, firstname, lastname, link])

    try:
        title = request.params["title"]
        firstname = request.params["firstname"]
        lastname = request.params["lastname"]
        organisation = request.params["organisation"]
        email = request.params["email"]
        permission = request.params["permission"]
    except:
        raise exc.HTTPBadRequest("Invalid request")

    if Helper.EMAIL_REGEX.match(email) is None: return exc.HTTPBadRequest(body="Not a valid e-mail address")

    # Create psuedo link
    link = Helper.HiddenPages.newAddress("/create_user/")
    link = os.path.join(request.host, link[1:])  # TODO: when the location is stable swap this line out.

    tempUsername = link[-10:]

    db.execute("User_addTemp", [tempUsername, email, None, None, permission, title, firstname, lastname, organisation])
    Helper.email("Invitation to Expert Climate model webtool", email, "invite.email",
                 [title, firstname, lastname, link])


@view_config(route_name='createUser', request_method='GET', renderer="templates/settings_createUser.html")
def createUser(request):
    if not Helper.HiddenPages.validate(request.path):
        return exc.HTTPNotFound()

    if not Helper.HiddenPages.validate(request.path):
        return exc.HTTPNotFound()

    user = db.executeOne("User_Info", [request.path[-10:]])

    return {"title": "Create an account", "user": user}


@view_config(route_name='createUser', request_method='POST', renderer="json")
def confirmUser(request):
    if not Helper.HiddenPages.validate(request.path):
        return exc.HTTPNotFound()

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

    if len(db.execute("User_Info", [username])):
        raise exc.HTTPBadRequest("Username Exists")

    salt, hashedPassword = Helper.hashPassword(password)
    db.execute("User_confirmTemp",
               [username, email, salt, hashedPassword, title, firstname, lastname, organisation, request.path[-10:]])

    Helper.HiddenPages.remove(request.path)
