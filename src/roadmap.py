from collections import namedtuple

from structures.graph import UniDirectionalGraph


GasStation = namedtuple('GasStation', (
    'price',  # Numeric
))
MapPoint = namedtuple('MapPoint', (
    'name',  # Any
    'gas_station',  # GasStation
))
Road = namedtuple('Road', (
    'length',  # Numeric
    'point_from',  # MapPoint
    'point_to',  # MapPoint
))


class RoadMap(UniDirectionalGraph):
    pass
