INFO = {
    'version': '0.9.2',
    'usage': 'use <ESC> to quit and <SPACE> to pause and continue',
}


SETTINGS = {
    'clients': 1000,
    'cluster_size_min': 5,
    'cluster_size_max': 7,
    'width': 1500,
    'height': 1000,
}


DIMENSION = [
{
    'x_factor': 0.05,
    'y_factor': 0.05,
},
]

DISPLAY = {
    'clients_intro': False,
    'dimensions': True,
    'dimensions_slow': False,
    'unite_areas': False,
    'routing': {
        'all': False,
        'best_starter': False,
    },
    'clients': {
        'init': False,
        'append':False,
    },
}

TEST = {
    'long_term': False,
    'level': 1,
}
