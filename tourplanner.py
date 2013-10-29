from client import ClientsCollection
from tour import calculate_all_tours
from config import SETTINGS, INFO

# TODO: zur gezielten tour-area-vergroesserung Entfernung zu benachbarten clients checken
# TODO: erst alle tour-areas festlegen, bevor erste Berechnung started
# TODO: strange Einzelgaenger zwischen 1. und 2. Tour?!? Vielleicht schon geloest??!

if __name__ == '__main__':
    all_clients = ClientsCollection(**SETTINGS)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (SETTINGS['clusters'] * SETTINGS['cluster_size']))
    calculate_all_tours(all_clients, SETTINGS)


