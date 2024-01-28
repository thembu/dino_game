import math

import neat
import pygame
import os
import random
import sys

pygame.init()

# global constants

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

Running = [pygame.image.load(os.path.join('assets/Dino', 'DinoRun1.png')),
           pygame.image.load(os.path.join('assets/Dino', 'DinoRun2.png'))]

Jumping = pygame.image.load(os.path.join('assets/Dino', 'DinoJump.png'))

BG = pygame.image.load(os.path.join('assets/Other', 'Track.png'))

SMALL_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png"))]

font = pygame.font.Font('freesansbold.ttf', 30)


class Dinasour:
    X_POS = 80
    Y_POS = 310
    Jump_Vel = 8.5

    def __init__(self, img=Running[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.Jump_Vel
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.step_index = 0

    def update(self):

        if self.dino_run:
            self.run()

        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

    def run(self):

        self.image = Running[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = Jumping
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8

        if self.jump_vel <= -self.Jump_Vel:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.Jump_Vel

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Obstacles:
    def __init__(self, image, number_of_cactus):
        self.image = image
        self.type = number_of_cactus
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacles):
    def __init__(self, image, number_of_cactus):
        super().__init__(image, number_of_cactus)
        self.rect.y = 325


class LargeCactus(Obstacles):
    def __init__(self, image, number_of_cactus):
        super().__init__(image, number_of_cactus)
        self.rect.y = 300


def remove(index):
    dinosaurs.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]

    return math.sqrt(dx ** 2 + dy ** 2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, dinosaurs, ge, nets
    run = True
    clock = pygame.time.Clock()
    dinosaurs = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        dinosaurs.append(Dinasour())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    obstacles = []
    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20
    points = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Score: " + str(points), True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))

        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))

        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)

        if len(dinosaurs) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))

            elif rand_int == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()

            for i, dinosaur in enumerate(dinosaurs):
                if dinosaur.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, dinosaur in enumerate(dinosaurs):
            output = nets[i].activate((dinosaur.rect.y,
                                       distance((dinosaur.rect.x, dinosaur.rect.y),
                                                obstacle.rect.midtop)))

            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False

        score()
        background()
        clock.tick(30)
        pygame.display.update()


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
