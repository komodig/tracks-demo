from time import sleep
import pygame
from pygame.locals import *
from config import SETTINGS, INFO


class ProcessControl():
    WAIT  = 0
    RUN   = 1
    PAUSE = 2

    def __init__(self):
        self.state = ProcessControl.RUN


class TourplannerSurface():
    def __init__(self, SETTINGS, INFO, tour, show_msg=False):
        pygame.init()
        self.show_msg = show_msg
        self.surface = pygame.display.set_mode((SETTINGS['width'], SETTINGS['height']))
        self.client_color = pygame.Color(*tour.client_color)
        self.route_color = pygame.Color(*tour.route_color)
        self.fps_clock = pygame.time.Clock()


        if self.show_msg:
            self.font_color = pygame.Color(180,255,80)
            self.font = pygame.font.Font('freesansbold.ttf', 24)
            self.surface_msg = self.font.render(INFO['usage'], False, self.font_color)
            self.msg_rect = self.surface_msg.get_rect()
            self.msg_rect.topleft = (250,200)
            self.surface.blit(self.surface_msg, self.msg_rect)

        self.process = ProcessControl()


def print_clients(tour_surface, clients, slow=False):
    for client in clients:
        pygame.draw.circle(tour_surface.surface, tour_surface.client_color, client.coords(), 4, 0)
        if slow:
            pygame.display.update()
            tour_surface.fps_clock.tick(30)
    if not slow:
        pygame.display.update()


def print_route(all_clients, tour):
    show_msg = False
    print_slowly = False
    if not all_clients.printed:
        all_clients.printed += 1
        show_msg = True
        print_slowly = True
    elif all_clients.printed <= 7:
        all_clients.printed += 1
        show_msg = True

    tour_surface = TourplannerSurface(SETTINGS, INFO, tour, show_msg)
    print_clients(tour_surface, all_clients.clients, print_slowly)
    for x in range(len(tour.sorted_clients) - 1):
        pygame.draw.line(tour_surface.surface, tour_surface.route_color, tour.sorted_clients[x].coords(), tour.sorted_clients[x+1].coords(), 2)
        pygame.display.update()
        tour_surface.fps_clock.tick(30)

    if all_clients.final_print:
        tour_surface.process.state = ProcessControl.WAIT
    handle_user_events(tour_surface.process)


def handle_user_events(process):
    while True:
        event = pygame.event.poll()

        if event.type == NOEVENT:
            if process.state == ProcessControl.RUN:
                break
            elif process.state == ProcessControl.WAIT or process.state == ProcessControl.PAUSE:
                sleep(1)
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                exit()
            elif event.key == K_SPACE:
                if process.state == ProcessControl.RUN:
                    print('  === paused ===')
                    process.state = ProcessControl.PAUSE
                elif process.state == ProcessControl.PAUSE:
                    process.state = ProcessControl.RUN
                    break

