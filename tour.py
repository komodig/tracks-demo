from copy import copy
from config import SETTINGS, DISPLAY
from time import sleep
from pygame import quit
from client import Client, has_area, get_client_area


class Tour():
    def __init__(self, clients=None):
        self.clients = clients
        self.plan = []
        self.final_length = 0.0


    def length(self):
        tour_length = 0.0
        last = None
        for tcli in self.plan:
            if last is None:
                last = tcli
            else:
                tour_length += tcli.distance_to(last)
                last = tcli

        if len(plan) == len(clients):
            self.final_length = tour_length
            print('tour length is final: %f' % self.final_length)

        return tour_length


    def get_last_assigned(self):
        if not len(self.plan):
            return None
        else:
            return self.plan[-1]


