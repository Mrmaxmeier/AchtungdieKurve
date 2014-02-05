import socket
from supersocket import *
import threading
import time


PORT = 45739


class Player:
	def __init__(self, name, id, socket, server, ip):
		self.name = name
		self.id = id
		self.position = [0,0]
		self.rotation = 0
		self.lastPositions = []
		self.socket = socket
		self.server = server
		self.isReady = False
		self.isDead = False
		self.ip = ip
		self.forceStart = False
	
	def update(self, dictionary = {}):
		dict = dictionary
		if "rot" in dict:
			self.rotation = dict["rot"]
		if "pos" in dict:
			self.position = dict["pos"]
		if "ready" in dict:
			self.isReady = dict["ready"]
		if "reset" in dict:
			self.server.needsReset = dict["reset"]
		if "dead" in dict:
			self.isDead = dict["dead"]
		if "forcestart" in dict:
			self.forceStart = dict["forcestart"]
		if not self.position in self.lastPositions:
			self.lastPositions.append(self.position)
	
	def getownPlayerInfo(self):
		dict = {"playerName":self.name, "playerID":self.id, "rot":self.rotation, "lastPositions": self.lastPositions}
		return repr(dict)
	
	
	def handle(self, send):
		def callback(msg):
			print("%d received: %s" % (id(send), msg))
			if not msg:
				return
			try:
				dict = eval(msg)
			except:
				dict = {}
				print("FEHELER BAIM EVALLEN: ", msg)
			self.update(dict)
			
		return callback
	
	




class Server(threading.Thread):
	def __init__(self, host, port):

		threading.Thread.__init__(self, daemon=True)
		
		self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversock.bind((host, port))
		self.serversock.listen(5)
		
		self.idtobegiven = 1
		
		self.scoreboard = {}
		
		self.id2player = {}
		self.playerList = []
		self.gameRunning = False
		self.needsReset = False
	
	
	def serve(self):
		try:
			while self.isAlive:
				(sock, addr) = self.serversock.accept()
				print("SOMEBODEY JOIINEAAD")
				socket = SuperSocket(sock)
				playerobj = Player("Deinemudda", self.idtobegiven, socket, self, addr)
				self.id2player[playerobj.id] = playerobj
				self.idtobegiven += 1
				self.playerList.append(playerobj)
				callback = playerobj.handle(socket.send)
				socket.listen(callback)
				self.scoreboard[playerobj.ip] = 0
				if started:
					socket.send("start")
					socket.flush()
				print("Finished creating %s" % str(addr))
		finally:
			self.serversock.close()
	
	
	def resolveList(self, str):
		#if str.startswith("[") and str.endswith("]"):
		iii = None
		if str[0] == "[" and str[-1] == "]":
			str = str[1:-1]
			iii = []
			for ii in b.split(","):
				self.resolveList(iii)
				iii.append(ii)
			b = iii
		if iii:
			return iii
		else:
			return str
	
	
	
	
	def run(self):
		self.serve()

	def listen(self, callback):
		self.callback = callback
		self.start()
	


server = Server("0.0.0.0", PORT)

def callback():
	pass

server.listen(callback)

running = True
started = False


def genScoreboard():
	msg = []
	for (ip, score) in sorted(server.scoreboard, key=server.scoreboard.get):
		msg.append(str(ip)+":"+str(score))
	msg = "\n".join(msg)
	print(msg)
	return msg



while running:
	if started:
		if len(server.playerList) > 1:
			d = 0
			winningplayer = None
			for p in server.playerList:
				if p.isDead:
					d += 1
				else:
					winningplayer = p
			if d + 1 == len(server.playerList):
				print("Neues Spiel, gewinner:",winningplayer.id)
				winningplayer.socket.send("victory")
				winningplayer.socket.flush()
				scr = genScoreboard()
				for p in server.playerList:
					p.socket.send("text "+scr)
					p.socket.flush()
		
		
		
		for p in server.playerList:
			p.update()
			for op in server.playerList:
				info = p.getownPlayerInfo()
				if op is not p:
					op.socket.send(info)
			p.lastPositions = []
		time.sleep(0.1)
		
		if server.needsReset:
			started = False
			server.gamerunning = False
			server.needsReset = False
			for player in server.playerList:
				player.isReady = False
				player.isDead = False
				player.socket.send("clear")
				player.socket.flush()
		
		
	else:
		started = True
		for p in server.playerList:
			if not p.isReady:
				started = False
		if server.playerList == []:
			started = False
		for p in server.playerList:
			if p.forceStart:
				p.forceStart = False
				print("Forcestarting")
				started = True
		if started:
			print("The Game will begin NOW")
			for p in server.playerList:
				p.socket.send("start")
				p.socket.flush()
