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

    return Helper.generatePageVariables(request, {"title":"Training Page", "questions":questions})

@view_config(route_name="collectModelKML", renderer="string")
def collectModelKML(request):
    cmo = ClimateModelOutput.load(os.path.join(CMOSTORAGE + request.matchdict['cmoid']))
    return cmo.get_kml(int(request.matchdict["layer"]))

@view_config(route_name="collectCMO", renderer="json")
def collectCMO(request):
    permissions(request)

    # Collect the question id from the request
    qid = request.params.get("qid", None)
    if qid is None: raise exc.HTTPBadRequest("Question ID not passed")

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
    mid = request.params.get("mid", None)
    qid = request.params.get("qid", None)
    score = request.params.get("score", None)
    if None in (mid, qid, score): raise exc.HTTPBadRequest("Necessary content is missing")

    print(mid, qid, score, type(mid), type(qid), type(score))

    # TODO: decide upon score range and values
    score = float(int(score))*0.05 # Reduce score to between 0-5

    # Add datapoint to the users current batch
    Trainer.addDatapoint(request.session["username"], qid, mid, score)

    print(Trainer._USERBATCHS)

    # Record the users opinion
    db.execute('labelModel', [request.session["username"], qid, mid, score])

    raise exc.HTTPNoContent()

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

class Trainer():
    """ Record a users batch information such that when it time for training, it can be done quickly
    and easily """

    _USERBATCHS = {}

    def info(username: str):
        return Trainer._USERBATCHS.get(username, {})

    def learnOnBatch(username: str, questionID: int):

        # Collect Expert information
        expert = db.executeOne("collectEMIdentifier",[request.session["username"],questionID])

        # Prepare batch information
        CMOs, scores = [], []
        for modelID, score in Trainer._USERBATCHS[username][questionID].items():
            CMOs.append(ClimateModelOutput.load(os.path.join(CMOSTORAGE + str(modelID))))
            scores.append(score)

        # Train the expert model
        try:
            ExpertModelAPI().partial_fit(model_id=expert["identifier"], data=CMOs, targets=scores)
            del Trainer._USERBATCHS[username][questionID] # remove batch information
        except Exception as e:
            # An error has occured within the ML backend
            print("Error when batch learning: "+e)


    def addDatapoint(username: str, questionID: int, modelID: int, score: int):

        collection = Trainer._USERBATCHS.get(username, {})
        questionBatch = collection.get(questionID, {})
        questionBatch[modelID] = score
        collection[questionID] = questionBatch
        Trainer._USERBATCHS[username] = collection