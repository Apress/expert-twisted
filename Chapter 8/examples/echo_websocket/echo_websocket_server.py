
import uuid

from autobahn.twisted.websocket import (
    WebSocketServerProtocol,
    WebSocketServerFactory
)


class EchoServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        """Called when a client is connecting to us"""
        # Print the IP address of the client this protocol instance is serving
        print(u"Client connecting: {0}".format(request.peer))

    def onOpen(self):
        """Called when the WebSocket connection has been opened"""
        print(u"WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        """Called for each WebSocket message received from this client

            Params:

                payload (str|bytes): the content of the message
                isBinary (bool): wether the message contains (False) encoded text
                                 or non textual data (True). Default is False.
        """
        # Simply prints any message we receive
        if isBinary:
            # This is a binary message and can contains pretty much anything.
            # Here we recreate the UUID from the bytes the client sent us.
            uid = uuid.UUID(bytes=payload)
            print(u"UUID received: {}".format(uid))
        else:
            # This is encoded text. Please note that is is NOT decoded for you,
            # isBinary is merely a courtesy flag manually set by the client
            # on each message. You must know the charset used (here utf8),
            # and call ".decode()" on the bytes object to get a string object.
            print(u"Text message received: {}".format(payload.decode('utf8')))

        # It's an echo server, so let's send back everything it receives
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        """Called when the WebSocket connection for this client closes

            Params:

                wasClean (bool): wether we were told the connection was going
                                 to be closed or if it just happened.
                code (int): any code among WebSocketClientProtocol.CLOSE_*
                reason (str): a message stating the reason the connection
                              was closed, in plain english.
        """
        print(u"WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    from twisted.internet import reactor

    # The WebSocket protocol netloc is WS. So WebSocket URLs looks exactly
    # like HTTP URLs, but replacing HTTP with WS.
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = EchoServerProtocol

    print(u"Listening on ws://127.0.0.1:9000")
    reactor.listenTCP(9000, factory)
    reactor.run()
