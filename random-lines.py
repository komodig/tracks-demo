from random import randrange
import pygame
from pygame.locals import *
from sys import exit
from time import sleep

def init_dots():
    dots = []
    for i in range(0,100):
        dots.append((randrange(1,800),randrange(1,600)))
    
    return dots


def print_dots(dotlist):
    pygame.init()
    surface = pygame.display.set_mode((800,600))
    red = pygame.Color(255,0,0)
    green = pygame.Color(0,255,0)
    blue = pygame.Color(0,0,255)
    fps_clock = pygame.time.Clock()
    
    for dot in dotlist:
        pygame.draw.circle(surface, green, (dot[0],dot[1]), 4, 0)
        pygame.display.update()
        fps_clock.tick(30)

    #dotlist.sort()
    idx = 0
    while idx+1 < len(dotlist):
        dot1 = dotlist[idx]
        dot2 = dotlist[idx+1]
        pygame.draw.line(surface, blue, dot1, dot2, 2)
        pygame.display.update()
        fps_clock.tick(30)
        idx += 1 

    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()

        sleep(1)


if __name__ == '__main__':
    dots = init_dots()
    print_dots(dots)

