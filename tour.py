from math import sqrt
from client import Client
from tourplanner_graphics import print_route, print_area, TourplannerSurface, \
        handle_user_events, ProcessControl
from client import find_next, ClientState as state
from copy import copy, deepcopy
from random import randrange
from config import SETTINGS, DISPLAY, DIMENSION
from time import sleep
from sys import stdout


class Tour():
    def __init__(self, origin, end, clients, start_client=None):
        self.client_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.route_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []   # for get_dimensions() a referenced list with state CANDIDATE
        self.sorted_clients = [] # clients appended here get state ASSOCIATED
        self.length = 0.0
        self.x_factor = DIMENSION[0]['x_factor']
        self.y_factor = DIMENSION[0]['y_factor']
        self.d_mod = 0

        if clients:         # this is for do_routing()
            self.clients = deepcopy(clients)
            for cli in self.clients:
                cli.state = state.CANDIDATE

        if start_client:
            for cli in self.clients:
                if cli == start_client:
                    self.assign(cli)
                    break

       # try:
       #     print('got tour area at (%d,%d) (%d x %d) with %d clients and %s as start client' % \
       #             (origin.x, origin.y, self.width, self.height, len(clients), start_client))
       # except TypeError:
       #     pass


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
#                if add_them:
#                    print('add_area_clients: skipping unfree client: %s' % client)
                continue
            if client.x > self.origin.x and client.x < self.end.x and \
                    client.y > self.origin.y and client.y < self.end.y:
                count += 1
                if add_them:
                    client.state = state.CANDIDATE
                    self.clients.append(client)
                    print('add_area_clients: appended client: %s' % client)
#                else:
#                    print('add_area_clients: counted client: %s' % client)

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


def define_tour_clients(all_clients, tour, cluster_size):
    ex = None
    kicked_clients = []
    while len(tour.clients) > cluster_size:
        ex = find_next(tour.end, tour.clients)
        ex.state = state.FREE
        kicked_clients.append(ex)
        tour.clients.remove(ex)

    ex = None
    if len(kicked_clients):
        print('kicked %d clients: %s' % (len(kicked_clients), kicked_clients))
        for kicked in kicked_clients:
            if ex is None or kicked.distance_to(tour.end) > ex.distance_to(tour.end):
                ex = kicked

    all_clients.append_init_tour(tour)

    return ex


def get_dimensions(all_clients, origin, lateral_length, dim_surface, SETTINGS):
    


def new_surface(SETTINGS):
    temp_origin = Client(0, 0)
    temp_end = Client(SETTINGS['width'], SETTINGS['height'])
    temp_tour = Tour(temp_origin, temp_end, [temp_origin])
    return TourplannerSurface(SETTINGS, None, temp_tour)


def clients_have_state(all_clients, booh_state):
    booh_clients = []
    for cli in all_clients.clients:
        if cli.state == booh_state:
            booh_clients.append(cli)
    print('remaining FREE clients: %d' % len(booh_clients))

    return len(booh_clients)


def calculate_all_tours(all_clients, SETTINGS):
    lateral_length = sqrt(SETTINGS['width'] * SETTINGS['height'] / (SETTINGS['clusters'] * 2))   # begin with explicit short dimension
    print('lateral_length: %f' % lateral_length)
    surface = new_surface(SETTINGS)
    origin = Client(0,0)

    while clients_have_state(all_clients, state.FREE):
        origin = get_dimensions(all_clients, origin, lateral_length, surface, SETTINGS)

    for ll in range(len(all_clients.init_tours)):
        print all_clients.init_tours[ll]
    sleep(2)
    handle_user_events(surface.process)
    for ll in range(len(all_clients.init_tours)):
        for tour in all_clients.init_tours[ll]:
            nice_tour = do_routing(all_clients, SETTINGS, tour)
            all_clients.best_tours.append(nice_tour)

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


