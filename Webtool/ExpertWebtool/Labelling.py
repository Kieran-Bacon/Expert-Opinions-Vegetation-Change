from pyramid.response import Response
from pyramid.view import view_config

@view_config(route_name="labelling", renderer="templates/labelling_main.html")
def labelling(request):
    return {"title":"Model Labelling"}