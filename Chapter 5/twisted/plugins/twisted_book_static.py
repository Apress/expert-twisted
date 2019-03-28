from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, strports
from twisted.web import static, server
from twisted.internet import reactor

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_static"
    description = "Static for book"
    class options(usage.Options):
        pass
    def makeService(self, options):
        root = static.File('static')
        site = server.Site(root)
        return strports.service('tcp:8000', site)
serviceMaker = ServiceMaker()
