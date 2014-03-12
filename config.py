from random import randrange

INFO = {
    'version': '1.0.1',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


SETTINGS = {
    'clients': 100,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 1600,
    'height': 1000,
}


DIMENSION = [
{
    'x_factor': 0.2,
    'y_factor': 0.2,
},
]

DISPLAY = {
    'intro': True,
    'clients_intro': False,
    'dimensions': True,
    'dimensions_slow': True,
    'unite_areas': True,
    'routing': {
        'all': False,
        'slow': 0,
        'best_starter': False,
    },
    'clients': {
        'init': False,
        'append': True,
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
