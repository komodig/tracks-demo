from math import sqrt, pow
from random import randrange


class ClientState():
    UNASSOCIATED = 1
    ASSOCIATED   = 2


class Client():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.state = ClientState.UNASSOCIATED
        print('created new client at x:%d y:%d' % (self.x, self.y))


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
    def __init__(self, clusters, cluster_size, width, height):
        self.clients = []
        self.max_distance = 0.0
        self.avg_distance = 0.0
        self.printed = 0
        self.final_print = False

        for i in range(clusters * cluster_size):
            self.clients.append(Client(randrange(1, width), randrange(1, height)))

        self.get_client_distances()
        print('\nmaximum client distance: %f\naverage client distance: %f' %(self.max_distance, self.avg_distance))


    def get_client_distances(self):
        for client in self.clients:
            for other in self.clients:
                dist = client.distance_to(other)
                if dist:                            # omit zero-distance to client itself
                    self.avg_distance += dist
                if dist > self.max_distance:
                    self.max_distance = dist

        self.avg_distance /= (pow(len(self.clients), 2) - len(self.clients)) # minus iterations with zero-distance to client itself 


def find_next(client, clientlist):
    closest = None
    for x in clientlist:
        if x == client or x.state == ClientState.ASSOCIATED:
            continue
        elif closest is None or client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


