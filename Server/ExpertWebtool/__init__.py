import os
from os.path import abspath

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

ROOT = os.path.dirname(os.path.realpath(__file__))
TEMPSTORAGE = os.path.join(ROOT, "temp") + "/"
CMOSTORAGE = os.path.join(ROOT,"data","CMO") + "/"
TEMPLATES = os.path.join(ROOT,"templates") + "/"

from . import Processes
from .DatabaseHandler import DatabaseHandler

def main(global_config, **settings):

    sessionFactory = SignedCookieSessionFactory('133c28fa3ddb944b6f4023b8afdd2a1d')
	
    config = Configurator(settings=settings, session_factory=sessionFactory) # Global settings from development.ini
    config.include('pyramid_jinja2')                                         # Html Templating language selection
    config.add_jinja2_renderer('.html')                                      # Allow jinja2 to parse html file types

    # Static resources
    config.add_static_view(name='fonts', path='static/fonts')
    config.add_static_view(name='imgs', path='static/imgs')
    config.add_static_view(name='images', path='static/imgs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='js', path='static/js')

    # Route requests
    config.add_route('index', '/')
    config.add_route('dashboardMain', '/dashboard.html')
    config.add_route('userProfile', '/user_profile.html')

    config.add_route('login', '/login.html')
    config.add_route('loggingIn','/login')
    config.add_route('logout', '/logout')
    config.add_route('createQuestion', '/createQuestion')
    config.add_route('deleteQuestion', '/deleteQuestion')

    config.add_route('beginPasswordReset', '/password_reset')
    config.add_route('passwordReset', '/password_reset/{username}/{privatekey}')
    config.add_route('assignmentPasswordReset', '/password_reset/assign')

    config.add_route('training', '/training.html')
    config.add_route('collectCMO','/training/collectCMO')
    config.add_route('scoreCMO', '/training/scoreCMO')
    config.add_route('submitBatch', '/training/submitBatch')
    config.add_route('removeBatch', '/training/removeBatch')
    config.add_route('collectModelKML', '/collect_model_kml/{cmoid}/{layer}')

    config.add_route('modelUploader', '/model_uploader.html')
    config.add_route('modelFileUploader', '/model_upload')

    config.add_route('evaluation', '/evaluation.html')
    config.add_route('evalModels', '/evaluation')
    config.add_route('uploadEvalModel', "/evaluate_model")

    config.add_route('personalSettings', '/settings/personal.html')
    config.add_route('updatePersonal', '/settings/update_personal')
    config.add_route('createUser', '/create_user/{accountLink}')
    config.add_route('manageUsers', '/settings/manage_users.html')
    config.add_route('inviteUser', '/settings/invite_user')

    # Link views
    config.scan(".General")    # General server functions
    config.scan(".Dashboard")  # Handles landing pages
    config.scan(".Training")   # Handles the training interactions
    config.scan(".Question")   # Handlers for question manipulation
    config.scan(".Evaluation") # Handles the prediction aspects of the tool
    config.scan(".Settings")   # Contains webtool settings functions

    # Load database information
    DatabaseHandler.load()

    # Begin supporting processes
    Processes.run()

    # Return the WSGI application object
    return config.make_wsgi_app()