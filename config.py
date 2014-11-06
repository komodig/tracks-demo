from random import randrange

INFO = {
    'version': '1.2.0',
    'usage': 'use <ESC> to quit and <SPACE> to pause',
}


FILES = {
    'pickled_clients': 'clients.bin',
}


SETTINGS = {
    'clients': 300,
    'cluster_size_min': 4,
    'cluster_size_max': 7,
    'width': 1024,
    'height': 768,
}


OPTIMIZE = {
    'shrink_areas': True,
    'merge_areas': True,
    'push_clients': True,
    'steal_clients': True,
}


DISPLAY = {
    'intro': True,
    'clients_intro': False,
    'areas': {
        'init': False,
        'add_info': True,
        'slow': False,
        'merge': False,
        'client_push': False,
        'client_steal': False,
        'unite_info': False,
        'show_final': False,  # inaccurate when final merged area is not a rectangle
    },
    'routing': {
        'all': False,
        'slow': 0,
        'best_starter': False,
    },
    'clients': {
        'init': False,
    },
    'color': {
        'spot': (randrange(0,255), randrange(0,255), randrange(0,255)),
        'line': (randrange(0,255), randrange(0,255), randrange(0,255)),
    },
    'color1': {
        'spot': (41, 110, 127),
        'line': (255, 30, 255),
    },
    'color2': {
        'spot': (100, 60, 127),
        'line': (70, 192, 248),
    },
    'color3': {
        'spot': (202, 102, 123),
        'line': (89, 28, 160),
    },
    'blau-violett': {
        'spot': (15, 101, 89),
        'line': (178, 36, 199),
    },
    'gruen-violett': {
        'spot': (43, 131, 50),
        'line': (157, 14, 227),
    },
    'violett-rot': {
        'spot': (55, 64, 206),
        'line': (183, 30, 41),
    },
}


TEST = {
    'long_term': False,
    'level': 0,
}
