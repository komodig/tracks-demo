from math import sqrt
from client import Client
from tourplanner_graphics import print_route
from client import find_next, ClientState as state
from copy import copy, deepcopy
from random import randrange

class Tour():
    def __init__(self, origin, width, height, clients, start_client):
        self.client_color = (randrange(0,255), randrange(0,255), randrange(0,255))
        self.route_color = (randrange(0,255), randrange(0,255), randrange(0,255))
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
        if client.state == state.CANDIDATE: continue
        if client.x > origin[0] and client.x < (origin[0] + lateral_length) and \
                client.y > origin[1] and client.y < (origin[1] + lateral_length):
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


def remove_excessive_clients(tour_clients, cluster_size, end_of_area):
    ex = None
    while len(tour_clients) > cluster_size:
        ex = find_next(end_of_area, tour_clients)
        print('kick this one out: %s' % ex)
        tour_clients.remove(ex)

    for cli in tour_clients:
        cli.state = state.CANDIDATE

    return ex


def calculate_all_tours(all_clients, clusters, cluster_size, width, height):
    lateral_length = sqrt(width * height / (clusters * 2))   # begin with explicit short dimension
    origin = (0,0)

    ex, earlier_tour = calculate_area_tour(all_clients, clusters, cluster_size, width, height, origin, lateral_length)
    all_clients.best_tours.append(earlier_tour)
    if ex is None:
        origin = (earlier_tour.origin[0] + earlier_tour.width, earlier_tour.origin[1])
    else:
        origin = (ex.x, 0)
    # TODO: the following is just for tour #2
    ex, earlier_tour = calculate_area_tour(all_clients, clusters, cluster_size, width, height, origin, lateral_length)
#    all_clients.best_tours.append(earlier_tour)

    all_clients.final_print = True
    print_route(all_clients, earlier_tour)

def calculate_area_tour(all_clients, clusters, cluster_size, width, height, origin, lateral_length):
    tour_clients = []

    while len(tour_clients) < cluster_size:
        if pow(lateral_length, 2) >= width * height / 5:
            print('\nnot enough clients, try something else!\n')
            exit()
        lateral_length += width/100
        print('find tour clients in area: %f x %f' % (lateral_length, lateral_length))
        tour_clients = find_tour_clients(origin, lateral_length, all_clients)

    next_area_start = remove_excessive_clients(tour_clients, cluster_size, Client(origin[0] + lateral_length, lateral_length))

    best_tour = None
    for start_client in tour_clients:
        tour = Tour(origin, lateral_length, lateral_length, tour_clients, start_client)
        res_tour = find_best_route(all_clients, tour, cluster_size)
        print_route(all_clients, res_tour)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
#    all_clients.final_print = True
#    print_route(all_clients, best_tour)
    return next_area_start, best_tour


