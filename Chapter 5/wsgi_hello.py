def application(
                environment,
                start_response):
    start_response('200 OK', [])#('Content-Type', 'text/html')])
    return [b'hello world']

