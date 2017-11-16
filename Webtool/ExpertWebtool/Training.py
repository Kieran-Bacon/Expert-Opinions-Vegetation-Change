from pyramid.response import Response
from pyramid.view import view_config

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
    # TODO: unlabelled = db.execute('collectUnlabelled', [request.session["username"]])

    models = db.execute_literal("SELECT mid FROM models", [])
    questions = db.execute_literal("SELECT qid FROM questions", [])
    answered = db.execute_literal("SELECT mid, qid FROM labels WHERE username = ?", [request.session["username"]])

    unlabelled = []
    for mid in models:
        for qid in questions:
            if (mid, qid) not in answered:
                unlabelled.append((mid,qid))
    
    # Randomly choose a model question pair to annotate
    if len(unlabelled):
        modelPath, question = unlabelled[random.randint(0,len(unlabelled))]
    else:
        question = "Hello"

    # Collect model information.

    return {"model": "placeholder", "question": question}

@view_config(route_name="model_uploader", renderer="templates/training_modelUploader.html")
def model_uploader(request):
	return {**request.session, **{"title": "Model Uploader"}}