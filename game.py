import numpy as np
import pygame
import os
import random
pygame.init()

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
                pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
                pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                     pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                     pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                     pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                     pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
             pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, action):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0
        # if userInput[pygame.K_UP] and not self.dino_jump:
        if np.array_equal(action, np.array([0, 1, 0])) and not self.dino_jump and not self.dino_duck:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        # elif userInput[pygame.K_DOWN] and not self.dino_jump:
        if np.array_equal(action, np.array([0, 0, 1])) and not self.dino_jump and not self.dino_duck:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        # elif not (self.dino_jump or userInput[pygame.K_DOWN]):
        elif np.array_equal(action, np.array([1, 0, 0])) and not self.dino_jump and not self.dino_duck:
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        if self.dino_duck:
            self.dino_rect = self.image.get_rect()
            self.dino_rect.x = self.X_POS
            self.dino_rect.y = self.Y_POS_DUCK
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_duck = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL
        #self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self, obstacles, game_speed):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 210
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1

class Dino_Game:
    def __init__(self):
        self.screen_height = SCREEN_HEIGHT
        self.screen_width = SCREEN_WIDTH
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.player = Dinosaur()
        self.cloud = Cloud()
        self.game_speed = 20
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.points = 0
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.obstacles = []
        self.user_action = [0, 0, 0]
        self.death_count = 0

    def score(self):
        self.points += 1
        if self.points % 100 == 0:
            self.game_speed += 1

        text = self.font.render("Points: " + str(self.points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        self.display.blit(text, textRect)

    def background(self):
        self.image_width = BG.get_width()
        self.display.blit(BG, (self.x_pos_bg, self.y_pos_bg))
        self.display.blit(BG, (self.image_width + self.x_pos_bg, self.y_pos_bg))
        if self.x_pos_bg <= -self.image_width:
            self.display.blit(BG, (self.image_width + self.x_pos_bg, self.y_pos_bg))
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed

    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.display.fill((255, 255, 255))
        self.user_action = action
        #print(self.user_action)
        #userInput = pygame.key.get_pressed()
        self.player.update(self.user_action)
        self.player.draw(self.display)

        if len(self.obstacles) == 0:
            if random.randint(0, 2) == 0:
                self.obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                self.obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                self.obstacles.append(Bird(BIRD))
        reward = 0
        loss = False
        for obstacle in self.obstacles:
            obstacle.draw(self.display)
            obstacle.update(self.obstacles, self.game_speed)

            if self.player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                self.death_count += 1
                reward = -10
                loss = True
                #self.menu(self.death_count)
                #return reward, loss, points
            # elif player.dino_rect.x == obstacle.rect.x:
            elif self.player.dino_rect.x == obstacle.rect.x + 10:
                reward = 10
            elif self.points % 100 == 0:
                reward = 2
        self.background()

        self.cloud.draw(self.display)
        self.cloud.update(self.game_speed)

        self.score()

        self.clock.tick(30)
        pygame.display.update()
        return reward, loss, self.points