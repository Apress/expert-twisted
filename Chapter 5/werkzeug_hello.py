from werkzeug import wrappers

@wrappers.Request.application
def application(request):
    return wrappers.Response('Hello World!')
