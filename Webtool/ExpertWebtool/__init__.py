from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from .DatabaseHandler import DatabaseHandler

def main(global_config, **settings):

    sessionFactory = SignedCookieSessionFactory('133c28fa3ddb944b6f4023b8afdd2a1d')
	
    config = Configurator(settings=settings, session_factory=sessionFactory) # Global settings from development.ini
    config.include('pyramid_jinja2')                                         # Html Templating language selection
    config.add_jinja2_renderer('.html')                                      # Allow jinja2 to parse html file types

    # Static resources
    config.add_static_view(name='fonts', path='static/fonts')
    config.add_static_view(name='imgs', path='static/imgs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='js', path='static/js')

    # Route requests
    config.add_route('blank', '/')

    config.add_route('login', 'login.html')
    config.add_route('loggingIn','login')
    config.add_route('logout', 'logout')

    config.add_route('training', '/training.html')
    config.add_route('model_uploader', '/model_uploader.html')
    config.add_route('evaluation', '/evalutation.html')

    # Link views
    config.scan(".General")    # General server functions
    config.scan(".Training")   # Handles the training interactions
    config.scan(".Evaluation") # Handles the prediction aspects of the tool

    # Load database information
    DatabaseHandler.load()

    # Return the WSGI application object
    return config.make_wsgi_app()