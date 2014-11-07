import pickle
from config import SETTINGS, INFO, FILES


class TourPlannerBase():
    def __init__(self, width, height, clients, cluster_size_min, cluster_size_max):
        self.width = width
        self.height = height
        self.clients = clients
        self.cluster_size_min = cluster_size_min
        self.cluster_size_max = cluster_size_max
        self.version = 0.0
        self.clients_list = []

    def settings_dict(self):
        return {'width': self.width, 'height': self.height, 'clients': self.clients, 'cluster_size_min': self.cluster_size_min, 'cluster_size_max': self.cluster_size_max}


def hash_client_list(hcl):
    # results of hashing the client list like this may not be unique but sufficient
    total_hash = 0
    for bc in hcl:
        total_hash += hash(bc)

    return total_hash


def load_clients_file():
    unpickled = None

    try:
        fh = open(FILES['pickled_clients'], 'rb')
    except IOError:
        return None
    else:
        unpickled = pickle.load(fh)
        fh.close()
        print('loaded clients from file: \'%s\'' % FILES['pickled_clients'])
        saved_settings = unpickled.settings_dict()
        if saved_settings != SETTINGS:
            print(saved_settings)
            print("\nOOOPS! saved settings differ from config file\n")
            exit(1)
        if unpickled.version != INFO['version']:
            print("\nOOOPS! saved clients version: %s != %s config file version\n" % (unpickled.version, INFO['version']))
            exit(1)

        return unpickled.clients_list


def save_clients_file(clients_list):
    with open(FILES['pickled_clients'], 'wb') as fh:
        tpb = TourPlannerBase(**SETTINGS)
        tpb.version = INFO['version']
        tpb.clients_list = clients_list

        pickle.dump(tpb, fh)

    print('saved clients to file: \'%s\'' % FILES['pickled_clients'])
