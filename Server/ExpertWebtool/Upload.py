from pyramid.view import view_config
import pyramid.httpexceptions as exc

from . import Helper
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="modelUploader", renderer="templates/training_modelUploader.html")
def modelUploader(request):
    Helper.permissions(request)
    questions = db.execute("collectQuestions",[])
    return Helper.pageVariables(request, {"title": "Content Uploader", "questions": questions})

@view_config(route_name="modelFileUploader", renderer="json")
def modelFileUploader(request):
    Helper.permissions(request)

    tempLocation = Helper.tempStorage(request.POST['file'].file) # Store the file temporarily 

    try:
        # Produce a climate model output object
        model = ClimateModelOutput(tempLocation)
    except Exception as e:
        # report the issue when trying to work on climate model output
        raise exc.HTTPServerError(str(e))
    finally:
        # Delete the tempory file
        os.remove(tempLocation)

    # Record the new model file and store appropriately 
    modelID = db.executeID("modelUploaded",[request.session["username"]])
    model.save(os.path.join(CMOSTORAGE, str(modelID)))

    return {}