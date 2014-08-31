Skink
=====

Control the DOM from Python using Websockets

Dependencies: Python 3, Tornado, Bottle

```
pip install skink
```

Proof of Concept
---

Skink is a Proof of Concept and under development. Even when stable and ready, there will still be plenty of good reasons not to use it in production.

Description
---

Skink uses Tornado and Websockets to give Python an access to the DOM of all connected users, and get your Python functions called when something is happening on the web page. It also has a blocking mode you can use to get the value of an element without using callbacks.

Skink will keep an open Websocket connection to every browser, and generate Javascript code for the browser to execute from your Python instructions. It does so in a lazy way and avoids unnecessary roundtrips with the browser. For example, the following two instructions will only result in one instruction being sent to the browser:

```python
page.document.getElementById('hello').innerHTML = "Hello You"
```

```python
page.document.getElementById('hello').innerHTML = page.document.getElementById('hello2').innerHTML
```

This is done by creating intermediate `skink.remote.JSObject` objects that distinguish between basic types, other JSObjects and callable objects.

Skink integrates with the [Bottle Web Framework](http://bottlepy.org/) for exposing standard HTTP resources.

Advanced Features
---

Register Python callbacks directly on JavaScript events:

```python
def my_python_function():
    print("Hello from Python")

page.document.getElementById('hello').onclick = my_python_function
```

Decorate functions that have to be called everytime a new client connects to a page:

```python
@page.on_open
def page_open():
    bob.document.getElementById('hello').innerHTML = "Hello You"
    bob.document.getElementById('message').onkeypress = my_python_function
```

Expose arbitrary Python functions to Javascript clients:

```python
def my_python_sum(a, b):
    print(a + b)

page.register(my_python_function, 'my_function')
```
From Javascript:
```javascript
skink.call('sum', [1, 2]);
```

Run arbitrary Javascript code in a page's clients:
```python
page.run("alert('Hello!');")
```

Example
---

Tip: launch with `python -i sample.py` to keep playing with Skink in the Python interpreter.

```python
import skink.server as server
import skink.remote as remote

from bottle import Bottle

# Define the static HTTP views with Bottle.py
b = Bottle()

@b.get('/alice')
@b.get('/bob')
def alice():
    return '''
        <html>
            <head>
                <meta charset="utf-8" />
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

                <script type='application/javascript' src='/skink/skink.js'></script>
            </body>
        </html>
    '''

# Start the web(socket) server with the Bottle app:
server.start_thread(b)

# Define the remote pages you want to control:
alice = remote.RemotePage('/alice')
bob = remote.RemotePage('/bob')

# Define the Python callbacks.
def alice_keypress():
    z = alice.document.getElementById('message').value._eval()
    bob.document.getElementById('hello2').innerHTML = 'Alice says: ' + z


def bob_keypress():
    z = bob.document.getElementById('message').value._eval()
    alice.document.getElementById('hello2').innerHTML = 'Bob says: ' + z

# Register the callbacks every time a client connects:
@alice.on_open
def alice_open():
    alice.document.getElementById('hello').innerHTML = "Hello Alice"
    alice.document.getElementById('message').onkeypress = alice_keypress


@bob.on_open
def bob_open():
    bob.document.getElementById('hello').innerHTML = "Hello Bob"
    bob.document.getElementById('message').onkeypress = bob_keypress

print("Open your browser on pages http://localhost:8000/alice and http://localhost:8000/bob")
```

![Skink photo](https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Garden_skink.jpg/800px-Garden_skink.jpg)

Photo of a garden Skink, Credits [Fir0002/Flagstaffotos](https://commons.wikimedia.org/wiki/File:Garden_skink.jpg)
