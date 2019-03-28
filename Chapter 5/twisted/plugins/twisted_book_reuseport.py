import socket

import attr

from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, internet as tainternet
from twisted.web import wsgi, server
from twisted.internet import reactor, tcp, interfaces as tiinterfaces, defer

import wsgi_hello

@interface.implementer(tiinterfaces.IStreamServerEndpoint)
@attr.s
class ListenerWithReuseEndPoint(object):
    port = attr.ib()
    reactor = attr.ib(default=None)
    backlog = attr.ib(default=50)
    interface = attr.ib(default='')

    def listen(self, protocolFactory):
        p = tcp.Port(self.port, protocolFactory, self.backlog, self.interface,
                     self.reactor)
        self._sock = sock = p.createInternetSocket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind((self.interface, self.port))
        sock.listen(self.backlog)
        return defer.succeed(reactor.adoptStreamPort(sock.fileno(),
                                                     p.addressFamily,
                                                     protocolFactory))
         

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_reuseport"
    description = "Reuse port"
    class options(usage.Options): pass
    def makeService(self, options):
        application = wsgi_hello.application
        pool = threadpool.ThreadPool(minthreads=1, maxthreads=100)
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        root = wsgi.WSGIResource(reactor, pool, application)
        site = server.Site(root)
        endpoint = ListenerWithReuseEndPoint(8000)
        service = tainternet.StreamServerEndpointService(endpoint, site)
        return service
serviceMaker = ServiceMaker()
