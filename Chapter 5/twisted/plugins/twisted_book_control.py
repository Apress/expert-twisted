import time

from zope import interface

from twisted.python import usage, reflect, threadpool, filepath
from twisted import plugin
from twisted.application import service, strports, internet
from twisted.web import wsgi, server, static
from twisted.internet import reactor, protocol
from twisted.protocols import basic

import wsgi_param

class UpdateMessage(basic.LineReceiver):

    def lineReceived(self, line):
        self.factory.application.greeting = line

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_control"
    description = "Changing application"
    class options(usage.Options): pass
    def makeService(self, options):
        s = service.MultiService()
        pool = threadpool.ThreadPool()
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        root = wsgi.WSGIResource(reactor, pool, wsgi_param.application)
        site = server.Site(root)
        strports.service('tcp:8000', site).setServiceParent(s)
        factory = protocol.Factory.forProtocol(UpdateMessage)
        factory.application = wsgi_param.application
        strports.service('tcp:8001',factory).setServiceParent(s)
        return s

serviceMaker = ServiceMaker()
