
from autobahn.twisted.websocket import (
    WebSocketServerProtocol,
    WebSocketServerFactory
)

class SignalingServerProtocol(WebSocketServerProtocol):

    connected_clients = []

    def onOpen(self):
        # Every time we receive a WebSocket connection, we store the
        # reference to the connected client in a class attribute
        # shared amond all Protocol instances. It's a naive implementation
        # but perfect as a simple example.
        self.connected_clients.append(self)
        self.broadcast(str(len(self.connected_clients)))

    def broadcast(self, message):
        """ Send a message to all connected clients

            Params:
                message (str): the message to send
        """
        for client in self.connected_clients:
            client.sendMessage(message.encode('utf8'))

    def onClose(self, wasClean, code, reason):
        # If a client disconnect, we remove the reference from the class
        # attribute.
        self.connected_clients.remove(self)
        self.broadcast(str(len(self.connected_clients)))


if __name__ == '__main__':

    from twisted.internet import reactor

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = SignalingServerProtocol

    print(u"Listening on ws://127.0.0.1:9000")
    reactor.listenTCP(9000, factory)
    reactor.run()
