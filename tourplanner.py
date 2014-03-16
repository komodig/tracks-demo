from random import randrange
from copy import deepcopy
from time import sleep
from math import sqrt, pow
from client import Client, ClientsCollection, find_next, get_client_area
from tour import Tour
from area import Area, get_clients_in_area, get_neighbours
from config import SETTINGS, INFO, TEST, DISPLAY, OPTIMIZE
from tourplanner_test import edge_test_clients
from tourplanner_graphics import print_route, print_area, print_clients, print_screen_set, \
        TourplannerSurface, handle_user_events, ProcessControl, intro


def do_routing(all_clients, tour, tour_surface):
    best_tour = None
    for start_client in tour.clients:
        new_tour = Tour(tour.clients, [start_client,])
        res_tour = find_best_route(all_clients, new_tour)
        if DISPLAY['routing']['best_starter']: print_route(all_clients, res_tour) #, tour_surface)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    return best_tour


def find_best_route(all_clients, tour):
    if tour.is_incomplete():
        other_tour = deepcopy(tour)

        latest = tour.get_last_assigned()
        assert latest, 'FATAL! No start_client found'
        next_client = find_next(latest, tour, all_clients)
        if next_client is None:
            return tour
        else:
            tour.assign(next_client)
#        tour_area = get_client_area(next_client, all_clients)
#        print_screen_set(TourplannerSurface(), 'ExIt', [None, [next_client,], True], [None, all_clients, tour_area.origin, tour_area.end])
        if DISPLAY['routing']['all']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour)

        next_next_client = find_next(next_client, other_tour, all_clients)
        if next_next_client is None:
            b = a
        else:
            other_tour.assign(next_next_client)
            if DISPLAY['routing']['all']: print_route(all_clients, other_tour)
            b = find_best_route(all_clients, other_tour)

        return a if a < b else b
    else:
        return tour


def factorize_float(clients, cluster_size_min, cluster_size_max, width, height):
    factors = []
    #assert width == height, 'to use sqrt and pow here we assume width == height'
    print('\n%d clients to go...\n' % clients)
    for avg_clients in range(2, cluster_size_max):
        factor = 1 / sqrt(clients / avg_clients)
        print('factor: %f' % factor)
        retour = clients / pow(1 / factor, 2)
        print('avg-clients (approximately): %f' % retour)
        factors.append(factor)

    return factors


def get_next_area_with_clients(origin, all_clients):
    area_width = SETTINGS['width'] * all_clients.factor #DIMENSION[0]['x_factor']
    area_height = SETTINGS['height'] * all_clients.factor #DIMENSION[0]['y_factor']
    end = Client(origin.x + area_width, origin.y + area_height)
    area = Area(origin, end)
    while not len(get_clients_in_area(area, all_clients)):
        if area.origin.x > SETTINGS['width']:
            if area.origin.y > SETTINGS['height']:
                print('END OF TOTAL AREA!')
                return None
            # get first of lower row
            area.origin.x = 0
            area.origin.y += area_height
            area.end.x = area_width
            area.end.y += area_height
        else:
            # get one to the right
            area.origin.x += area_width
            area.end.x += area_width

    if OPTIMIZE['shrink_areas']:
        while True:
            area_clients = get_clients_in_area(area, all_clients)
            if len(area_clients) <= SETTINGS['cluster_size_max'] or (area.end.x - area.origin.x) < area_width * 0.75:
                break
            else:
                area.end.x -= area_width/10
                print('shrinking...')

    return area


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


def unite_areas(one, other):
    if DISPLAY['areas']['unite_info']: print('unite_areas(): 1. area ORIG(%d,%d) END(%d,%d) (%d x %d) with %d clients' % \
                (one.origin.x, one.origin.y, one.end.x, one.end.y, one.width, one.height, len(one.clients)))
    if DISPLAY['areas']['unite_info']: print('unite_areas(): 2. area ORIG(%d,%d) END(%d,%d) (%d x %d) with %d clients' % \
                (other.origin.x, other.origin.y, other.end.x, other.end.y, other.width, other.height, len(other.clients)))
    if one.origin.x < other.origin.x or one.origin.y < other.origin.y:
        origin = one.origin
        end = other.end
    else:
        origin = other.origin
        end = one.end

    new_area = Area(origin, end)
    new_area.clients = (one.clients + other.clients)
    # TODO: accurate dimensions for non-rectangular areas
    if DISPLAY['areas']['unite_info']: print('unite_areas(): 3. area ORIG(%d,%d) END(%d,%d) (%d x %d) with %d clients' % \
                (new_area.origin.x, new_area.origin.y, new_area.end.x, new_area.end.y, new_area.width, new_area.height, len(new_area.clients)))
    return new_area


