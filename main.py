###################################################################
#
# Author:		redacted
# Title: 		Transversion
# Version/Date: 1.0     24/06/2020
#               1.1     05/07/2020
# Notes:        Based on a game by Ocean Software, 1984
#
###################################################################

# Imports
import pygame
import time
import winsound
import sys
import os

# Set up Pygame and game window
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centre game window
pygame.init()
screen_width = 1090
screen_height = 800
win = pygame.display.set_mode((screen_width, screen_height))  # set width and height of window
win.fill((100, 100, 100))
pygame.display.set_caption("Transversion")

# Initialise fonts
font = pygame.font.SysFont('timesnewroman', 25, True)
font_big = pygame.font.SysFont('timesnewroman', 35, True)

# Initialise images
img_coin = pygame.image.load('coin.png')
bg_menu = pygame.image.load('menu.png')
bg_game = pygame.image.load('game.png')

# Initialise colours
GRIDGREY = (50, 50, 50)
WHITE = (250, 250, 250)
PALEYELLOW = (250, 250, 150)
YELLOW = (250, 250, 50)
PALERED = (250, 110, 110)
CYAN = (50, 250, 250)
LILAC = (160, 180, 250)
LIGHTGREEN = (0, 250, 100)
RED = (255, 0, 0)

# Initialise other variables
clock = pygame.time.Clock()
is_music_playing = True

lasttime = 9999999999  # The time for the game just played
besttime_session = 9999999999
besttime_alltime = 9999999999
newbesttime_session = False
newbesttime_alltime = False


