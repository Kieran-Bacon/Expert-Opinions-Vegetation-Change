from pyramid.view import view_config

from . import Helper

@view_config(route_name="evaluation", renderer="templates/evaluation_main.html")
def evaluation(request):
    Helper.permissions(request)
    return Helper.pageVariables(request, {"title":"Evaluation"})