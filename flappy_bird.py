import pygame
import os
import random
import neat

ia_playing = True
generation = 0

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800


PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'pipe.png')))
FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'base.png')))
BACKGROUND_IMAGE =pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bg.png')))
BIRD_IMAGES = [
  pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird1.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird2.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird3.png'))),
]


pygame.font.init()
POINTS_FONT = pygame.font.SysFont('Oswald', 25)



class Bird:
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMAGES[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        displacement = 1.5 * (self.time ** 2) + self.speed * self.time

        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED
    
    def draw(self, screen):
        self.image_count += 16

        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME * 2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME * 3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME * 4:
            self.image = self.IMAGES[1]
        elif self.image_count >= self.ANIMATION_TIME * 4 + 1:
            self.image =  self.IMAGES[0]
            self.image_count = 0

        if self.angle <= -80:
            self.image = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.image, self.angle)
        pos_image_center = self.image.get_rect(topleft=(self.x, self.y)).center
        retangle = rotated_image.get_rect(center=pos_image_center)
        screen.blit(rotated_image, retangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 10

    def __init__(self, x):
        self.x = x
        self.heigth = 0
        self.pos_top = 0
        self.pos_base = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BASE = PIPE_IMAGE
        self.passed_on = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.pos_top = self.height - self.PIPE_TOP.get_height()
        self.pos_base = self.height + self.DISTANCE
    
    def move(self):
        self.x -= self.SPEED
    
    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.pos_top))
        screen.blit(self.PIPE_BASE, (self.x, self.pos_base))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        top_distance = (self.x - bird.x, self.pos_top - round(bird.y))
        base_distance = (self.x - bird.x, self.pos_base - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)

        if base_point or top_point:
            return True
        else:
            return False


class Floor:
    SPEED = 10
    WIDTH = FLOOR_IMAGE.get_width()
    IMAGE = FLOOR_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE,(self.x1, self.y))
        screen.blit(self.IMAGE,(self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(screen)

    for pipe in pipes:
        pipe.draw(screen)
    
    text = POINTS_FONT.render(f"Points: {points}", 1, (255,255,255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    if ia_playing:
        text = POINTS_FONT.render(f"Generation: {generation}", 1, (255,255,255))
        screen.blit(text, (10,10))

    floor.draw(screen)
    pygame.display.update()

def main(genomes, config):
    global generation
    generation += 1

    if ia_playing:
        neural_network = []
        genomes_list = []
        birds = []
        for _, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_network.append(net)
            genome.fitness = 0
            genomes_list.append(genome)
            birds.append(Bird(230,350))

    else:
        birds = [Bird(230, 350)]

    floor = Floor(730)
    pipes =  [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    clock = pygame.time.Clock()

    playing = True
    while playing:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 playing = False
                 pygame.quit()
                 quit()
            if not ia_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > ((pipes[0].x + pipes[0].PIPE_TOP.get_width())):
                pipe_index = 1
        else:
            playing = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            genomes_list[i].fitness += 0.1
            output = neural_network[i].activate((bird.y, 
                                                abs(bird.y - pipes[pipe_index].height),
                                                abs(bird.y - pipes[pipe_index].pos_base)))
            if output[0] > 0.5:
                bird.jump()

        floor.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ia_playing:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        neural_network.pop(i)
                if not pipe.passed_on and bird.x > pipe.x:
                    pipe.passed_on = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
        
        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
            for genome in genomes_list:
                genome.fitness += 5
        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)
                if ia_playing:
                    genomes_list.pop(i)
                    neural_network.pop(i)

        draw_screen(screen, birds, pipes, floor, points)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ia_playing:
        population.run(main)
    else:
        main(None, None)


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    config_path = os.path.join(path,'config.txt')
    run(config_path)
