import os
import sys
import neat
import pygame
from car import Car

window_width = 1280
window_height = 720

pygame.init()
generation_font = pygame.font.SysFont("comics", 30)
font = pygame.font.SysFont("comics", 30)

road = pygame.image.load(os.path.join('assets', 'road_0.png'))
generation = 0


def start(genomes, config_car):
    # we initial neat network here
    nets = []
    cars = []

    for idx, gen in genomes:
        net = neat.nn.FeedForwardNetwork.create(gen, config_car)
        nets.append(net)
        gen.fitness = 0

        # adding the cars
        cars.append(Car())

    # Initial the game in pygame
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()

    global generation
    generation += 1

    while True:
        # just for exiting the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Input my data and get result from network
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            # here we get the output of the network
            i = output.index(max(output))
            # if it is 0, we go right else we go left by 10 angles
            if i == 0:
                car.angle += 10
            else:
                car.angle -= 10

        # Update the cars and fitness
        remain_cars = 0
        for i, car in enumerate(cars):
            if car.check_alive():
                remain_cars += 1
                car.update(road)
                # here we are giving our car a reward if it stills alive
                genomes[i][1].fitness += car.get_reward()

        # check remaining cars
        if remain_cars == 0:
            break
        # Drawing
        screen.blit(road, (0, 0))
        for i, car in enumerate(cars):
            if car.check_alive():
                car.draw(screen)

        text = generation_font.render("Generation : " + str(generation), True, (165, 154, 0))
        text_rect = text.get_rect()
        text_rect.center = (75, 25)
        screen.blit(text, text_rect)

        text = font.render("remain cars : " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (90, 55)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    # Set configuration file of neat
    config_path = "config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    # using the algorithm config of neat
    p = neat.Population(config)

    # adding a reporter
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    print("Example of input: 0")
    num = input("Input the road number (from 0-4): ")
    if int(num) > 4 or int(num) < 0:
        print("Invalid input!")
        print("Example of input: 0")
        sys.exit(0)
    road = pygame.image.load(os.path.join('assets', f'road_{num}.png'))

    # run neat cars for 20 generations of 30 cars
    p.run(start, 20)
