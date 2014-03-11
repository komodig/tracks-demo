from time import sleep
from client import Client, ClientsCollection, find_next
from tour import Tour
from area import Area, get_clients_in_area, get_neighbours
from config import SETTINGS, INFO, TEST, DISPLAY, DIMENSION
from tourplanner_test import edge_test_clients
from tourplanner_graphics import print_route, print_area, print_clients, print_screen_set, \
        TourplannerSurface, handle_user_events, ProcessControl, intro


def do_routing(all_clients, tour, tour_surface):
    best_tour = None
    for start_client in tour.clients:
        tour = Tour(tour.origin, tour.end, 'created in do_routing with clients and starter', tour.clients, start_client, all_clients)
        res_tour = find_best_route(all_clients, tour)
        #print('tour length: %f' % res_tour.length)
        if DISPLAY['routing']['best_starter']: print_route(all_clients, res_tour) #, tour_surface)
        if best_tour is None or res_tour < best_tour:
            best_tour = res_tour

    print('best tour length: %f' % best_tour.length)
    best_tour.tour_log('yeah routing returned me as best tour')
    return best_tour


def find_best_route(all_clients, tour):
    if tour.is_incomplete(all_clients):
        other_tour = deepcopy(tour)
        tour.tour_log('wtf they produced a clone of me to find best route')
        other_tour.tour_log('wow i am a clone to find best route')

        latest = tour.get_last_assigned()
        assert latest, 'FATAL! No start_client found'
        next_client = find_next(latest, tour.clients, all_clients)
        if next_client is None:
            return tour
        if not tour.assign(next_client, all_clients): print_screen_set(TourplannerSurface(), True, [None, [next_client,], True], [None, all_clients, tour.origin, tour.end])
        if DISPLAY['routing']['all']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour)

        next_next_client = find_next(next_client, other_tour.clients, all_clients)
        if next_next_client is None:
            b = a
        else:
            if not other_tour.assign(next_next_client, all_clients): print_screen_set(TourplannerSurface(), True, [None, [next_client,], True], [None, all_clients, tour.origin, tour.end])
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
        print('sa.clients: %d' % len(sa.clients))
        avg += len(sa.clients)

    return avg/cnt


def areas_short_of_clients(all_clients, clients_minimum):
    wanted = all_clients.get_valid_areas()
    return [ area for area in wanted if len(area.clients) < clients_minimum ]


def unite_areas(one, other):
    if DISPLAY['unite_areas']: print('unite_areas(): 1. area at (%d,%d) (%d x %d) with %d clients' % \
            (one.origin.x, one.origin.y, one.width, one.height, len(one.clients)))
    if DISPLAY['unite_areas']: print('unite_areas(): 2. area at (%d,%d) (%d x %d) with %d clients' % \
            (other.origin.x, other.origin.y, other.width, other.height, len(other.clients)))
    if one.origin.x < other.origin.x or one.origin.y < other.origin.y:
        origin = one.origin
        end = other.end
    else:
        origin = other.origin
        end = one.end

    # united_clients = one.clients + other.clients
    new_area = Area(origin, end)
    new_area.add_clients_in_area(all_clients)
    if DISPLAY['unite_areas']: print('unite_areas(): 3. area at (%d,%d) (%d x %d) with %d clients' % \
            (new.origin.x, new.origin.y, new.width, new.height, len(new.clients)))
    return new


def merge_with_neighbours(to_merge, all_clients, cluster_min, cluster_max):
    surface = TourplannerSurface()
    neighbours = get_neighbours(to_merge, all_clients, surface)
    if DISPLAY['dimensions']:
        print_clients(surface, all_clients.clients)
        mark_these = areas_short_of_clients(all_clients, cluster_min)
        for xsarea in mark_these:
            print_clients(surface, xsarea.clients, False, True)

    sleep(1)
    return

    top_united = None
    willing_neighbour = None
    for nei in neighbours:
        if (len(nei.clients) + len(to_merge.clients)) > cluster_max:
            continue
        united = unite_areas(to_merge, nei)
        # here area -> tours needed
        best_united = do_routing(all_clients, united, surface)
        if top_united is None or best_united < top_united:
            top_united = copy(best_united)
            willing_neighbour = nei

    if best is None:
        print('sorry, can\'t unite!')
        # TODO: is this final? don't route this again!!
        return to_merge

    # areas.remove(willing_neighbour) causes strange behaviour so remove differently
    for area in all_clients.get_valid_areas():
        if area == to_merge:
            area.valid = False
        if area == willing_neighbour:
            area.valid = False

    if len(best.clients) >= SETTINGS['cluster_size_max']:
        print('final tour calculation done: %f' % best.length)
        best.final = True
    all_clients.small_areas.append(best)
    if DISPLAY['dimensions_slow']:
        for nei in neighbours: print_area(surface, all_clients, nei.origin, nei.end)
    surface.change_route_color()
    if DISPLAY['dimensions']: print_area(surface, all_clients, best.origin, best.end)
    if DISPLAY['dimensions_slow']: sleep(1)
    return best


def prepare_areas_with_clients(all_clients, surface):
    small_area = Area(Client(0, 0), Client(0, 0))

    while True:
        last_end = Client(small_area.end.x, small_area.origin.y)
        small_area = get_next_area_with_clients(last_end, all_clients)
        if small_area is None:
            break
        else:
            small_area.add_clients_in_area(all_clients)

        if DISPLAY['dimensions']: print_area(surface, all_clients, small_area.origin, small_area.end)
        all_clients.small_areas.append(small_area)
        handle_user_events(surface.process)


def optimize_areas(all_client, surface):
    optimize_these = areas_short_of_clients(all_clients, SETTINGS['cluster_size_min'])
    for optimizable in optimize_these:
        merge_with_neighbours(optimizable, all_clients, SETTINGS['cluster_size_min'], SETTINGS['cluster_size_max'])
        handle_user_events(surface.process)


def calculate_all_tours(all_clients):
# FIXME: div by zero error
#    print('average of %d members' % get_average_members(all_clients))

    print('\nstart final routing\n')
    for final_area in all_clients.get_valid_areas():
        # here area -> tours needed
        best = do_routing(all_clients, final_area, surface)
        all_clients.best_tours.append(best)

        if calculation.length() > 0.0 and calculation.final_length:
            print('  pre-calculated: %f' % calculation.final_length)
            all_clients.best_tours.append(calculation)

        handle_user_events(surface.process)

#    if duplicates: print('avoided second tour calculation: %d' % duplicates)

    tour_count = len(all_clients.get_valid_areas())
    print('results in %d areas on %d x %d screen' % (tour_count, SETTINGS['width'], SETTINGS['height']))
    l_min, l_max = get_min_max_members(all_clients)
    print('area members min: %d  max %d' % (l_min, l_max))
    print('total length: %f' % all_clients.summarize_total_length())
    all_clients.final_print = False
    print_route(all_clients, all_clients.best_tours[0])

    if TEST['long_term']:
        sleep(3)
        handle_user_events(surface.process)
        exit(3)
    else:
        surface.process.state = ProcessControl.WAIT
        handle_user_events(surface.process)


if __name__ == '__main__':
    if DISPLAY['intro']:
        intro()

    all_clients = ClientsCollection(**SETTINGS)
    if TEST['level'] == 1:
        edge_test_clients(all_clients)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (len(all_clients.clients)))
    surface = TourplannerSurface()
    prepare_areas_with_clients(all_clients, surface)
    optimize_areas(all_clients, surface)
    # calculate_all_tours(all_clients)
