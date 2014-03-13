from random import randrange

INFO = {
    'version': '1.0.5',
    'usage': 'use <ESC> to quit and <SPACE> to pause',
}


SETTINGS = {
    'clients': 300,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 1200,
    'height': 700,
}


DIMENSION = [
{
    'x_factor': 0.1,
    'y_factor': 0.1,
},
]

DISPLAY = {
    'intro': True,
    'clients_intro': False,
    'areas': {
        'init': True,
        'add_info': True,
        'slow': False,
        'merge': True,
        'unite_info': False,
        'show_final': False,
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
}

TEST = {
    'long_term': False,
    'level': 1,
}
