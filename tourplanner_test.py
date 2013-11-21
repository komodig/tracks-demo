import client 
import config

def edge_test_clients(all_clients):
    all_clients.clients[0].x = 0
    all_clients.clients[1].x = config.SETTINGS['width']
    all_clients.clients[2].y = 0
    all_clients.clients[3].y = config.SETTINGS['height']
    print all_clients.clients[0:4]


def length_test_client_generator():
    clients = []
    y = 10
    for x in range(1, 10):
        clients.append(client.Client(x*20, y))
    y = 30
    for x in range(1, 10):
        clients.append(client.Client(x*20, y))

    clients.append(client.Client(300, 10))
    clients.append(client.Client(310, 10))
    clients.append(client.Client(320, 10))
    clients.append(client.Client(400, 10))
    clients.append(client.Client(450, 10))
    for it in clients:
        print it 
    return clients


