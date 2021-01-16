from math import radians, sin, cos, sqrt, pow
import pygame
import os

window_width = 1280
window_height = 720


def rotation_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)

    # to change also the center of teh origin_rec
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


class Car:
    def __init__(self):
        self.surface = pygame.image.load(os.path.join('assets', 'car.png'))
        self.surface = pygame.transform.smoothscale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.position = [600, 600]
        self.angle = 0
        self.speed = 0
        # set the center of rotation on the edge of the car
        self.center = [self.position[0] + 50, self.position[1] + 50]
        self.radars = []

        # four edge of the car (position of the walls of the car)
        self.four_points = []
        self.is_alive = True
        self.distance = 0
        self.time_spent = 0

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.position)

    def check_collision(self, road):
        for p in self.four_points:
            if road.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree, road):
        length = 0
        x = int(self.center[0] + cos(radians(360 - (self.angle + degree))))
        y = int(self.center[1] + sin(radians(360 - (self.angle + degree))))
        #                                 R     G    B   Alpha
        while not road.get_at((x, y)) == (255, 255, 255, 255) and length < 300:
            # length of the radar with respect to the wall
            length = length + 1
            x = int(self.center[0] + cos(radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + sin(radians(360 - (self.angle + degree))) * length)

        # the euclidean distance between teh car and the wall
        dist = int(sqrt(pow(x - self.center[0], 2) + pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, road):

        self.speed = 10

        # updating x position
        self.rotate_surface = rotation_center(self.surface, self.angle)
        self.position[0] += cos(radians(360 - self.angle)) * self.speed

        # calculating the distance taken
        self.distance += self.speed
        # calculating time spent
        self.time_spent += 1

        # updating y position
        self.position[1] += sin(radians(360 - self.angle)) * self.speed

        # we calculate the 4 collision points here
        # setting the edge of the car
        self.center = [int(self.position[0]) + 50, int(self.position[1]) + 50]

        # length of the collision distance positions
        length = 50

        #  position of the walls of the car
        left_top = [self.center[0] + cos(radians(360 - (self.angle + 30))) * length,
                    self.center[1] + sin(radians(360 - (self.angle + 30))) * length]

        right_top = [self.center[0] + cos(radians(360 - (self.angle + 150))) * length,
                     self.center[1] + sin(radians(360 - (self.angle + 150))) * length]

        left_bottom = [self.center[0] + cos(radians(360 - (self.angle + 210))) * length,
                       self.center[1] + sin(radians(360 - (self.angle + 210))) * length]

        right_bottom = [self.center[0] + cos(radians(360 - (self.angle + 330))) * length,
                        self.center[1] + sin(radians(360 - (self.angle + 330))) * length]

        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(road)
        self.radars.clear()

        # we check the radar from the 5 points -90 -45 0 45 90
        for d in range(-90, 120, 45):
            self.check_radar(d, road)

    # for getting the data of the radar, so we give them to the neural network
    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]

        # Neat takes list
        for i, r in enumerate(radars):
            ret[i] = int(r[1])
        return ret

    def check_alive(self):
        return self.is_alive

    # car taken more distance get more rewards
    def get_reward(self):
        return self.distance / 50.0
