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

'''
Example of using Skink to build a (very) minimalist web messaging app.
'''

# First, we start the Tornado server:

import logging
logging.basicConfig(level=logging.DEBUG)

import skink.server as server
import skink.remote as remote

from bottle import Bottle
b = Bottle()


@b.get('/alice')
@b.get('/bob')
def alice():
    return '''
        <html>
            <head>
                <meta charset="utf-8" />
                <link rel="stylesheet" type="text/css" href="/skink/style.css">
            </head>
            <body>
                <h1>My super simple chat</h1>

                <div id='stderr'></div>

                <div id='hello'>
                    Hello !
                </div>
                <div id='hello2'>
                    Hello2 !
                </div>

                <div>
                    <input id='message' />
                </div>

                <script type='application/javascript' src='/skink/skink.js'>
                </script>
            </body>
        </html>
    '''

server.start_thread(b, port=9000)

# Second, we wait for Alice and Bob to connect on the page:

print("Open your browser on pages http://localhost:8000/alice "
      "and http://localhost:8000/bob")

# Finally, we register the input fields of Alice and Bob to send messages
# to each other by replacing the content of a div.

alice = remote.RemotePage('/alice')
bob = remote.RemotePage('/bob')


def alice_keypress():
    z = alice.document.getElementById('message').value._eval()
    bob.document.getElementById('hello2').innerHTML = 'Alice says: ' + z


def bob_keypress():
    z = bob.document.getElementById('message').value._eval()
    alice.document.getElementById('hello2').innerHTML = 'Bob says: ' + z


@alice.on_open
def alice_open():
    alice.document.getElementById('hello').innerHTML = "Hello Alice"
    alice.document.getElementById('message').onkeypress = alice_keypress


@bob.on_open
def bob_open():
    bob.document.getElementById('hello').innerHTML = "Hello Bob"
    bob.document.getElementById('message').onkeypress = bob_keypress
