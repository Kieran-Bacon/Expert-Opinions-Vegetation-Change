from pyramid.config import Configurator
from pyramid.response import Response

def main(global_config, **settings):
	
    config = Configurator(settings=settings) # Global settings from development.ini
    config.include('pyramid_jinja2')         # Html Templating language selection
    config.add_jinja2_renderer('.html')      # Allow jinja2 to parse html file types

    # Static resources
    config.add_static_view(name='fonts', path='static/fonts')
    config.add_static_view(name='imgs', path='static/imgs')
    config.add_static_view(name='css', path='static/css')
    config.add_static_view(name='js', path='static/js')

    # Route requests
    config.add_route('blank', '/')
    config.add_route('labelling', '/labelling.html')
    config.add_route('training', '/training.html')
    config.add_route('evaluation', '/evalutation.html')

    # Link views
    config.scan(".General")    # General server functions
    config.scan(".Labelling")   # Handles model labelling interactions
    config.scan(".Training")   # Handles the training interactions
    config.scan(".Evaluation") # Handles the prediction aspects of the tool

    # Return the WSGI application object
    return config.make_wsgi_app()