def mark_short_area_clients(surface, all_clients, cluster_min):
    print_clients(surface, all_clients.clients)
    mark_these = areas_short_of_clients(all_clients, cluster_min)
    for xsarea in mark_these:
        print_clients(surface, xsarea.clients, False, True)


def merge_with_neighbours(to_merge, all_clients, cluster_min, cluster_max):
    surface = TourplannerSurface()
    neighbours = get_neighbours(to_merge, all_clients, surface)
    if DISPLAY['areas']['merge']:
        mark_short_area_clients(surface, all_clients, cluster_min)

    final_area = None
    willing_neighbour = None
    for nei in neighbours:
        if (len(nei.clients) + len(to_merge.clients)) > cluster_max:
            continue
        united_area = unite_areas(to_merge, nei)
        # here area -> tours needed
        united_tour = Tour(united_area.clients)
        best_united = do_routing(all_clients, united_tour, surface)
        if final_area is None or best_united < final_area.tours[-1]:
            united_area.tours = [best_united,]
            assert len(united_area.tours) == 1, 'BUT HOW? multi-tours not implemented yet!'
            final_area = united_area
            willing_neighbour = nei

    if final_area is None:
        print('sorry, can\'t unite!')
        return None

    # deleting still referenced objects is difficult, so we use valid-flag:
    all_areas = all_clients.get_valid_areas()
    for varea in all_areas:
        if varea == to_merge or varea == willing_neighbour:
            varea.valid = False

    all_clients.small_areas.append(final_area)

    if DISPLAY['areas']['merge']:
        res_surface = TourplannerSurface()
        mark_short_area_clients(res_surface, all_clients, cluster_min)
        print_screen_set(res_surface, 'GoOn', [None, final_area.clients] , None, [all_clients, final_area.tours[-1]])
        for nei in neighbours:
            print_area(res_surface, all_clients, nei.origin, nei.end)
        res_surface.change_color('color3')
        print_screen_set(res_surface, 'GoOn', [None, to_merge.clients] , [None, None, to_merge.origin, to_merge.end], None)
        res_surface.change_color('color2')
        print_screen_set(res_surface, 'GoOn', [None, willing_neighbour.clients] , [None, None, willing_neighbour.origin, willing_neighbour.end], None)
        res_surface.change_color('color')

    if DISPLAY['areas']['slow']: sleep(1)
    handle_user_events(surface.process)

    return final_area


def push_to_neighbours(to_shrink, all_clients, cluster_min, cluster_max, recursion_max, surface):
    neighbours = get_neighbours(to_shrink, all_clients, surface)

    push_client = None
    best_tour = None
    best_neighbour = None
    for nei in neighbours:
        if (len(nei.clients) + 1) > cluster_max:
            continue

        for give_away_client in to_shrink.clients:
            new_neighbour_clients = nei.clients + [give_away_client,]
            nei_tour = Tour(new_neighbour_clients)
            res_tour = do_routing(all_clients, nei_tour, surface)

            if best_tour is None or res_tour < best_tour:
                best_neighbour = nei
                best_tour = res_tour
                push_client = give_away_client

    if best_neighbour is None:
        if recursion_max > 0:
            print('recursion_max: %d' % recursion_max)
            for nei in neighbours:
                push_res = push_to_neighbours(nei, all_clients, cluster_min, cluster_max, (recursion_max - 1), surface)
                if push_res:
                    return push_res
            return None
        else:
            print('sorry, can\'t push any clients!')
            return None

    # i append the shrinked tour to area tours instead of replacing the old tour.
    # not sure, what's the benefit besides tour history
    to_shrink.clients.remove(push_client)
    shrinked_tour = Tour(to_shrink.clients)
    best_shrinked = do_routing(all_clients, shrinked_tour, surface)
    to_shrink.tours.append(best_shrinked)
    best_neighbour.clients.append(push_client)
    best_neighbour.tours.append(best_tour)

    if DISPLAY['areas']['client_push']:
        surface.change_color('color3')
        print_screen_set(surface, 'GoOn', [None, to_shrink.clients] , [None, None, to_shrink.origin, to_shrink.end], [all_clients, to_shrink.tours[-1]])
        if DISPLAY['areas']['slow']: sleep(1)
        surface.change_color('color2')
        print_screen_set(surface, 'GoOn', [None, best_neighbour.clients] , [None, None, best_neighbour.origin, best_neighbour.end], [all_clients, best_neighbour.tours[-1]])
        if DISPLAY['areas']['slow']: sleep(1)
        surface.change_color('color')

    if DISPLAY['areas']['slow']: sleep(1)
    handle_user_events(surface.process)

    return best_neighbour


