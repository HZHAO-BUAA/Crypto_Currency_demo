"""Module containing the server capabilities"""
from bottle import Bottle


class Server:
    """Server class for all the objects that have to be server."""

    def __init__(self, port, relay):
        self.relay = relay
        self.port = port
        self._app = Bottle()
        self._route()

    def _route(self):
        self._app.route("/", method="GET", callback=self.index)

    def startServer(self):
        self._app.run(host='localhost', port=self.port)

    def index(self):
        return str(self.port)
