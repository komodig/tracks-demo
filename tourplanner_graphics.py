from time import sleep
import pygame
from pygame.locals import *
from random import randrange
from config import SETTINGS, INFO
from client import count_with_state, get_with_state, ClientState as state

class ProcessControl():
    WAIT  = 0
    RUN   = 1
    PAUSE = 2

    def __init__(self):
        self.state = ProcessControl.RUN


class TourplannerSurface():
    def __init__(self, show_msg=False):
        pygame.init()
        self.show_msg = show_msg
        self.surface = pygame.display.set_mode((SETTINGS['width'], SETTINGS['height']))
        self.client_color = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
        self.route_color = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
        self.emph_color = pygame.Color(255,255,255)
        self.fps_clock = pygame.time.Clock()


        if self.show_msg:
            self.font_color = pygame.Color(100,150,60)
            self.font = pygame.font.Font('freesansbold.ttf', 24)
            self.surface_msg = self.font.render(INFO['usage'], False, self.font_color)
            self.msg_rect = self.surface_msg.get_rect()
            self.msg_rect.topleft = (250,200)
            self.surface.blit(self.surface_msg, self.msg_rect)

        self.process = ProcessControl()

    def change_route_color(self):
        rgb = (0,255,0)
        self.route_color = pygame.Color(*rgb)


def print_clients(tour_surface, clients, slow=False, circle=False):
    width = 2 if circle else 0
    dotsize = 3 if len(clients) <= 500 else 2
    radius = 16 if circle else 3
    color = tour_surface.emph_color if circle else tour_surface.client_color
    for client in clients:
        pygame.draw.circle(tour_surface.surface, color, client.coords(), radius, width)
        if slow:
            pygame.display.update()
            tour_surface.fps_clock.tick(30)
    if not slow:
        pygame.display.update()


def print_earlier_tours(all_clients, surface):
    for earlier in all_clients.best_tours:
        assigned = earlier.first_assigned
        while assigned.next_assigned:
            pygame.draw.line(surface.surface, surface.route_color, assigned.coords(), assigned.next_assigned.coords(), 2)
            assigned = assigned.next_assigned


def print_route(all_clients, tour):
    if all_clients.first_print:
        tour_surface = print_screen_set(TourplannerSurface(True), False, [None, all_clients.clients, True])
        all_clients.first_print = False
        sleep(2)
        handle_user_events(tour_surface.process)
    else:
        tour_surface = print_screen_set(TourplannerSurface(), False, [None, all_clients.clients, False])

    assigned = tour.first_assigned
    while assigned.next_assigned:
        print_earlier_tours(all_clients, tour_surface)
        pygame.draw.line(tour_surface.surface, tour_surface.route_color, assigned.coords(), assigned.next_assigned.coords(), 2)
        assigned = assigned.next_assigned
        pygame.display.update()
        tour_surface.fps_clock.tick(30)

    if all_clients.final_print:
        tour_surface.process.state = ProcessControl.WAIT
    handle_user_events(tour_surface.process)


def print_area(tour_surface, all_clients, origin, end):
    print_clients(tour_surface, all_clients.clients, False)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (end.x, origin.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (end.x, origin.y), (end.x, end.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (origin.x, end.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, end.y), (end.x, end.y), 2)
    pygame.display.update()
    tour_surface.fps_clock.tick(30)


def print_screen_set(surface, exit_afterwards, p_client_param=None, p_area_param=None, p_tour_param=None):
    print('print_screen_set()')
    if p_client_param:
        p_client_param[0] = surface
        print_clients(*p_client_param)
    if p_area_param:
        p_area_param[0] = surface
        print_area(*p_area_param)
    if p_tour_param: print_route(*p_tour_param)

    if exit_afterwards: exit(7)
    return surface


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
                exit(0)
            elif event.key == K_SPACE:
                if process.state == ProcessControl.RUN:
                    print('  === paused ===')
                    process.state = ProcessControl.PAUSE
                elif process.state == ProcessControl.PAUSE:
                    process.state = ProcessControl.RUN
                    break

