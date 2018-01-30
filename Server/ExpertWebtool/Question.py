from pyramid.response import Response
from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from ExpertRep import ExpertModelAPI

from . import Helper
from .Helper import permissions
from .DatabaseHandler import DatabaseHandler as db
import hashlib, uuid
import sqlite3

@view_config(route_name="createQuestion", renderer="json")
def createQuestion(request):
    """ Add a parsed question text into the database if it is from a authorised
	user """
    permissions(request)

    questionText = request.params.get("text", None)

    # TODO: Parse/edit the question text
    # Remove starting and trailing white space
    # Remove unnecessary white space
    # Ensure last character is question mark

    if questionText is None or len(db.execute_literal("SELECT * FROM questions WHERE text = ?", [questionText])) > 0:
        request.response.status = 400
        return {"error": "Question already exists"}

    qid = db.executeID("insertQuestion",[questionText])

    # For every user create a new expert model to represent this question.
    # TODO: Move this functionality to be operated on after returning qid.
    usernames = db.execute_literal("SELECT username FROM users", [])
    for row in usernames:
        identifier = ExpertModelAPI().create_model(model_type="KNN")
        print(identifier)
        db.execute_literal("INSERT INTO expertModels VALUES(?, ?, ?)", [identifier, row["username"], qid])

    return {"qid": qid}

@view_config(route_name="deleteQuestion", renderer="json")
def deleteQuestion(request):
    """ Delete a question from the data base if the request is authorised """
    permissions(request)

    qid = request.params.get("qid", None)

    if qid is None:
        request.response.status = 400
        return {"error": "qid is not supplied"}
    
    db.execute("deleteQuestion", [qid])        # Delete the question row
    db.execute("deleteQuestionLabels", [qid])  # Delete annotated label info

    # Delete expert model information
    for row in db.execute_literal("SELECT identifier FROM expertModels WHERE qid = ?", [qid]):
        print(row["identifier"])
        try:
            ExpertModelAPI().delete_model(model_id=row["identifier"])
        except:
            # TODO: fix
            print("Error passed for convience - Must fix")
            pass
    db.execute_literal("DELETE FROM expertModels WHERE qid = ?", [qid])

    return {}