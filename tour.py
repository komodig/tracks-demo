from client import Client
from tourplanner_graphics import print_route, print_area, print_clients, TourplannerSurface, \
        handle_user_events, ProcessControl
from client import find_next, ClientState as state
from copy import copy, deepcopy
from config import SETTINGS, INFO, DISPLAY, DIMENSION
from time import sleep
from pygame import quit


class Tour():
    def __init__(self, origin, end, clients, start_client=None):
        self.origin = origin
        self.end = end
        self.width = end.x - origin.x
        self.height = end.y - origin.y
        self.clients = []   # for get_area() a referenced list with state CANDIDATE
        self.sorted_clients = [] # clients appended here get state ASSOCIATED
        self.length = 0.0
        self.valid = True
        self.can_unite = True

        if clients:         # this is for do_routing()
            self.clients = deepcopy(clients)
            for cli in self.clients:
                cli.state = state.CANDIDATE

        if start_client:
            for cli in self.clients:
                if cli == start_client:
                    self.assign(cli)
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
        return ('%s' % self.sorted_clients)


    def assign(self, client):
        if len(self.sorted_clients):
            self.length += client.distance_to(self.sorted_clients[-1])
        client.state = state.ASSOCIATED
        self.sorted_clients.append(client)


    def add_area_clients(self, all_clients, add_them=True):
        count = 0
        for client in all_clients.clients:
            if client.state != state.FREE:
                continue
            if (client.x > self.origin.x or client.x == self.origin.x == 0) and client.x <= self.end.x and \
                    (client.y > self.origin.y or client.y == self.origin.y == 0) and client.y <= self.end.y:
                count += 1
                if add_them:
                    client.state = state.CANDIDATE
                    self.clients.append(client)
                    if DISPLAY['clients']['append']: print('add_area_clients: appended client: %s' % client)

        if add_them:
            print('got area at (%d,%d) (%d x %d) with %d clients' % \
                    (self.origin.x, self.origin.y, self.width, self.height, len(self.clients)))
        return count


    def count_area_clients(self, all_clients):
        count = self.add_area_clients(all_clients, False)
        return count


def do_routing(all_clients, tour, tour_surface):
    best_tour = None
    for start_client in tour.clients:
        tour = Tour(tour.origin, tour.end, tour.clients, start_client)
        res_tour = find_best_route(all_clients, tour)
        if DISPLAY['routing']['best_starter']: print_route(all_clients, res_tour) #, tour_surface)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    return best_tour


