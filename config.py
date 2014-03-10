INFO = {
    'version': '0.9.2',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


SETTINGS = {
    'clients': 120,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 1200,
    'height': 700,
}


DIMENSION = [
{
    'x_factor': 0.2,
    'y_factor': 0.2,
},
]

DISPLAY = {
    'intro': False,
    'clients_intro': True,
    'dimensions': True,
    'dimensions_slow': True,
    'unite_areas': True,
    'routing': {
        'all': False,
        'best_starter': True,
    },
    'clients': {
        'init': False,
        'append': True,
    },
}

TEST = {
    'long_term': False,
    'level': 1,
}
