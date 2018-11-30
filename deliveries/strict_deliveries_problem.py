from framework.graph_search import *
from framework.ways import *
from .map_problem import MapProblem
from .deliveries_problem_input import DeliveriesProblemInput
from .relaxed_deliveries_problem import RelaxedDeliveriesState, RelaxedDeliveriesProblem

from typing import Set, FrozenSet, Optional, Iterator, Tuple, Union


class StrictDeliveriesState(RelaxedDeliveriesState):
    """
    An instance of this class represents a state of the strict
     deliveries problem.
    This state is basically similar to the state of the relaxed
     problem. Hence, this class inherits from `RelaxedDeliveriesState`.

    TODO:
        If you believe you need to modify the state for the strict
         problem in some sense, please go ahead and do so.
    """
    pass


class StrictDeliveriesProblem(RelaxedDeliveriesProblem):
    """
    An instance of this class represents a strict deliveries problem.
    """

    name = 'StrictDeliveries'

    def __init__(self, problem_input: DeliveriesProblemInput, roads: Roads,
                 inner_problem_solver: GraphProblemSolver, use_cache: bool = True):
        super(StrictDeliveriesProblem, self).__init__(problem_input)
        self.initial_state = StrictDeliveriesState(
            problem_input.start_point, frozenset(), problem_input.gas_tank_init_fuel)
        self.inner_problem_solver = inner_problem_solver
        self.roads = roads
        self.use_cache = use_cache
        self._init_cache()

    def _init_cache(self):
        self._cache = {}
        self.nr_cache_hits = 0
        self.nr_cache_misses = 0

    def _insert_to_cache(self, key, val):
        if self.use_cache:
            self._cache[key] = val

    def _get_from_cache(self, key):
        if not self.use_cache:
            return None
        if key in self._cache:
            self.nr_cache_hits += 1
        else:
            self.nr_cache_misses += 1
        return self._cache.get(key)

    def expand_state_with_costs(self, state_to_expand: GraphProblemState) -> Iterator[Tuple[GraphProblemState, float]]:
        """
        This method represents the `Succ: S -> P(S)` function of the strict deliveries problem.
        The `Succ` function is defined by the problem operators as shown in class.
        The relaxed problem operators are defined in the assignment instructions.
        It receives a state and iterates over the successor states.
        Notice that this is an *Iterator*. Hence it should be implemented using the `yield` keyword.
        For each successor, a pair of the successor state and the operator cost is yielded.
        """
        assert isinstance(state_to_expand, StrictDeliveriesState)
        # print("cur location ", state_to_expand.current_location)
        # print("drop so far")
        # for item in state_to_expand.dropped_so_far:
        #     print(item.index)
        # if not (state_to_expand.dropped_so_far < self.drop_points):
        #     print("drop points")
        #     for item in self.drop_points:
        #         print(item.index)
        #     print("dif",-self.drop_points)
        #     exit(1)
        for drop_point in self.possible_stop_points-state_to_expand.dropped_so_far:
            # assert drop_point not in state_to_expand.dropped_so_far
            cost = self._get_from_cache(hash((state_to_expand.current_location.index, drop_point.index)))
            if cost is None:
                map_prob = MapProblem(self.roads, state_to_expand.current_location.index, drop_point.index)
                map_res = self.inner_problem_solver.solve_problem(map_prob)
                cost = map_res.final_search_node.cost
                self._insert_to_cache(hash((state_to_expand.current_location.index, drop_point.index)), cost)
            assert cost is not None
            if cost < state_to_expand.fuel:
                succ_dropped_so_far = set()
                succ_dropped_so_far = succ_dropped_so_far.union(state_to_expand.dropped_so_far)
                if drop_point in self.drop_points:
                    succ_dropped_so_far.add(drop_point)
                    succ_state = StrictDeliveriesState(drop_point, succ_dropped_so_far, state_to_expand.fuel - cost)
                    yield [succ_state, cost]
                if drop_point in self.gas_stations:
                    succ_state = StrictDeliveriesState(drop_point, succ_dropped_so_far, self.gas_tank_capacity)
                    yield [succ_state, cost]

    def is_goal(self, state: GraphProblemState) -> bool:
        """
        This method receives a state and returns whether this state is a goal.
        """
        assert isinstance(state, StrictDeliveriesState)
        return state.dropped_so_far == self.drop_points
