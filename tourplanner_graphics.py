import pygame
from pygame.locals import *
from random import randrange


class ProcessControl():
    RUN   = 1
    PAUSE = 2
    WAIT  = 3


class TourplannerSurface():
    def __init__(self, settings, info, show_msg=False):
        pygame.init()
        self.show_msg = show_msg
        self.surface = pygame.display.set_mode((settings['width'], settings['height']))
        self.color1 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
        self.color2 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
        self.fps_clock = pygame.time.Clock()


        if self.show_msg:
            self.font_color = pygame.Color(180,255,80)
            self.font = pygame.font.Font('freesansbold.ttf', 24)
            self.surface_msg = self.font.render(info['usage'], False, self.font_color)
            self.msg_rect = self.surface_msg.get_rect()
            self.msg_rect.topleft = (250,200)
            self.surface.blit(self.surface_msg, self.msg_rect)


def print_clients(tour_surface, clients, slow=False):
    for client in clients:
        pygame.draw.circle(tour_surface.surface, tour_surface.color1, client.coords(), 4, 0)
        if slow:
            pygame.display.update()
            tour_surface.fps_clock.tick(30)
    if not slow:
        pygame.display.update()


def handle_user_events():
    while True:
        event = pygame.event.poll()

        if event.type == NOEVENT:
            return ProcessControl.RUN
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            return ProcessControl.PAUSE