def steal_clients_from_neighbours(thief, all_clients, cluster_min, cluster_max, surface):
    neighbours = get_neighbours(thief, all_clients, surface)

    wanted_client = None
    best_tour = None
    best_neighbour = None
    for nei in neighbours:
        if (len(nei.clients) - 1) < cluster_min:
            continue

        for steal_this in nei.clients:
            new_clients = (thief.clients + [steal_this,])
            bigger_tour = Tour(new_clients)
            res_tour = do_routing(all_clients, bigger_tour, surface)

            if best_tour is None or res_tour < best_tour:
                best_neighbour = nei
                best_tour = res_tour
                wanted_client = steal_this

    if best_neighbour is None:
        return None

    test_len = len(best_neighbour.clients)
    best_neighbour.clients.remove(wanted_client)
    assert len(best_neighbour.clients) + 1 == test_len, 'FUCK! failed to remove client'
    new_neighbour_tour = Tour(best_neighbour.clients)
    res_tour = do_routing(all_clients, new_neighbour_tour, surface)
    best_neighbour.tours.append(res_tour)
    thief.clients.append(wanted_client)
    thief.tours.append(best_tour)

    if DISPLAY['areas']['client_steal']:
        surface.change_color('color3')
        print_screen_set(surface, 'GoOn', [None, thief.clients] , [None, None, thief.origin, thief.end], [all_clients, thief.tours[-1]])
        if DISPLAY['areas']['slow']: sleep(1)
        surface.change_color('color2')
        print_screen_set(surface, 'GoOn', [None, best_neighbour.clients] , [None, None, best_neighbour.origin, best_neighbour.end], [all_clients, best_neighbour.tours[-1]])
        if DISPLAY['areas']['slow']: sleep(1)
        surface.change_color('color')

    if DISPLAY['areas']['slow']: sleep(1)
    handle_user_events(surface.process)

    return best_neighbour


def prepare_areas_with_clients(all_clients, surface):
    small_area = Area(Client(0, 0), Client(0, 0))

    while True:
        last_end = Client(small_area.end.x, small_area.origin.y)
        small_area = get_next_area_with_clients(last_end, all_clients)
        if small_area is None:
            break
        else:
            small_area.add_clients_in_area(all_clients)

        if DISPLAY['areas']['init']: print_area(surface, all_clients, small_area.origin, small_area.end)
        all_clients.small_areas.append(small_area)
        handle_user_events(surface.process)


