
### WebPocket

Actor-model based WebSocket client in Python

#### Example

```python
from webpocket import WebPocket

class Client(WebPocket):
	def __init__(self, url):
		super(Client, self).__init__(url)
		self.ready = False

	def on_open(self):
		print 'opened'
		self.ready = True

	def on_text(self, text):
		print 'received:', text

if __name__ == '__main__':

	pocket = Client('ws://localhost/websocket/echo', run=True)

	import time
	try:
		while True:
			time.sleep(3)
			if pocket.ready:
				pocket.send('hello')
	except KeyboardInterrupt:
		pocket.close()
```
