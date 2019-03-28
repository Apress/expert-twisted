from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, strports
from twisted.web import wsgi, server, static, vhost
from twisted.internet import reactor

import wsgi_hello

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_vhost"
    description = "Virtual hosting for book"
    class options(usage.Options):
        optParameters = [["port", "p", None,
                          "strports description of the port to "
                          "start the server on."]]
    def makeService(self, options):
        application = wsgi_hello.application
        pool = threadpool.ThreadPool(minthreads=1, maxthreads=100)
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        dynamic = wsgi.WSGIResource(reactor, pool, application)
        files = static.File('static')
        root = vhost.NameVirtualHost()
        root.addHost(b'app.example.org', dynamic)
        root.addHost(b'static.example.org', files)
        site = server.Site(root)
        return strports.service(options['port'], site)
serviceMaker = ServiceMaker()