def optimize_areas(all_clients, surface):
    if OPTIMIZE['merge_areas']:
        print('\noptimizing by merging areas\n')
        impossibles = []
        while True:
            print('running merge loop...')
            optimize_these = areas_short_of_clients(all_clients, SETTINGS['cluster_size_min'])
            if len(optimize_these) - len(impossibles) == 0:
                break
            for optimizable in optimize_these:
                if not optimizable.valid or optimizable in impossibles:
                    continue
                result = merge_with_neighbours(optimizable, all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'])
                if result is None:
                    impossibles.append(optimizable)

    if OPTIMIZE['push_clients']:
        print('\noptimizing by pushing clients away\n')
        repetitions = 0
        opt_count_before = None
        while repetitions < 2:
            print('running push loop...')
            optimize_these = areas_overloaded_with_clients(all_clients, SETTINGS['cluster_size_max'])
            opt_count = len(optimize_these)
            if opt_count_before is not None:
                if opt_count == opt_count_before:
                    repetitions += 1
                else:
                    repetitions = 0
            opt_count_before = opt_count
            for optimizable in optimize_these:
                push_surface = TourplannerSurface()
                push_to_neighbours(optimizable, all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'], 100, push_surface)

    if OPTIMIZE['steal_clients']:
        print('\noptimizing by stealing clients\n')
        no_success = 0
        while no_success < 3:
            print('running steal loop...')
            failed = success = 0
            optimize_these = areas_short_of_clients(all_clients, SETTINGS['cluster_size_min'])
            for optimizable in optimize_these:
                steal_surface = TourplannerSurface()
                res_steal = steal_clients_from_neighbours(optimizable, all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'], steal_surface)
                if res_steal:
                    success += 1
                else:
                    failed += 1
            print('successful: %d failed: %d' % (success, failed))
            if success == 0:
                no_success += 1


def calculate_all_tours(all_clients):
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
        best_tour = do_routing(all_clients, final_tour, surface)
        print('best tour length: %f (%d clients)' % (best_tour.length(), len(best_tour.plan)))
        final_area.tours = [best_tour,]
        all_clients.final_areas.append(final_area)

        handle_user_events(surface.process)


def statistics(all_clients):
#    if duplicates: print('avoided second tour calculation: %d' % duplicates)

    area_count = len(all_clients.get_valid_areas())
    print('results in %d areas on %d x %d screen' % (area_count, SETTINGS['width'], SETTINGS['height']))
    print('average of %d members' % get_average_members(all_clients))
    l_min, l_max = get_min_max_members(all_clients)
    print('area members min: %d  max %d' % (l_min, l_max))

    # FIXME: how can areas off-clustersize count more than total area_count?!?
    if all_clients.areas_too_small is not None:
        print('off clustersize: %d (%d too small / %d too big)' % ((all_clients.areas_too_small + all_clients.areas_too_big), all_clients.areas_too_small, all_clients.areas_too_big))
        print('now:')
    all_clients.areas_too_small = len(areas_short_of_clients(all_clients, SETTINGS['cluster_size_min']))
    all_clients.areas_too_big = len(areas_overloaded_with_clients(all_clients, SETTINGS['cluster_size_max']))
    print('off clustersize: %d (%d too small / %d too big)' % ((all_clients.areas_too_small + all_clients.areas_too_big), all_clients.areas_too_small, all_clients.areas_too_big))
    print('total length: %f' % all_clients.summarize_total_length())


def run(all_clients, surface):
    prepare_areas_with_clients(all_clients, surface)
    statistics(all_clients)
    optimize_areas(all_clients, surface)
    calculate_all_tours(all_clients)

    assert len(all_clients.get_valid_areas()) == len(all_clients.final_areas), 'SHIT! i someone is missing'

    print_route(all_clients, all_clients.final_areas[-1].tours[-1])


def check_clients_unique(clients_collection):
    for xcli in clients_collection.clients:
        found = 0
        for fin_area in clients_collection.final_areas:
            if xcli in fin_area.tours[-1].plan:
                found += 1
                if xcli not in fin_area.clients:
                    print('OOOPS! plan-client not in area-clients')
        try:
            assert found == 1, 'FATAL! Client in multiple plans'
        except AssertionError:
            print('FATAL! Client in multiple plans')
            exit(1)


if __name__ == '__main__':
    if DISPLAY['intro']: intro()

    factors = factorize_float(**SETTINGS)
    print('init %d clients' % SETTINGS['clients'])
    surface = TourplannerSurface()

    base_clients = []
    while len(base_clients) < SETTINGS['clients']:
        base_clients.append(Client(randrange(1, SETTINGS['width']), randrange(1, SETTINGS['height'])))

    all_collections = []
    for fact in factors:
        collection = ClientsCollection(base_clients, fact, SETTINGS['clients'], SETTINGS['width'], SETTINGS['height'])
        if TEST['level'] == 1:
            edge_test_clients(collection)
        total_length = run(collection, surface)
        all_collections.append(collection)
        sleep(2)

    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))

    least_off_size = None
    best_length = None
    for col in all_collections:
        statistics(col)
        check_clients_unique(col)
        assert col.areas_off_size() is not None, 'CRAZY! final statistics missing: off_size!'
        assert col.total_length, 'CRAZY! final statistics missing: total_length!'
        if least_off_size  is None or col.areas_off_size() < least_off_size.areas_off_size():
            least_off_size = col
        if best_length is None or col.total_length < best_length.total_length:
            best_length = col

        print('\n///////////////////////////////////////\n')

    print('\nand the winner is...\n')
    statistics(least_off_size)
    print('\n')
    if least_off_size == best_length:
        print('AWESOME! best in length and least areas off-size\n')

    least_off_size.final_print = True if not TEST['long_term'] else False
    final_surface = TourplannerSurface()
    final_surface.change_color('violett-rot')
    print_screen_set(final_surface, 'GoOn', None, None, [least_off_size, least_off_size.final_areas[-1].tours[-1]])

    print('used colors:')
    print(DISPLAY['color']['spot'])
    print(DISPLAY['color']['line'])

    if TEST['long_term']:
        sleep(3)
        handle_user_events(surface.process)
        exit(3)
    else:
        surface.process.state = ProcessControl.WAIT
        handle_user_events(surface.process)


