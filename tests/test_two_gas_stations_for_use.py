from decimal import Decimal

from roadmap import Road, RoadMap, GasStation, MapPoint
from route import RoutePoint, RouteRefuel
from truck import Truck, TruckState
from pathfinder import find_path


def test_graph_from_example():
    roadmap = RoadMap()

    MP1 = MapPoint(name='1', gas_station=GasStation(price=Decimal('3.17')))
    MP2 = MapPoint(name='2', gas_station=GasStation(price=Decimal('2.6')))
    MP3 = MapPoint(name='3', gas_station=None)
    MP4 = MapPoint(name='4', gas_station=None)
    MP5 = MapPoint(name='5', gas_station=None)

    roadmap.add_edge(MP1, MP2, Road(Decimal(10), point_from=MP1, point_to=MP2))
    roadmap.add_edge(MP1, MP5, Road(Decimal(100), point_from=MP1, point_to=MP5))
    roadmap.add_edge(MP1, MP4, Road(Decimal(30), point_from=MP1, point_to=MP4))
    roadmap.add_edge(MP2, MP3, Road(Decimal(50), point_from=MP2, point_to=MP3))
    roadmap.add_edge(MP4, MP3, Road(Decimal(20), point_from=MP4, point_to=MP3))
    roadmap.add_edge(MP4, MP5, Road(Decimal(60), point_from=MP4, point_to=MP5))
    roadmap.add_edge(MP3, MP5, Road(Decimal(10), point_from=MP3, point_to=MP5))

    truck = Truck(
        capacity=Decimal(500),
        min_volume=Decimal(40),
        mpg=Decimal(24)
    )

    vol0 = Decimal(40)

    expected_cost = (
        Decimal(10)/Decimal(24) * Decimal('3.17') +
        Decimal(50)/Decimal(24) * Decimal('2.6') +
        Decimal(10)/Decimal(24) * Decimal('2.6')
    )

    route = find_path(
        roadmap=roadmap,
        from_point=MP1,
        to_point=MP5,
        across_points=(),
        truckstate=TruckState(truck=truck, volume=vol0),
    )
    assert route.route_points == (
        RoutePoint(MP1, 1),
        RoutePoint(MP2, 2),
        RoutePoint(MP3, 3),
        RoutePoint(MP5, 4),
    )
    assert route.cost == expected_cost
    assert route.route_fuel_pool.refuel_list == [
        RouteRefuel(RoutePoint(MP1, 1), Decimal(10)/Decimal(24)),
        RouteRefuel(RoutePoint(MP2, 2),
                    Decimal(50)/Decimal(24) + Decimal(10)/Decimal(24)),
    ]


if __name__ == '__main__':
    test_graph_from_example()
