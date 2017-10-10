from pyramid.response import Response
from pyramid.view import view_config

@view_config(route_name="training", renderer="templates/training_main.html")
def training(request):
    return {"title":"Training Page"}