from time import sleep
from client import Client, ClientsCollection
from tour import calculate_tours 
from tourplanner_graphics import TourplannerSurface, print_clients, handle_user_events

info = {
    'version': '0.1.2',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


settings = {
    'clusters': 5,
    'cluster_size': 7,
    'width': 1200,
    'height': 800,
}


if __name__ == '__main__':
    all_clients = ClientsCollection(**settings)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (info['version'], info['usage']))
    print('running %d clients...' % (settings['clusters'] * settings['cluster_size']))

    surface = TourplannerSurface(settings, info, True)
    print_clients(surface, all_clients.clients, True)
    calculate_tours(surface, all_clients, **settings)

    while True:
        handle_user_events()
        sleep(2)


