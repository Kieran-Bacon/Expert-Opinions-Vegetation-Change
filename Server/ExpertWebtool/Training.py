from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

import random

from ExpertRep import ExpertModelAPI, ClimateModelOutput

from . import CMOSTORAGE
from . import Helper
from .Helper import *
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="training", renderer="templates/training_main.html")
def training(request):
    permissions(request)

    # Collect all question ids
    allQuestions = db.execute("collectQuestions", [])

    # Select questions the user still has unannotated models for
    questions = []
    for qInfo in allQuestions:
        if len(db.execute('collectUnlabelled', [request.session["username"],qInfo["qid"]])):
            questions.append({"qid": qInfo["qid"], "text": qInfo["text"]})

    return Helper.pageVariables(request, {"title":"Training Page", "questions":questions})

@view_config(route_name="collectModelKML", renderer="string")
def collectModelKML(request):
    cmo = ClimateModelOutput.load(os.path.join(CMOSTORAGE + request.matchdict['cmoid']))
    return cmo.get_kml(int(request.matchdict["layer"]))

@view_config(route_name="collectCMO", renderer="json")
def collectCMO(request):
    permissions(request)

    # Collect the question id from the request
    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    # Collect the collection of unlabelled models for that user and question
    unlabelled = db.execute('collectUnlabelled', [request.session["username"],qid])

    # Select and return a modelID at random
    # TODO: Include directed learning
    if len(unlabelled):
        modelID, = random.choice(unlabelled)
        return {"mid": modelID}
    
    # No models left to annotate, no model id to return
    raise exc.HTTPNoContent()

@view_config(route_name="scoreCMO")
def scoreCMO(request):
    permissions(request)

    # Collect information
    try:
        mid = int(request.params["mid"])
        qid = int(request.params["qid"])
        score = int(request.params["score"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Necessary content is missing")

    # TODO: decide upon score range and values
    score = float(int(score))*0.05 # Reduce score to between 0-5

    # Record the users opinion
    db.execute('labelModel', [request.session["username"], qid, mid, score])

    raise exc.HTTPNoContent()

@view_config(route_name="submitBatch", renderer="json")
def submitBatch(request):
    permissions(request)

    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    username = request.session["username"]

    # Collect Expert information
    expert = db.executeOne("collectEMIdentifier",[username,qid])
    batch = db.execute("collectBatch", [username, qid])

    # Prepare batch information
    CMOs, scores = [], []
    for CMOid, score in batch:
        CMOs.append(ClimateModelOutput.load(os.path.join(CMOSTORAGE+str(CMOid))))
        scores.append(score)
    
    # Train the expert model
    try:
        ExpertModelAPI().partial_fit(model_id=expert["identifier"], data=CMOs, targets=scores)
        db.execute("submitBatch",[username, qid]) # Update batch assignment
    except Exception as e:
        # An error has occured within the ML backend
        raise exc.HTTPBadRequest("Error on learning batch")

    return {}

@view_config(route_name="removeBatch", renderer="json")
def removeBatch(request):
    permissions(request)

    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    db.execute("deleteBatch",[request.session["username"], qid])

    return {}