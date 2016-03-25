from time import sleep
import pygame
from pygame.locals import *
from config import SETTINGS, INFO, DISPLAY
from client import Client
from copy import copy

class ProcessControl():
    WAIT  = 0
    RUN   = 1
    PAUSE = 2

    def __init__(self):
        self.state = ProcessControl.RUN


class TourplannerSurface():
    def __init__(self, display_surface, show_msg=False):
        self.show_msg = show_msg
        self.client_color = pygame.Color(*DISPLAY['color']['spot'])
        self.route_color = pygame.Color(*DISPLAY['color']['line'])
        self.emph_color = pygame.Color(255,255,255)
        self.fps_clock = pygame.time.Clock()
        self.surface = pygame.Surface(display_surface.get_size(), pygame.SRCALPHA, 32)

        self.surface.fill((255,0,255))
        self.surface.set_colorkey((255,0,255))
        self.surface = self.surface.convert_alpha()

        if self.show_msg:
            self.font_color = pygame.Color(100,150,60)
            self.font = pygame.font.Font('freesansbold.ttf', 24)
            self.surface_msg = self.font.render(INFO['usage'], False, self.font_color)
            self.msg_rect = self.surface_msg.get_rect()
            self.msg_rect.topleft = (250,200)
            display_surface.blit(self.surface_msg, self.msg_rect)

        self.process = ProcessControl()

    def change_color(self, color_scheme):
        self.client_color = pygame.Color(*DISPLAY[color_scheme]['spot'])
        self.route_color = pygame.Color(*DISPLAY[color_scheme]['line'])


def pygame_init():
    pygame.init()
    surface = pygame.display.set_mode((SETTINGS['width'], SETTINGS['height']))

    return surface


def display_clear(display_surface):
    display_surface.fill((255,255,255))
    pygame.display.update()


def display_update(display_surf, other_surf):
    display_surf.blit(other_surf.surface, (0,0))
    pygame.display.update()
    other_surf.fps_clock.tick(30)


def scaled_radius(clients, cluster_size_min, cluster_size_max, width, height):
    space_per_client = width * height / clients
    #print('space per client: %d' % space_per_client)
    if space_per_client < 500:
        return 1
    elif space_per_client < 1000:
        return 2
    else:
        return 3


def print_clients(tour_surface, clients, slow=False, circle=False):
    width = 2 if circle else 0
    radius = 16 if circle else scaled_radius(**SETTINGS)
    color = tour_surface.emph_color if circle else tour_surface.client_color
    for client in clients:
        pygame.draw.circle(tour_surface.surface, color, client.coords(), radius, width)

    return tour_surface


def print_earlier_tours(all_clients, surface):
    previous = None
    for earlier in all_clients.final_areas:
        area_tour = earlier.tours[-1]
        for assigned in area_tour.plan:
            if previous is not None:
                pygame.draw.line(surface.surface, surface.route_color, previous.coords(), assigned.coords(), 2)
            previous = assigned
        previous = None


def print_route(display_surface, all_clients, tour, tour_surface=None):
    display_clear(display_surface)
    slowly = False
    if all_clients.first_print:
        tour_surface = TourplannerSurface(display_surface)
        slowly = True
        all_clients.first_print = False
        sleep(2)
        handle_user_events(tour_surface.process)

    if tour_surface is None:
        tour_surface = TourplannerSurface(display_surface)

    if all_clients.final_print:
        tour_surface.change_color('color2')

    tour_surface = print_clients(tour_surface, all_clients.clients, False)

    prev = None
    for rcli in tour.plan:
        if not prev:
            prev = rcli
            continue
#        print_earlier_tours(all_clients, tour_surface)
#        tour_surface = print_clients(tour_surface, all_clients.clients, False)
        pygame.draw.line(tour_surface.surface, tour_surface.route_color, prev.coords(), rcli.coords(), 2)
        prev = rcli

    display_update(display_surface, tour_surface)
    seconds = DISPLAY['routing']['slow']
    if seconds:
        sleep(seconds)

    if all_clients.final_print:
        if DISPLAY['areas']['show_final']:
            tour_surface.change_color('color2')
            for fa in all_clients.final_areas:
                print_area(tour_surface, all_clients, fa.origin, fa.end)
        tour_surface.process.state = ProcessControl.WAIT
    handle_user_events(tour_surface.process)

    return tour_surface


def print_area(tour_surface, clients_inside, origin, end):
    if clients_inside: print_clients(tour_surface, clients_inside.clients, False)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (end.x, origin.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (end.x, origin.y), (end.x, end.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (origin.x, end.y), 2)
    pygame.draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, end.y), (end.x, end.y), 2)
    pygame.display.update()
    tour_surface.fps_clock.tick(30)


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


def intro(display_surface):
    wd6 = SETTINGS['width'] / 6
    hd6 = SETTINGS['height'] / 6
    center = Client(SETTINGS['width'] / 2, SETTINGS['height'] / 2)
    intro_clients = []
    intro_clients.append(Client(center.x - wd6 - wd6/5, center.y + hd6))
    intro_clients.append(Client(center.x - wd6, center.y - hd6 - hd6/7))
    intro_clients.append(Client(center.x + wd6/10, center.y - int(2.3 * hd6)))
    intro_clients.append(Client(center.x + wd6, center.y - hd6 + hd6/6))
    intro_clients.append(Client(center.x + wd6 - wd6/4, center.y + hd6 - hd6/5))

    order = (0, 1, 2, 3, 1, 4, 3, 0, 4)

    intro_surface = TourplannerSurface(display_surface)
    for cx in range(len(order)):
        try:
            ax = order[cx]
            bx = order[cx + 1]
        except IndexError:
            sleep(3)
            handle_user_events(intro_surface.process)
            return

        a = intro_clients[ax]
        b = intro_clients[bx]
        pygame.draw.line(intro_surface.surface, intro_surface.route_color, (a.x, a.y), (b.x, b.y), 8)
        sleep(0.1)
        pygame.display.update()
        intro_surface.fps_clock.tick(30)


