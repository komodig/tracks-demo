from math import sqrt
from client import Client
from tourplanner_graphics import print_route, print_area, print_clients, TourplannerSurface, \
        handle_user_events, ProcessControl
from client import find_next, ClientState as state
from copy import copy, deepcopy
from random import randrange
from config import SETTINGS, DISPLAY, DIMENSION
from time import sleep
from sys import stdout
from pygame import quit


class Tour():
    def __init__(self, origin, end, clients, start_client=None):
        self.client_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.route_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []   # for get_area() a referenced list with state CANDIDATE
        self.sorted_clients = [] # clients appended here get state ASSOCIATED
        self.length = 0.0

        if clients:         # this is for do_routing()
            self.clients = deepcopy(clients)
            for cli in self.clients:
                cli.state = state.CANDIDATE

        if start_client:
            for cli in self.clients:
                if cli == start_client:
                    self.assign(cli)
                    break


    def __lt__(self, other):
        return self.length < other.length


    def __repr__(self):
        return ('%s' % self.sorted_clients)


    def assign(self, client):
        if len(self.sorted_clients):
            self.length += client.distance_to(self.sorted_clients[-1])
        client.state = state.ASSOCIATED
        self.sorted_clients.append(client)


    def add_area_clients(self, all_clients, add_them=True):
        count = 0
        for client in all_clients.clients:
            if client.state != state.FREE:
                continue
            if (client.x > self.origin.x or client.x == self.origin.x == 0) and client.x <= self.end.x and \
                    (client.y > self.origin.y or client.y == self.origin.y == 0) and client.y <= self.end.y:
                count += 1
                if add_them:
                    client.state = state.CANDIDATE
                    self.clients.append(client)
                    print('add_area_clients: appended client: %s' % client)

        if add_them:
            print('got tour area at (%d,%d) (%d x %d) with %d clients' % \
                    (self.origin.x, self.origin.y, self.width, self.height, len(self.clients)))
        return count


    def count_area_clients(self, all_clients):
        count = self.add_area_clients(all_clients, False)
        return count


def find_best_route(all_clients, tour, cluster_size):
    if len(tour.sorted_clients) < cluster_size:
        other_tour = deepcopy(tour)

        next_client = find_next(tour.sorted_clients[-1], tour.clients)
        tour.assign(next_client)
        if DISPLAY['routing']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour, cluster_size)

        next_next_client = find_next(next_client, other_tour.clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            if DISPLAY['routing']: print_route(all_clients, other_tour)
            b = find_best_route(all_clients, other_tour, cluster_size)

        return a if a < b else b
    else:
        return tour


def get_next_area_with_clients(origin, all_clients):
    area_width = SETTINGS['width'] * DIMENSION[0]['x_factor']
    area_height = SETTINGS['height'] * DIMENSION[0]['y_factor']
    end = Client(origin.x + area_width, origin.y + area_height)
    area = Tour(origin, end, None)
    while area.count_area_clients(all_clients) == 0:
        if area.end.x + area_width > SETTINGS['width']:
            if area.end.y + area_height > SETTINGS['height']:
                print('END OF TOTAL AREA!')
                return None
            area.origin.x = 0
            area.origin.y += area_height
            area.end.x = area_width
            area.end.y += area_height
        else:
            area.origin.x += area_width
            area.end.x += area_width

    return area


def get_area(all_clients, last_tour, dim_surface):
    last_end = Client(last_tour.end.x, last_tour.origin.y)
    small_area = get_next_area_with_clients(last_end, all_clients)
    if small_area is None:
        return None
    cli = small_area.add_area_clients(all_clients)
    print('small_area has %d clients' % cli)
    return small_area


def new_surface(SETTINGS):
    temp_origin = Client(0, 0)
    temp_end = Client(SETTINGS['width'], SETTINGS['height'])
    temp_tour = Tour(temp_origin, temp_end, [temp_origin])
    return TourplannerSurface(SETTINGS, None, temp_tour)


def clients_have_state(all_clients, booh_state, surface):
    booh_clients = []
    for cli in all_clients.clients:
        if cli.state == booh_state:
            booh_clients.append(cli)
    print('remaining FREE clients: %d' % len(booh_clients))
    print_clients(surface, booh_clients, False, True)

    return len(booh_clients)


def calculate_all_tours(all_clients, SETTINGS):
    surface = new_surface(SETTINGS)
    small_area = Tour(Client(0, 0), Client(0, 0), None)

    while True:
        small_area = get_area(all_clients, small_area, surface)
        if small_area is None:
            break
        print_area(SETTINGS, all_clients, small_area.origin, small_area.end, surface)
        all_clients.small_areas.append(small_area)

    free_clients = clients_have_state(all_clients, state.FREE, surface)
    sleep(1)
    if free_clients:
        surface.process.state = ProcessControl.WAIT
    handle_user_events(surface.process)
    quit() # pygame
    exit(0)

    all_clients.final_print = True
    print_route(all_clients, nice_tour)


def do_routing(all_clients, SETTINGS, tour):
    best_tour = None
    for start_client in tour.clients:
        tour = Tour(tour.origin, tour.end, tour.clients, start_client)
        res_tour = find_best_route(all_clients, tour, SETTINGS['cluster_size'])
        print_route(all_clients, res_tour)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    return best_tour


