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

Skink will keep an open Websocket connection to every browser, and generate Javascript code for the to execute from your Python instructions. It does so in a lazy way and avoids unnecessary roundtrips with the browser. For example, the following two instructions will only result in one instruction being sent to the browser:

```
page.document.getElementById('hello').innerHTML = "Hello You"
```

```
page.document.getElementById('hello').innerHTML = page.document.getElementById('hello2').innerHTML
```

```
page.document.getElementById('hello').onclick = py_callback_function
```

This is done by creating intermediate `skink.remote.JSObject` objects that distinguish between basic types, other JSObjects and callable objects.

Howto
---

Tip: launch with `python -i sample.py` to keep playing with Skink in the Pythin interpreter.

```python
import skink.server as server
import skink.remote as remote

# Start Skink's Tornado server in another thread:
import threading
threading.Thread(target=server.start, args=()).start()

# Get access to the remote page:
page = remote.RemotePage('/')

# Wait for a client to connect:
input("Start doing crazy stuff ?")

# This will send the corresponding JS instruction to be executed in all connected browsers
page.document.getElementById('hello').innerHTML = "Hello You"

# Here, we define a callback on a DOM element:

def callback():
    print('You called a callback')

page.document.getElementById('hello').onclick = callback

# You can also evaluate the content of the DOM:

page.run('window.a = 42')
a = page.eval('a')
assert a == 42

# Wait for quitting
input("Press Enter to quit.")
```

Known issues and future development
---

* Only a single page is supported yet
* No arguments can be passed to Python callbacks from JS
* There is no sync, clients who connect late will only get the future instructions

![Skink photo](https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Garden_skink.jpg/800px-Garden_skink.jpg)

Photo of a garden Skink, Credits [Fir0002/Flagstaffotos](https://commons.wikimedia.org/wiki/File:Garden_skink.jpg)
