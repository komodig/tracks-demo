from copy import copy, deepcopy
from client import Client, ClientsCollection, find_next
from tour import Tour
from config import SETTINGS, INFO, TEST, DISPLAY, DIMENSION
from tourplanner_test import edge_test_clients
from tourplanner_graphics import print_route, print_area, print_clients, print_screen_set, \
        TourplannerSurface, handle_user_events, ProcessControl, intro


def do_routing(all_clients, tour, tour_surface):
    if tour.warning: print('warning! routing dangerous tour')
    best_tour = None
    for start_client in tour.clients:
        tour = Tour(tour.origin, tour.end, 'created in do_routing with clients and starter', tour.clients, start_client)
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
        if not tour.assign(next_client): print_screen_set(TourplannerSurface(), True, [None, [next_client,], True], [None, all_clients, tour.origin, tour.end])
        if DISPLAY['routing']['all']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour)

        next_next_client = find_next(next_client, other_tour.clients, all_clients)
        if next_next_client is None:
            b = a
        else:
            if not other_tour.assign(next_next_client): print_screen_set(TourplannerSurface(), True, [None, [next_client,], True], [None, all_clients, tour.origin, tour.end])
            if DISPLAY['routing']['all']: print_route(all_clients, other_tour)
            b = find_best_route(all_clients, other_tour)

        return a if a < b else b
    else:
        return tour


def get_next_area_with_clients(origin, all_clients):
    area_width = SETTINGS['width'] * DIMENSION[0]['x_factor']
    area_height = SETTINGS['height'] * DIMENSION[0]['y_factor']
    end = Client(origin.x + area_width, origin.y + area_height, 'created in get_next_area_with_clients used as end coords')
    area = Tour(origin, end, 'created in get_next_area_with_clients but empty', None)
    while area.count_area_clients(all_clients) == 0:
        if area.end.x + area_width > SETTINGS['width']:
            if area.end.y + area_height > SETTINGS['height']:
                print('END OF TOTAL AREA!')
                return None
            # time for \r:
            area.origin.x = 0
            area.origin.y += area_height
            area.end.x = area_width
            area.end.y += area_height
        else:
            area.origin.x += area_width
            area.end.x += area_width

    return area


def get_next_area(all_clients, last_tour, dim_surface):
    last_end = Client(last_tour.end.x, last_tour.origin.y, 'created in get_next_area used as upper right corner coords')
    small_area = get_next_area_with_clients(last_end, all_clients)
    if small_area is None:
        return None
    cli_sum = small_area.add_clients_in_area(all_clients)
    return small_area


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


def tours_with_count(all_clients, count):
    wanted = all_clients.get_valid_areas()
    return [ area for area in wanted if len(area.clients) == count ]


def unite_areas(one, other):
    one.tour_log('should unite with neighbour')
    other.tour_log('should get united as neighbour')
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

    one.tour_log('deliver clients to assimilate neighbour!')
    other.tour_log('deliver clients to get assimilated as neighbour')
    united_clients = one.clients + other.clients
    for uc in united_clients:
        uc.c_log('getting new siblings to estimate best way to unite tours')
    new = Tour(origin, end, 'created in unite with clients (first half)', united_clients)
    if DISPLAY['unite_areas']: print('unite_areas(): 3. area at (%d,%d) (%d x %d) with %d clients' % \
            (new.origin.x, new.origin.y, new.width, new.height, len(new.clients)))
    return new


def assimilate_the_weak(all_clients, cluster_min, cluster_max, mcount):
    to_assimilate = tours_with_count(all_clients, mcount)
    surface = TourplannerSurface()

    if DISPLAY['dimensions']:
        print_clients(surface, all_clients.clients)
        mark_these = tours_with_count(all_clients, mcount)
        for tour in mark_these:
            print_clients(surface, tour.clients, False, True)

    ass = None
    for it in to_assimilate:
        it.tour_log('chosen to assimilate')
        if it.can_unite:
            it.tour_log('...and can unite')
            ass = it
            break
        else:
            it.tour_log('...but can\'t unite')

    if ass is None: return None

    neighbours = []
    for tour in all_clients.get_valid_areas():
        # north, east, south, west
        if (tour.origin.x == ass.origin.x and tour.end.y == ass.origin.y) or \
                (tour.origin.x == ass.end.x and tour.end.y == ass.end.y) or \
                (tour.origin.x == ass.origin.x and tour.origin.y == ass.end.y) or \
                (tour.end.x == ass.origin.x and tour.end.y == ass.end.y):
            tour.tour_log('append as neighbour area')
            neighbours.append(tour)
            if DISPLAY['dimensions']: print_area(surface, all_clients, tour.origin, tour.end)

    best = None
    chosen = None
    for nei in neighbours:
        if (len(nei.clients) + len(ass.clients)) > cluster_max:
            continue
        united = unite_areas(ass, nei)
        best_united = do_routing(all_clients, united, surface)
        if best is None or best_united < best:
            best = copy(best_united)
            chosen = copy(nei)

    if best is None:
        print('sorry, can\'t unite!')
        # TODO: is this final? don't route this again!!
        ass.tour_log('can not unite any further')
        ass.can_unite = False
        return ass

    best.tour_log('best united')
    # areas.remove(chosen) causes strange behaviour so remove differently
    for area in all_clients.get_valid_areas():
        if area == ass:
            area.tour_log('not valid any more (ass)')
            area.valid = False
        if area == chosen:
            area.tour_log('not valid any more (nei)')
            area.valid = False

    if len(best.clients) >= SETTINGS['cluster_size_max']:
        print('final tour calculation done: %f' % best.length)
        best.tour_log('final calculation done: %f' % best.length)
        best.final = True
    all_clients.small_areas.append(best)
    if DISPLAY['dimensions_slow']:
        for nei in neighbours: print_area(surface, all_clients, nei.origin, nei.end)
    surface.change_route_color()
    if DISPLAY['dimensions']: print_area(surface, all_clients, best.origin, best.end)
    if DISPLAY['dimensions_slow']: sleep(1)
    return best


def calculate_all_tours(all_clients):
    surface = TourplannerSurface()
    small_area = Tour(Client(0, 0, 'created in calculate_all_tours zero-zero'),
            Client(0, 0, 'created in calculate_all_tours zero-zero'), 'created in calculate_all_tours but empty just zero-zero-clients', None)

    while True:
        small_area = get_next_area(all_clients, small_area, surface)
        if small_area is None:
            break
        if DISPLAY['dimensions']: print_area(surface, all_clients, small_area.origin, small_area.end)
        small_area.tour_log('thrown in all areas pool')
        all_clients.small_areas.append(small_area)
        handle_user_events(surface.process)

# FIXME: div by zero error
#    print('average of %d members' % get_average_members(all_clients))

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

    print('\nstart final routing\n')
    for ttl in all_clients.get_valid_areas():
        ttl.tour_log('may final routing begin')

    doubles = 0
    for connect_this in all_clients.get_valid_areas():
        if connect_this.final:
            print('  pre-calculated: %f' % connect_this.length)
            #assert best.length == connect_this.length, 'second tour calculation different'
            doubles += 1
            all_clients.best_tours.append(connect_this)
        else:
            connect_this.tour_log('ready for final routing')
            best = do_routing(all_clients, connect_this, surface)
            all_clients.best_tours.append(best)

        handle_user_events(surface.process)

    if doubles: print('avoided second tour calculation: %d' % doubles)

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
    calculate_all_tours(all_clients)


