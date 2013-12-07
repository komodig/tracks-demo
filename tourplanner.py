from client import ClientsCollection
from tour import calculate_all_tours
from config import SETTINGS, INFO, TEST, DISPLAY
from tourplanner_test import edge_test_clients
from tourplanner_graphics import intro

if __name__ == '__main__':
    if DISPLAY['intro']:
        intro()

    all_clients = ClientsCollection(**SETTINGS)
    if TEST['level'] == 1:
        edge_test_clients(all_clients)
    print('\n*\n*   tourplanner (version: %s)\n*\n*   %s\n*\n' % (INFO['version'], INFO['usage']))
    print('running %d clients...' % (len(all_clients.clients)))
    calculate_all_tours(all_clients)


