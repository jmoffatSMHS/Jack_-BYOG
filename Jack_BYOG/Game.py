import sys
import time
import pygame
import os
import math
WIN_W = 1200
WIN_H = 700
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
LIGHT_GREY = (211, 211, 211)
TIMER = 0


class Game:
    def __init__(self, total_width, total_height, screen_rect, clock, beg_time):
        self.intro = True
        self.play = True
        self.outro = True
        self.begin_wait = True
        self.screen = pygame.display.set_mode((total_width, total_height), pygame.SRCALPHA)
        self.container = pygame.Rect(0,0, screen_rect.width, screen_rect.height)
        self.clock = clock
        self.beg_time = beg_time
        self.fps = 30
        self.title = Text(100, BLACK, "TBD", 'center', 0)
        self.subtitle = Text(50, BLACK, "Click to start", 'center', 'center')
        self.outrotext_lose = Text(100, RED, 'You Died', 'center', 'center')
        self.outrotext_win = Text(100, BLUE, 'You Won!', 'center', 'center')
        self.replay = Text(50, BLACK, 'Click to play again', 'center', 0)

    def blink(self):
        cur_time = pygame.time.get_ticks()
        if ((cur_time - self.beg_time) % 1000) < 500:
            return True
        else:
            return False


class Text(pygame.sprite.Sprite):
    def __init__(self, size, color, text, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render(text, 1, color)
        self.rect = self.image.get_rect()
        if xpos == 'center':
            xpos = WIN_W / 2 - self.rect.width / 2
        if ypos == 'center':
            ypos = WIN_H / 2 - self.rect.height / 2
        self.rect = self.rect.move(xpos,  ypos)
        self.color = color
        self.xpos = xpos
        self.ypos = ypos
        self.size = size

    def update(self):
        return True

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(BLACK)
        self.rect = pygame.Rect(x, y, 32, 32)


class Player(pygame.sprite.Sprite):
    def __init__(self, container):
        pygame.sprite.Sprite.__init__(self)
        self.x_speed = 0
        self.y_speed = 0
        self.energy = 1
        self.image = pygame.image.load('Sprites/MegaSprite.gif').convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect()
        self.rect.centerx = container.centerx
        self.rect.y = container.bottom - self.rect.height * 2
        self.container = container
        self.shooting = True
        self.shot_count = 0
        self.out_of_ammo = False
        self.onground = False
        self.facing_right = True
        self.facing_left = False

    def update(self, left, right, spacedown, mousedown, platforms, game, blast_group, enemy_bullet_group, mouseposx, mouseposy):
        global TIMER
        # Speed changes
        if spacedown:
            if self.onground:
                self.y_speed -= 10
        if left:
            self.x_speed = -8
        if right:
            self.x_speed = 8
        if not self.onground:
            self.y_speed += 0.4
            if self.y_speed > 50:
                self.y_speed = 50
        if not (left or right):
            self.x_speed = 0

        # Movement - x
        self.rect.left += self.x_speed
        # Collision - x
        self.collide(self.x_speed, 0, platforms)
        # Movement - y
        self.rect.top += self.y_speed
        # in the air
        self.onground = False
        # Collision - y
        self.collide(0, self.y_speed, platforms)

        # Boundaries
        self.rect.clamp_ip(self.container)

        # Shooting
        if not mousedown:
            self.shooting = False
        elif mousedown and not self.shooting and not self.out_of_ammo:
            self.shooting = True
            RA = self.get_angle()
            print(RA)
            blast = Blast(self.rect, RA)
            blast_group.add(blast)

            # Recoil from shot
            #if direction == 'up':
                #self.y_speed = 0
                #self.y_speed += 7
                #self.rect.top += self.y_speed
            #if direction == 'down':
                #self.y_speed = 0
                #self.y_speed -= 7
                #self.rect.top += self.y_speed

            #self.x_speed -= 100
            #self.rect.left += self.x_speed
            self.shot_count += 1
        if self.shot_count >= 3:
            self.out_of_ammo = True
        if self.shot_count < 3:
            self.out_of_ammo = False

        # Collision with bullet
        collisions = pygame.sprite.spritecollide(self, enemy_bullet_group, True)

        # Facing other direction:

        if left:
            self.facing_left = True
            right = False
        if right:
            self.facing_right = True
            left = False
        if self.facing_right == True:
            if left:
                print('face left')
                self.image = pygame.transform.flip(self.image, 180, 0)

        if self.facing_left == True:
            if right:
                print("face right")
                self.image = pygame.transform.flip(self.image, 180, 0)




        # Death
        if self.energy < 1:
            self.kill()
            game.play = False
            game.outro = True

    def collide(self, x_speed, y_speed, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if x_speed > 0:
                    self.rect.right = p.rect.left
                if x_speed < 0:
                    self.rect.left = p.rect.right
                if y_speed > 0:
                    self.rect.bottom = p.rect.top
                    self.shot_count = 0
                    self.onground = True
                    self.y_speed = 0
                if y_speed < 0:
                    self.y_speed += 10
                    self.rect.top = p.rect.bottom

    def get_angle(self):
        mousepos = pygame.mouse.get_pos()
        mousex = mousepos[0]
        mousey = mousepos[1]
        playerx = self.rect.x
        playery = self.rect.y
        dx = abs(mousex - playerx)
        dy = abs(mousey - playery)
        # Q1
        if mousex > playerx and mousey < playery:
            a = math.degrees(math.atan(dx/dy))
            RA = 90 - a

            return RA
        # Q2
        if mousex < playerx and mousey < playery:
            a = math.degrees(math.atan(dx/dy))
            RA = 90 + a

            return RA
        # Q3
        if  mousex < playerx and mousey > playery:
            a = math.degrees(math.atan(dy/dx))
            RA = 180 + a

            return RA
        # Q4
        if mousex > playerx and mousey > playery:
            a = math.degrees(math.atan(dy/dx))
            RA = 360 - a
            return RA





class Blast(pygame.sprite.Sprite):
    def __init__(self, player_rect, RA):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(('Sprites/Wind.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 50))
        self.rect = self.image.get_rect()
        self.RA = RA
        self.player_rect = player_rect
        self.rect.left = player_rect.centerx
        self.rect.bottom = player_rect.centery
        self.image = pygame.transform.rotate(self.image, RA)


        self.creation_time = pygame.time.get_ticks()
        self.player_rect = player_rect
    def update(self):
        self.rect.left = self.player_rect.centerx
        self.rect.bottom = self.player_rect.centery
        cur_time = pygame.time.get_ticks()
        if cur_time - 200 > self.creation_time:
            self.kill()


class Camera(object):
    def __init__(self, total_width, total_height):
        self.state = pygame.Rect(0, 0, total_width, total_height)

    def apply(self, obj):
        return obj.rect.move(self.state.topleft)

    def update(self, player_rect, screen_width, screen_height):
        position = self.player_camera(player_rect, screen_width, screen_height)
        x = position[0]
        y = position[1]

        # Stop scrolling at left edge
        if -x < 0:
            x = 0
        # Stop scrolling at right edge
        elif x < -(self.state.width - screen_width):
            x = -(self.state.width - screen_width)
        # Stop scrolling at top
        if -y < 0:
            y = 0
        # Stop scrolling at bottom4
        if y < -(self.state.height - screen_height):
            y = -(self.state.height - screen_height)

        self.state = pygame.Rect(x, y, self.state.width, self.state.height)
        return self.state

    def player_camera(self, player_rect, screen_width, screen_height):
        x = -player_rect.x + screen_width / 2
        y = -player_rect.y + screen_height / 2
        return x, y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, container):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Sprites/MegaSprite.gif')
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.centerx = container.centerx + 25
        self.rect.y = container.bottom - 200
        self.x_speed = 0
        self.y_speed = 0
        self.create_time = pygame.time.get_ticks()
        self.shooting = True
        self.container = container
        self.onground = False
    def update(self, enemy_bullet_group, moveleft, moveright, blast_group, camera_rect, platforms):
        if not self.onground:
            self.y_speed += 0.5
            if self.y_speed > 50:
                self.y_speed = 50


        # Shooting
        if TIMER == 60:
            self.shooting = True
        if TIMER % 60 == 0 and self.shooting:
            enemy_bullet = Enemy_bullet(self)
            enemy_bullet_group.add(enemy_bullet)
            enemy_bullet.set_pos(self)

        # Movement - x
        self.rect.left += self.x_speed
        # Collision - x
        self.collide(self.x_speed, 0, platforms)
        # Movement - y
        self.rect.top += self.y_speed
        # in the air
        self.onground = False
        # Collision - y
        self.collide(0, self.y_speed, platforms)

        # Collisions

        collisions = pygame.sprite.spritecollide(self, blast_group, True)

        if collisions:
            self.x_speed += 2
            self.rect.left += self.x_speed

    def collide(self, x_speed, y_speed, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if x_speed > 0:
                    self.rect.right = p.rect.left
                if x_speed < 0:
                    self.rect.left = p.rect.right
                if y_speed > 0:
                    self.rect.bottom = p.rect.top
                    self.shot_count = 0
                    self.onground = True
                    self.y_speed = 0
                if y_speed < 0:
                    self.y_speed += 100
                    self.rect.top = p.rect.bottom


class Enemy_bullet(pygame.sprite.Sprite):
    def __init__(self, enemy):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 15
        self.image = pygame.image.load('Sprites/Laser.png')
        self.image = pygame.transform.scale(self.image, (25,25))
        self.rect = self.image.get_rect()

    def set_pos(self, enemy):
        self.rect.centerx = enemy.rect.centerx
        self.rect.centery = enemy.rect.centery

    def update(self, camera):
        # Move left
        self.rect.x -= 1

        # Remove when off camera
        if self.rect.x <= camera.left:
            print("offscreen")
            self.kill()






def main():
    global WIN_W, WIN_H, TIMER
    pygame.init()

    # Load Level

    level = [ "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P             PPP                                    P",
              "P                                                    P",
              "P                                    PPPPP           P",
              "P                                                    P",
              "P            PPPPP                                   P",
              "P                                                    P",
              "P                                   PPPPP            P",
              "P              PP                                    P",
              "P                            PPPPP                   P",
              "P                                                    P",
              "P             PPPP       PP               PPPP       P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P       PPPPPP                          PPPPPP       P",
              "P                                                    P",
              "P                       PPPPPP                       P",
              "P                                                    P",
              "P                                                    P",
              "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

    # Create game objects
    screen_width = len(level[0]) * 32
    screen_height = len(level) * 32
    enemy_moveleft = False
    enemy_moveright = False
    
    screen_rect = pygame.rect.Rect(0, 0, screen_width, screen_height)

    game = Game(WIN_W, WIN_H, screen_rect, pygame.time.Clock(), pygame.time.get_ticks())
    player = Player(game.container)
    camera = Camera(screen_width, screen_height)
    enemy = Enemy(game.container)

    game.screen.fill(WHITE)
    # Create Groups
    platform_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player_group.add(player)
    blast_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    enemy_group.add(enemy)
    enemy_bullet_group = pygame.sprite.Group()
    # Key presses
    left = False
    right = False
    mousedown = False
    spacedown = False

    # Build Level
    x = y = 0
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x,y)
                platform_group.add(p)
            x += 32
        y += 32
        x = 0

    # Gameplay

    while True:
        while game.intro:
            # Fill screen and title
            game.screen.fill(WHITE)
            game.screen.blit(game.title.image, game.title.rect)

            # Blinking subtitle
            if game.blink():
                game.screen.blit(game.subtitle.image, game.subtitle.rect)

            # Checks for exiting or clicking
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.screen.blit(game.subtitle.image, game.subtitle.rect)
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    game.intro = False
                    game.play = True
            game.clock.tick(game.fps)

            pygame.display.flip()

        while game.play:

            # Checking all keys 
            for e in pygame.event.get():
                if e.type == pygame.QUIT: sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    spacedown = True
                if e.type == pygame.KEYDOWN and e.key == pygame.K_a:
                    left = True
                    right = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_d:
                    right = True
                    left = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mousedown = True

                if e.type == pygame.KEYUP and e.key == pygame.K_SPACE:
                    spacedown = False
                if e.type == pygame.KEYUP and e.key == pygame.K_a:
                    left = False
                if e.type == pygame.KEYUP and e.key == pygame.K_d:
                    right = False
                if e.type == pygame.MOUSEBUTTONUP:
                    mousedown = False

                # Mouse positiona
                mousepos = pygame.mouse.get_pos()
                mouseposx = mousepos[0]
                mouseposy = mousepos[1]


            # Update

            camera_rect = camera.update(player.rect, WIN_W, WIN_H)
            game.screen.fill(WHITE)
            player_group.update(left, right, spacedown, mousedown, platform_group, game, blast_group, enemy_bullet_group, mouseposx, mouseposy)
            platform_group.update()
            blast_group.update()
            enemy_group.update(enemy_bullet_group, enemy_moveleft, enemy_moveright, blast_group, camera_rect, platform_group)
            enemy_bullet_group.update(camera_rect)

            # Draw Everything
            for p in platform_group:
                game.screen.blit(p.image, camera.apply(p))
            for s in player_group:
                game.screen.blit(s.image, camera.apply(s))
            for b in blast_group:
                game.screen.blit(b.image, camera.apply(b))
            for e in enemy_group:
                game.screen.blit(e.image, camera.apply(e))
            for f in enemy_bullet_group:
                game.screen.blit(f.image, camera.apply(f))

            # Limits frames per iteration of while loop
            game.clock.tick(game.fps)
            # Writes to main surface
            pygame.display.flip()

            if game.begin_wait:
                time.sleep(2)
                game.begin_wait = False

            TIMER += 0.0333333333


        while game.outro:
            # Checks if window exit button pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            game.screen.fill(WHITE)

            # Blit end of game text
            game.screen.blit(game.outrotext_win.image, game.outrotext_win.rect)
            # Window exit button or replaying game
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
            game.clock.tick(game.fps)
            pygame.display.flip()





if __name__ == "__main__":
    # Force static position of screen
    os.environ['SDL_VIDEO_CENTERED' ] = '1'
    main()