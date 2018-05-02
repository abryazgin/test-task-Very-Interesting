from type_hints import Iterable
from roadmap import RoadMap
from route import (
    RouteManager, MapPoint, ImpossibleMove, NoAvailableRoutes,
    NoCompletedRoutes
)
from truck import TruckState


class NoSolution(Exception):
    pass


def find_path(
        roadmap: RoadMap,
        from_point: MapPoint,
        to_point: MapPoint,
        across_points: Iterable(MapPoint),
        truckstate: TruckState,
):
    """
    Find minimal-cost-path on map `roadmap` from `from_point` to `to_point`
    for truck with state `truckstate` over sub-points `across_points`

    Logic:
    * prepare Route Manager with initial route
    * while exist available routes to development - develop them
    * when available routes ends - get low-cost-route from completed

    :raises NoSolution
    """
    manager = RouteManager(
        to_point=to_point,
        across_points=across_points,
        fuel_capacity=truckstate.truck.capacity,
        mpg=truckstate.truck.mpg,
    )
    manager.start(
        start_map_point=from_point,
        start_fuel_vol=truckstate.volume - truckstate.truck.min_volume
    )

    try:
        while True:
            route = manager.pop_available()
            for mp, road in roadmap.iter_neighbors(route.end):
                try:
                    manager.move(previous_route=route, road=road)
                except ImpossibleMove:
                    print('We no have fuel to `{0}` in route `{1}`'.format(
                        mp, route))
    except NoAvailableRoutes:
        print('Searching end!')

    try:
        return manager.get_completed()
    except NoCompletedRoutes:
        raise NoSolution
