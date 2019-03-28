from twisted.internet import task, defer, endpoints, protocol
from twisted.protocols import amp

from twisted.plugins import twisted_book_configure

@task.react
@defer.inlineCallbacks
def main(reactor):
    endpoint = endpoints.TCP4ClientEndpoint(reactor, "127.0.0.1", 8001)
    prot = yield endpoint.connect(protocol.Factory.forProtocol(amp.AMP))
    res1 = yield prot.callRemote(twisted_book_configure.GetCapitalize)
    res2 = yield prot.callRemote(twisted_book_configure.GetExclaim)
    print(res1['value'], res2['value'])
    yield prot.callRemote(twisted_book_configure.SetCapitalize, value=0.5)
    yield prot.callRemote(twisted_book_configure.SetExclaim, value=0.5)
    res1 = yield prot.callRemote(twisted_book_configure.GetCapitalize)
    res2 = yield prot.callRemote(twisted_book_configure.GetExclaim)
    print(res1['value'], res2['value'])
