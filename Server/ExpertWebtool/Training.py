from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

import random

from ExpertRep import ExpertModelAPI, ClimateModelOutput

from . import CMOSTORAGE
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

    # if the information has been given, record it
    if None not in (modelID, questionID, score) and "" not in (modelID, questionID, score):

        # TODO: Discuss the score values
        score = float(int(score))*0.05 # Reduce score to between 0-5

        # Collect the expert model identifier
        expert = db.executeOne("collectEMIdentifier",[request.session["username"],questionID])

        # Produce the climate model output object the score relates too
        cmo = ClimateModelOutput.load(os.path.join(CMOSTORAGE + str(modelID)))

        # Train the expert model
        try:
            ExpertModelAPI().partial_fit(model_id=expert["identifier"], data=[cmo], targets=[score])
        except:
            #TODO: Doesn't like a single datapoint apparently.
            pass

        # Store the training information
        db.execute('labelModel', [request.session["username"], questionID, modelID, score])

    # Collected all model question pairs still not annotated by the user
    unlabelled = db.execute('collectUnlabelled', [request.session["username"]])

    if not len(unlabelled):
        # Redirect the user as they have done all the annotations they can
        request.response.status = 303
        return {"context":"Completed labelling"}
    
    # Randomly choose a model question pair to annotate
    modelID, questionID, question = random.choice(unlabelled)

    # Load climate model output
    output = ClimateModelOutput.load(os.path.join(CMOSTORAGE + str(modelID)))

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

    tempLocation = tempStorage(request.POST['file'].file) # Store the file temporarily 
    
    try:
        # Produce a climate model output object
        model = ClimateModelOutput(tempLocation)
    except Exception as e:
        # report the issue when trying to work on climate model output
        request.response.status = 406
        return {"alert": str(e)}
    finally:
        # Delete the tempory file
        os.remove(tempLocation)
    
    # Record the new model file and store appropriately 
    modelID = db.executeID("modelUploaded",[request.session["username"]])
    model.save(os.path.join(CMOSTORAGE, str(modelID)))

    return {}