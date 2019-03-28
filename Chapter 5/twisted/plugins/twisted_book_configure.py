from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, strports
from twisted.web import wsgi, server
from twisted.internet import reactor, protocol
from twisted.protocols import amp

import pyramid_dynamic

class GetCapitalize(amp.Command):
    arguments = []
    response = [(b'value', amp.Float())]

class GetExclaim(amp.Command):
    arguments = []
    response = [(b'value', amp.Float())]

class SetCapitalize(amp.Command):
    arguments = [(b'value', amp.Float())]
    response = []

class SetExclaim(amp.Command):
    arguments = [(b'value', amp.Float())]
    response = []

class AppConfiguration(amp.CommandLocator):

    @GetCapitalize.responder
    def get_capitalize(self):
        return {'value': pyramid_dynamic.FEATURES['capitalize']}

    @GetExclaim.responder
    def get_exclaim(self):
        return {'value': pyramid_dynamic.FEATURES['exclaim']}

    @SetCapitalize.responder
    def set_capitalize(self, value):
        pyramid_dynamic.FEATURES['capitalize'] = value
        return {}

    @SetExclaim.responder
    def set_exclaim(self, value):
        pyramid_dynamic.FEATURES['exclaim'] = value
        return {}


@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_configure"
    description = "WSGI for book"
    class options(usage.Options):
        pass
    def makeService(self, options):
        application = pyramid_dynamic.application
        pool = threadpool.ThreadPool(minthreads=1, maxthreads=100)
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        root = wsgi.WSGIResource(reactor, pool, application)
        site = server.Site(root)
        control = protocol.Factory()
        control.protocol = lambda: amp.AMP(locator=AppConfiguration())
        ret = service.MultiService()
        strports.service('tcp:8000', site).setServiceParent(ret)
        strports.service('tcp:8001', control).setServiceParent(ret)
        return ret
serviceMaker = ServiceMaker()
