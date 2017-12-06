from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

import random

from ExpertRep import ExpertModelAPI, ClimateModelOutput

from . import MODELSTORAGE
from .Helper import *
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="training", renderer="templates/training_main.html")
def training(request):
    permissions(request)

    # Redirect user if they have labelled everything
    if len(db.execute('collectUnlabelled', [request.session["username"]])) == 0:
        raise exc.HTTPFound(request.route_url("allLabelled"))

    return {**request.session, **{"title":"Training Page"}}

@view_config(route_name="retrieveLabellingInformation", renderer="json")
def retrieveLabellingInformation(request):
    permissions(request) # Check user permissions for this action

    # Collect form information
    modelID = request.params.get('mid', None)
    questionID = request.params.get('qid', None)
    score = request.params.get('score', None)

    print("Check ::", modelID, questionID, score)
    print(type(modelID), type(questionID), type(score))

    # if the information has been given, record it
    if None not in (modelID, questionID, score) and "" not in (modelID, questionID, score):
        cmo = ClimateModelOutput.load(os.path.join(MODELSTORAGE + str(modelID)))
        ExpertModelAPI().partial_fit(model_id=request.session["username"], data=[cmo], targets=[int(score)*0.05])
        db.execute('labelModel', [request.session["username"], modelID, questionID, score])

    # Collected all model question pairs still not annotated by the user
    unlabelled = db.execute('collectUnlabelled', [request.session["username"]])

    if not len(unlabelled):
        # Redirect the user as they have done all the annotations they can
        request.response.status = 303
        return {"context":"Completed labelling"}
    
    # Randomly choose a model question pair to annotate
    modelID, questionID, question = random.choice(unlabelled)

    # Load climate model output
    output = ClimateModelOutput.load(os.path.join(MODELSTORAGE + str(modelID)))

    return {"mid": modelID, "model": output.get_kml(),\
            "qid": questionID, "question": question}

@view_config(route_name="allLabelled", renderer="templates/base.html")
def allLabelled(request):
    return {**request.session, **{"title":"All labelled", "alert":"All pairs have been labelled, check back later for new pairings"}}

@view_config(route_name="modelUploader", renderer="templates/training_modelUploader.html")
def modelUploader(request):
    permissions(request)
    questions = db.execute("collectQuestions",[])
    return {**request.session, **{"title": "Content Uploader", "questions": questions}}

@view_config(route_name="modelFileUploader", renderer="json")
def modelFileUploader(request):
    permissions(request)

    tempLocation = tempStorage(request.POST['file'].file)
    
    try:
        model = ClimateModelOutput(tempLocation)
    except Exception as e:
        request.response.status = 406
        return {"alert": str(e)}
    finally:
        os.remove(tempLocation)
    
    model.save(os.path.join(MODELSTORAGE, str(modelID)))
    modelID = db.executeID("modelUploaded",[request.session["username"]])

    return {}