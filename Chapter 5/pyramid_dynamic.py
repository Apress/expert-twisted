import random

from pyramid import config, response

FEATURES = dict(capitalize=0.0, exclaim=0.0)
     
def hello_world(request):
    if random.random() < FEATURES['capitalize']:
        message = 'Hello world'
    else:
        message = 'hello world'
    if random.random() < FEATURES['exclaim']:
        message += '!'
    return response.Response(message)

with config.Configurator() as conf:
    conf.add_route('hello', '/')
    conf.add_view(hello_world, route_name='hello')
    application = conf.make_wsgi_app()
