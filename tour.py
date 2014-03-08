from client import Client
from tourplanner_graphics import print_route, print_area, print_clients, print_screen_set, \
        TourplannerSurface, handle_user_events, ProcessControl
from client import find_next, count_with_state, get_with_state, ClientState as state
from copy import copy, deepcopy
from config import SETTINGS, INFO, DISPLAY, DIMENSION, TEST
from time import sleep
from pygame import quit


class Tour():
    def __init__(self, origin, end, log_str, clients, start_client=None):
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
                prepare_added_client(cli)

        if start_client:
            for cli in self.clients:
                if cli == start_client:
                    #print('assigning start_client')
                    cli.c_log('the following assignment is as start_client')
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
        return ('%s' % self.clients)


    def add_clients(self, client_list):  # when areas unite
        for cta in client_list:
            prepare_added_client(cta)
            cta.c_log('appended in add_clients')
            self.clients.append(cta)


    def get_last_assigned(self):
        if self.first_assigned is None:
            return None
        else:
            last_assigned = self.first_assigned
            while last_assigned.next_assigned:
                last_assigned = last_assigned.next_assigned
            return last_assigned


    def assign(self, incoming):
        self.tour_log('try to get client assigned...')
        client = None
        for it in self.clients:
            if it == incoming:
                try:
                    assert it.next_assigned is None, 'REALLY STRANGE! should it be assigned with next set?'
                except AssertionError:
                    it.c_log('matched incoming but have next_assigned set')
                    self.warning = True
                    continue
                client = it # in case of cloned client
                client.c_log('matched incoming and getting assigned')
                break

        assert client, 'FATAL! Trying to assing not-member-client!'
        # FIXME: the following assertion failed sometimes.
        try:
            assert client.next_assigned is None, 'STRANGE! client to assign has next_assigned set!'
        except AssertionError:
            print('duuh!')
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
        client.state = state.ASSOCIATED
        return client


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
                    client.c_log('assuming state CANDIDATE in add_area_clients')
                    self.clients.append(client)
                    if DISPLAY['clients']['append']: print('add_area_clients: appended client: %s' % client)

        if add_them:
            print('got area at (%d,%d) (%d x %d) with %d clients' % \
                    (self.origin.x, self.origin.y, self.width, self.height, len(self.clients)))
        return count


    def count_area_clients(self, all_clients):
        count = self.add_area_clients(all_clients, False)
        return count


    def tour_log(self, log_str):
        self.logbook.append(log_str)


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
    if count_with_state(tour.clients, state.ASSOCIATED) < len(tour.clients):
        other_tour = deepcopy(tour)
        tour.tour_log('wtf they produced a clone of me to find best route')
        other_tour.tour_log('wow i am a clone to find best route')

        latest = tour.get_last_assigned()
        assert latest, 'FATAL! No start_client found'
        next_client = find_next(latest, tour.clients)
        if next_client is None:
            return tour
        if not tour.assign(next_client): print_screen_set(TourplannerSurface(), True, [None, [next_client,], True], [None, all_clients, tour.origin, tour.end])
        if DISPLAY['routing']['all']: print_route(all_clients, tour)
        a = find_best_route(all_clients, tour)

        next_next_client = find_next(next_client, other_tour.clients)
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
            area.origin.x = 0
            area.origin.y += area_height
            area.end.x = area_width
            area.end.y += area_height
        else:
            area.origin.x += area_width
            area.end.x += area_width

    return area


def get_area(all_clients, last_tour, dim_surface):
    last_end = Client(last_tour.end.x, last_tour.origin.y, 'created in get_area used as upper right corner coords')
    small_area = get_next_area_with_clients(last_end, all_clients)
    if small_area is None:
        return None
    cli_sum = small_area.add_area_clients(all_clients)
    return small_area


def get_min_max_members(all_clients):
    min = len(all_clients.clients)
    max = 0
    for x in get_valid_areas(all_clients):
        this = len(x.clients)
        if this < min: min = this
        if this > max: max = this
    return min, max


def get_average_members(all_clients):
    avg = 0
    cnt = 0
    for sa in get_valid_areas(all_clients):
        avg += len(sa.clients)
        cnt += 1

    return avg/cnt


def tours_with_count(all_clients, count):
    wanted = get_valid_areas(all_clients)
    return [ area for area in wanted if len(area.clients) == count ]


def unite(one, other):
    one.tour_log('should unite with neighbour')
    other.tour_log('should get united as neighbour')
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

    one.tour_log('deliver clients to assimilate neighbour!')
    new = Tour(origin, end, 'created in unite with clients (first half)', one.clients)
    other.tour_log('deliver clients to get assimilated as neighbour')
    new.add_clients(other.clients)
    if DISPLAY['unite_areas']: print('unite(): 3. area at (%d,%d) (%d x %d) with %d clients' % \
            (new.origin.x, new.origin.y, new.width, new.height, len(new.clients)))
    return new


def prepare_added_client(c_to_add):
    c_to_add.c_log('getting prepared: next -> None, state -> CANDIDATE')
    c_to_add.next_assigned = None
    c_to_add.state = state.CANDIDATE


def get_valid_areas(all_clients):
    return [ area for area in all_clients.small_areas if area.valid ]


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
    for tour in get_valid_areas(all_clients):
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
        united = unite(ass, nei)
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
    for area in get_valid_areas(all_clients):
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
        small_area = get_area(all_clients, small_area, surface)
        if small_area is None:
            break
        if DISPLAY['dimensions']: print_area(surface, all_clients, small_area.origin, small_area.end)
        small_area.tour_log('put in all areas pool')
        all_clients.small_areas.append(small_area)
        handle_user_events(surface.process)

    print('average of %d members' % get_average_members(all_clients))
    print('CANDIDATE clients: %d' % count_with_state(all_clients.clients, state.CANDIDATE))
    print('FREE clients: %d' % count_with_state(all_clients.clients, state.FREE))

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
    for ttl in get_valid_areas(all_clients):
        ttl.tour_log('may final routing begin')

    doubles = 0
    for connect_this in get_valid_areas(all_clients):
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

    tour_count = len(get_valid_areas(all_clients))
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


