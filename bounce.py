# -*- coding: utf-8 *-*
import pygame
import sys
import random
from pygame.locals import *


GRAVITY = 0.5


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

    def collide(self, player, particles, sprites):
        if (self.rect.colliderect(player.rect)):
            if ((player.velocity.x == 0) or
                ((player.velocity.x > 0) and
                  (self.rect.left < player.lastrect.right)) or
                ((player.velocity.x < 0) and
                  (player.lastrect.left < self.rect.right))):
                # Player was previously above/below the platform
                if (player.velocity.y > 0):
                    # Player is falling
                    player.rect.bottom = self.rect.top
                    player.onground = True
                    player.explode(particles, sprites)
                else:
                    # Player is rising
                    player.rect.top = self.rect.bottom
                player.velocity.y = 0
            else:
                # Player has hit an edge
                if (player.velocity.x > 0):
                    # Player is moving right
                    player.rect.right = self.rect.left
                else:
                    # Player is moving left
                    player.rect.left = self.rect.right
                player.velocity.x = 0

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
        self.lastrect = Rect(self.rect.left, self.rect.top,
                             self.rect.width, self.rect.height)
        self.velocity = Vector(0, 0)
        self.onground = True

    def jump(self):
        self.onground = False
        self.velocity.y = -10

    def move(self, direction):
        if self.onground:
            self.velocity.x = direction * 4
        else:
            self.velocity.x += direction * 0.5
            if abs(self.velocity.x) > 4:
                self.velocity.x = direction * 4

    def stop(self):
        self.velocity.x = 0

    def explode(self, particles, sprites):
        if (self.velocity.y > 1):
            numparticles = 5 + random.randrange(1, 2 + int(self.velocity.y))
        else:
            numparticles = 25

        for i in range(numparticles):
            velx = random.randrange(-5, 5)
            vely = random.randrange(-10, -1)
            particle = Particle(4, Vector(velx, vely),
                                self.rect)
            particles.add(particle)
            sprites.add(particle)


class Particle(pygame.sprite.Sprite):
    def __init__(self, size, velocity, origin):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect()
        self.rect.top = origin.top + (origin.height / 2)
        self.rect.left = origin.left + (origin.width / 2)
        self.velocity = velocity

    def update(self, screenrect, sprites, particles):
        self.velocity.y += GRAVITY

        self.rect.left += self.velocity.x
        self.rect.top += self.velocity.y

        if (not screenrect.colliderect(self.rect)):
            particles.remove(self)
            sprites.remove(self)


class Bounce:
    def __init__(self):
        # Init pygame
        pygame.init()
        # Init pygame screen and draw background
        self.screenrect = Rect(0, 0, 700, 500)
        self.screen = pygame.display.set_mode((self.screenrect.width,
                                               self.screenrect.height))
        self.background = pygame.Surface((self.screenrect.width,
                                          self.screenrect.height))
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, [0, 0])
        pygame.display.set_caption("Platformer")

        # Define game objects container
        self.sprites = pygame.sprite.OrderedUpdates()
        self.particles = pygame.sprite.OrderedUpdates()

        # Player object
        self.player = Player(30)
        self.player.rect.top = self.screenrect.height - self.player.rect.height
        self.sprites.add(self.player)

        # Platforms
        self.platforms = []
        self.platforms.append(Platform(self.screenrect.height - 80, 100, 300))
        self.platforms.append(Platform(self.screenrect.height - 160, 240, 100))
        self.platforms.append(Platform(self.screenrect.height - 240, 40, 150))
        self.platforms.append(Platform(self.screenrect.height - 240, 340, 150))
        self.sprites.add(self.platforms)

        # Loop until this is set True
        self.done = False

    def paint(self):
        self.sprites.clear(self.screen, self.background)
        things = self.sprites.draw(self.screen)
        pygame.display.update(things)
        pygame.display.flip()

    def nextState(self):
        # Update particles
        for particle in self.particles:
            particle.update(self.screenrect, self.sprites, self.particles)

        # Gravity!
        if not self.player.onground:
            self.player.velocity.y += GRAVITY

        # Save current position
        self.player.lastrect.top = self.player.rect.top
        self.player.lastrect.left = self.player.rect.left
        self.player.lastrect.height = self.player.rect.height
        self.player.lastrect.width = self.player.rect.width

        # Update position
        self.player.rect.left += self.player.velocity.x
        self.player.rect.top += self.player.velocity.y

        # Collide with ground
        if not self.player.onground:
            if (self.player.rect.bottom >= self.screenrect.height):
                self.player.explode(self.particles, self.sprites)
                self.player.rect.bottom = self.screenrect.height
                self.player.velocity.y = 0
                self.player.onground = True

        # Collide with walls
        if (self.player.rect.left < 0):
            self.player.velocity.x = 0
            self.player.rect.left = 0
        if (self.player.rect.right > self.screenrect.width):
            self.player.velocity.x = 0
            self.player.rect.right = self.screenrect.width

        # Fall off platforms
        onplatform = False
        for platform in self.platforms:
            onplatform |= platform.onplatform(self.player)

        if not onplatform and self.player.rect.bottom < self.screenrect.height:
            self.player.onground = False

        # Collide with platforms
        for platform in self.platforms:
            platform.collide(self.player, self.particles, self.sprites)

    def processEvents(self):
        # Handle key preses from event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_SPACE:
                    self.player.explode(self.particles, self.sprites)

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
