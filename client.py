from math import sqrt, pow
from random import randrange
from config import DISPLAY, TEST
from tourplanner_test import length_test_client_generator


class Client():
    def __init__(self, x=0, y=0, log_str=None):
        self.x = x
        self.y = y
        self.next_assigned = None
        self.logbook = []

        if log_str: self.logbook.append(log_str)
        if DISPLAY['clients']['init']: print('created new client at x:%d y:%d' % (self.x, self.y))


    def __repr__(self):
        return ('%d,%d' % (self.x, self.y))


    def __eq__(self, other):
        return False if other is None else (self.x == other.x and self.y == other.y)


    def coords(self):
        return (self.x, self.y)


    def distance_to(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return sqrt(pow(x,2) + pow(y,2))


    def c_log(self, log_str):
        self.logbook.append(log_str)


    def print_logbook(self):
        for lstr in self.logbook: print lstr


class ClientsCollection():
    def __init__(self, clients, cluster_size_min, cluster_size_max, width, height):
        self.clients = []
        self.small_areas = []
        self.best_tours = []
        self.max_distance = 0.0
        self.avg_distance = 0.0
        self.total_length = 0.0
        self.first_print = True if DISPLAY['clients_intro'] else False
        self.final_print = False

        if TEST['level'] == 2:
            self.clients = length_test_client_generator()
        else:
            while len(self.clients) < clients:
                self.clients.append(Client(randrange(1, width), randrange(1, height)))

        self.get_client_distances()
        print('\nmaximum client distance: %f\naverage client distance: %f' %(self.max_distance, self.avg_distance))


    def __len__(self):
        return len(self.clients)


    def __repr__(self):
        return '%s' % (self.clients)


    def summarize_total_length(self):
        self.total_length = 0.0
        for best in self.best_tours:
            self.total_length += best.length
        return self.total_length


    def get_client_distances(self):
        for client in self.clients:
            for other in self.clients:
                dist = client.distance_to(other)
                if dist:                            # omit zero-distance to client itself
                    self.avg_distance += dist
                if dist > self.max_distance:
                    self.max_distance = dist

        self.avg_distance /= (pow(len(self.clients), 2) - len(self.clients)) # minus iterations with zero-distance to client itself


    def get_valid_areas(self):
        return [ area for area in self.small_areas if area.valid ]


def find_next(client, clientlist, all_clients, skip_candidates=False):
    closest = None
    for x in clientlist:
        if x == client or has_area_and_tour(x, all_clients) \
                or (skip_candidates and has_area_but_no_tour(x, all_clients)):
            continue
        elif closest is None or client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


def get_client_area(xclient, all_clients):
    cli_area = [ xarea for xarea in all_clients.get_valid_areas() if xclient in xarea.clients ]
    assert(len(cli_area) <= 1, 'FATAL: client can\'t be in more than one area!')
    return cli_area


def has_no_area(xclient, all_clients):
    client_area = get_client_area(xclient, all_clients)
    return (len(client_area) == 0)


def has_area_but_no_tour(xclient, all_clients):
    pass


def has_area_and_tour(xclient, all_clients):
    client_area = get_client_area(xclient, all_clients)
    if not client_area.first_assigned:
        return False
    else:
        cli_it = client_area.first_assigned
        while True:
            if cli_it is xclient:
                return True
            elif not cli_it.next_assigned:
                return False
            else:
                cli_it = cli_it.next_assigned


