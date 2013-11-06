from client import ClientsCollection
from tour import calculate_all_tours
from config import SETTINGS, INFO, TEST

# TODO: zur gezielten tour-area-vergroesserung Entfernung zu benachbarten clients checken
# TODO: erst alle tour-areas festlegen, bevor erste Berechnung started
# TODO: strange Einzelgaenger zwischen 1. und 2. Tour?!? Vielleicht schon geloest??!

if __name__ == '__main__':
    all_clients = ClientsCollection(**SETTINGS)
    if TEST['level'] == 1:
        all_clients.clients[0].x = 0
        all_clients.clients[1].x = 1200
        all_clients.clients[2].y = 0
        all_clients.clients[3].y = 700
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (SETTINGS['clusters'] * SETTINGS['cluster_size']))
    calculate_all_tours(all_clients, SETTINGS)


