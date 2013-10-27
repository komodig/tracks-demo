from client import ClientsCollection
from tour import calculate_tours
from config import SETTINGS, INFO

# TODO: zur gezielten tour-area-vergrösserung Entfernung zu benachbarten clients checken
# TODO: find_tour_clients sollte bei clients > cluster_size überzählige clients rauswerfen

if __name__ == '__main__':
    all_clients = ClientsCollection(**SETTINGS)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (SETTINGS['clusters'] * SETTINGS['cluster_size']))
    calculate_tours(all_clients, **SETTINGS)