class AreaPlaying(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(win, (0, 0, 0), (self.x, self.y, self.width, self.height))


class Player(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.vel = 32
        self.hitbox = (self.x, self.y, 24, 24)
        self.x += 16
        self.y += 16
        self.facing = 0

    def move(self, cooldownloop):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close game when TR cross is clicked
                python = sys.executable
                os.execl(python, python, * sys.argv)

        # key press events
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and you.x > area_playing.x + you.vel:
            you.x -= you.vel
            self.facing = 3
        elif keys[pygame.K_RIGHT] and you.x < area_playing.x + area_playing.width - you.width // 2 - 32:
            you.x += you.vel
            self.facing = 1
        elif keys[pygame.K_UP] and you.y > area_playing.y + you.vel:
            you.y -= you.vel
            self.facing = 0
        elif keys[pygame.K_DOWN] and you.y < area_playing.y + area_playing.height - you.height // 2 - 32:
            you.y += you.vel
            self.facing = 2
        if keys[pygame.K_p]:  # Pause
            pause()
        if keys[pygame.K_q]:  # Quit to menu
            main_menu()
        return cooldownloop

    def draw(self, win):
        # directions: 0 is top, 1 is right, 2 is bottom, 3 is left
        img_list = [pygame.image.load('player_u.png'), pygame.image.load('player_r.png'),
                    pygame.image.load('player_d.png'), pygame.image.load('player_l.png')]
        img_to_use = img_list[self.facing]
        win.blit(img_to_use, (self.x, self.y))

        self.hitbox = (self.x, self.y, 24, 24)
        # pygame.draw.rect(win, RED, self.hitbox, 2)


class Turret(object):
    def __init__(self, x, y, start_speed, direction):
        self.x = x
        self.y = y
        self.start_speed = start_speed
        self.direction = direction

        self.dx = start_speed
        self.dy = start_speed
        self.firedyet = False
        self.haspassedby = False
        self.hitbox = (self.x, self.y, 32, 32)
        if direction == 0 or direction == 2:
            self.x += 16
        if direction == 1 or direction == 3:
            self.y += 16

    def move(self):
        # * move *
        # directions: 0 is top, 1 is right, 2 is bottom, 3 is left
        if not self.firedyet:
            if self.direction == 0 or self.direction == 2:  # move sideways
                self.x += self.dx
                # Check turret is within grid area
                if self.x >= area_playing.x + area_playing.width - 16:
                    self.dx *= -1
                    self.firedyet = False
                    self.haspassedby = False
                if self.x <= area_playing.x:
                    self.dx *= -1
                    self.firedyet = False
                    self.haspassedby = False
            if self.direction == 1 or self.direction == 3:  # move sideways
                self.y += self.dy
                # Check turret is within grid area
                if self.y >= area_playing.y + area_playing.height - 16:
                    self.dy *= -1
                    self.firedyet = False
                    self.haspassedby = False
                if self.y <= area_playing.y:
                    self.dy *= -1
                    self.firedyet = False
                    self.haspassedby = False

    def draw(self, win):
        # * draw *
        # directions: 0 is top, 1 is right, 2 is bottom, 3 is left
        img_list = [pygame.image.load('tur_t.png'), pygame.image.load('tur_r.png'),
                    pygame.image.load('tur_b.png'), pygame.image.load('tur_l.png')]
        img_to_use = img_list[self.direction]
        win.blit(img_to_use, (self.x, self.y))
        self.hitbox = (self.x, self.y, 32, 32)
        # pygame.draw.rect(win, RED, self.hitbox, 2)


class Coin(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.hitbox = (self.x, self.y, 24, 24)

    def draw(self, win):
        win.blit(img_coin, (self.x, self.y))
        self.hitbox = (self.x, self.y, 24, 24)
        # pygame.draw.rect(win, RED, self.hitbox, 2)


class Bullet(object):
    def __init__(self, x, y, dx, dy, turretid):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.turretid = turretid

        self.hitbox = (self.x, self.y, 32, 32)
        self.tobedestroyed = False
        # winsound.PlaySound("bounce.wav", winsound.SND_ASYNC)  # Make a sound on creation

    def move(self):
        if self.dx == 32 and self.x >= area_playing.x + area_playing.width - 32:
            self.tobedestroyed = True
        elif self.dx == -32 and self.x <= area_playing.x:
            self.tobedestroyed = True
        elif self.dy == 32 and self.y >= area_playing.y + area_playing.height - 32:
            self.tobedestroyed = True
        elif self.dy == -32 and self.y <= area_playing.y:
            self.tobedestroyed = True

    def draw(self, win):
        if not self.tobedestroyed:
            self.x += self.dx
            self.y += self.dy
            self.hitbox = (self.x, self.y, 32, 32)

            # The turretid parameter can also be used to determine which way to face the bullet,
            # but need to invert the directions
            img_list = [pygame.image.load('bullet_d.png'), pygame.image.load('bullet_l.png'),
                        pygame.image.load('bullet_u.png'), pygame.image.load('bullet_r.png')]
            img_to_use = img_list[self.turretid]
            win.blit(img_to_use, (self.x, self.y))


def collide(object1, object2, check_x=True, check_y=True):
    # object1, object2, should x-coordinate be checked?, should y-coordinate be checked?
    # hitboxes: 0 x, 1 y, 2 width, 3 height
    x1 = object1.hitbox[0]
    y1 = object1.hitbox[1]
    width1 = object1.hitbox[2]
    height1 = object1.hitbox[3]

    x2 = object2.hitbox[0]
    y2 = object2.hitbox[1]
    width2 = object2.hitbox[2]
    height2 = object2.hitbox[3]

    # Not needed
    # if x1 == x2 and y1 == y2:  # check object is colliding with itself, return false if so
    #     return False

    if (y1 < y2 + height2 and y1 + height1 > y2) or not check_y:  # check y co-ordinates
        if (x1 + width1 > x2 and x1 < x2 + width2) or not check_x:  # check x co-ordinates
            return True


def draw_text(text, fonttouse, color, surface, x, y):
    textobj = fonttouse.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def read_alltimebestime():
    try:
        with open("best_time.txt", 'r') as fd:
            data = fd.read()  # just reading a number string, so no need to slice and dice
    except FileNotFoundError:
        print("FileNotFoundError")
        return 9999999999

    try:
        nums = float(data)
    except ValueError:
        print("ValueError")
        nums = 9999999999

    return nums


def game_over():
    global lasttime
    global besttime
    global besttime_session
    global besttime_alltime
    global newbesttime_session
    global newbesttime_alltime

    besttime_alltime = (read_alltimebestime())

    if lasttime < besttime_session:
        besttime_session = lasttime
        newbesttime_session = True
    else:
        newbesttime_session = False

    if lasttime < besttime_alltime:
        besttime_alltime = lasttime
        newbesttime_alltime = True
        # Write to file
        f = open("best_time.txt", 'w')
        f.write(str(round(besttime_alltime, 2)))
        f.close()
    else:
        newbesttime_alltime = False


def main_menu():
    # Global variables
    global besttime_session
    global besttime_alltime
    global newbesttime_session
    global newbesttime_alltime
    global lasttime

    img_play = pygame.image.load('btn_play.png').convert()

    while True:
        clock.tick(27)

        # Draw items onto screen
        # background
        win.blit(bg_menu, (0, 0))

        # texts
        draw_text('--- Transversion ---', font, WHITE, win, 450, 20)
        draw_text('2020', font, YELLOW, win, 20, 80)
        draw_text('Press Space or click play to begin', font, YELLOW, win, 20, 110)

        draw_text('Arrow keys to move, P to pause, Q to return to main menu', font, CYAN, win, 20, 170)
        draw_text('Steal the gold from the planet, but avoid the turrets defending  it!',
                  font, CYAN, win, 20, 200)

        if not lasttime == 9999999999:
            draw_text('Previous game\'s time: ' + str(lasttime) + " s", font, LILAC, win, 20, 260)
        else:
            draw_text('Previous game\'s time: Not set', font, LILAC, win, 20, 260)

        if not besttime_session == 9999999999:
            draw_text('Session best time: ' + str(besttime_session) + " s", font, LILAC, win, 20, 290)
        else:
            draw_text('Session best time: Not set', font, LILAC, win, 20, 290)

        if not besttime_alltime == 9999999999:
            draw_text('All-time best time: ' + str(besttime_alltime) + " s", font, LILAC, win, 20, 320)
        else:
            draw_text('All-time best time: Not set', font, LILAC, win, 20, 320)

        if newbesttime_alltime:
            draw_text('New all-time highscore! ', font, LIGHTGREEN, win, 20, 370)
        elif newbesttime_session:
            draw_text('New session highscore! ', font, LIGHTGREEN, win, 20, 370)

        # play button
        btn = win.blit(img_play, (20, 410))

        # key press events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close game when TR cross is clicked
                python = sys.executable
                os.execl(python, python, *sys.argv)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 2nd parameter for left-button click
                x, y = event.pos  # Set the x, y positions of the mouse click
                if btn.collidepoint(x, y):
                    main_game()

        keys = pygame.key.get_pressed()  # Start game
        if keys[pygame.K_SPACE]:
            main_game()

        pygame.display.update()


def pause():
    pause_loop = True
    while pause_loop:
        clock.tick(27)
        # key press events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close game when cross is clicked
                python = sys.executable
                os.execl(python, python, * sys.argv)

        keys = pygame.key.get_pressed()  # Start game
        if keys[pygame.K_RETURN]:
            pause_loop = False

        # Draw items onto screen
        draw_text('PAUSED', font, WHITE, win, 500, 350)
        draw_text('Press Enter', font, WHITE, win, 500, 380)

        pygame.display.update()


def win_lose(haswon):
    pause_loop = True
    while pause_loop:
        clock.tick(27)
        # key press events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Close game when cross is clicked
                python = sys.executable
                os.execl(python, python, * sys.argv)

        keys = pygame.key.get_pressed()  # Start game
        if keys[pygame.K_RETURN]:
            main_menu()

        # Draw items onto screen
        if haswon:
            draw_text('You Win!', font, YELLOW, win, 500, 350)
            draw_text('Time taken: ' + str(lasttime), font, YELLOW, win, 500, 410)
            draw_text('Press Enter', font, YELLOW, win, 500, 470)
            draw_text('' + str(lasttime), font, YELLOW, win, 920, 40)  # ensure both times match
        else:
            draw_text('You Lose!', font, PALERED, win, 500, 380)
            draw_text('Press Enter', font, PALERED, win, 500, 410)
        pygame.display.update()


def draw_grid(start_x, start_y, rows, columns, box_side_length, line_color, surface):
    for x in range(rows):
        for y in range(columns):
            rect = pygame.Rect(start_x + x * box_side_length, start_y + y * box_side_length,
                               box_side_length, box_side_length)
            pygame.draw.rect(surface, line_color, rect, 1)


def redraw_game_window():
    # global timestart
    # Will be drawn in order of depth starting with the back
    # draw background
    win.blit(bg_game, (0, 0))

    # draw playing areas
    area_playing.draw()

    # draw grid
    # start_x, start_y, rows, columns, box_side_length, line_color, surface
    draw_grid(area_playing.x, area_playing.y, 30, 20, 32, GRIDGREY, win)

    # draw texts
    draw_text('--- Transversion ---', font, WHITE, win, 450, 20)
    draw_text('Gold left: ' + str(coinsleft), font, PALEYELLOW, win, 120, 40)
    if coinsleft > 0:
        timenow = round(time.time() - timestart, 2)
        draw_text('' + str(timenow), font, LIGHTGREEN, win, 920, 40)

    # draw objects
    for coin in coins:
        coin.draw(win)

    for turret in turrets:
        turret.draw(win)

    you.draw(win)

    for bullet in bullets:
        bullet.draw(win)

    # update display
    pygame.display.update()


def level_0():  # test level
    global coins
    global coinsleft
    coinsleft = 0
    coins = []
    offset = 20

    # 1 line of coins near centre
    for a in range(0, 7):
        coins.append(Coin(412 + a * 32 + offset, 292 + offset))
        coinsleft += 1


def level_1():
    global coins
    global coinsleft
    coinsleft = 0
    coins = []
    offset = 20
    # Draw coins onto grid
    # Boxes of coins in corners
    for a in range(0, 5):
        for b in range(0, 5):
            if not (a == 2 and b == 2):
                coins.append(Coin(92 + a*32 + offset, 132 + b*32 + offset))
                coinsleft += 1

    for a in range(0, 5):
        for b in range(0, 5):
            if not (a == 2 and b == 2):
                coins.append(Coin(796 + a*32 + offset, 548 + b*32 + offset))
                coinsleft += 1

    for a in range(0, 5):
        for b in range(0, 5):
            if not (a == 2 and b == 2):
                coins.append(Coin(92 + a*32 + offset, 548 + b*32 + offset))
                coinsleft += 1

    for a in range(0, 5):
        for b in range(0, 5):
            if not (a == 2 and b == 2):
                coins.append(Coin(796 + a*32 + offset, 132 + b*32 + offset))
                coinsleft += 1

    # Hollow square of coins in centre
    for a in range(0, 7):
        coins.append(Coin(412 + a * 32 + offset, 292 + offset))
        coins.append(Coin(412 + a * 32 + offset, 484 + offset))
        coinsleft += 2

    for a in range(0, 5):
        coins.append(Coin(412 + offset, 324 + a * 32 + offset))
        coins.append(Coin(604 + offset, 324 + a * 32 + offset))
        coinsleft += 2


def level_2():
    global coins
    global coinsleft
    coinsleft = 0
    coins = []
    offset = 20

    # Coins over entire grid
    for a in range(0, 29):
        for b in range(0, 19):
            coins.append(Coin(60 + a * 32 + offset, 100 + b*32 + offset))
            coinsleft += 1

    # Remove coins from around player
    for a in range(0, 3):
        for b in range(0, 3):
            for coin in coins:
                if coin.x == 476 + a * 32 + offset and coin.y == 356 + b*32 + offset:
                    coins.remove(coin)
                    coinsleft -= 1


def main_game():
    # *** mainloop ***
    global deaths
    global coins
    global turrets
    global bullets
    global area_playing
    global cooldownloop
    global font
    global you
    global coinsleft
    global lasttime
    global timestart

    # Initialise variables and lists
    cooldownloop = 0

    timestart = time.time()  # Used to time how long it takes to complete level
    area_playing = AreaPlaying(60, 100, 960, 640)  # x, y, width, height
    you = Player(508, 388, 64, 64)  # x, y, width, height
    bullets = []
    # turret directions: 0 is top, 1 is right, 2 is bottom, 3 is left
    turrets = [Turret(60, 68, 32, 0), Turret(1020, 100, 32, 1), Turret(988, 740, -32, 2),
               Turret(28, 708, -32, 3)]  # x, y, speed, which side it is at

    # call function to add coins to the grid
    # level_0()
    level_1()
    # level_2()

    winsound.PlaySound("blip.wav", winsound.SND_ASYNC)
    run = True
    while run:
        # Set game timing
        clock.tick(10)  # 27

        # cooldown timer (x loops through main loop)
        if cooldownloop > 0:
            cooldownloop += 1
        if cooldownloop > 15:
            cooldownloop = 0

        # * COLLISION AND OTHER CHECKS *
        for turret in turrets:
            if not turret.firedyet:
                if collide(turret, you, True, False):  # top and bottom turrets
                    # print("Aligned with turret ", turret.direction)
                    if turret.direction == 0:  # should the bullet start moving up or down?
                        bullets.append(Bullet(turret.x, turret.y, 0, 32, turret.direction))
                        turret.firedyet = True
                    else:
                        bullets.append(Bullet(turret.x, turret.y, 0, -32, turret.direction))
                        turret.firedyet = True
                if collide(turret, you, False, True):  # side turrets
                    turret.firedyet = True
                    # print("Aligned with turret ", turret.direction)
                    if turret.direction == 1:  # should the bullet start l or r?
                        bullets.append(Bullet(turret.x, turret.y, -32, 0, turret.direction))
                        turret.firedyet = True
                    else:
                        bullets.append(Bullet(turret.x, turret.y, 32, 0, turret.direction))
                        turret.firedyet = True

        # check if turret has passed player without firing
        for turret in turrets:  # directions: 0 is top, 1 is right, 2 is bottom, 3 is left
            if not turret.haspassedby and not turret.firedyet:
                if turret.direction == 0:
                    if turret.dx == 32 and turret.x > you.x:
                        bullets.append(Bullet(turret.x, turret.y, 0, 32, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                    if turret.dx == -32 and turret.x < you.x:
                        bullets.append(Bullet(turret.x, turret.y, 0, 32, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                if turret.direction == 2:
                    if turret.dx == 32 and turret.x > you.x:
                        bullets.append(Bullet(turret.x, turret.y, 0, -32, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                    if turret.dx == -32 and turret.x < you.x:
                        bullets.append(Bullet(turret.x, turret.y, 0, -32, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                if turret.direction == 1:
                    if turret.dy == 32 and turret.y > you.y:
                        bullets.append(Bullet(turret.x, turret.y, -32, 0, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                    if turret.dy == -32 and turret.y < you.y:
                        bullets.append(Bullet(turret.x, turret.y, -32, 0, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                if turret.direction == 3:
                    if turret.dy == 32 and turret.y > you.y:
                        bullets.append(Bullet(turret.x, turret.y, 32, 0, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True
                    if turret.dy == -32 and turret.y < you.y:
                        bullets.append(Bullet(turret.x, turret.y, 32, 0, turret.direction))
                        turret.firedyet = True
                        turret.haspassedby = True

        for bullet in bullets:  # Collision between player and bullets
            if collide(you, bullet):
                winsound.PlaySound("gameover.wav", winsound.SND_ASYNC)
                lasttime = 9999999999
                game_over()
                win_lose(False)

        for coin in coins:  # Collision between player and coins
            if collide(you, coin):
                winsound.PlaySound("coin.wav", winsound.SND_ASYNC)
                coins.pop(coins.index(coin))
                coinsleft -= 1

        for bullet in bullets:  # check for bullets to be removed
            if bullet.tobedestroyed:
                bullets.pop(bullets.index(bullet))
                turrets[bullet.turretid].firedyet = False
                turrets[bullet.turretid].haspassedby = True

        # Check for collected all coins
        if coinsleft <= 0:
            redraw_game_window()
            lasttime = time.time() - timestart
            lasttime = round(lasttime, 2)
            winsound.PlaySound("win.wav", winsound.SND_ASYNC)
            redraw_game_window()
            game_over()
            win_lose(True)

        # *** MOVEMENT ***
        cooldownloop = you.move(cooldownloop)  # Move player and check player is in area

        for turret in turrets:  # Move turrets
            turret.move()

        for bullet in bullets:  # Move bullets
            bullet.move()

        # *** DRAW TO SCREEN ***
        redraw_game_window()


game_over()  # read best time from text file first
main_menu()
main_game()
