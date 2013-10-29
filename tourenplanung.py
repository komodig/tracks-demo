from random import randrange
import pygame
from pygame.locals import *
from sys import exit
from time import sleep
from math import sqrt, pow
from copy import copy

settings = {'width': 1000, 'height': 700}

def init_dots():
    dots = []
    for i in range(0,200):
        dots.append((randrange(1, settings['width']), randrange(1, settings['height'])))
    
    return dots


def distance(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]

    return sqrt(pow(x,2) + pow(y,2))


def find_next(dot, dotlist):
    closest = dotlist[0] 
    for x in dotlist[1:]:
        if distance(dot, x) < distance(dot, closest):
            closest = x

    return closest


def get_exit_event():
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            exit()


def print_dots(dotlist, wait_for_user=1):
    pygame.init()
    surface = pygame.display.set_mode((settings['width'], settings['height']))
    color1 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    color2 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    fps_clock = pygame.time.Clock()
    
    for dot in dotlist:
        pygame.draw.circle(surface, color1, (dot[0],dot[1]), 4, 0)
        pygame.display.update()
        fps_clock.tick(30)

    dot1 = dotlist[0]
    dotlist.remove(dot1)
    while len(dotlist):
        dot2 = find_next(dot1, dotlist) 
        pygame.draw.line(surface, color2, dot1, dot2, 2)
        pygame.display.update()
        fps_clock.tick(30)
        try:
            dotlist.remove(dot1)
        except ValueError:
            pass
        dot1 = copy(dot2)

    if wait_for_user:
        while 1:
            get_exit_event()
            sleep(1)
    else:
        sleep(3)
        get_exit_event()


if __name__ == '__main__':
    for c in range(0,100):
        dots = init_dots()
        print_dots(dots, 0)

