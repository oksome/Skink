Skink
=====

Control the DOM from Python using Websockets

Dependencies: Python 3, Tornado

```
pip install skink
```

Description
---

Skink uses Tornado and Websockets to give Python an access to the DOM of all connected users, and get your Python functions called when something is happening on the web page.

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

# Finally, we define a callback on a DOM element:

def callback():
    print('You called a callback')

page.document.getElementById('hello').onclick = callback

# Wait for quitting
input("Press Enter to quit.")
```

Known issues and future development
---

* Only a single page is supported yet
* No arguments can be passed to Python callbacks from JS
* There is no sync, clients who connect late will only get the future instructions
