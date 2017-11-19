from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

import random

from .helper import *
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="training", renderer="templates/training_main.html")
def training(request):
    permissions(request)
    return {**request.session, **{"title":"Training Page"}}

@view_config(route_name="retrieveLabellingInformation", renderer="json")
def retrieveLabellingInformation(request):
    permissions(request) # Check user permissions for this action

    # Collect form information
    modelID = request.params.get('model', None)
    questionID = request.params.get('question', None)
    score = request.params.get('score', None)

    print( "CMO ::", modelID, questionID, score)

    # if the information has been given, record it
    if None not in (modelID, questionID, score):
        db.execute('labelModel', [request.session["username"], modelID, questionID, score])

    # Collected all model question pairs still not annotated by the user
    unlabelled = db.execute('collectUnlabelled', [request.session["username"]])

    if not len(unlabelled):
        # Redirect the user as they have done all the annotations they can
        raise exc.HTTPFound(request.route_url("AllLabelled"))
    
    # Randomly choose a model question pair to annotate
    modelPath, question = random.choice(unlabelled)

    # TODO: collect the CMO data.

    return {"model": "placeholder", "question": question}

@view_config(route_name="model_uploader", renderer="templates/training_modelUploader.html")
def model_uploader(request):
	return {**request.session, **{"title": "Model Uploader"}}