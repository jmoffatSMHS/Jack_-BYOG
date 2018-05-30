import sys, time, pygame, os, random, math
WIN_W = 1200
WIN_H = 700
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
TIMER = 0

class Game:
    def __init__(self, total_width, total_height, screen_rect, clock, beg_time):
        self.intro = True
        self.play = True
        self.outro = True
        self.begin_wait = True
        self.screen = pygame.display.set_mode((total_width, total_height), pygame.SRCALPHA)
        self.container = pygame.Rect(0, 0, screen_rect.width, screen_rect.height)
        self.clock = clock
        self.beg_time = beg_time
        self.fps = 60
        self.title = Text(100, BLACK, "TBD", 'center', 0)
        self.subtitle = Text(50, BLACK, "Click here to start", 'center', 'center')
        self.outrotext_win = Text(100, BLUE, "You Won!", 'center', 'center')
        self.outrotext_lose = Text(100, RED, "You Died", 'center', 'center')
        self.replay = Text(50, BLACK, 'Click to play again', 'center', 0)
        self.mousedown = False

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
        self.rect = self.rect.move(xpos, ypos)
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


class Camera(object):
    def __init__(self, screen_width, screen_height):
        self.state = pygame.Rect(0, 0, screen_width, screen_height)

    def apply(self, obj):
        return obj.rect.move(self.state.topleft)

    def update(self, player_rect, screen_width, screen_height):
        pos = self.player_camera(player_rect, screen_width, screen_height)
        x = pos[0]
        y = pos[1]
        # Stop scrolling at left edge
        if -x < 0:
            x = 0
        # Stop scrolling at right edge
        elif x < -(self.state.width - screen_width):
            x = -(self.state.width - screen_width)
        # Stop scrolling at top
        if -y < 0:
            y = 0
        # Stop scrolling at bottom
        if y < -(self.state.height - screen_height):
            y = -(self.state.height - screen_height)

        self.state = pygame.Rect(x, y, self.state.width, self.state.height)
        return self.state

    def player_camera(self, player_rect, screen_width, screen_height):
        x = -player_rect.x + screen_width / 2
        y = -player_rect.y + screen_height / 2

        return x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, container):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 20
        self.energy = 5
        # Placeholder sprite
        self.image = pygame.image.load('clash.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.centerx = container.centerx
        self.rect.y = container.centery
        self.container = container
        self.shooting = True

    def update(self, game):
        global TIMER
        # Movement
        key = pygame.key.get_pressed()

        if key[pygame.K_w]:
            self.rect.y -= self.speed
        if key[pygame.K_s]:
            self.rect.y += self.speed
        if key[pygame.K_a]:
            self.rect.x -= self.speed
        if key[pygame.K_d]:
            self.rect.x += self.speed

        self.rect.clamp_ip(self.container)

        # Death
        if self.energy < 1:
            self.kill()
            game.play = False
            game.outro = True
def main():
    global WIN_W, WIN_H, TIMER
    pygame.init()

    # Load Level

    level = [ "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P                                                    P",
              "P       PPPPPP                          PPPPPP       P",
              "P                                                    P",
              "P                       PPPPPP                       P",
              "P                                                    P",
              "P                                                    P",
              "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

    # Create Game objects
    screen_width = len(level[0]) * 32
    screen_height = len(level) * 32

    screen_rect = pygame.rect.Rect(0, 0, screen_width, screen_height)

    game = Game(WIN_W, WIN_H, screen_rect, pygame.time.Clock(), pygame.time.get_ticks())
    game.screen.fill(WHITE)
    camera = Camera(screen_width, screen_height)
    player = Player(game.container)
    
    # Create Groups
    platform_group = pygame.sprite.Group()
    ship_group = pygame.sprite.Group()
    ship_group.add(player)
    # Build Level

    x = y = 0
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
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
                    game.screen.fill(WHITE)
                    game.intro = False
                    game.play = True
            game.clock.tick(game.fps)

            pygame.display.flip()

        while game.play:
            # Checks if exit button pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game.mousedown = True
                if event.type == pygame.MOUSEBUTTONUP:
                    game.mousedown = False

            # Update
            platform_group.update()
            ship_group.update(game)
            camera.update(player.rect, WIN_H, WIN_W)



            # Draw Everything
            for p in platform_group:
                game.screen.blit(p.image, camera.apply(p))
            ship_group.draw(game.screen)

            # Limits frames per iteration of while loop
            game.clock.tick(game.fps)
            # Writes to main surface
            pygame.display.flip()

            if game.begin_wait:
                time.sleep(2)
                game.begin_wait = False

                TIMER += 1

        while game.outro:
            # Checks if exit button pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            game.screen.fill(WHITE)

            # Blit ending text
            game.screen.blit(game.outrotext_win.image, game.outrotext_win.rect)
            if game.blink():
                game.screen.blit(game.replay.image, game.replay.rect)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.screen.bli(game.replay.image, game.replay.rect)
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    game.outro = False
                    game.intro = True
            game.clock.tick(game.fps)
            pygame.display.flip()



if __name__ == "__main__":
    # Force static position of screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    main()

