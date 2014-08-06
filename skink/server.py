# -*- coding:Utf-8 -*-

# Copyright (c) 2014 "OKso http://okso.me"
#
# This file is part of Skink.
#
# Intercom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import random
import threading
import logging
import json

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

from os.path import dirname, realpath, join, isfile

LISTENERS = {}
CALLBACKS = {}
EVALUATIONS = {}
RESULTS = {}

STATIC_PATH = dirname(realpath(__file__))
print('STATIC_PATH', [STATIC_PATH])


def launch_exception(message):
    error_name = message['name']
    error_descr = message['description']
    mapping = {
        'ReferenceError': NameError,
    }
    if message['name'] in mapping:
        raise mapping[error_name](error_descr)
    else:
        raise Exception('{}: {}'.format(error_name, error_descr))


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        index_path = 'static/index.html' if isfile('static/index.html') \
                     else join(STATIC_PATH, 'static/index.html')

        self.write(open(index_path).read()
                   % {'username': "User%d" % random.randint(0, 100)})


class ScriptFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/javascript")
        self.write(open(join(STATIC_PATH, 'static/skink.js')).read()
                   % {'username': "User%d" % random.randint(0, 100)})


class StylesheetFileHandler(tornado.web.RequestHandler):
    def get(self):
        index_path = 'static/style.css' if isfile('static/style.css') \
                     else join(STATIC_PATH, 'static/style.css')

        self.write(open(index_path).read())


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        path = self.page_path()
        listeners = LISTENERS[path] = LISTENERS.get(path, [])
        listeners.append(self)

    def on_message(self, message):
        logging.debug(('on_message', message))

        msg = json.loads(message)

        if msg['action'] == 'callback':
            logging.debug('callback')
            callback_id = msg['callback']
            if callback_id in CALLBACKS:
                logging.debug(('calling callback in a thread:', callback_id))
                callback = CALLBACKS[callback_id]
                args = msg.get('args', ())
                threading.Thread(target=callback, args=args).start()
                logging.debug('done (in a thread)')
                self.write_message('done')
            else:
                logging.debug('unknown callback')
                self.write_message('unknown callback')

        # Return value (or exception) from an eval:
        elif msg['action'] == 'eval':
            callback_id = msg['callback']
            value = msg['value']
            logging.debug(('callback_id', callback_id, 'value', value))
            if callback_id in EVALUATIONS:
                RESULTS[callback_id] = lambda: value
                EVALUATIONS[callback_id].set()
                logging.debug('gone')
                self.write_message('gone')
            else:
                logging.debug('unknown callback')
                self.write_message('unknown callback')

        elif msg['action'] == 'exception':
            callback_id = msg['callback']
            logging.warn("Exception")
            if callback_id in EVALUATIONS:
                RESULTS[callback_id] = lambda: launch_exception(msg)
                EVALUATIONS[callback_id].set()
            else:
                logging.debug('unknown callback')
                self.write_message('unknown callback')
        else:
            logging.debug('not found')
            self.write_message('not found')

    def on_close(self):
        LISTENERS[self.page_path()].remove(self)

    def page_path(self):
        return self.request.uri.split('?', 1)[1]


settings = {
    'auto_reload': True,
}

application = tornado.web.Application([
    (r'/', IndexPageHandler),
    (r'/alice', IndexPageHandler),
    (r'/bob', IndexPageHandler),
    (r'/skink.js', ScriptFileHandler),
    (r'/style.css', StylesheetFileHandler),
    (r'/realtime/', RealtimeHandler),
], **settings)


def start():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
