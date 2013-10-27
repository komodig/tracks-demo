from math import sqrt
from client import Client
from tourplanner_graphics import print_route
from client import find_next, ClientState as state
from copy import copy, deepcopy

class Tour():
    def __init__(self, origin, width, height, clients, start_client):
        self.origin = origin
        self.width = width
        self.height = height
        self.clients = deepcopy(clients)
        self.sorted_clients = []
        self.length = 0.0

        for c in self.clients:
            if c == start_client:
                self.assign(c)
                break

        print('got tour area at (%d,%d) (%d x %d) with %d clients and %s as start client' % \
                (origin[0], origin[1], width, height, len(clients), start_client))


    def __lt__(self, other):
        return self.length < other.length


    def __repr__(self):
        return ('%s' % self.sorted_clients)


    def assign(self, client):
        if len(self.sorted_clients):
            self.length += client.distance_to(self.sorted_clients[-1])
        client.state = state.ASSOCIATED
        self.sorted_clients.append(client)


def find_tour_clients(origin, lateral_length, clients):
    tour_clients = []
    for client in clients.clients:
        if client.x > origin[0] and client.x < (origin[0] + lateral_length) and \
                client.y > origin[1] and client.y < (origin[1] + lateral_length):
            tour_clients.append(client)

    return tour_clients


def find_best_route(all_clients, tour, cluster_size):
    if len(tour.sorted_clients) < cluster_size:
        other_tour = deepcopy(tour)

        next_client = find_next(tour.sorted_clients[-1], tour.clients)
        tour.assign(next_client)
        print_route(all_clients, tour.sorted_clients)
        a = find_best_route(all_clients, tour, cluster_size)

        next_next_client = find_next(next_client, other_tour.clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            print_route(all_clients, other_tour.sorted_clients)
            b = find_best_route(all_clients, other_tour, cluster_size)

        return a if a < b else b
    else:
        return tour



def calculate_tours(all_clients, clusters, cluster_size, width, height):
    lateral_length = sqrt(width * height / (clusters * 2))   # begin with explicit short dimension
    origin = (0,0)
    tour_clients = []

    while len(tour_clients) < cluster_size:
        if pow(lateral_length, 2) >= width * height / 5:
            print('bad tours, try something else!')
            break
        lateral_length += width/100
        print('find tour clients in area: %f x %f' % (lateral_length, lateral_length))
        tour_clients = find_tour_clients(origin, lateral_length, all_clients)

    best_tour = None
    for start_client in tour_clients:
        tour = Tour(origin, lateral_length, lateral_length, tour_clients, start_client)
        res_tour = find_best_route(all_clients, tour, cluster_size)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    print_route(all_clients, best_tour.sorted_clients)

