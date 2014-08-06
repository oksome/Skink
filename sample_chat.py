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

import threading
threading.Thread(target=server.start, args=()).start()

# Second, we wait for Alice and Bob to connect on the page:

print("Open your browser on pages http://localhost:8000/alice and http://localhost:8000/bob")

print('Waiting for clients on pages /alice and /bob ...')
import time
while len(server.LISTENERS.get('/alice', [])) < 1 \
   or len(server.LISTENERS.get('/bob', [])) < 1:
    time.sleep(0.1)
    print('LISTENERS', server.LISTENERS)
print('Got a client')

# Finally, we register the input fields of Alice and Bob to send messages
# to each other by replacing the content of a div.

alice = remote.RemotePage('/alice')
bob = remote.RemotePage('/bob')

alice.document.getElementById('hello').innerHTML = "Hello Alice"
bob.document.getElementById('hello').innerHTML = "Hello Bob"

def alice_keypress():
    z = alice.document.getElementById('message').value._eval()
    bob.document.getElementById('hello2').innerHTML = z

def bob_keypress():
    z = bob.document.getElementById('message').value._eval()
    alice.document.getElementById('hello2').innerHTML = z

alice.document.getElementById('message').onkeypress = alice_keypress
bob.document.getElementById('message').onkeypress = bob_keypress
