from math import sqrt
from client import Client
from tourplanner_graphics import print_route
from client import find_next, ClientState as state
from copy import copy, deepcopy
from random import randrange


class Tour():
    def __init__(self, origin, end, clients, start_client):
        self.client_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.route_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.origin = origin
        self.width = end[0]
        self.height = end[1]
        self.clients = deepcopy(clients)
        self.sorted_clients = []
        self.length = 0.0

        for c in self.clients:
            if c == start_client:
                self.assign(c)
                break

        print('got tour area at (%d,%d) (%d x %d) with %d clients and %s as start client' % \
                (origin[0], origin[1], self.width, self.height, len(clients), start_client))


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
        if client.x > origin[0] and client.x < (origin[0] + end[0]) and \
                client.y > origin[1] and client.y < (origin[1] + end[1]):
            tour_clients.append(client)

    return tour_clients


def find_best_route(all_clients, tour, cluster_size):
    if len(tour.sorted_clients) < cluster_size:
        other_tour = deepcopy(tour)

        next_client = find_next(tour.sorted_clients[-1], tour.clients)
        tour.assign(next_client)
        #print_route(all_clients, tour)
        a = find_best_route(all_clients, tour, cluster_size)

        next_next_client = find_next(next_client, other_tour.clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            #print_route(all_clients, other_tour)
            b = find_best_route(all_clients, other_tour, cluster_size)

        return a if a < b else b
    else:
        return tour


def define_tour_clients(all_clients, tour_clients, cluster_size, end_of_area):
    ex = None
    while len(tour_clients) > cluster_size:
        ex = find_next(Client(end_of_area[0], end_of_area[1]), tour_clients)
        print('kick this one out: %s' % ex)
        tour_clients.remove(ex)

    for cli in tour_clients:
        cli.state = state.CANDIDATE
    all_clients.init_tours.append(tour_clients)
    for x in all_clients.clients:
        for y in all_clients.init_tours[-1]:
            if x is y: print('found it!!')
    print all_clients.init_tours[-1]

    return ex


def get_dimensions(all_clients, origin, clusters, cluster_size, width, height):
    lateral_length = sqrt(width * height / (clusters * 2))   # begin with explicit short dimension
    end = (origin[0] + lateral_length, origin[1] + lateral_length)
    tour_clients = []

    print('    find tour clients in area: %s - %s' % (origin, end))
    while len(tour_clients) < cluster_size:
        if end[0] > width and end[1] > height:
            print('\nnot enough clients, try something else!\n')
            exit()
        end = (end[0] + width/100, end[1] + height/100)
        tour_clients = find_tour_clients(origin, end, all_clients)

    ex = define_tour_clients(all_clients, tour_clients, cluster_size, end)
    print('    finally got area: %s x %s with %d clients' % (origin, end, len(tour_clients)))

    if ex is None: ex = Client(end[0], end[1])
    new_x = ex.x if ex.x < width else 0
    new_y = 0 if ex.x < width else origin[1] + lateral_length
    origin = (new_x, new_y)
    end = (new_x + lateral_length, new_y + lateral_length)

    return origin, end


def clients_have_state(all_clients, booh_state):
    booh_clients = []
    for cli in all_clients.clients:
        if cli.state == booh_state:
            booh_clients.append(cli)
    print('BOOH: %d' % len(booh_clients))

    return True if len(booh_clients) else False


def calculate_all_tours(all_clients, SETTINGS):
    origin = (0,0)
    for it in range(SETTINGS['clusters']):
        origin, end = get_dimensions(all_clients, origin, **SETTINGS)
        clients_have_state(all_clients, state.UNASSOCIATED)

    for tour_clients in all_clients.init_tours:
        nice_tour = calculate_area_tour(all_clients, SETTINGS, tour_clients, origin, end)
        all_clients.best_tours.append(nice_tour)

    all_clients.final_print = True
    print_route(all_clients, nice_tour)


def calculate_area_tour(all_clients, SETTINGS, tour_clients, origin, end):
    best_tour = None
    for start_client in tour_clients:
        tour = Tour(origin, end, tour_clients, start_client)
        res_tour = find_best_route(all_clients, tour, SETTINGS['cluster_size'])
        print_route(all_clients, res_tour)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    return best_tour


