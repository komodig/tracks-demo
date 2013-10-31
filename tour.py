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
        self.width = end.x
        self.height = end.y
        self.clients = deepcopy(clients)
        self.sorted_clients = []
        self.length = 0.0

        if start_client:
            for c in self.clients:
                if c == start_client:
                    self.assign(c)
                    break

        print('got tour area at (%d,%d) (%d x %d) with %d clients and %s as start client' % \
                (origin.x, origin.y, self.width, self.height, len(clients), start_client))


    def __lt__(self, other):
        return self.length < other.length


    def __repr__(self):
        return ('%s' % self.sorted_clients)


    def assign(self, client):
        if len(self.sorted_clients):
            self.length += client.distance_to(self.sorted_clients[-1])
        client.state = state.ASSOCIATED
        self.sorted_clients.append(client)


def find_tour_clients(origin, end, clients):
    tour_clients = []
    for client in clients.clients:
        if client.state == state.CANDIDATE: continue
        if client.x > origin.x and client.x < end.x and \
                client.y > origin.y and client.y < end.y:
            tour_clients.append(client)

    return tour_clients


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


def define_tour_clients(all_clients, tour_clients, cluster_size, end_of_area):
    ex = None
    end = Client(end_of_area.x, end_of_area.y)
    kicked_clients = []
    while len(tour_clients) > cluster_size:
        ex = find_next(end, tour_clients)
        kicked_clients.append(ex)
        tour_clients.remove(ex)

    ex = None
    if len(kicked_clients):
        print('kicked %d clients: %s' % (len(kicked_clients), kicked_clients))
        for kicked in kicked_clients:
            if ex is None or kicked.distance_to(end) > ex.distance_to(end):
                ex = kicked

    for cli in tour_clients:
        cli.state = state.CANDIDATE
    all_clients.init_tours.append(tour_clients)

    return ex


def get_dimensions(all_clients, origin, lateral_length, dim_surface, clusters, cluster_size, width, height):
    end = Client(origin.x + lateral_length, origin.y + lateral_length)
    tour_clients = []
    calculating = '+'

    while len(tour_clients) < cluster_size:
        if (end.x > width and end.y > height):
            clients_left = clients_have_state(all_clients, state.UNASSOCIATED)
            if clients_left < cluster_size:
                print('\nnot enough clients left: %d, try something else!\n' % clients_left)
                dim_surface.process.state = ProcessControl.WAIT
                handle_user_events(dim_surface.process)
            elif clients_left >= cluster_size:
                origin  = Client(0,0)
                end = Client(width, height)
                return origin, end, dim_surface

        stdout.write(calculating)
        stdout.flush()
        calculating += '+'

        end = Client(end.x + width * all_clients.x_factor, end.y + height * all_clients.y_factor)
        tour_clients = find_tour_clients(origin, end, all_clients)

        if dim_surface is None:
            dim_surface = new_surface(origin, end)
        print_area(SETTINGS, all_clients, origin, end, dim_surface)

    ex = define_tour_clients(all_clients, tour_clients, cluster_size, end)
    print('\nFINALLY! got nice area origin: [%s] end: [%s] with %d clients' % (origin, end, len(tour_clients)))
    if ex is None:
        origin  = Client(end.x - lateral_length/2, origin.y) # -lateral_length/2 because it might be good to start a little to the left. just a feeling :-)
    else:
        origin  = Client(ex.x, origin.y)

    if origin.x + lateral_length >= width:
        origin = Client(0, lateral_length)

    print('starting with new area origin: [%s] end: [%s]' % (origin, end))

    return origin, end, dim_surface


def new_surface(origin, end):
    temp_client = Client(0, 0)
    temp_tour = Tour(origin, end, [temp_client], temp_client)
    return TourplannerSurface(SETTINGS, None, temp_tour)


def clients_have_state(all_clients, booh_state):
    booh_clients = []
    for cli in all_clients.clients:
        if cli.state == booh_state:
            booh_clients.append(cli)
    #print('BOOH: %d' % len(booh_clients))

    return len(booh_clients)


def calculate_all_tours(all_clients, SETTINGS):
    lateral_length = sqrt(SETTINGS['width'] * SETTINGS['height'] / (SETTINGS['clusters'] * 2))   # begin with explicit short dimension
    origin = Client(0,0)
    dim_surface = None

    while clients_have_state(all_clients, state.UNASSOCIATED):
        origin, end, dim_surface = get_dimensions(all_clients, origin, lateral_length, dim_surface, **SETTINGS)

    sleep(2)
    handle_user_events(dim_surface.process)

    for tour_clients in all_clients.init_tours:
        nice_tour = do_routing(all_clients, SETTINGS, tour_clients, origin, end)
        all_clients.best_tours.append(nice_tour)

    all_clients.final_print = True
    print_route(all_clients, nice_tour)


def do_routing(all_clients, SETTINGS, tour_clients, origin, end):
    best_tour = None
    for start_client in tour_clients:
        tour = Tour(origin, end, tour_clients, start_client)
        res_tour = find_best_route(all_clients, tour, SETTINGS['cluster_size'])
        print_route(all_clients, res_tour)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    return best_tour


