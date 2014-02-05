from pygame import *
from math import *
from random import *
from sys import exit

fullscreen = 1
size = (1000, 700)

COLS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]

class Player:
	SIZE = 10
	SPEED = 4
	MARGIN = 2
	ANGLE = 0.07
	angles = [pi/2, -pi/2, pi/4, -pi/4, 0]
	def __init__(self, rect, keya, keyb, i):
		self.keya = keya
		self.keyb = keyb
		self.i = i
		self.rect = rect
		self.x, self.y = randrange(rect.left, rect.right-200), randrange(rect.top+50, rect.bottom-50)
		self.angle = pi/2
		self.col = getcol(i)
		self.winmsg = font.Font(None, 100).render("Player %d wins!" % self.i, 0, self.col)
	
	def draw(self, screen):
		draw.circle(screen, self.col, (int(self.x), int(self.y)), self.SIZE)
	
	def drawWin(self, screen):
		screen.blit(self.winmsg, self.winmsg.get_rect(center=self.rect.center))
	
	def update(self, screen, keys):
		if keys[self.keya]: self.angle += self.ANGLE
		if keys[self.keyb]: self.angle -= self.ANGLE
		for dan in self.angles:
			dx = sin(self.angle+dan)
			dy = cos(self.angle+dan)
			frx = self.x + dx*(self.SIZE+self.MARGIN)
			fry = self.y + dy*(self.SIZE+self.MARGIN)
			if not self.rect.collidepoint(frx, fry) or screen.get_at((int(frx), int(fry))) != (0, 0, 0):
				draw.circle(screen, self.col, (int(self.x), int(self.y)), self.SIZE*2)
				return False
		self.x += dx*self.SPEED
		self.y += dy*self.SPEED
		return True

def isExit(e):
	return (e.type == QUIT) or (e.type == KEYDOWN and e.key == K_ESCAPE)
def isPause(e):
	return e.type == KEYDOWN and e.key == K_SPACE
def isRestart(e):
	return e.type == KEYDOWN and e.key == K_RETURN

def genPlayers(rect):
	return [Player(rect, ka, kb, i) for i, (ka, kb) in enumerate([(K_a, K_s), (K_k, K_l)])]

def getcol(i):
	return tuple(x*255 for x in COLS[i%len(COLS)])

def askPlayers(screen, rect, clock):
	yspace = 150
	f = font.Font(None, 100)
	s1 = ""; s2 = ""; bit = 0
	l = []
	while 1:
		for e in event.get():
			if isExit(e): exit()
			elif e.type == KEYDOWN and e.key == K_SPACE:
				if s1 and s2:
					l.append((s1, s2, k1, k2))
					s1 = ""; s2 = ""; bit = 0
			elif e.type == KEYDOWN and e.key == K_RETURN:
				return [Player(rect, k1, k2, i) for i, (s1, s2, k1, k2) in enumerate(l)]
			elif e.type == KEYDOWN:
				s = key.name(e.key)
				if not bit: s1 = s; k1 = e.key
				else: s2 = s; k2 = e.key
				bit = not bit

		screen.fill((0, 0, 0))
		i = 0
		for (d1, d2, xxx, yyy) in l:
			surf = f.render(d1, 0, getcol(i)); screen.blit(surf, surf.get_rect(topleft=rect.topleft).move(0, yspace*i))
			surf = f.render("Player %d ready!" % i, 0, getcol(i)); screen.blit(surf, surf.get_rect(midtop=rect.midtop).move(0, yspace*i))
			surf = f.render(d2, 0, getcol(i)); screen.blit(surf, surf.get_rect(topright=rect.topright).move(0, yspace*i))
			i += 1
		surf = f.render(s1, 0, getcol(i)); screen.blit(surf, surf.get_rect(topleft=rect.topleft).move(0, yspace*i))
		surf = f.render(s2, 0, getcol(i)); screen.blit(surf, surf.get_rect(topright=rect.topright).move(0, yspace*i))

		display.flip()
		clock.tick(30)

def main():
	init()
	display.set_caption("PYTHON FTW")
	if fullscreen:
		screen = display.set_mode((0,0), NOFRAME | HWSURFACE)
	else:
		screen = display.set_mode(size)
	rect = screen.get_rect()
	clock = time.Clock()
	players = askPlayers(screen, rect, clock)
	screen.fill((0, 0, 0))
	firsttime = True
	while 1:
		for e in event.get():
			if isExit(e): exit()
			if isRestart(e):
				firsttime = True
				players = askPlayers(screen, rect, clock)
				screen.fill((0, 0, 0))

		keys = key.get_pressed()
		for p in players:
			if not p.update(screen, keys):
				print "BOOM"
				players.remove(p)

		for p in players:
			p.draw(screen)
		if len(players) == 1:
			players[0].drawWin(screen)
		display.flip()

		clock.tick(2 if firsttime else 30)
		firsttime = False
		if random() < 0.01: print clock.get_fps()

if __name__ == "__main__":
	main()
