from random import randrange
from math import factorial
import json
from copy import deepcopy
from client import Client, ClientsCollection, find_next
from utils import load_clients_file, save_clients_file, load_json_file, export_as_file
from tour import Tour
from area import Area
from config import SETTINGS, INFO, TEST, DISPLAY
if DISPLAY['enable']:
    from tourplanner_graphics import print_route, graphics_init, intro


class Counter():
    value = 0

    def incr(self):
        self.value += 1


def do_routing(display_surface, all_clients, tour):
    iterations = Counter()
    best_tour = None

    for start_client in tour.clients:
        new_tour = Tour(tour.clients, [start_client,])
        res_tour = find_best_route(display_surface, all_clients, new_tour, iterations)
        if DISPLAY['routing']['best_starter']: print_route(display_surface, all_clients, res_tour)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour
            if DISPLAY['routing']['best']:
                print('new best tour: %f' % best_tour.length())
                print_route(display_surface, all_clients, None)

    max_iterations = factorial(len(tour.clients))
    print('%d of %d possible iterations' % (iterations.value, max_iterations))

    return best_tour


def find_best_route(display_surface, all_clients, tour, iterations):
    if tour.is_incomplete():
        other_tour = deepcopy(tour)

        latest = tour.get_last_assigned()
        assert latest, 'FATAL! No start_client found'
        next_client = find_next(latest, tour, all_clients)
        assert next_client, 'FATAL! How can tour.plan be incomplete without next client?'
        tour.assign(next_client)

        if DISPLAY['routing']['all']: print_route(display_surface, all_clients, tour)
        a = find_best_route(display_surface, all_clients, tour, iterations)

        next_next_client = find_next(next_client, other_tour, all_clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            if DISPLAY['routing']['all']: print_route(display_surface, all_clients, other_tour)
            b = find_best_route(display_surface, all_clients, other_tour, iterations)

        return a if a < b else b
    else:
        iterations.incr()
        return tour


def get_min_max_members(all_clients):
    min = len(all_clients.clients)
    max = 0
    for x in all_clients.get_valid_areas():
        this = len(x.clients)
        if this < min: min = this
        if this > max: max = this
    return min, max


def get_average_members(all_clients):
    avg = 0.0
    all_areas = all_clients.get_valid_areas()
    cnt = len(all_areas)
    for sa in all_areas:
        avg += len(sa.clients)

    return avg/cnt


def areas_overloaded_with_clients(all_clients, clients_maximum):
    wanted = all_clients.get_valid_areas()
    big_areas = [ area for area in wanted if len(area.clients) > clients_maximum ]
    return big_areas


def areas_short_of_clients(all_clients, clients_minimum):
    wanted = all_clients.get_valid_areas()
    short_areas = [ area for area in wanted if len(area.clients) < clients_minimum ]
    return short_areas


def areas_with_client_count(all_clients, count):
    wanted = all_clients.get_valid_areas()
    wanted_areas = [ area for area in wanted if len(area.clients) == count ]
    for war in wanted_areas:
        assert len(war.clients) == len(war.tours[-1].clients), 'OOOPS! amount of clients differs area != tour'
    return wanted_areas


def calculate_all_tours(display_surface, all_clients):
    avg = len(all_clients.clients) / pow(1 / all_clients.factor, 2)
    print('\nstart final routing (avg: %d)\n' % avg)
    for final_area in all_clients.get_valid_areas():
        if len(final_area.tours):
            calculation = final_area.tours[-1]
            if calculation.length() > 0.0 and calculation.final_length:
                print('  pre-calculated: %f (%d clients)' % (calculation.final_length, len(calculation.plan)))
                all_clients.final_areas.append(final_area)
                continue

        # here area -> tours needed
        final_tour = Tour(final_area.clients)
        best_tour = do_routing(display_surface, all_clients, final_tour)
        print('best tour length: %f (%d clients)' % (best_tour.length(), len(best_tour.plan)))
        final_area.tours = [best_tour,]
        all_clients.final_areas.append(final_area)


def statistics(all_clients, replay=False):
#    if duplicates: print('avoided second tour calculation: %d' % duplicates)

    area_count = len(all_clients.get_valid_areas(True))
    print('\n %d areas/tours and %d clients' % (area_count, len(all_clients.clients)))
    fac = SETTINGS['clients'] / pow(1 / all_clients.factor, 2)
    print(' average of %d members (%d by factor)' % (get_average_members(all_clients), fac))
    l_min, l_max = get_min_max_members(all_clients)
    print(' tour members min: %d  max %d' % (l_min, l_max))
    print('\n total length: %f' % all_clients.summarize_total_length())

    if not replay:
        too_short = len(areas_short_of_clients(all_clients, SETTINGS['cluster_size_min']))
        too_big = len(areas_overloaded_with_clients(all_clients, SETTINGS['cluster_size_max']))
        all_clients.areas_too_small.append(too_short)
        all_clients.areas_too_big.append(too_big)
    print('\n tour size progression:')
    for his in range(len(all_clients.areas_too_small)):
        print(' tours off-size: %d (%d too small / %d too big)' % \
                ((all_clients.areas_too_small[his] + all_clients.areas_too_big[his]), all_clients.areas_too_small[his], all_clients.areas_too_big[his]))
    if replay:
        print('')
        cmin = l_min if l_min < SETTINGS['cluster_size_min'] else SETTINGS['cluster_size_min']
        cmax = l_max if l_max > SETTINGS['cluster_size_max'] else SETTINGS['cluster_size_max']
        for cnt in range(cmin, cmax + 1):
            acount = len(areas_with_client_count(all_clients, cnt))
            if cnt == SETTINGS['cluster_size_min']: print('- - - - - - - - - - - - - - - -')
            print(' tours with size %d = %d' % (cnt, acount))
            if cnt == SETTINGS['cluster_size_max']: print('- - - - - - - - - - - - - - - -')
    print('')


def serialize_final_route(tour, counter, error):
    tour_plan = {'error': error, 'counter': counter, 'spots': {}}
    prev = None
    for idx, rcli in enumerate(tour.plan):
        if not prev:
            prev = rcli
            continue
        tour_plan['spots'][idx] = (prev.coords(), rcli.coords())
        prev = rcli

    return json.dumps(tour_plan)


def load_clients_list():
    unpickled = load_clients_file()
    if unpickled is None:
        base_clients = []
        while len(base_clients) < SETTINGS['clients']:
            newc = Client(randrange(1, SETTINGS['width']), randrange(1, SETTINGS['height']))
            if newc not in base_clients:
                base_clients.append(newc)

        save_clients_file(base_clients)

        return base_clients
    else:
        return unpickled


def get_user_clients():
    pass


def check_clients_unique(clients_collection):
    for xcli in clients_collection.clients:
        found = 0
        for fin_area in clients_collection.final_areas:
            if xcli in fin_area.tours[-1].plan:
                found += 1
                if xcli not in fin_area.clients:
                    print('OOOPS! plan-client not in area-clients')
        assert found == 1, 'FATAL! Client in multiple plans'


def single_tour_serialized(req_data=None, maximum=10):
    if DISPLAY['enable']: display_surface = graphics_init()
    else: display_surface = None
    if DISPLAY['intro']: intro(display_surface)

    if not req_data:
        base_clients = load_clients_list()
        client_count = SETTINGS['clients']
        screen_width = SETTINGS['width']
        screen_height = SETTINGS['height']
        error_code = 0
    else:
        base_clients = []
        for k,v in req_data['spots'].items():
            if len(base_clients) < maximum:
                base_clients.append(Client(v['x'], v['y']))

        client_count = req_data['counter']
        screen_width = req_data['screen']['x']
        screen_height = req_data['screen']['y']
        error_code = req_data['error']

    if not base_clients:
        return None

    collection = ClientsCollection(base_clients, 1, client_count, screen_width, screen_height)
    area = Area(Client(0,0), Client(screen_width, screen_height))
    collection.small_areas = [area,]
    area.add_clients_in_area(collection)
    calculate_all_tours(display_surface, collection)
    if DISPLAY['enable']:
        statistics(collection)

    collection.final_print = True
    if DISPLAY['enable']:
        surface = print_route(display_surface, collection, collection.final_areas[-1].tours[-1])
    else:
        return serialize_final_route(collection.final_areas[-1].tours[-1], client_count, error_code)

    if DISPLAY['enable']: export_as_file(surface, '/tmp/pygame.png')


if __name__ == '__main__':
    single_tour_serialized()


