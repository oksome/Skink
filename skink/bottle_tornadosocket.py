# -*- coding:Utf-8 -*-
#
# This file comes from bottle-tornadosocket
# https://github.com/cime/bottle-tornadosocket

from bottle import ServerAdapter

class TornadoWebSocketServer(ServerAdapter):
    """ The super hyped asynchronous server by facebook. Untested. """
    def run(self, handler): # pragma: no cover
        import tornado.wsgi, tornado.httpserver, tornado.ioloop

        default_handlers = [
            (r".*", tornado.web.FallbackHandler, { 'fallback': tornado.wsgi.WSGIContainer(handler) })
        ]

        if self.options['handlers'] is not None and isinstance(self.options['handlers'], list):
            handlers = list(self.options['handlers']) + list(default_handlers)
        else:
            handlers = default_handlers

        tornado_app = tornado.web.Application(handlers)
        tornado.httpserver.HTTPServer(tornado_app).listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
