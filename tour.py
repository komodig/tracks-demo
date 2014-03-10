from copy import copy
from config import SETTINGS, DISPLAY
from time import sleep
from pygame import quit
from client import Client, has_area, get_client_area


class Tour():
    def __init__(self, origin, end, log_str, clients, start_client=None, all_clients=None):
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []
        self.length = 0.0
        self.valid = True
        self.can_unite = True
        self.final = False
        self.first_assigned = None
        self.logbook = []
        self.warning = False

        self.logbook.append(log_str)

        if clients:         # this is for clones in do_routing()
            # creating new clients better than using copy() ?
            clone = lambda cc: Client(cc.x, cc.y, 'created in Tour.__init__ to copy client')
            self.clients = [ clone(ccd) for ccd in clients ]

            for cli in self.clients:
                reset_client(cli)

        if start_client:
            for cli in self.clients:
                if cli == start_client:
                    #print('assigning start_client')
                    cli.c_log('the following assignment is as start_client')
                    self.tour_log('assign start_client...')
                    assert(all_clients is not None, 'shit, forgot all_clients param in Tour init')
                    self.assign(cli, all_clients)
                    break


    def __eq__(self, other):
        return (self.origin == other.origin and self.end == other.end)


    def __cmp__(self, other):
        if len(self.clients) < len(other.clients):
            return -1
        elif len(self.clients) == len(other.clients):
            return 0
        elif len(self.clients) > len(other.clients):
            return 1
        else:
            return -1


    def __lt__(self, other):
        return self.length < other.length


    def __repr__(self):
        return ('%s' % self.clients)


    def get_last_assigned(self):
        if self.first_assigned is None:
            return None
        else:
            last_assigned = self.first_assigned
            while last_assigned.next_assigned:
                last_assigned = last_assigned.next_assigned
            return last_assigned


    def assign(self, incoming, all_clients):
        self.tour_log('try to get client assigned...')
        client = None
        for it in self.clients:
            if it == incoming:
                try:
                    assert it.next_assigned is None, 'REALLY STRANGE! should it be assigned with next set?'
                except AssertionError:
                    ca = get_client_area(it, all_clients)
                    it.c_log('matched incoming but have next assigned set in tour (%d,%d) (%d x %d) with %d clients' % (ca.origin.x, ca.origin.y, ca.width, ca.height, len(ca.clients)))
                    self.warning = True
                    continue
                client = it # in case of cloned client
                client.c_log('matched incoming and getting assigned to area at (%d,%d) (%d x %d) with %d clients' % (self.origin.x, self.origin.y, self.width, self.height, len(self.clients)))
                break

        try:
            assert client, 'FATAL! Trying to assing not-member-client!'
        except AssertionError:
            print('incoming Client L O G B O O K :')
            incoming.print_logbook()
            print('tour L O G B O O K :')
            self.print_logbook()
            return None

        # FIXME: the following assertion failed sometimes.
        try:
            assert client.next_assigned is None, 'STRANGE! client to assign has next_assigned set!'
        except AssertionError:
            print('incoming Client L O G B O O K :')
            incoming.print_logbook()
            print('member Client L O G B O O K :')
            client.print_logbook()
            return None

        if self.first_assigned is None:
            self.first_assigned = client
            client.c_log('being assigned as first (%s)' % hex(id(client)))
        else:
            last = self.get_last_assigned()
            self.length += client.distance_to(last)
            last.next_assigned = client
            last.c_log('next_assigned is set to: %s (my own: %s)' % (hex(id(client)), hex(id(last))))
            client.c_log('being assigned next of: %s (my own: %s) assuming state ASSOCIATED' % (hex(id(last)), hex(id(client))))

        return client


    def add_clients_in_area(self, all_clients, add_permanently=True):
        count = 0
        for client in all_clients.clients:
            if has_area(client, all_clients):
                continue
            if (client.x > self.origin.x or client.x == self.origin.x == 0) and client.x <= self.end.x and \
                    (client.y > self.origin.y or client.y == self.origin.y == 0) and client.y <= self.end.y:
                count += 1
                if add_permanently:
                    client.c_log('now has area without tour in add_clients_in_area')
                    self.clients.append(client)
                    if DISPLAY['clients']['append']: print('add_clients_in_area: appended client: %s' % client)

        if add_permanently:
            print('got area at (%d,%d) (%d x %d) with %d clients' % \
                    (self.origin.x, self.origin.y, self.width, self.height, len(self.clients)))
        return count


    def is_incomplete(self, all_clients):
        members = 0
        member = None

        try:
            assert(len(self.clients) <= SETTINGS['cluster_size_max'], 'WARNING: area is too big!')
            assert(len(self.clients) >= SETTINGS['cluster_size_min'], 'WARNING: area is too small!')
        except AssertionError:
            pass

        if self.first_assigned is None:
            return True
        else:
            members += 1
            member = self.first_assigned

        while True:
            assert(member in self.clients, 'FATAL! non-area-client in area-tour!')
            if not member.next_assigned:
                break
            member = member.next_assigned
            members += 1

        if members == len(self.clients): print('TOUR COMPLETE!')
        return (members < len(self.clients))


    def count_area_clients(self, all_clients):
        count = self.add_clients_in_area(all_clients, False)
        return count


    def tour_log(self, log_str):
        self.logbook.append(log_str)


    def print_logbook(self):
        for lstr in self.logbook: print lstr


def reset_client(c_to_add):
    c_to_add.c_log('getting prepared: has area but no tour')
    c_to_add.next_assigned = None


