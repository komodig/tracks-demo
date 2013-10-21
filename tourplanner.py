from random import randrange
import pygame
from pygame.locals import *
from sys import exit
from time import sleep
from copy import copy
from clients import Client

settings = {'width': 1000, 'height': 700}

def init_clients():
    clients = []
    for i in range(0,20):
        clients.append(Client(randrange(1, settings['width']), randrange(1, settings['height'])))

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


def print_clients(clientlist, wait_for_user=1):
    pygame.init()
    surface = pygame.display.set_mode((settings['width'], settings['height']))
    color1 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    color2 = pygame.Color(randrange(0,255), randrange(0,255), randrange(0,255))
    fps_clock = pygame.time.Clock()

    for client in clientlist:
        pygame.draw.circle(surface, color1, client.coords(), 4, 0)
        pygame.display.update()
        fps_clock.tick(30)

    client1 = clientlist[0]
    clientlist.remove(client1)
    while len(clientlist):
        client2 = find_next(client1, clientlist)
        pygame.draw.line(surface, color2, client1.coords(), client2.coords(), 2)
        pygame.display.update()
        fps_clock.tick(30)
        try:
            clientlist.remove(client1)
        except ValueError:
            pass
        client1 = copy(client2)

    if wait_for_user:
        while 1:
            get_exit_event()
            sleep(1)
    else:
        sleep(3)
        get_exit_event()


if __name__ == '__main__':
    while True:
        clients = init_clients()
        print_clients(clients, 0)

