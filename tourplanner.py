from client import Client, ClientsCollection
from tourplanner_graphics import TourplannerSurface, print_clients, handle_user_events, ProcessControl
import tour
from config import SETTINGS, INFO


if __name__ == '__main__':
    all_clients = ClientsCollection(**SETTINGS)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (SETTINGS['clusters'] * SETTINGS['cluster_size']))

    surface = TourplannerSurface(SETTINGS, INFO, True)
    print_clients(surface, all_clients.clients, True)
    tour.calculate_tours(all_clients, **SETTINGS)

    surface.process.state = ProcessControl.WAIT
    handle_user_events(surface.process)


