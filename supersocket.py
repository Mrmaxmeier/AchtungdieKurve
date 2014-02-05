import threading

class SuperSocket(threading.Thread):
	packsize = 1
	def __init__(self, sock):
		threading.Thread.__init__(self)
		self.sock = sock
		#self.sock.setblocking(False)
		self.inBuf = ""
		self.isAlive = True
		self.toSend = ""
		self.packi = 0

	def send(self, msg):
		print "Sending: ", msg
		self.toSend += msg + "\0"
		self.packi += 1
		if not self.packi % self.packsize: self.flush()
	
	def flush(self):
		print "SEND"
		try:
			self.sock.send(self.toSend)
			self.toSend = ""
		except Exception as e:
			print("Exception while sending:", e)
			self.isAlive = False
			return e

	def recv(self, chsize=1024):
		try:
			while not "\0" in self.inBuf:
				recvd = self.sock.recv(chsize).decode("UTF-8")
				if not recvd:
					print("Connection closed!")
					self.isAlive = False
					return None
				self.inBuf += recvd
		except Exception as e:
			print("Exception while recving:", e)
			self.isAlive = False
			return e
		msg, _, self.inBuf = self.inBuf.partition("\0")
		return msg

	def run(self):
		while self.isAlive:
			self.callback(self.recv())

	def listen(self, callback):
		self.callback = callback
		self.start()

	def close(self):
		self.isAlive = False
		self.sock.close()
