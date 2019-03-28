import pkg_resources

from zope import interface

from twisted.python import usage, threadpool
from twisted import plugin
from twisted.application import service, strports
from twisted.web import static, server, resource
from twisted.internet import reactor

@interface.implementer(service.IServiceMaker, plugin.IPlugin)
class ServiceMaker(object):
    tapname = "twisted_book_pkg_resources"
    description = "Static for book"
    class options(usage.Options):
        pass
    def makeService(self, options):
        root = resource.Resource()
        fname = pkg_resources.resource_filename("static_server", "a_file.html")
        static_resource = static.File(fname)
        root.putChild('', static_resource)
        site = server.Site(root)
        return strports.service('tcp:8000', site)
serviceMaker = ServiceMaker()
