from time import sleep
from config import SETTINGS, INFO, DISPLAY
if DISPLAY['enable']:
    from pygame import display, SRCALPHA, NOFRAME, Color, Surface, draw, time as pygame_time, init as pygame_init
    from pygame.locals import *
from client import Client
from copy import copy
from utils import export_as_file


class TourplannerSurface():
    def __init__(self, display_surface, show_msg=False):
        self.client_color = Color(*DISPLAY['color']['spot'])
        self.route_color = Color(*DISPLAY['color']['line'])
        self.emph_color = Color(255,0,0)
        self.fps_clock = pygame_time.Clock()
        self.surface = Surface(display_surface.get_size(), SRCALPHA, 32)

        self.surface.fill((255,0,255))
        self.surface.set_colorkey((255,0,255))
        self.surface = self.surface.convert_alpha()


    def change_color(self, color_scheme):
        self.client_color = Color(*DISPLAY[color_scheme]['spot'])
        self.route_color = Color(*DISPLAY[color_scheme]['line'])


def graphics_init():
    pygame_init()
    if DISPLAY['enable']:
        surface = display.set_mode((SETTINGS['width'], SETTINGS['height']))
    else:
        surface = display.set_mode((SETTINGS['width'], SETTINGS['height']), NOFRAME)

    return surface


def display_clear(display_surface):
    display_surface.fill((255,255,255))
    if DISPLAY['enable']:
        display.update()


def display_update(display_surf, other_surf):
    display_surf.blit(other_surf.surface, (0,0))

    if DISPLAY['enable']:
        display.update()
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


def print_clients(tour_surface, clients, slow=False, circle=False, tour=None):
    width = 2 if circle else 0
    radius = 16 if circle else scaled_radius(**SETTINGS)
    color = tour_surface.emph_color if circle else tour_surface.client_color
    for client in clients:
        draw.circle(tour_surface.surface, color, client.coords(), radius, width)
        if tour and client == tour.plan[0]:
            draw.circle(tour_surface.surface, tour_surface.emph_color, client.coords(), 16, 2)

    return tour_surface


def print_earlier_tours(all_clients, surface):
    previous = None
    for earlier in all_clients.final_areas:
        area_tour = earlier.tours[-1]
        for assigned in area_tour.plan:
            if previous is not None:
                draw.line(surface.surface, surface.route_color, previous.coords(), assigned.coords(), 2)
            previous = assigned
        previous = None


def print_route(display_surface, all_clients, tour):
    display_clear(display_surface)
    slowly = False
    tour_surface = TourplannerSurface(display_surface)
    if all_clients.first_print:
        slowly = True
        all_clients.first_print = False
        sleep(2)

    if all_clients.final_print:
        tour_surface.change_color('color2')

    tour_surface = print_clients(tour_surface, tour.clients, False, False, tour)

    prev = None
    for rcli in tour.plan:
        if not prev:
            prev = rcli
            continue
#        print_earlier_tours(all_clients, tour_surface)
#        tour_surface = print_clients(tour_surface, all_clients.clients, False)
        draw.line(tour_surface.surface, tour_surface.route_color, prev.coords(), rcli.coords(), 2)
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

    return tour_surface


def print_area(tour_surface, clients_inside, origin, end):
    if clients_inside: print_clients(tour_surface, clients_inside.clients, False)
    draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (end.x, origin.y), 2)
    draw.line(tour_surface.surface, tour_surface.route_color, (end.x, origin.y), (end.x, end.y), 2)
    draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, origin.y), (origin.x, end.y), 2)
    draw.line(tour_surface.surface, tour_surface.route_color, (origin.x, end.y), (end.x, end.y), 2)
    display.update()
    tour_surface.fps_clock.tick(30)


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
            return

        a = intro_clients[ax]
        b = intro_clients[bx]
        draw.line(intro_surface.surface, intro_surface.route_color, (a.x, a.y), (b.x, b.y), 8)
        sleep(0.1)
        display.update()
        intro_surface.fps_clock.tick(30)


