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

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

from os.path import dirname, realpath, join, isfile

LISTENERS = []
CALLBACKS = {}
EVALUATIONS = {}
RESULTS = {}

STATIC_PATH = dirname(realpath(__file__))
print('STATIC_PATH', [STATIC_PATH])


def parse(prefix, result):
    '''
    Parses the result from JS message, transforms type and raises
    the appropriate exception if required.
    '''
    if prefix == '?':
        jstype, value = result.split(':', 1)
        mapping = {
            'number': float,
        }
        return mapping.get(jstype, str)(value)
    elif prefix == '!':
        error_name, error_message = result.split(':', 1)
        mapping = {
            'ReferenceError': NameError,
        }
        if error_name in mapping:
            raise mapping[error_name](error_message)
        else:
            raise Exception('{}: {}'.format(error_name, error_message))


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        index_path = 'static/index.html' if isfile('static/index.html') \
                     else join(STATIC_PATH, 'static/index.html')

        self.write(open(index_path).read()
                   % {'username': "User%d" % random.randint(0, 100),
                      'host': 'localhost',
                      'port': 8000})


class ScriptFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/javascript")
        self.write(open(join(STATIC_PATH, 'static/skink.js')).read()
                   % {'username': "User%d" % random.randint(0, 100),
                      'host': 'localhost',
                      'port': 8000})


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('Client connected')
        LISTENERS.append(self)

    def on_message(self, message):
        logging.debug(('on_message', message))

        # Execute a callback:
        if message.startswith('$'):
            logging.debug('$')
            callback_id = message[1:]
            if callback_id in CALLBACKS:
                logging.debug(('calling callback in a thread:', callback_id))
                callback = CALLBACKS[callback_id]
                threading.Thread(target=callback, args=()).start()
                logging.debug('done (in a thread)')
                self.write_message('done')
            else:
                logging.debug('unknown callback')
                self.write_message('unknown callback')

        # Return value (or exception) from an eval:
        elif message.startswith('?') or message.startswith('!'):
            logging.debug(message[0])
            callback_id, result = message[1:].split('=', 1)
            logging.debug(('callback_id', callback_id, 'result', result))
            if callback_id in EVALUATIONS:
                RESULTS[callback_id] = lambda: parse(message[0], result)
                EVALUATIONS[callback_id].set()
                logging.debug('gone')
                self.write_message('gone')
            else:
                logging.debug('unknown callback')
                self.write_message('unknown callback')

        else:
            logging.debug('not found')
            self.write_message('not found')

    def on_close(self):
        LISTENERS.remove(self)


settings = {
    'auto_reload': True,
}

application = tornado.web.Application([
    (r'/', IndexPageHandler),
    (r'/skink.js', ScriptFileHandler),
    (r'/realtime/', RealtimeHandler),
], **settings)


def start():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
