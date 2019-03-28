import time

from zope import interface

from twisted.python import usage, reflect, threadpool, filepath
from twisted import plugin
from twisted.application import service, strports, internet
from twisted.web import wsgi, server, static
from twisted.internet import reactor

import wsgi_param

def update(application, reactor):
    stamp = time.ctime(reactor.seconds())
    application.greeting = "hello world, it's {}".format(stamp)

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_scheduled"
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
        ts = internet.TimerService(1, update, wsgi_param.application, reactor)
        ts.setServiceParent(s)
        return s

serviceMaker = ServiceMaker()
