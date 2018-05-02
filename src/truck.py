from collections import namedtuple


Truck = namedtuple('Truck', ('capacity', 'min_volume', 'mpg',))

TruckState = namedtuple('TruckState', ('truck', 'volume',))
