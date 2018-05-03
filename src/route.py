from collections import namedtuple
from type_hints import Numeric, Iterable
from decimal import Decimal

from structures.sortedlist import insort
from roadmap import Road, MapPoint


RoutePoint = namedtuple('RoutePoint', ('map_point', 'number',))
Route = namedtuple('Route', (
    'route_points',  # Iterable[RoutePoints]
    'route_fuel_pool',  # RouteFuelPool
    'points_to_across',  # Iterable[MapPoint]
    'end',  # MapPoint
    'cost',  # Numeric
    'length',  # int
))


class ImpossibleMove(Exception):
    pass


class NoAvailableRoutes(Exception):
    pass


class NoCompletedRoutes(Exception):
    pass


class RoutePool:
    """
    Sorted pool of routes

    Store:
        * routes available to completing
        * completed|finished routes
        * closed routes ("bad" or dead-end)
    """

    def __init__(self):
        self.available_list = list()
        self.completed_list = list()
        self.closed_list = list()

    def __append(self, list_name, route: Route):
        insort(getattr(self, list_name),
               route,
               key=RoutePool.order_key)

    def __getlast(self, list_name, pop: bool, exc: Exception):
        l = getattr(self, list_name)
        if not l:
            raise exc
        return l.pop() if pop else l[len(l) - 1]

    def append_available(self, route):
        self.__append('available_list', route)

    def append_completed(self, route):
        self.__append('completed_list', route)

    # TODO add routes and use for non-duplicating optimization
    def append_closed(self, route):
        self.__append('closed_list', route)

    def get_available(self, pop: bool):
        return self.__getlast(
            'available_list', pop=pop, exc=NoAvailableRoutes)

    def get_completed(self, pop: bool):
        return self.__getlast(
            'completed_list', pop=pop, exc=NoCompletedRoutes)

    @staticmethod
    def order_key(route):
        return -route.route_fuel_pool.cost


class RouteManager:
    """
    Route manager
    Working with all routes (available|completed|closed)
    """

    def __init__(
            self,
            to_point: MapPoint,
            across_points: Iterable[MapPoint],
            fuel_capacity: Numeric,
            mpg: Numeric,
    ):
        self.to_point = to_point
        self.across_points = set(across_points)
        self.rfm = RouteFuelManager(fuel_capacity)
        self.route_pool = RoutePool()
        self.mpg = mpg

    def start(
            self,
            start_map_point: MapPoint,
            start_fuel_vol: Numeric,
    ) -> None:
        """
        Initialize Route on start point
        """
        start_route_point = RoutePoint(map_point=start_map_point, number=1)
        start_route_fuel_pool = self.rfm.start(
            start_route_point=start_route_point,
            start_fuel_vol=start_fuel_vol,
        )
        start_route = Route(
            route_points=(start_route_point,),
            route_fuel_pool=start_route_fuel_pool,
            points_to_across=self.across_points,
            end=start_map_point,
            cost=start_route_fuel_pool.cost,
            length=1
        )
        self.route_pool.append_available(start_route)

    def pop_available(self) -> Route:
        """ pop available route with minimal cost """
        return self.route_pool.get_available(pop=True)

    def get_completed(self) -> Route:
        """ get completed route with minimal cost """
        return self.route_pool.get_completed(pop=False)

    def move(
            self,
            previous_route: Route,
            road: Road,
    ) -> None:
        """
        Generate new Route after moving

        Logic:

        :raises RouteManager.ImpossibleMove
        """
        next_map_point = road.point_to
        next_route_point = RoutePoint(
            map_point=next_map_point,
            number=previous_route.length + 1)
        next_route_fuel_pool = self.rfm.move(
            previous_pool=previous_route.route_fuel_pool,
            used_volume=Decimal(road.length/self.mpg),
            new_route_point=next_route_point,
        )
        if next_map_point in previous_route.points_to_across:
            points_to_across = previous_route.points_to_across.copy()
            points_to_across.remove(next_map_point)
        else:
            points_to_across = previous_route.points_to_across
        new_route = Route(
            route_points=previous_route.route_points + (next_route_point,),
            route_fuel_pool=next_route_fuel_pool,
            points_to_across=points_to_across,
            end=next_map_point,
            cost=next_route_fuel_pool.cost,
            length=previous_route.length + 1
        )
        # if route completed:
        # * if all across-points visited
        # * and if we are at finish
        if not points_to_across and self.to_point == next_map_point:
            self.route_pool.append_completed(
                self.prepare_solution(new_route))
        else:
            completed_route = None
            try:
                completed_route = self.get_completed()
            except NoCompletedRoutes:
                pass
            if (  # if we have completed route with lowest cost - don't move
                completed_route and
                completed_route.cost <= next_route_fuel_pool.cost
            ):
                return
            self.route_pool.append_available(new_route)

    @staticmethod
    def prepare_solution(route) -> Route:
        """ get completed route with minimal cost """
        return Route(
            route_points=route.route_points,
            route_fuel_pool=RouteFuelManager.make_clear_refuels_pool(
                route.route_fuel_pool),
            points_to_across=route.points_to_across,
            end=route.end,
            cost=route.cost,
            length=route.length,
        )


