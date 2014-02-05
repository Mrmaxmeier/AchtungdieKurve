from pygame import *
from math import *
from random import *
from socket import *
from supersocket import *
from threading import Thread
#from sys import exit
import os
exit = os._exit

fullscreen = 0
size = (1280, 720)

COLS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]

class Player:
	SIZE = 10
	SPEED = 4 * 30
	MARGIN = 2
	ANGLE = 0.07 * 30
	angles = [pi/2, -pi/2, pi/4, -pi/4, 0]
	def __init__(self, rect, keya, keyb, i, sock):
		self.sock = sock
		self.keya = keya
		self.keyb = keyb
		self.i = i
		self.rect = rect
		self.col = getcol(i)
		self.font = font.Font(None, 100)
		self.winmsg = self.font.render("EPIC WIN!!!", 0, self.col)
		self.reset()
	
	def reset(self):
		self.started = False
		self.won = False
		self.dead = False
		self.x, self.y = randrange(self.rect.left, self.rect.right-200), randrange(self.rect.top+50, self.rect.bottom-50)
		self.angle = pi/2
	
	def draw(self, screen):
		draw.circle(screen, self.col, (int(self.x), int(self.y)), self.SIZE)
		if self.won: self.drawWin(screen)
	
	def drawWin(self, screen):
		screen.blit(self.winmsg, self.winmsg.get_rect(center=self.rect.center))
	
	def drawText(self, text, screen):
		for i, line in enumerate(text.split("\n")):
			textimg = self.font.render(line, 0, self.col)
			screen.blit(textimg, textimg.get_rect(topleft=self.rect.topleft).move(0, i*100))
	
	def update(self, screen, keys, dt):
		if keys[self.keya]: self.angle += self.ANGLE*dt
		if keys[self.keyb]: self.angle -= self.ANGLE*dt
		for dan in self.angles:
			dx = sin(self.angle + dan)
			dy = cos(self.angle + dan)
			frx = self.x + dx*(self.SIZE+self.MARGIN)
			fry = self.y + dy*(self.SIZE+self.MARGIN)
			if not self.rect.collidepoint(frx, fry) or screen.get_at((int(frx), int(fry))) != (0, 0, 0):
				draw.circle(screen, self.col, (int(self.x), int(self.y)), self.SIZE*2)
				self.dead = True
				return False
		self.x += dx*self.SPEED*dt
		self.y += dy*self.SPEED*dt
		self.sock.send(repr({"pos": [int(self.x), int(self.y)]}))
		return True

def isExit(e):
	return (e.type == QUIT) or (e.type == KEYDOWN and e.key == K_ESCAPE)
def isStart(e):
	return e.type == KEYDOWN and e.key == K_RETURN
def isForceStart(e):
	return e.type == KEYDOWN and e.key == K_1
def isReset(e):
	return e.type == KEYDOWN and e.key == K_BACKSPACE

def getcol(i):
	return tuple(x*255 for x in COLS[i%len(COLS)])

def askPlayerSock(screen, rect, clock):
	yspace = 150
	f = font.Font(None, 100)
	s1 = ""; s2 = ""; bit = 0
	running = 1
	nframes = 0
	while running:
		for e in event.get():
			if isExit(e): exit(0)
			elif e.type == KEYDOWN and e.key == K_RETURN:
				if s1 and s2:
					running = 0
			elif e.type == KEYDOWN:
				#try:
				#	s = repr(e.unicode)
				#except ex:
				#	s = ""
				#if not s: s = "<%d>" % e.key
				s = key.name(e.key)
				if not bit: s1 = s; k1 = e.key
				else: s2 = s; k2 = e.key
				bit = not bit

		screen.fill((0, 0, 0))
		surf = f.render(s1, 0, getcol(0)); screen.blit(surf, surf.get_rect(topleft=rect.topleft))
		surf = f.render("Tasten eingeben!", 0, getcol(0)); screen.blit(surf, surf.get_rect(midtop=rect.midtop))
		surf = f.render(s2, 0, getcol(0)); screen.blit(surf, surf.get_rect(topright=rect.topright))
		draw.circle(screen, (nframes%256, 0, nframes%256), (0, 0), 15)

		display.flip()
		clock.tick(30)
		nframes += 10
	try:
		file = open(".ip", "r")
		ip = file.readline()
		file.close()
	except:
		ip = "ip"
	while 1:
		for e in event.get():
			if isExit(e): exit(0)
			elif e.type == KEYDOWN and e.key == K_RETURN:
				screen.fill((0, 255, 255))
				display.flip()
				file = open(".ip", "w")
				file.write(ip)
				file.close()
				sock = socket()
				sock.connect((ip, 1339))
				supersock = SuperSocket(sock)
				player = Player(rect, k1, k2, 0, supersock)
				return (player, supersock)
			elif e.type == KEYDOWN and e.key == K_BACKSPACE:
				ip = ip[:-1]
			elif e.type == KEYDOWN:
				try:
					ip += e.unicode
				except ex:
					pass

		screen.fill((0, 0, 0))
		surf = f.render("IP eingeben:", 0, (255, 255, 255)); screen.blit(surf, surf.get_rect(topleft=rect.topleft))
		surf = f.render(ip, 0, (255, 255, 255)); screen.blit(surf, surf.get_rect(topright=rect.topright))
		draw.circle(screen, (nframes%256, 0, nframes%256), (0, 0), 15)
		nframes += 10

		display.flip()
		clock.tick(30)

def callback(screen, l, player):
	def f(text):
		print "f called: ", text
		if not text: return
		elif text == "start":
			player.started = True
		elif text == "clear":
			screen.fill((0, 0, 0))
			player.reset()
		elif text == "victory":
			player.won = True
		elif text.startswith("text"):
			t, m, text = text.partition(" ")
			player.drawText(text, screen)
		else:
			try:
				d = eval(text)
				col = getcol(d["playerID"])
				recvd = d["lastPositions"]
				for pos in recvd:
					l.append((col, tuple(pos)))
			except: pass
	return f

def main():
	init()
	display.set_caption("PYTHON MULTIPLAYER FTW")
	if fullscreen:
		screen = display.set_mode((0,0), NOFRAME | HWSURFACE)
	else:
		screen = display.set_mode(size)
	rect = screen.get_rect()
	clock = time.Clock()
	player, sock = askPlayerSock(screen, rect, clock)
	l = []
	sock.listen(callback(screen, l, player))
	screen.fill((0, 0, 0))
	nframes = 0
	while 1:
		for e in event.get():
			if isExit(e): exit(0)
			if isStart(e):
				sock.send(repr({"ready": True}))
				sock.flush()
			if isForceStart(e):
				sock.send(repr({"forcestart": True}))
				sock.flush()
			if isReset(e):
				sock.send(repr({"reset": True}))
				sock.flush()

		keys = key.get_pressed()
		if (not player.dead) and player.started:
			if not player.update(screen, keys, clock.get_time()/1000.0):
				print "BOOM"
				sock.send(repr({"dead": True}))
				sock.flush()
		#else: print "not started:", player.started

		player.draw(screen)
		for x in l:
			col, pos = x
			print "drawing", pos, col, Player.SIZE
			draw.circle(screen, col, pos, Player.SIZE)
			#draw.line(screen, col, (100, 100), pos, 5)
			l.remove(x)
		draw.circle(screen, (nframes%256, 0, nframes%256), (0, 0), 15)
		display.flip()

		clock.tick(30)
		if random() < 0.01: print clock.get_fps()
		nframes += 10

if __name__ == "__main__":
	main()
