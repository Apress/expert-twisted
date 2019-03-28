# coding: utf8

import uuid

from autobahn.twisted.util import sleep
from autobahn.twisted.websocket import (
    WebSocketClientProtocol,
    WebSocketClientFactory
)

from twisted.internet.defer import Deferred, inlineCallbacks


class EchoClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        # Print the server ip address we are connected to
        print(u"Server connected: {0}".format(response.peer))

    @inlineCallbacks
    def onOpen(self):

        print(u"WebSocket connection open.")

        # Send messages every seconds
        i = 0
        while True:
            # Send a text message. You MUST encode it manually.
            self.sendMessage(u"© Hellø wørld {} !".format(i).encode('utf8'))
            # If you send non text data, signal it by setting "isBinary". Here
            # we create a unique random ID, and send it as bytes.
            self.sendMessage(uuid.uuid4().bytes, isBinary=True)
            i += 1
            yield sleep(1)

    def onMessage(self, payload, isBinary):
        # Let's not convert the messages so you an see their raw form
        if isBinary:
            print(u"Binary message received: {!r} bytes".format(payload))
        else:
            print(u"Encoded text received: {!r}".format(payload))

    def onClose(self, wasClean, code, reason):
        print(u"WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    from twisted.internet import reactor

    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory.protocol = EchoClientProtocol

    reactor.connectTCP(u"127.0.0.1", 9000, factory)
    reactor.run()
