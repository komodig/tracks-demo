import pickle
from config import FILES


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
        return unpickled


def save_clients_file(clients_list):
    with open(FILES['pickled_clients'], 'wb') as fh:
        pickle.dump(clients_list, fh)

    print('saved clients to file: \'%s\'' % FILES['pickled_clients'])
