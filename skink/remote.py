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


class JSObject(object):

    def __init__(self, name, page):
        self._command = name
        self._page = page

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

    def __call__(self, *args, **kwargs):
        # Converting args to strings, or adding quotes if strings:
        args = ['"' + arg + '"' if type(arg) == str else str(arg) for arg in args]
        command = self._command + '(' + ', '.join(args) + ')'
        return JSObject(command, self._page)

    def _run(self):
        return self._page.run(self._command)

    def _eval(self):
        return self._page.eval(self._command)


class RemotePage(object):

    def __init__(self, path):
        '''
            remote: object used to access remote JS code.
        '''
        self.path = path
        self.document = JSObject('document', self)
        self.window = JSObject('window', self)
        self.alert = JSObject('alert', self)
        self.prompt = JSObject('prompt', self)

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
