import pygame
import os
import random

class Snek():
    def __init__(self, x, y):
        self.pos = []
        for i in range(0, 5):
            self.pos.append([x - i, y])
        self.UP = 0
        self.RIGHT = 1
        self.DOWN = 2
        self.LEFT = 3
        self.direction = self.RIGHT
        self.MOVE_FREQ = 5
        self.moveCounter = self.MOVE_FREQ

    def move(self, eatApple):
        if eatApple:
            newX = self.pos[len(self.pos) - 1][0]
            newY = self.pos[len(self.pos) - 2][1]
            self.pos.append([newX, newY])

        nextX = self.pos[0][0]
        nextY = self.pos[0][1]
        if self.direction == self.UP:
            nextY -= 1
        elif self.direction == self.RIGHT:
            nextX += 1
        elif self.direction == self.DOWN:
            nextY += 1
        elif self.direction == self.LEFT:
            nextX -= 1
        for i in range(0, len(self.pos)):
            if eatApple and i == len(self.pos) - 1:
                continue
            oldX = self.pos[i][0]
            oldY = self.pos[i][1]
            self.pos[i][0] = nextX
            self.pos[i][1] = nextY
            nextX = oldX
            nextY = oldY

    def isDead(self):
        x = self.pos[0][0]
        y = self.pos[0][1]
        collision = False
        for i in range(1, len(self.pos)):
            if self.pos[0][0] == self.pos[i][0] and self.pos[0][1] == self.pos[i][1]:
                collision = True
        return x >= (640 / 32) or x < 0 or y >= (480 / 32) or y < 0 or collision

class Game():
    def __init__(self):
        self.SCREEN_WIDTH = 640
        self.SCREEN_HEIGHT = 480
        self.TARGET_FPS = 60

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.gameInit()

        self.running = True
        self.run()
        self.quit()

    def gameInit(self):
        self.snek = Snek(10, 5)
        self.ongoing = True
        self.apple = [-1, -1]
        self.spawnApple()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snek.direction = self.snek.UP
                elif event.key == pygame.K_RIGHT:
                    self.snek.direction = self.snek.RIGHT
                elif event.key == pygame.K_DOWN:
                    self.snek.direction = self.snek.DOWN
                elif event.key == pygame.K_LEFT:
                    self.snek.direction = self.snek.LEFT
                elif event.key == pygame.K_SPACE:
                    if not self.ongoing:
                        self.snek = Snek(10, 5)
                        self.spawnApple()
                        self.ongoing = True

    def update(self):
        if self.ongoing:
            self.snek.moveCounter -= 1
            if self.snek.moveCounter == 0:
                self.snek.moveCounter = self.snek.MOVE_FREQ
                ateApple = self.apple[0] == self.snek.pos[0][0] and self.apple[1] == self.snek.pos[0][1]
                self.snek.move(ateApple)
                if ateApple:
                    self.spawnApple()
                if self.snek.isDead():
                    self.ongoing = False

    def render(self):
        self.screen.fill(self.BLACK)

        pygame.draw.rect(self.screen, self.RED, (self.apple[0]*32, self.apple[1]*32, 32, 32), False)
        for piece in self.snek.pos:
            pygame.draw.rect(self.screen, self.GREEN, (piece[0]*32, piece[1]*32, 32, 32), False)

        pygame.display.flip()

    def spawnApple(self):
        appleOk = False
        appleX = -1
        appleY = -1
        while not appleOk:
            appleOk = True
            appleX = random.randint(0, (self.SCREEN_WIDTH / 32) - 1)
            appleY = random.randint(0, (self.SCREEN_HEIGHT / 32) - 1)
            for piece in self.snek.pos:
                if piece[0] == appleX and piece[1] == appleY:
                    appleOk = False
                    break
        self.apple = [appleX, appleY]

    def run(self):
        SECOND = 1000
        beforeTime = pygame.time.get_ticks()
        frames = 0
        while self.running:
            self.clock.tick(self.TARGET_FPS)
            self.input()
            self.update()
            self.render()
            frames += 1

            afterTime = pygame.time.get_ticks()
            if afterTime - beforeTime >= SECOND:
                print("FPS = " + str(frames))
                frames = 0
                beforeTime += SECOND

    def quit(self):
        pygame.quit()

os.environ['SDL_VIDEO_CENTERED'] = '1' #centers the pygame window
game = Game()
