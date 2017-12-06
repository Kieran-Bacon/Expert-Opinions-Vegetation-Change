from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

import random

from . import MODELSTORAGE
from .Helper import *
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

    # TODO: collect the CMO data as NetCDFFile object.

    return {"model": "placeholder", "question": question}

@view_config(route_name="modelUploader", renderer="templates/training_modelUploader.html")
def modelUploader(request):
    permissions(request)
    questions = db.execute("collectQuestions",[])
    for a in questions:
        print(a[0], a[1])
    return {**request.session, **{"title": "Content Uploader", "questions": questions}}

@view_config(route_name="modelFileUploader", renderer="json")
def modelFileUploader(request):
    permissions(request)

    tempLocation = tempStorage(request.POST['file'].file)
    
    try:
        model = NetCDFFile(tempLocation)
    except Exception as e:
        request.response.status = 406
        return {"alert": str(e)}
    finally:
        os.remove(tempLocation)

    modelID = db.executeID("modelUploaded",[request.session["username"]])
    model.save(os.path.join(MODELSTORAGE, modelID))

    return {}