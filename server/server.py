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
		self.bucket = []
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
		if "pos" in dict and not self.position in self.lastPositions:
			self.lastPositions.append(self.position)
	
	def delPoss(self):
		self.movePoss()
		self.bucket = []

	def movePoss(self):
		self.bucket += self.lastPositions
		self.lastPositions = []

	def getOwnPlayerInfo(self, bucket=False):
		if bucket:	poss = self.bucket
		else:		poss = self.lastPositions
		return repr({"playerName":self.name, "playerID":self.id, "rot":self.rotation, "lastPositions": poss})
	
	
	def handle(self, send):
		def callback(msg):
			print("%d received: %s" % (self.id, msg))
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
		self.started = False
		self.starting = False
		self.won = False
	
	
	def serve(self):
		try:
			while self.isAlive:
				(sock, (ip, port)) = self.serversock.accept()
				print("SOMEBODEY JOIINEAAD")
				socket = SuperSocket(sock)
				playerobj = Player("Deinemudda", self.idtobegiven, socket, self, ip)
				self.id2player[playerobj.id] = playerobj
				self.idtobegiven += 1
				self.playerList.append(playerobj)
				callback = playerobj.handle(socket.send)
				socket.listen(callback)
				self.scoreboard[playerobj.ip] = 0
				if self.started:
					for op in self.playerList:
						if op is not playerobj:
							socket.send(op.getOwnPlayerInfo(True))
					socket.send("start")
					socket.flush()
				print("Finished creating %s" % ip)
		finally:
			self.serversock.close()
	
	
	def run(self):
		self.serve()


server = Server("0.0.0.0", PORT)
server.start()


def genScoreboard():
	def snd(x): return -x[1]
	return "\n".join(["%d.: %s mit %d" % (i+1, ip.split(".")[-1], score)
		for i, (ip, score) in enumerate(sorted(server.scoreboard.items(), key=snd))])



while 1:
	for p in server.playerList:
		if not p.socket.isAlive:
			print("killing dead sock!")
			server.playerList.remove(p)
	if server.started:
		if server.starting:
			print("................starting................")
			for p in server.playerList:
				p.delPoss()
			server.starting = False
		if len(server.playerList) > 1 and not server.won:
			d = 0
			winningplayer = None
			for p in server.playerList:
				if p.isDead:
					d += 1
				else:
					winningplayer = p
			if d + 1 == len(server.playerList):
				print("Neues Spiel, gewinner:",winningplayer.id)
				server.won = True
				server.scoreboard[winningplayer.ip] += 1
				winningplayer.socket.send("victory")
				winningplayer.socket.flush()
				scr = genScoreboard()
				for p in server.playerList:
					p.socket.send("text "+scr)
					p.socket.flush()
		
		
		print("broadcasting positions...")
		for p in server.playerList:
			for op in server.playerList:
				info = p.getOwnPlayerInfo()
				if op is not p:
					op.socket.send(info)
			p.movePoss()
		time.sleep(0.1)
		
		if server.needsReset:
			server.started = False
			server.needsReset = False
			server.won = False
			for player in server.playerList:
				player.isReady = False
				player.isDead = False
				player.delPoss()
				player.socket.send("clear")
				player.socket.flush()
	else:
		start = True
		for p in server.playerList:
			if not p.isReady:
				start = False
		if server.playerList == []:
			start = False
		for p in server.playerList:
			if p.forceStart:
				p.forceStart = False
				print("Forcestarting")
				start = True
		if start:
			print("The Game will begin NOW")
			server.started = True
			server.starting = True
			for p in server.playerList:
				p.socket.send("start")
				p.socket.flush()
