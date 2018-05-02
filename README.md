# Test task for ["Very Interesting" or "Saritasa"](http://www.interesnee.ru/)

## Task

Suggest a driver how to deliver the goods to the destination having the lowest expense.


A company has a delivery truck that may pick up loads from different customers along the route, which is always uni-directional graph (i.e. movement happens only in one direction):

* A truck has a fuel tank equal to 500 Gallons.
* A truck may re-fuel only at specific gas stations, having different gas prices, for example
spot 1 has price $3/Gallon, whole spot 3 has a price of $3.17/Gallon

Your solution should tell the driver to which gas station to go along the route and how much fuel to buy in order to deliver goods to the final destination at the lowest expense possible. We don't care if it's the longest route, as soon as we have the lowest expense. 

Few additional constraints:
* Truck always starts with 40 gallons at the start point
* Start point always has a fuel station where they can add additional fuel if needed. 
* During the trip, they may need to load additional goods at spots where no gas stations are located which they mandatory should visit and can't skip. For example, a driver may go to spot 4 to load up an additional load.
* A driver should arrive at any gas station with at least 40 gallons in the tank to avoid the risk of stopping in the middle of nowhere
* MPG (miles per gallon) of the truck is 24 Miles per gallon.
* Elevation (increase or decrease) should not be considered in the equation
* Traffic conditions are not considered (i.e. that MPG lowers with big traffic)

You can use any python version and any functionality offered by STD lib of python. 
No use of PyPi libs is allowed. 


## Solution
* used Python 3.5 
* initial mountpoint - `src/pathfinder.py` method `find_path`
* used Dijkstra algorithm to search accepted routes
* used minimal-cost-route choosing for algorithm
* used "last fuel stack" to realize logic with low-cost-fuel 
    (see `src.route.RouteFuelManager`)
* examples in `tests/test_*`

PS:
* used pytest for testing, no for solution
* TODO test with big data
* TODO Dijkstra -> A* for constant use solution: 
** pre-calculatee minimal distance between points
** use minimal-distance for imperial-function in A*
* TODO optimize/non-duplicate routes: if route "bad" 
(has greatest cost, no have more visited across-points and no have better 
fuel-pool) - close him
* TODO refactor ordered-lists to sorted-trees
* TODO refactor answer object (Route)
* TODO refactor modules - `src/route.py` -> `src/route.py` & `src/fuel.py` (`manager.py` ?)
