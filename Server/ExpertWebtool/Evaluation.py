from pyramid.view import view_config
import pyramid.httpexceptions as exc

import os

from . import TEMPSTORAGE

from . import Helper
from .DatabaseHandler import DatabaseHandler as db

from ExpertRep import ExpertModelAPI, ClimateModelOutput

@view_config(route_name="evaluation", renderer="templates/evaluation_main.html")
def evaluation(request):
    Helper.permissions(request)

    expertInfo = db.execute("User_expertInfo",[])
    questions = db.execute("collectQuestions",[])

    split = int((len(expertInfo)/2)+0.5)
    print(split)

    return Helper.pageVariables(request, {"title":"Evaluation", "lexperts": expertInfo[:split], "rexperts":expertInfo[split:], "questions":questions})

@view_config(route_name="evalModels", renderer="json")
def evalModels(request):
    Helper.permissions(request)

    # Collect information to evaluate
    try:
        experts = request.params.getall("experts[]")
        questions = request.params.getall("questions[]")
    except Exception as e:
        raise exc.HTTPBadRequest()

    # Collect Expert information
    expertNames = [" ".join([i["title"], i["firstname"], i["lastname"]]) for e in experts for i in db.execute("User_Info", [e])]

    # Collect uploaded models to evaluate
    modelDirectory = os.path.join(TEMPSTORAGE,request.session["username"])
    CMOnames = os.listdir(modelDirectory)
    CMOpaths = [os.path.join(modelDirectory, filename) for filename in CMOnames]
    CMOs = [ClimateModelOutput.load(path) for path in CMOpaths]

    # Data type to return to the page
    data = {"experts": expertNames, "questions": []}

    for question in questions:

        questionContents = {"text": db.executeOne("questionName", [question])["text"], "models": []}

        predictions = []
        for expert in experts:

            # Collect the experts model identifier
            identifier = db.executeOne("collectEModel", [expert, question])["identifier"]

            # Predict on the CMO's and storage the results
            predictions.append(ExpertModelAPI().predict(model_id=identifier, data=CMOs))

        for i in range(len(CMOs)):
            modelInfo = {"name": CMOnames[i], "values": [round(opinion[i]*20,5) for opinion in predictions]}
            questionContents["models"].append(modelInfo)

        data["questions"].append(questionContents)

    # Remove uploaded models that have not been evaluated.
    Helper.emptyDirectory(modelDirectory)

    return data

@view_config(route_name="uploadEvalModel")
def uploadEvalModel(request):
    Helper.permissions(request)

    tempLocation = Helper.tempStorage(request.POST['file'].file)  # Store the file temporarily 
    try:
        # Produce a climate model output object
        model = ClimateModelOutput(tempLocation)
    except Exception as e:
        # report the issue when trying to work on climate model output
        raise exc.HTTPBadRequest(str(e))
    finally:
        # Delete the tempory file
        os.remove(tempLocation)

    # Record model within the users temp space
    directory = os.path.join(TEMPSTORAGE, request.session["username"])
    try:
        if not os.path.isdir(directory):
            # Ensure tempory space for the models
            os.mkdir(directory)

        # Save the model in the tempory space.
        model.save(os.path.join(directory, request.POST["file"].filename[:20]))
    except Exception as e:
        raise exc.HTTPBadRequest(str(e))

    return exc.HTTPOk()