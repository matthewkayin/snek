import pygame
import os
import random
import ihandler


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
        self.move_counter = self.MOVE_FREQ

    def move(self, eat_apple):
        if eat_apple:
            new_x = self.pos[len(self.pos) - 1][0]
            new_y = self.pos[len(self.pos) - 2][1]
            self.pos.append([new_x, new_y])

        next_x = self.pos[0][0]
        next_y = self.pos[0][1]
        if self.direction == self.UP:
            next_y -= 1
        elif self.direction == self.RIGHT:
            next_x += 1
        elif self.direction == self.DOWN:
            next_y += 1
        elif self.direction == self.LEFT:
            next_x -= 1
        for i in range(0, len(self.pos)):
            if eat_apple and i == len(self.pos) - 1:
                continue
            oldX = self.pos[i][0]
            oldY = self.pos[i][1]
            self.pos[i][0] = next_x
            self.pos[i][1] = next_y
            next_x = oldX
            next_y = oldY

    def is_dead(self):
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

        pygame.font.init()
        self.smallfont = pygame.font.SysFont("Serif", 14)
        self.bigfont = pygame.font.SysFont("Serif", 22)
        self.fps_text = self.smallfont.render("FPS", False, self.GREEN)

        pygame.joystick.init()
        self.joystick_labels = []
        self.joystick_label_pool = "ABCDEFGHIJ"  # we shouldn't ever need more than this
        self.joystick_count = pygame.joystick.get_count()
        self.joystick_text = self.smallfont.render("Joysticks: " + str(self.joystick_count), False, self.GREEN)
        for i in range(0, self.joystick_count):
            pygame.joystick.Joystick(i).init()
            self.joystick_labels.append(self.joystick_label_pool[i])
        self.ihandler = ihandler.IHandler(["AXIS SNEK HORIZ", "AXIS SNEK VERT", "RESET GAME"])

        self.game_init()

        self.running = True
        self.show_fps = False

        self.run()
        self.quit()

    def game_init(self):
        self.snek = Snek(10, 5)
        self.ongoing = True
        self.apple = [-1, -1]
        self.spawn_apple()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.ihandler.loadMapping(False)
                elif event.key == pygame.K_F2:
                    self.ihandler.start_mapping()
                elif event.key == pygame.K_F3:
                    self.show_fps = not self.showFps
                else:
                    self.ihandler.key_down("K" + str(event.key))
            elif event.type == pygame.KEYUP:
                if event.key != pygame.K_ESCAPE and event.key != pygame.K_F1 and event.key != pygame.K_F2 and event.key != pygame.K_F3:
                    self.ihandler.key_up("K" + str(event.key))
            elif event.type == pygame.JOYBUTTONDOWN:
                self.ihandler.key_down(self.joystick_labels[event.joy] + str(event.button))
            elif event.type == pygame.JOYBUTTONUP:
                self.ihandler.key_up(self.joystick_labels[event.joy] + str(event.button))
            elif event.type == pygame.JOYAXISMOTION:
                axis = self.joystick_labels[event.joy] + "x" + str(event.axis)
                pos = pygame.joystick.Joystick(event.joy).get_axis(event.axis)
                if self.ihandler.is_mapped_axis(axis):
                    self.ihandler.axis_moved(axis, pos)
                axis_pos = axis + "+"
                axis_neg = axis + "-"
                if pos == 0:
                    self.ihandler.key_up(axis_pos)
                    self.ihandler.key_up(axis_neg)
                elif pos > 0:
                    self.ihandler.key_down(axis_pos)
                    self.ihandler.key_up(axis_neg)
                elif pos < 0:
                    self.ihandler.key_down(axis_neg)
                    self.ihandler.key_up(axis_pos)
            elif event.type == pygame.JOYHATMOTION:
                axis = self.joystick_labels[event.joy] + "t" + str(event.hat)
                axis_h_pos = axis + "h+"
                axis_h_neg = axis + "h-"
                axis_v_pos = axis + "v+"
                axis_v_neg = axis + "v-"
                pos = pygame.joystick.Joystick(event.joy).get_hat(event.hat)
                if pos[0] == 0:
                    self.ihandler.key_up(axis_h_pos)
                    self.ihandler.key_up(axis_h_neg)
                elif pos[0] == 1:
                    self.ihandler.key_down(axis_h_pos)
                    self.ihandler.key_up(axis_h_neg)
                elif pos[0] == -1:
                    self.ihandler.key_up(axis_h_pos)
                    self.ihandler.key_down(axis_h_neg)
                if pos[1] == 0:
                    self.ihandler.key_up(axis_v_pos)
                    self.ihandler.key_up(axis_v_neg)
                elif pos[1] == 1:
                    self.ihandler.key_down(axis_v_pos)
                    self.ihandler.key_up(axis_v_neg)
                elif pos[1] == -1:
                    self.ihandler.key_up(axis_v_pos)
                    self.ihandler.key_down(axis_v_neg)

    def update(self):
        # handle inputs from ihandler
        '''
        event = ''
        while event != "EMPTY":
            event = self.ihandler.key_queue()
            if event == "SNEK UP":
                self.snek.direction = self.snek.UP
            elif event == "SNEK RIGHT":
                self.snek.direction = self.snek.RIGHT
            elif event == "SNEK DOWN":
                self.snek.direction = self.snek.DOWN
            elif event == "SNEK LEFT":
                self.snek.direction = self.snek.LEFT
            elif event == "RESET GAME":
                if not self.ongoing:
                    self.snek = Snek(10, 5)
                    self.spawn_apple()
                    self.ongoing = True
                    '''

        if self.ongoing:
            self.snek.move_counter -= 1
            if self.snek.move_counter == 0:
                self.snek.move_counter = self.snek.MOVE_FREQ
                ate_apple = self.apple[0] == self.snek.pos[0][0] and self.apple[1] == self.snek.pos[0][1]
                self.snek.move(ate_apple)
                if ate_apple:
                    self.spawn_apple()
                if self.snek.is_dead():
                    self.ongoing = False

    def render(self):
        self.screen.fill(self.BLACK)

        '''
        pygame.draw.rect(self.screen, self.RED, (self.apple[0] * 32, self.apple[1] * 32, 32, 32), False)
        for piece in self.snek.pos:
            pygame.draw.rect(self.screen, self.GREEN, (piece[0] * 32, piece[1] * 32, 32, 32), False)
        '''

        pos = [0, 0]
        pos[0] = (self.SCREEN_WIDTH / 2) + 20 * self.ihandler.get_state("AXIS SNEK HORIZ")
        pos[1] = (self.SCREEN_HEIGHT / 2) + 20 * self.ihandler.get_state("AXIS SNEK VERT")
        pygame.draw.rect(self.screen, self.RED, (pos[0], pos[1], 20, 20), False)

        if self.show_fps:
            self.screen.blit(self.fps_text, (0, 0))
            self.screen.blit(self.joystick_text, (0, 15))

        pygame.display.flip()

    def spawn_apple(self):
        apple_ok = False
        apple_x = -1
        apple_y = -1
        while not apple_ok:
            apple_ok = True
            apple_x = random.randint(0, (self.SCREEN_WIDTH / 32) - 1)
            apple_y = random.randint(0, (self.SCREEN_HEIGHT / 32) - 1)
            for piece in self.snek.pos:
                if piece[0] == apple_x and piece[1] == apple_y:
                    apple_ok = False
                    break
        self.apple = [apple_x, apple_y]

    def map_input(self):
        self.screen.fill(self.BLACK)

        header = self.bigfont.render("Mapping Key Inputs!", False, self.WHITE)
        instructions = self.bigfont.render("Press the key you want for... " + self.ihandler.to_map(), False, self.WHITE)
        self.screen.blit(header, (self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 - 50))
        self.screen.blit(instructions, (self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 - 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1 or event.key == pygame.K_F2 or event.key == pygame.K_F3:
                    print("You can't map those keys!")
                    continue
                self.ihandler.key_down("K" + str(event.key))
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1 or event.key == pygame.K_F2 or event.key == pygame.K_F3:
                    continue
                self.ihandler.key_up("K" + str(event.key))
            elif event.type == pygame.JOYBUTTONDOWN:
                self.ihandler.key_down(self.joystick_labels[event.joy] + str(event.button))
            elif event.type == pygame.JOYBUTTONUP:
                self.ihandler.key_up(self.joystick_labels[event.joy] + str(event.button))
            elif event.type == pygame.JOYAXISMOTION:
                axis = self.joystick_labels[event.joy] + "x" + str(event.axis)
                pos = pygame.joystick.Joystick(event.joy).get_axis(event.axis)
                if self.ihandler.to_map().startswith("AXIS ") and pos != 0:
                    self.ihandler.key_down(axis)
                axis_pos = axis + "+"
                axis_neg = axis + "-"
                if pos == 0:
                    self.ihandler.key_up(axis_neg)
                elif pos > 0:
                    self.ihandler.key_down(axis_pos)
                elif pos < 0:
                    self.ihandler.key_down(axis_neg)
            elif event.type == pygame.JOYHATMOTION:
                axis = self.joystick_labels[event.joy] + "t" + str(event.hat)
                axis_h_pos = axis + "h+"
                axis_h_neg = axis + "h-"
                axis_v_pos = axis + "v+"
                axis_v_neg = axis + "v-"
                pos = pygame.joystick.Joystick(event.joy).get_hat(event.hat)
                if pos[0] == 0:
                    self.ihandler.key_up(axis_h_pos)
                elif pos[0] == 1:
                    self.ihandler.key_down(axis_h_pos)
                elif pos[0] == -1:
                    self.ihandler.key_down(axis_h_neg)
                if pos[1] == 0:
                    self.ihandler.key_up(axis_v_pos)
                elif pos[1] == 1:
                    self.ihandler.key_down(axis_v_pos)
                elif pos[1] == -1:
                    self.ihandler.key_down(axis_v_neg)

    def run(self):
        SECOND = 1000
        before_time = pygame.time.get_ticks()
        frames = 0
        while self.running:
            self.clock.tick(self.TARGET_FPS)
            if self.ihandler.is_mapping():
                self.map_input()
            else:
                self.input()
                self.update()
                self.render()
                frames += 1

            after_time = pygame.time.get_ticks()
            if after_time - before_time >= SECOND:
                # print("FPS = " + str(frames))
                self.fps_text = self.smallfont.render('FPS: ' + str(frames), False, self.GREEN)
                frames = 0
                before_time += SECOND

    def quit(self):
        pygame.joystick.quit()
        pygame.font.quit()
        pygame.quit()


os.environ['SDL_VIDEO_CENTERED'] = '1'  # centers the pygame window
game = Game()
