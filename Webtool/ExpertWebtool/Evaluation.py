from pyramid.response import Response
from pyramid.view import view_config

@view_config(route_name="evaluation", renderer="templates/training_main.html")
def evaluation(request):
    return {"title":"Training Page"}