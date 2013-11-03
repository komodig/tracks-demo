from math import sqrt
from client import Client
from tourplanner_graphics import print_route
from client import find_next, ClientState as state
from copy import copy

class Tour():
    def __init__(self, origin, width, height, clients):
        self.origin = origin
        self.width = width
        self.height = height
        self.clients = clients
        self.sorted_clients = []
        self.length = 0.0
        print('got tour area at (%d,%d) (%d x %d) with %d clients' % (origin[0], origin[1], width, height, len(clients)))


    def assign(self, client):
        if len(self.sorted_clients):
            self.length += client.distance_to(self.sorted_clients[-1])
        self.sorted_clients.append(client)
        client.state = state.ASSOCIATED


def find_tour_clients(origin, lateral_length, clients):
    tour_clients = []
    for client in clients.clients:
        if client.x > origin[0] and client.x < (origin[0] + lateral_length) and \
                client.y > origin[1] and client.y < (origin[1] + lateral_length):
            tour_clients.append(client)

    return tour_clients


def reset_tour_clients(tour):
    for c in tour.clients:
        c.state = state.UNASSOCIATED

    tour.sorted_clients = []
    tour.length = 0.0


def check_next_to_next_client(last_assigned, next_client, tour_clients):
    next_client.state = state.CANDIDATE
    try:
        next_next_client = find_next(next_client, tour_clients)
    except TypeError:
        next_client.state = state.UNASSOCIATED
        return None, False

    next_next_client.state = state.CANDIDATE
    try:
        next_next_next_client = find_next(next_next_client, tour_clients)
    except TypeError:
        next_next_client.state = state.UNASSOCIATED
        return None, False

    length = last_assigned.distance_to(next_client)
    length += next_client.distance_to(next_next_client)
    length += next_next_client.distance_to(next_next_next_client)
    alternative_length = last_assigned.distance_to(next_next_client)
    alternative_length += next_next_client.distance_to(next_client)
    alternative_length += next_client.distance_to(next_next_next_client)
    #next_client.state = state.UNASSOCIATED
    #next_next_client.state = state.UNASSOCIATED
    if alternative_length < length:
        print('YEAH %f < %f' % (alternative_length, length))
        return next_next_client, True


def find_best_route(all_clients, tour, cluster_size):
    best_route = None
    for client in tour.clients:
        reset_tour_clients(tour)
        tour.assign(client)
        while len(tour.sorted_clients) < cluster_size:
            next_client = find_next(tour.sorted_clients[-1], tour.clients)
            if next_client is None: break
            #next_next_client, is_better = check_next_to_next_client(tour.sorted_clients[-1], next_client, tour.clients)
            #if is_better:
            #    tour.assign(next_next_client)
            tour.assign(next_client)

        if best_route is None or tour.length < best_route.length:
            best_route = copy(tour)
        print_route(all_clients, tour.sorted_clients)
    print('best route length: %f' % best_route.length)
    print_route(all_clients, best_route.sorted_clients)


def calculate_tours(all_clients, clusters, cluster_size, width, height):
    lateral_length = sqrt(width * height / (clusters * 2))   # begin with explicit short dimension
    origin = (0,0)
    tour_clients = []

    while len(tour_clients) < cluster_size:
        lateral_length += width/100
        print('find tour clients in area: %f x %f' % (lateral_length, lateral_length))
        tour_clients = find_tour_clients(origin, lateral_length, all_clients)

    tour = Tour(origin, lateral_length, lateral_length, tour_clients)
    find_best_route(all_clients, tour, cluster_size)

