class Area():
    def __init__(self, origin, end):
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []
        self.tours = []


    def __eq__(self, other):
        return (self.origin == other.origin and self.end == other.end and self.clients == other.clients)


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


    def add_clients_in_area(self, all_clients):
        self.clients = get_clients_in_area(self, all_clients)
        assert(len(self.clients), 'FATAL! there should be clients in this area')
        print('%d clients in area at (%d,%d) (%d x %d)' % \
                (len(self.clients), self.origin.x, self.origin.y, self.width, self.height))


def located_in_area(client, area):
    if (client.x > area.origin.x or client.x == area.origin.x == 0) and client.x <= area.end.x and \
            (client.y > area.origin.y or client.y == area.origin.y == 0) and client.y <= area.end.y:
        return True
    else:
        return False


def get_clients_in_area(area, all_clients):
    area_clients = [ cli for cli in all_clients.clients if located_in_area(cli, area)]
    return area_clients


