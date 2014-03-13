from copy import deepcopy
from time import sleep
from client import Client, ClientsCollection, find_next, get_client_area
from tour import Tour
from area import Area, get_clients_in_area, get_neighbours
from config import SETTINGS, INFO, TEST, DISPLAY, DIMENSION
from tourplanner_test import edge_test_clients
from tourplanner_graphics import print_route, print_area, print_clients, print_screen_set, \
        TourplannerSurface, handle_user_events, ProcessControl, intro


def do_routing(all_clients, tour, tour_surface):
    best_tour = None
    for start_client in tour.clients:
        new_tour = Tour(tour.clients, [start_client,])
        res_tour = find_best_route(all_clients, new_tour)
        #print('tour length: %f' % res_tour.length)
        if DISPLAY['routing']['best_starter']: print_route(all_clients, res_tour) #, tour_surface)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f (%d clients)' % (best_tour.length(), len(best_tour.plan)))
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


def get_next_area_with_clients(origin, all_clients):
    area_width = SETTINGS['width'] * DIMENSION[0]['x_factor']
    area_height = SETTINGS['height'] * DIMENSION[0]['y_factor']
    end = Client(origin.x + area_width, origin.y + area_height)
    area = Area(origin, end)
    while not len(get_clients_in_area(area, all_clients)):
        if area.end.x + area_width > SETTINGS['width']:
            if area.end.y + area_height > SETTINGS['height']:
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


def areas_short_of_clients(all_clients, clients_minimum):
    wanted = all_clients.get_valid_areas()
    return [ area for area in wanted if len(area.clients) < clients_minimum ]


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
        if final_area is None or best_united < final_area.tours[0]:
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
        mark_short_area_clients(surface, all_clients, cluster_min)
        res_surface = print_route(all_clients, final_area.tours[0])
        surface.change_color('color')
        for nei in neighbours:
            print_area(surface, all_clients, nei.origin, nei.end)
        if DISPLAY['areas']['slow']: sleep(1)
        res_surface.change_color('color3')
        print_screen_set(res_surface, 'GoOn', [None, to_merge.clients] , [None, None, to_merge.origin, to_merge.end], None)
        res_surface.change_color('color2')
        print_screen_set(res_surface, 'GoOn', [None, willing_neighbour.clients] , [None, None, willing_neighbour.origin, willing_neighbour.end], None)
        if DISPLAY['areas']['slow']: sleep(1)
        res_surface.change_color('color')

    if DISPLAY['areas']['slow']: sleep(1)
    handle_user_events(surface.process)

    return final_area


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


def optimize_areas(all_client, surface):
    print('\noptimizing\n')
    not_mergebles = []
    while True:
        optimize_these = areas_short_of_clients(all_clients, SETTINGS['cluster_size_min'])
        if len(optimize_these) - len(not_mergebles) == 0:
            break
        for optimizable in optimize_these:
            if not optimizable.valid or optimizable in not_mergebles:
                continue
            result = merge_with_neighbours(optimizable, all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'])
            if result is None:
                not_mergebles.append(optimizable)

            handle_user_events(surface.process)


def calculate_all_tours(all_clients):
    print('\nstart final routing\n')
    for final_area in all_clients.get_valid_areas():
        if len(final_area.tours):
            calculation = final_area.tours[0]
            if calculation.length() > 0.0 and calculation.final_length:
                print('  pre-calculated: %f (%d clients)' % (calculation.final_length, len(calculation.plan)))
                all_clients.final_areas.append(final_area)
                continue

        # here area -> tours needed
        final_tour = Tour(final_area.clients)
        best_tour = do_routing(all_clients, final_tour, surface)
        final_area.tours = [best_tour,]
        all_clients.final_areas.append(final_area)

        handle_user_events(surface.process)


def statistics():
#    if duplicates: print('avoided second tour calculation: %d' % duplicates)

    area_count = len(all_clients.get_valid_areas())
    print('results in %d areas on %d x %d screen' % (area_count, SETTINGS['width'], SETTINGS['height']))
    print('average of %d members' % get_average_members(all_clients))
    l_min, l_max = get_min_max_members(all_clients)
    print('area members min: %d  max %d' % (l_min, l_max))
    print('total length: %f' % all_clients.summarize_total_length())
    print('used colors:')
    print(DISPLAY['color']['spot'])
    print(DISPLAY['color']['line'])


if __name__ == '__main__':
    if DISPLAY['intro']: intro()

    all_clients = ClientsCollection(**SETTINGS)

    if TEST['level'] == 1:
        edge_test_clients(all_clients)
    print('init %d clients' % (len(all_clients.clients)))
    surface = TourplannerSurface()
    prepare_areas_with_clients(all_clients, surface)
    optimize_areas(all_clients, surface)
    calculate_all_tours(all_clients)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    statistics()

    assert len(all_clients.get_valid_areas()) == len(all_clients.final_areas), 'SHIT! i someone is missing'

    all_clients.final_print = True if not TEST['long_term'] else False
    print_route(all_clients, all_clients.final_areas[-1].tours[0])

    if TEST['long_term']:
        sleep(3)
        handle_user_events(surface.process)
        exit(3)
    else:
        surface.process.state = ProcessControl.WAIT
        handle_user_events(surface.process)

