import webob

def application(environment, start_response):
    request = webob.Request(environment)
    response = webob.Response(
                     text='Hello world!')
    return response(environment, start_response)
