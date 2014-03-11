from random import randrange

INFO = {
    'version': '1.0.1',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


SETTINGS = {
    'clients': 60,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 1200,
    'height': 700,
}


DIMENSION = [
{
    'x_factor': 0.25,
    'y_factor': 0.25,
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
        'best_starter': True,
    },
    'clients': {
        'init': False,
        'append': True,
    },
    'color': {
        'spot': (randrange(0,255), randrange(0,255), randrange(0,255)),
        'line': (randrange(0,255), randrange(0,255), randrange(0,255)),
    },
}

TEST = {
    'long_term': False,
    'level': 0,
}