"""
Route refuel possibility
"""
RouteFuelPossibility = namedtuple('RouteFuelPossibility', (
    'route_point',  # RoutePoint
    'possible_vol',  # Numeric
    'used_vol',  # Numeric
))


"""
Route refuel aggregated fact
"""
RouteRefuel = namedtuple('RouteRefuel', (
    'route_point',  # RoutePoint
    'volume',  # Numeric
))


"""
Pool of available Fuel-points on route
and already completed refuels
and full cost of refuels of route
"""
RouteFuelPool = namedtuple('RouteFuelPool', (
    'existing_fuel_vol',  # Numeric
    'rfp_queue',  # Iterable[RouteFuelPossibility]
    'refuel_list',  # Iterable[RouteRefuel]
    'cost',  # Numeric
))


class RouteFuelManager:
    """
    Fuel manager
    Solve problem with storage and choice GasStation|RoutePoint to re-fuel
    Choose from ALREADY visited RoutePoints
    """

    def __init__(self, fuel_capacity: Numeric):
        self.fuel_capacity = fuel_capacity

    def start(
            self,
            start_route_point: RoutePoint,
            start_fuel_vol: Numeric,
    ) -> RouteFuelPool:
        """
        Start route method.
        Initialize RouteFuelPool on start point
        """
        return RouteFuelPool(
            existing_fuel_vol=start_fuel_vol,
            rfp_queue=(
                RouteFuelPossibility(
                    route_point=start_route_point,
                    possible_vol=self.fuel_capacity - start_fuel_vol,
                    used_vol=0
                ),
            ),
            refuel_list=(),
            cost=0,
        )

    @staticmethod
    def make_clear_refuels_pool(
            pool: RouteFuelPool,
    ) -> RouteFuelPool:
        """
        Make pool with only refuels, without refuel-stack
        """
        refuels = [
            RouteRefuel(route_point=rfp.route_point, volume=rfp.used_vol)
            for rfp in pool.rfp_queue]
        refuels += list(pool.refuel_list)
        return RouteFuelPool(
            existing_fuel_vol=pool.existing_fuel_vol,
            rfp_queue=(),
            refuel_list=sorted(refuels, key=lambda x: x.route_point.number),
            cost=pool.cost,
        )

    def move(
            self,
            previous_pool: RouteFuelPool,
            used_volume: Numeric,
            new_route_point: RoutePoint
    ) -> RouteFuelPool:
        """
        Generate new RouteFuelPool after moving

        Logic:
        * use existing (pre-fueled fuel) if exist
        * for all previous GasStations, where we can yet refuel and
          sorted by price:
           * "pick up" already refueled (from others gas stations) volume
           * "pick up" all needed fuel from gas station
           * if gas station is useful yet - save to next using,
             else - save to "log"
        * if NOT all needed fuel "picked up" - raise exception
          RouteFuelManager.ImpossibleMove
        * if in new RoutePoint we have new gas station add them in pool
        * generate and return new RouteFuelPool

        :raises RouteFuelManager.ImpossibleMove
        """
        cost = previous_pool.cost
        existing_fuel_vol = max(
            previous_pool.existing_fuel_vol - used_volume, 0)
        volume_to_refuel = max(
            used_volume - previous_pool.existing_fuel_vol, 0)

        rfp_queue = []
        refuel_list = list(previous_pool.refuel_list)
        already_refueled_volume = 0

        # do refuel
        for rfp in previous_pool.rfp_queue:
            possible_vol = max(
                rfp.possible_vol - already_refueled_volume, 0)
            refueled_vol = min(possible_vol, volume_to_refuel)
            possible_vol = possible_vol - refueled_vol
            volume_to_refuel = volume_to_refuel - refueled_vol
            already_refueled_volume += refueled_vol
            used_vol = rfp.used_vol + refueled_vol
            cost += rfp.route_point.map_point.gas_station.price * refueled_vol
            # if RouteFuelPossibility is useful yet
            if possible_vol:
                rfp_queue.append(
                    RouteFuelPossibility(
                        route_point=rfp.route_point,
                        possible_vol=possible_vol,
                        used_vol=used_vol,
                    )
                )
            else:
                # if "useless" - keep aggregated refuel fact in the storage
                refuel_list.append(
                    RouteRefuel(
                        route_point=rfp.route_point,
                        volume=used_volume,
                    )
                )

        if volume_to_refuel != 0:
            raise ImpossibleMove

        if new_route_point.map_point.gas_station:
            insort(
                rfp_queue,
                RouteFuelPossibility(
                    route_point=new_route_point,
                    possible_vol=self.fuel_capacity - existing_fuel_vol,
                    used_vol=0,
                ),
                key=lambda x: x.route_point.map_point.gas_station.price
            )

        return RouteFuelPool(
            existing_fuel_vol=existing_fuel_vol,
            rfp_queue=rfp_queue,
            refuel_list=refuel_list,
            cost=cost
        )
