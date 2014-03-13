from config import DISPLAY
from tourplanner_graphics import print_area

class Area():
    def __init__(self, origin, end):
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []
        self.tours = []
        self.valid = True


    def __eq__(self, other):
        return (self.origin == other.origin and self.end == other.end and self.clients == other.clients)


    def __cmp__(self, other):
        if len(self.clients) < len(other.clients):
            return -1
        elif self.clients == other.clients and self.origin == other.origin and self.end == other.end:
            return 0
        elif len(self.clients) > len(other.clients):
            return 1
        else:
            return -1


    def __repr__(self):
        return ('%s' % self.clients)


    def add_clients_in_area(self, all_clients):
        self.clients = get_clients_in_area(self, all_clients)
        assert len(self.clients), 'FATAL! there should be clients in this area'
        if DISPLAY['areas']['add_info']: print('%d clients in area: ORIG(%d,%d) END(%d,%d) (%d x %d)' % \
                (len(self.clients), self.origin.x, self.origin.y, self.end.x, self.end.y, self.width, self.height))


def located_in_area(client, area):
    if (client.x > area.origin.x or client.x == area.origin.x == 0) and client.x <= area.end.x and \
            (client.y > area.origin.y or client.y == area.origin.y == 0) and client.y <= area.end.y:
        return True
    else:
        return False


def get_clients_in_area(area, all_clients):
    area_clients = [ cli for cli in all_clients.clients if located_in_area(cli, area)]
    return area_clients


def get_neighbours(area, all_clients, surface):
    neighbours = []
    for xa in all_clients.get_valid_areas():
        # north, east, south, west
        if (xa.origin.x == area.origin.x and xa.end.y == area.origin.y) or \
                (xa.origin.x == area.end.x and xa.end.y == area.end.y) or \
                (xa.origin.x == area.origin.x and xa.origin.y == area.end.y) or \
                (xa.end.x == area.origin.x and xa.end.y == area.end.y):
            neighbours.append(xa)
    for show in neighbours:
        if DISPLAY['areas']['merge']: print_area(surface, all_clients, show.origin, show.end)

    return neighbours
