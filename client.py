from math import sqrt, pow
from config import DISPLAY, TEST
from tourplanner_test import length_test_client_generator


class Client():
    def __init__(self, x=0, y=0, log_str=None):
        self.x = x
        self.y = y

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


class ClientsCollection():
    def __init__(self, clients, factor, num_of_clients, width, height):
        self.clients = clients
        self.factor = factor
        self.small_areas = []
        self.final_areas = []
        self.areas_too_big = []
        self.areas_too_small = []
        self.total_length = 0.0
        self.first_print = True if DISPLAY['clients_intro'] else False
        self.final_print = False

        if TEST['level'] == 2:
            self.clients = length_test_client_generator()


    def __eq__(self, other):
        if self.summarize_total_length() == other.summarize_total_length():
            return True
        else:
            return False


    def __len__(self):
        return len(self.clients)


    def __repr__(self):
        return '%s' % (self.clients)


    def summarize_total_length(self):
        total_length = 0.0
        for best in self.final_areas:
            total_length += best.tours[-1].length()
        if len(self.final_areas) == len(self.get_valid_areas()):
            self.total_length = total_length
        return total_length


    def get_valid_areas(self):
        return [ area for area in self.small_areas if area.valid ]


    def areas_off_size(self):
        if len(self.areas_too_big) and len(self.areas_too_small):
            return (self.areas_too_big[-1] + self.areas_too_small[-1])
        else:
            return None


def find_next(client, tour, all_clients):
    closest = None
    for x in tour.clients:
        if x == client or x in tour.plan:
            continue
        elif closest is None or client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


def get_client_area(xclient, all_clients):
    cli_area = [ xarea for xarea in all_clients.get_valid_areas() if xclient in xarea.clients ]
    assert len(cli_area) == 1, 'FATAL: client must belong to exactly one area!'
    return cli_area[0] if len(cli_area) else None


def has_area(xclient, all_clients):
    client_area = get_client_area(xclient, all_clients)
    return (client_area is not None)


def has_area_and_tour(xclient, all_clients):
    client_area = get_client_area(xclient, all_clients)
    for clit in client_area.tours:
        if xclient in clit.plan:
            return True

    return False


