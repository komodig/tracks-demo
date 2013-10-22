from random import randrange
import pygame
from pygame.locals import *
from sys import exit
from time import sleep
from copy import copy
from clients import Client


class Info():
    def __init__(self, version, usage):
        self.version = version
        self.usage = usage

    def __repr__(self):
        return self.version


class Settings():
    def __init__(self, clusters, cluster_size, width, height):
        self.clusters = clusters
        self.cluster_size = cluster_size
        self.width = width
        self.height = height


settings = Settings(clusters=5, cluster_size=7, width=1200, height=800)
info = Info(version='0.1.1', usage=
"""
*   Usage:
*
*   You can control the running process by using
*   <ESC> to quit
*   <SPACE> to pause and continue
""")


class Surface():
    def __init__(self, surface, color1, color2, fps_clock):
        self.surface = surface
        self.color1 = color1
        self.color2 = color2
        self.fps_clock = fps_clock


class ProcessControl():
    RUN   = 1
    PAUSE = 2
    WAIT  = 3


def init_clients():
    clients = []
    for i in range(settings.clusters * settings.cluster_size):
        clients.append(Client(randrange(1, settings.width), randrange(1, settings.height)))

    return clients


def find_next(client, clientlist):
    closest = clientlist[0]
    for x in clientlist:
        if x == client:
            continue
        elif client.distance_to(x) < client.distance_to(closest):
            closest = x

    return closest


def handle_user_events():
    while True:
        event = pygame.event.poll()

        if event.type == NOEVENT:
            return ProcessControl.RUN
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN and event.key == K_SPACE:
            return ProcessControl.PAUSE


def print_cluster(surface_config, clientlist, start_client):
    if len(clientlist) < settings.cluster_size:
        print('not enough clients')
        exit()

    tour_length = 0.0

    cluster_clients = []
    cluster_clients.append(start_client)
    clientlist.remove(start_client)

    for i in range(settings.cluster_size - 1):
        next_client = find_next(cluster_clients[0], clientlist)
        cluster_clients.append(next_client)
        clientlist.remove(next_client)

    client1 = cluster_clients[0]
    del cluster_clients[0]
    while len(cluster_clients):
        client2 = find_next(client1, cluster_clients)
        pygame.draw.line(surface_config.surface, surface_config.color2, client1.coords(), client2.coords(), 2)
        tour_length += client1.distance_to(client2)
        pygame.display.update()
        surface_config.fps_clock.tick(30)
        try:
            cluster_clients.remove(client1)
        except ValueError:
            pass
        client1 = copy(client2)

    return clientlist, client1, tour_length


def print_clients(surface_config, clientlist, slow=False):
    for client in clientlist:
        pygame.draw.circle(surface_config.surface, surface_config.color1, client.coords(), 4, 0)
        if slow:
            pygame.display.update()
            surface_config.fps_clock.tick(30)
    if not slow:
        pygame.display.update()


def print_routes(surface_config, clientlist, first_client):
    length = 0.0
    last_used = None

    for i in range(0, settings.clusters):
        if last_used is None:
            start_client = first_client
        else:
            start_client = find_next(last_used, clientlist)
        clientlist, last_used, cluster_length = print_cluster(surface_config, clientlist, start_client)
        length += cluster_length

        # rest a little when figure is complete
        if not len(clientlist):
            sleep(2)

        process = ProcessControl.RUN
        while True:
            cmd = handle_user_events()
            if cmd == ProcessControl.RUN and process == ProcessControl.RUN:
                break
            elif cmd == ProcessControl.PAUSE and process == ProcessControl.RUN:
                process = ProcessControl.WAIT
            elif cmd == ProcessControl.PAUSE and process == ProcessControl.WAIT:
                process = ProcessControl.RUN
                break
            sleep(1)

    return length


def init_surface():
    pygame.init()
    surface = pygame.display.set_mode((settings.width, settings.height))
    color1 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    color2 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    fps_clock = pygame.time.Clock()
    return Surface(surface, color1, color2, fps_clock)


if __name__ == '__main__':
    clients = init_clients()
    print('\n*   Version: %s\n*%s' % (info.version, info.usage))

    print('running %d clients...' % (settings.clusters * settings.cluster_size))
    clients_perm = copy(clients)
    best_tour = None
    for x in range(len(clients_perm)):
        surface_config = init_surface()
        print_clients(surface_config, clients_perm, True if x == 0 else False)
        print('tour starting Client %d (%d, %d)' % (x + 1, clients[x].x, clients[x].y))
        length = print_routes(surface_config, clients, clients[x])
        clients_perm[x].tour_length(length)
        print('client %d tour length: %f' % (x + 1, clients_perm[x].tour_length()))
        if best_tour is None or (length < clients_perm[best_tour].tour_length()):
            best_tour = x
            print('new best tour!')
        clients = copy(clients_perm)

    print('finished! displaying best tour...')
    best = clients[best_tour]
    print('starting Client %d (%d, %d) length: %f' % (best_tour + 1, best.x, best.y, best.tour_length()))
    surface_config = init_surface()
    length = print_routes(surface_config, clients, clients[best_tour])
    while True:
        handle_user_events()
        sleep(2)

