from math import sqrt
from client import Client


class Tour():
    def __init__(self, dimension, clients):
        self.dimension = dimension
        self.clients = clients
        self.length = 0.0


def find_next(client, clientlist):
    closest = clientlist[0]
    for x in clientlist:
        if x == client:
            continue
        elif client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


def calculate_tours(surface, clients, clusters, cluster_size, width, height):
    tour_start_dimension = width * height / (clusters * 2)   # begin with explicit short dimension
    start_client = find_next(Client(0,0), clients.clients) 
    print('start client: %s' % start_client) 

