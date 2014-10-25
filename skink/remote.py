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

import threading
import logging
import json

import skink.server as server
from skink.catalog import attributes


def to_js_string(target):
    if type(target) in (str, int, float, bool):
        return json.dumps(target)
    elif type(target) == JSObject:
        return JSObject._command
    else:
        raise TypeError("{} cannot be converted to JS".format(target))


class JSObject(object):

    def __init__(self, name, page, attributes=None):
        """
            Representat a new Javascript object.

            :param name: Name of the object.
            :param page: Reference to the RemotePage.
            :param dir: Additional fiels in dir(self).
        """
        self._command = name
        self._page = page
        self._attributes = attributes if attributes else []

    def __getattr__(self, name):
        return JSObject(self._command + '.' + name, self._page)

    def __setattr__(self, name, value):
        # Default behaviour for _ attributes:
        if name.startswith('_'):
            super(JSObject, self).__setattr__(name, value)
        else:
            if type(value) == JSObject:
                value = value._command
            elif type(value) in (str,):
                value = u'"' + value + u'"'
            elif callable(value):
                server.CALLBACKS[str(id(value))] = value
                value = '''function() {
                    console.log('$%s');
                    skink.call("%s");
                }
                ''' % (str(id(value)), str(id(value)))
            command = self._command + '.' + name + ' = ' + value + ';'
            logging.debug(('__setattr__', name, value, command))
            self._page.run(command)

    def __dir__(self):
        return super().__dir__() + self._attributes

    def __call__(self, *args, **kwargs):
        """
            Return a JSObject that represents the call of the object with
            the given parameters.
        """
        # Converting args to strings, or adding quotes if strings:
        args = [to_js_string(arg) for arg in args]
        command = "{}({})".format(self._command, ', '.join(args))
        return JSObject(command, self._page)

    def __add__(self, other):
        """
            Returns a JSObject that represents the result of the addition
            of two JSObjects.
        """
        return JSObject(
            "( {} + {} )".format(self._command, to_js_string(other)),
            self._page)

    def _run(self):
        """
            Send the command to be executed by all connected clients.
        """
        return self._page.run(self._command)

    def _eval(self):
        """
            Return the value of the element in the first connected client
            in a blocking manner.
        """
        return self._page.eval(self._command)


class RemotePage(object):

    def __init__(self, path):
        '''
            remote: object used to access remote JS code.
        '''
        self.path = path
        self.document = JSObject('document', self,
                                 attributes.get('document'))
        self.window = JSObject('window', self,
                               attributes.get('window'))
        self.alert = JSObject('alert', self,
                              attributes.get('alert'))
        self.prompt = JSObject('prompt', self,
                               attributes.get('prompt'))

    def run(self, command):
        logging.info(('run', [command]))
        for listener in server.LISTENERS.get(self.path, []):
            logging.debug(('listener:', listener))
            listener.write_message('$' + command)

    def eval(self, command):
        'Blocking call, returns the value of the execution in JS'
        event = threading.Event()
        # TODO: Add event to server
        #job_id = str(id(command))
        import random
        job_id = str(random.random())
        server.EVALUATIONS[job_id] = event

        message = '?' + job_id + '=' + command
        logging.info(('message:', [message]))
        for listener in server.LISTENERS.get(self.path, []):
            logging.debug(('listener:', listener))
            listener.write_message(message)

        success = event.wait(timeout=30)

        if success:
            value_parser = server.RESULTS[job_id]
            del server.EVALUATIONS[job_id]
            del server.RESULTS[job_id]
            return value_parser()
        else:
            del server.EVALUATIONS[job_id]
            if job_id in server.RESULTS:
                del server.RESULTS[job_id]
            raise IOError('Evaluation failed.')

    def register(self, callback, name):
        'Register a callback on server and on connected clients.'
        server.CALLBACKS[name] = callback
        self.run('''
            window.skink.%s = function(args=[]) {
                window.skink.call("%s", args);
            }''' % (name, name))

    def on_open(self, function):
        handlers = server.OPEN_HANDLERS.get(self.path, [])
        handlers.append(function)
        server.OPEN_HANDLERS[self.path] = handlers
