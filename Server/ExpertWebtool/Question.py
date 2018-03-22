# Pyramid installs
from pyramid.view import view_config
import pyramid.httpexceptions as exc

# Externel Libaries
import hashlib, uuid
import sqlite3

# Package modules
from ExpertRep import ExpertModelAPI
from . import Helper
from .DatabaseHandler import DatabaseHandler as db

@view_config(route_name="createQuestion", renderer="json")
def createQuestion(request):
    """ Add a parsed question text into the database if it is from a authorised
	user """
    Helper.permissions(request)

    try:
        questionText = request.params["text"]
    except KeyError as e:
        raise exc.HTTPBadRequest("Requires question text")

    # TODO: Parse/edit the question text
    # Remove starting and trailing white space
    # Remove unnecessary white space
    # Ensure last character is question mark

    # Record new question
    qid = db.executeID("insertQuestion",[questionText])

    # For every user create a new expert model to represent this question.
    # TODO: Move this functionality to be operated on after returning qid.

    for user in db.execute("collectUserModelSpec",[]):
        identifier = ExpertModelAPI().create_model(model_type=user["modelSpec"])
        db.execute("eModel_insertModel", [identifier, user["username"], qid])

    return {"qid": qid}

@view_config(route_name="deleteQuestion", renderer="json")
def deleteQuestion(request):
    """ Delete a question from the data base if the request is authorised """
    Helper.permissions(request)

    try:
        qid = request.params["qid"]
    except KeyError as e:
        raise exc.HTTPBadRequest("Requires question identification")
    
    db.execute("deleteQuestion", [qid])        # Delete the question row
    db.execute("deleteQuestionLabels", [qid])  # Delete annotated label info

    # Delete expert model information
    for row in db.execute_literal("SELECT identifier FROM expertModels WHERE qid = ?", [qid]):
        try:
            ExpertModelAPI().delete_model(model_id=row["identifier"])
        except:
            # TODO: fix
            print("Error passed for convience - Must fix")
            pass

    # Delete all rows related to question models        
    db.execute_literal("DELETE FROM expertModels WHERE qid = ?", [qid])

    return {}