def find_best_route(all_clients, tour):
    if len(tour.sorted_clients) < len(tour.clients):
        other_tour = deepcopy(tour)

        next_client = find_next(tour.sorted_clients[-1], tour.clients)
        if next_client is None:
            return tour
        tour.assign(next_client)
        if DISPLAY['routing']['all']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour)

        next_next_client = find_next(next_client, other_tour.clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            if DISPLAY['routing']['all']: print_route(all_clients, other_tour)
            b = find_best_route(all_clients, other_tour)

        return a if a < b else b
    else:
        return tour


def get_next_area_with_clients(origin, all_clients):
    area_width = SETTINGS['width'] * DIMENSION[0]['x_factor']
    area_height = SETTINGS['height'] * DIMENSION[0]['y_factor']
    end = Client(origin.x + area_width, origin.y + area_height)
    area = Tour(origin, end, None)
    while area.count_area_clients(all_clients) == 0:
        if area.end.x + area_width > SETTINGS['width']:
            if area.end.y + area_height > SETTINGS['height']:
                print('END OF TOTAL AREA!')
                return None
            area.origin.x = 0
            area.origin.y += area_height
            area.end.x = area_width
            area.end.y += area_height
        else:
            area.origin.x += area_width
            area.end.x += area_width

    return area


def get_area(all_clients, last_tour, dim_surface):
    last_end = Client(last_tour.end.x, last_tour.origin.y)
    small_area = get_next_area_with_clients(last_end, all_clients)
    if small_area is None:
        return None
    cli_sum = small_area.add_area_clients(all_clients)
    return small_area


def clients_have_state(all_clients, booh_state, surface):
    booh_clients = 0
    if booh_state == state.ASSOCIATED:
        for tour in all_clients.best_tours:
            booh_clients += len(tour.clients)
    else:
        for cli in all_clients.clients:
            if cli.state == booh_state:
                booh_clients += 1

    return booh_clients


def get_average_members(all_clients):
    avg = 0
    cnt = 0
    for sa in get_valid_areas(all_clients):
        avg += len(sa.clients)
        cnt += 1

    return avg/cnt


def tours_with_count(all_clients, count):
    wanted = []
    for area in get_valid_areas(all_clients):
        if len(area.clients) == count:
            wanted.append(area)

    return wanted


def unite(one, other):
    if DISPLAY['unite_areas']: print('unite(): 1. area at (%d,%d) (%d x %d) with %d clients' % \
            (one.origin.x, one.origin.y, one.width, one.height, len(one.clients)))
    if DISPLAY['unite_areas']: print('unite(): 2. area at (%d,%d) (%d x %d) with %d clients' % \
            (other.origin.x, other.origin.y, other.width, other.height, len(other.clients)))
    if one.origin.x < other.origin.x or one.origin.y < other.origin.y:
        origin = one.origin
        end = other.end
    else:
        origin = other.origin
        end = one.end

    new = Tour(origin, end, one.clients)
    new.clients.extend(other.clients)
    if DISPLAY['unite_areas']: print('unite(): 3. area at (%d,%d) (%d x %d) with %d clients' % \
            (new.origin.x, new.origin.y, new.width, new.height, len(new.clients)))
    return new


def get_valid_areas(all_clients):
    areas = []
    for area in all_clients.small_areas:
        if area.valid:
            areas.append(area)

    return areas


def assimilate_the_weak(all_clients, cluster_min, cluster_max, with_member_count):
    to_assimilate = tours_with_count(all_clients, with_member_count)
    surface = TourplannerSurface()

    if DISPLAY['dimensions']:
        print_clients(surface, all_clients.clients)
        mark_these = tours_with_count(all_clients, with_member_count)
        for tour in mark_these:
            print_clients(surface, tour.clients, False, True)

    ass = None
    for it in to_assimilate:
        if it.can_unite:
            ass = it
            break

    if ass is None: return None

    neighbours = []
    for tour in get_valid_areas(all_clients):
        # north, east, south, west
        if (tour.origin.x == ass.origin.x and tour.end.y == ass.origin.y) or \
                (tour.origin.x == ass.end.x and tour.end.y == ass.end.y) or \
                (tour.origin.x == ass.origin.x and tour.origin.y == ass.end.y) or \
                (tour.end.x == ass.origin.x and tour.end.y == ass.end.y):
            neighbours.append(tour)
            if DISPLAY['dimensions']: print_area(all_clients, tour.origin, tour.end, surface)

    best = None
    chosen = None
    for nei in neighbours:
        if (len(nei.clients) + len(ass.clients)) > cluster_max:
            continue
        united = unite(ass, nei)
        best_nei = do_routing(all_clients, united, surface)
        if best is None or best_nei < best:
            best = copy(united)
            chosen = copy(nei)

    if best is None:
        print('sorry, can\'t unite!')
        # TODO: is this final? don't route this again!!
        ass.can_unite = False
        return ass

    # areas.remove(chosen) causes strange behaviour so remove differently
    # MAYBE because do_routing() plays in sorted_client not small_areas?!
    for area in get_valid_areas(all_clients):
        if area == ass: area.valid = False
        if area == chosen: area.valid = False

    all_clients.small_areas.append(best)
    surface.change_route_color()
    if DISPLAY['dimensions']: print_area(all_clients, best.origin, best.end, surface)
    return best


def calculate_all_tours(all_clients):
    surface = TourplannerSurface()
    small_area = Tour(Client(0, 0), Client(0, 0), None)

    while True:
        small_area = get_area(all_clients, small_area, surface)
        if small_area is None:
            break
        if DISPLAY['dimensions']: print_area(all_clients, small_area.origin, small_area.end, surface)
        all_clients.small_areas.append(small_area)
        handle_user_events(surface.process)

    print('average of %d members' % get_average_members(all_clients))
    print('CANDIDATE clients: %d' % clients_have_state(all_clients, state.CANDIDATE, surface))
    print('FREE clients: %d' % clients_have_state(all_clients, state.FREE, surface))

    tour_size = 1
    while True:
        mark_these = tours_with_count(all_clients, tour_size)
        if not len(mark_these):
            if tour_size < SETTINGS['cluster_size_min']:
                tour_size += 1
            else:
                break
        if assimilate_the_weak(all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'], tour_size) is None:
            break
        handle_user_events(surface.process)

    for brautpaare in get_valid_areas(all_clients):
        best = do_routing(all_clients, brautpaare, surface)
        all_clients.best_tours.append(best)
        handle_user_events(surface.process)

    print('ASSOCIATED clients: %d' % clients_have_state(all_clients, state.ASSOCIATED, surface))
    print('results in %d areas on %d x %d screen' % (len(get_valid_areas(all_clients)), SETTINGS['width'], SETTINGS['height']))
    print('total length: %f' % all_clients.summarize_total_length())
    all_clients.final_print = False
    print_route(all_clients, all_clients.best_tours[0])

    surface.process.state = ProcessControl.WAIT
    handle_user_events(surface.process)


