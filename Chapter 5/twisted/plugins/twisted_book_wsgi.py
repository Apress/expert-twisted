from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, strports
from twisted.web import wsgi, server
from twisted.internet import reactor

import wsgi_hello

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_wsgi"
    description = "WSGI for book"
    class options(usage.Options):
        pass
    def makeService(self, options):
        application = wsgi_hello.application
        pool = threadpool.ThreadPool(minthreads=1, maxthreads=100)
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        root = wsgi.WSGIResource(reactor, pool, application)
        site = server.Site(root)
        return strports.service('tcp:8000', site)
serviceMaker = ServiceMaker()
