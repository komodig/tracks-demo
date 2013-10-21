from random import randrange
import pygame
from pygame.locals import *
from sys import exit
from time import sleep
from copy import copy
from clients import Client

class Settings():
    def __init__(self, clusters, cluster_size, width, height):
        self.clusters = clusters
        self.cluster_size = cluster_size
        self.width = width
        self.height = height


settings = Settings(clusters=10, cluster_size=7, width=1000, height=700)


class Surface():
    def __init__(self, surface, color1, color2, fps_clock):
        self.surface = surface
        self.color1 = color1
        self.color2 = color2
        self.fps_clock = fps_clock


def init_clients():
    clients = []
    for i in range(0, settings.clusters * settings.cluster_size):
        clients.append(Client(randrange(1, settings.width), randrange(1, settings.height)))

    return clients


def find_next(client, clientlist):
    closest = clientlist[0]
    for x in clientlist[1:]:
        if client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


def get_exit_event():
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            exit()


def print_cluster(surface_config, clientlist, last_used):
    if len(clientlist) < settings.cluster_size:
        print('not enough clients')
        exit()

    cluster_clients = []
    if last_used is None:
        cluster_clients.append(clientlist[0])
        del clientlist[0]
    else:
        first_of_cluster = find_next(last_used, clientlist)
        cluster_clients.append(first_of_cluster)
        clientlist.remove(first_of_cluster)

    for i in range(0, settings.cluster_size - 1):
        next_client = find_next(cluster_clients[0], clientlist)
        cluster_clients.append(next_client)
        clientlist.remove(next_client)

    client1 = cluster_clients[0]
    del cluster_clients[0]
    while len(cluster_clients):
        client2 = find_next(client1, cluster_clients)
        pygame.draw.line(surface_config.surface, surface_config.color2, client1.coords(), client2.coords(), 2)
        pygame.display.update()
        surface_config.fps_clock.tick(30)
        try:
            cluster_clients.remove(client1)
        except ValueError:
            pass
        client1 = copy(client2)

    return clientlist, client1


def print_clients(surface_config, clientlist, wait_for_user=1):
    for client in clientlist:
        pygame.draw.circle(surface_config.surface, surface_config.color1, client.coords(), 4, 0)
        pygame.display.update()
        surface_config.fps_clock.tick(30)

    last_used = None
    for i in range(0, settings.clusters):
        print('clients left: %d' % len(clientlist))
        clientlist, last_used = print_cluster(surface_config, clientlist, last_used)

    if wait_for_user:
        while 1:
            get_exit_event()
            sleep(1)
    else:
        sleep(3)
        get_exit_event()


def init_surface():
    pygame.init()
    surface = pygame.display.set_mode((settings.width, settings.height))
    color1 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    color2 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    fps_clock = pygame.time.Clock()
    return Surface(surface, color1, color2, fps_clock)


if __name__ == '__main__':
    while True:
        surface_config = init_surface()
        clients = init_clients()
        print_clients(surface_config, clients, 1)

