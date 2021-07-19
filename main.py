##########################################
# Author: Manbir Singh Judge
# Date: 12-7-2021 to 13-7-2021
# Todo: Background Music, Help Menu, Settings Menu, Support for Arrow Keys, Different speed of ships, bullets of enemies become for powerfull and freqeunt and level increases
# Tools Used ( except Comipler etc. ): Sublime Text 3
##########################################

import pygame
import os
import time
import random
import sys

pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invader by Manbir Singh Judge')

# Space Ships
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))  # Player's Ship

# Lasers
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))


# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (WIDTH, HEIGHT))

# SFX
CHANNEL_0 = pygame.mixer.Channel(0)
CHANNEL_1 = pygame.mixer.Channel(1)
CHANNEL_2 = pygame.mixer.Channel(2)

BOOM_SOUND = pygame.mixer.Sound('assets/sounds/boom.wav')
SHOOT_SOUND = pygame.mixer.Sound('assets/sounds/laser_1.mp3')
LOST_SOUND = pygame.mixer.Sound('assets/sounds/lost.mp3')

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 0)

	def collision(self, obj):
		return collide(self, obj)


class Ship:
	COOLDOWN = 1  # How Fast Can you Shoot Lasers ( If FPS = 60 and COOLDOWN = 30, then Delay In Shooting will be Half a Second )

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))

		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()

		for laser in self.lasers:
			laser.move(vel)

			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)

			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	# CONFUSE
	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0

		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	# CONFUSE
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)

			self.cool_down_counter = 1

			if self.ship_img == YELLOW_SPACE_SHIP:
				CHANNEL_0.play(SHOOT_SOUND)


	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()


class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
 
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def draw(self, window):
		super().draw(window)

		self.health_bar(window)

	def move_lasers(self, vel, objs):
		self.cooldown()

		for laser in self.lasers:
			laser.move(vel)

			if laser.off_screen(HEIGHT):                                          
				self.lasers.remove(laser)

			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)

						if laser in self.lasers:
							self.lasers.remove(laser)

						CHANNEL_1.play(BOOM_SOUND)

	def health_bar(self, window):
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,  self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,  self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
	COLOR_MAP = {
		'red': (RED_SPACE_SHIP, RED_LASER),
		'blue': (BLUE_SPACE_SHIP, BLUE_LASER),
		'green': (GREEN_SPACE_SHIP, GREEN_LASER),
	}

	def __init__(self, x, y, color, health=100):
		super().__init__(x, y, health)

		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)

			self.cool_down_counter = 1


def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y

	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  # (x, y)


def main():
	run = True
	FPS = 60

	level = 0
	lives = 5

	main_font = pygame.font.SysFont('comicsans', 50)
	lost_font = pygame.font.SysFont('comicsans', 70)

	enemies = []
	wave_lenght = 5  # Number on Enemies in Each Level ( will be Increased as Level Increases )

	enemy_vel = 1
	player_vel = 5
	laser_vel = 7  # Speed of Lasers

	player = Player(300, 630)

	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

	# Added by Me
	new_wave_comming = True
	new_wave_comming_count = 0
	# new_wave_blink = False

	def redraw_window():
		WIN.blit(BG, (0, 0))

		# Draw Enemies
		for enemy in enemies:
			enemy.draw(WIN)

		# Draw Ship
		player.draw(WIN)

		# Draw Text
		lives_label = main_font.render(f'Lives: {lives}', 1, (255, 255, 255))
		level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))

		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

		# Drawing Wave Label
		if new_wave_comming:
			new_wave_label = main_font.render('New Wave Comming', 1, (255, 89, 0))
			WIN.blit(new_wave_label, (WIDTH / 2 - new_wave_label.get_width() / 2, 10))

		# Drawing Lost Label
		if lost:
			lost_label = lost_font.render('You Lost!', 1, (255, 0, 0))
			WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

		pygame.display.update()

	while run:
		clock.tick(FPS)

		if lives <= 0 or player.health <= 0:
			lost = True

		if lost:
			channel_2_busy = pygame.mixer.Channel(2).get_busy()
			if channel_2_busy != True:
				CHANNEL_2.play(LOST_SOUND)

			if lost_count > FPS * 3:
				run = False

			else:
				lost_count += 1
				redraw_window()

				continue


		if new_wave_comming:
			if new_wave_comming_count > FPS * 3:
				new_wave_comming = False
				new_wave_comming_count = 0

			else:
				new_wave_comming_count += 1

		if len(enemies) == 0:
			level += 1
			wave_lenght += 2  # How much the Wave Would be Bigger when New Level Starts ( Original: 5 )

			new_wave_comming = True

			for i in range(wave_lenght):
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
				enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					sys.exit()

				if event.key == pygame.K_ESCAPE:
					run = False

		keys = pygame.key.get_pressed()

		if keys[pygame.K_a] and player.x - player_vel > 0:  # Left
			player.x -= player_vel

		if keys[pygame.K_d] and player.x + player_vel + player.get_width() < HEIGHT:  # Right
			player.x += player_vel

		if keys[pygame.K_w] and player.y - player_vel > 0:  # Up
			player.y -= player_vel

		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < HEIGHT:  # Down
			player.y += player_vel

		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2 * 60) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 20
				enemies.remove(enemy)

			elif enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1
				enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)

		redraw_window()


def main_menu():
	title_font = pygame.font.SysFont('comicsans', 70)

	run = True

	while run:
		WIN.blit(BG, (0, 0))

		title_label = title_font.render("Press Any Button to Begin ...", 1, (255, 255, 255))
		WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))

		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
					run = False

				else:
					main()

			if event.type == pygame.MOUSEBUTTONDOWN:
				main()


	pygame.quit()


if __name__ == "__main__":
	main_menu()
