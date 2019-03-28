class _Application(object):
    def __init__(self, greeting='hello world'):
        self.greeting = greeting
    def __call__(self, environment, start_response):
        start_response('200 OK', [])#('Content-Type', 'text/html')])
        return [self.greeting.encode('utf-8')]

application = _Application()
