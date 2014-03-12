from random import randrange

INFO = {
    'version': '1.0.1',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


SETTINGS = {
    'clients': 20,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 800,
    'height': 500,
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
    'areas': {
        'init': True,
        'slow': True,
        'unite_info': True,
        'final_areas': True,
    },
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
