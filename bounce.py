# -*- coding: utf-8 *-*
import pygame
import sys
from pygame.locals import *


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Platform(pygame.sprite.Sprite):
    def __init__(self, top, left, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, 10))
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left

    def collide(self, player):
        if (self.rect.colliderect(player.rect)):
            if (player.velocity.y > 0):
                player.rect.bottom = self.rect.top
                player.onground = True
            else:
                player.rect.top = self.rect.bottom
            player.velocity.y = 0

    def onplatform(self, player):
        if (self.rect.left <= player.rect.right and
            player.rect.left <= self.rect.right):
            if (player.rect.bottom == self.rect.top):
                return True
        return False


class Player(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect()
        self.velocity = Vector(0, 0)
        self.onground = True

    def jump(self):
        self.onground = False
        self.velocity.y = -10

    def move(self, direction):
        if self.onground:
            self.velocity.x = direction * 4
        else:
            self.velocity.x += direction * 0.2
            if abs(self.velocity.x) > 4:
                self.velocity.x = direction * 4

    def stop(self):
        self.velocity.x = 0


class Bounce:

    def __init__(self):
        # Init pygame
        pygame.init()
        # Init pygame screen and draw background
        self.size = Rect(0, 0, 700, 500)
        self.screen = pygame.display.set_mode((self.size.width,
                                               self.size.height))
        self.background = pygame.Surface((self.size.width,
                                          self.size.height))
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, [0, 0])
        pygame.display.set_caption("Platformer")

        # Define game objects container
        self.sprites = pygame.sprite.OrderedUpdates()

        # Player object
        self.player = Player(30)
        self.player.rect.top = self.size.height - self.player.rect.height
        self.sprites.add(self.player)

        # Platforms
        self.platforms = []
        self.platforms.append(Platform(self.size.height - 80, 100, 300))
        self.platforms.append(Platform(self.size.height - 160, 200, 100))
        self.platforms.append(Platform(self.size.height - 240, 40, 150))
        self.platforms.append(Platform(self.size.height - 240, 340, 150))
        self.sprites.add(self.platforms)

        # Loop until this is set True
        self.done = False

    def paint(self):
        self.sprites.clear(self.screen, self.background)
        things = self.sprites.draw(self.screen)
        pygame.display.update(things)
        pygame.display.flip()

    def nextState(self):
        # Gravity!
        if not self.player.onground:
            self.player.velocity.y += 0.5

        # Update position
        self.player.rect.left += self.player.velocity.x
        self.player.rect.top += self.player.velocity.y

        # Collide with ground
        if not self.player.onground:
            if (self.player.rect.bottom >= self.size.height):
                self.player.rect.bottom = self.size.height
                self.player.velocity.y = 0
                self.player.onground = True

        # Collide with walls
        if (self.player.rect.left < 0):
            self.player.velocity.x = 0
            self.player.rect.left = 0
        if (self.player.rect.right > self.size.width):
            self.player.velocity.x = 0
            self.player.rect.right = self.size.width

        # Fall off platforms
        onplatform = False
        for platform in self.platforms:
            onplatform |= platform.onplatform(self.player)

        if not onplatform and self.player.rect.bottom < self.size.height:
            self.player.onground = False

        # Collide with platforms
        for platform in self.platforms:
            platform.collide(self.player)

    def processEvents(self):
        # Handle key preses from event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()

        # Handle currently pressed keys
        pressed = pygame.key.get_pressed()

        if pressed[K_UP] and self.player.onground:
            self.player.jump()
        if pressed[K_LEFT]:
            self.player.move(-1)
        if pressed[K_RIGHT]:
            self.player.move(1)
        if not pressed[K_LEFT] and not pressed[K_RIGHT]:
            if self.player.onground:
                self.player.stop()

    def gameLoop(self):
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()

        # -------- Main Program Loop -----------
        while self.done is False:
            # Handle events
            self.processEvents()

            # Update the state
            self.nextState()

            # Paint the new step
            self.paint()

            # Sleep until the next frame
            clock.tick_busy_loop(30)

if __name__ == '__main__':
    bounce = Bounce()
    bounce.gameLoop()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()
