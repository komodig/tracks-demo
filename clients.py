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
        self.tour_length_when_first = 0.0
        print('created new client with x:%d y:%d' % (self.x, self.y))


    def __repr__(self):
        return ('%d,%d' % (self.x, self.y))


    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)


    def coords(self):
        return (self.x, self.y)


    def distance_to(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return sqrt(pow(x,2) + pow(y,2))


    def tour_length(self, length=None):
        if length is None:
            return self.tour_length_when_first
        else:
            self.tour_length_when_first = length


class ClientsCollection():
    def __init__(self, clusters, cluster_size, width, height):
        self.clients = []

        for i in range(clusters * cluster_size):
            self.clients.append(Client(randrange(1, width), randrange(1, height)))


    def clist(self, idx=None):
        if idx is None:
            return self.clients
        else:
            return self.clients[idx]

