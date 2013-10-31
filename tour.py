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
        self.clients = []   # for get_dimensions() a referenced list of clients is needed!
        self.sorted_clients = []
        self.length = 0.0

        if clients:         # this is for do_routing()
            self.clients = deepcopy(clients)

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


def client_in_list(client, cli_list):
    for cli in cli_list:
        if cli == client: return True

    return False


def find_clients(area, clients):
    for client in clients.clients:
        if client_in_list(client, area.clients) or client.state == state.CANDIDATE:
            continue
        if client.x > area.origin.x and client.x < area.end.x and \
                client.y > area.origin.y and client.y < area.end.y:
            area.clients.append(client)

    return area


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


def define_tour_clients(all_clients, tour, cluster_size, end):
    ex = None
    kicked_clients = []
    while len(tour.clients) > cluster_size:
        ex = find_next(end, tour.clients)
        kicked_clients.append(ex)
        tour.clients.remove(ex)

    ex = None
    if len(kicked_clients):
        print('kicked %d clients: %s' % (len(kicked_clients), kicked_clients))
        for kicked in kicked_clients:
            if ex is None or kicked.distance_to(end) > ex.distance_to(end):
                ex = kicked

    for cli in tour.clients:
        cli.state = state.CANDIDATE

    if all_clients.init_tours.state == TourState.FIXED:
        all_clients.init_tours.append([tour, ])
        all_clients.init_tours_state = TourState.OPEN:
    elif all_clients.init_tours_state == TourState.OPEN:
        all_clients.init_tours[-1].append(tour)
    else:
        print('dunno what to do with tour!')
        exit(1)

    return ex


def neighbour_candidates(area, all_clients, SETTINGS):
    neighbours = find_clients(area, all_clients)
    print('found neighbours: %d' % len(neighbours))
    return (len(neighbours.clients) % SETTINGS['cluster_size'])


def get_dimensions(all_clients, origin, lateral_length, dim_surface, SETTINGS):
    end = Client(origin.x + lateral_length, origin.y + lateral_length)
    area = Tour(origin, end, None)
    while len(find_clients(area, all_clients).clients) < SETTINGS['cluster_size']:
        Tour(Client(area.end.x, area.origin.y), Client(SETTINGS['width'], area.end.y), all_clients)
        quantity_east = candidates_east(area, all_clients, SETTINGS))
        quantity_south = candidates_south(area, all_clients, SETTINGS))


def new_surface(origin, end):
    temp_client = Client(0, 0)
    temp_tour = Tour(origin, end, [temp_client])
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

    while clients_have_state(all_clients, state.UNASSOCIATED):
        get_dimensions(all_clients, Client(0,0), lateral_length, None, SETTINGS)

#    sleep(2)
#    handle_user_events(dim_surface.process)
#
#    for tour_clients in all_clients.init_tours:
#        nice_tour = do_routing(all_clients, SETTINGS, tour_clients, origin, end)
#        all_clients.best_tours.append(nice_tour)

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


