from framework.graph_search import *
from framework.ways import *
from .deliveries_problem_input import DeliveriesProblemInput

from typing import Set, FrozenSet, Iterator, Tuple, Union


class RelaxedDeliveriesState(GraphProblemState):
    """
    An instance of this class represents a state of the relaxed
     deliveries problem.
    Notice that our state has "real number" field, which makes our
     states space infinite.
    """

    def __init__(self, current_location: Junction,
                 dropped_so_far: Union[Set[Junction], FrozenSet[Junction]],
                 fuel: float):
        self.current_location: Junction = current_location
        self.dropped_so_far: FrozenSet[Junction] = frozenset(dropped_so_far)
        self.fuel: float = fuel
        assert fuel > 0

    @property
    def fuel_as_int(self):
        """
        Sometimes we have to compare 2 given states. However, our state
         has a float field (fuel).
        As we know, floats comparison is an unreliable operation.
        Hence, we would like to "cluster" states within some fuel range,
         so that 2 states in the same fuel range would be counted as equal.
        """
        return int(self.fuel * 1000000)

    def __eq__(self, other):
        """
        This method is used to determine whether two given state objects represents the same state.
        Notice: Never compare floats using `==` operator! Use `fuel_as_int` instead of `fuel`.
        """
        if(self.fuel_as_int == other.fuel_as_int) and\
                (self.current_location==other.current_location)\
            and (self.dropped_so_far <= other.dropped_so_far)\
                and (self.dropped_so_far >= other.dropped_so_far):
            return True
        else:
            return False

    def __hash__(self):
        """
        This method is used to create a hash of a state.
        It is critical that two objects representing the same state would have the same hash!
        A common implementation might be something in the format of:
        >>>          return hash((self., self.some_field2, self.some_field3))

        Notice: Do NOT give float fields to `hash(...)`.
                Otherwise the upper requirement would not met.
                In our case, use `fuel_as_int`.
        """
        return hash((self.current_location.index, self.dropped_so_far, self.fuel_as_int))

    def __str__(self):
        """
        Used by the printing mechanism of `SearchResult`.
        """
        return str(self.current_location.index)


class RelaxedDeliveriesProblem(GraphProblem):
    """
    An instance of this class represents a relaxed deliveries problem.
    """

    name = 'RelaxedDeliveries'

    def __init__(self, problem_input: DeliveriesProblemInput):
        self.name += '({})'.format(problem_input.input_name)
        assert problem_input.start_point not in problem_input.drop_points
        initial_state = RelaxedDeliveriesState(
            problem_input.start_point, frozenset(), problem_input.gas_tank_init_fuel)
        super(RelaxedDeliveriesProblem, self).__init__(initial_state)
        self.start_point = problem_input.start_point
        self.drop_points = frozenset(problem_input.drop_points)
        self.gas_stations = frozenset(problem_input.gas_stations)
        self.gas_tank_capacity = problem_input.gas_tank_capacity
        self.possible_stop_points = self.drop_points | self.gas_stations

    def expand_state_with_costs(self, state_to_expand: GraphProblemState) -> Iterator[Tuple[GraphProblemState, float]]:
        """
        This method represents the `Succ: S -> P(S)` function of the relaxed deliveries problem.
        The `Succ` function is defined by the problem operators as shown in class.
        The relaxed problem operators are defined in the assignment instructions.
        It receives a state and iterates over the successor states.
        Notice that this is an *Iterator*. Hence it should be implemented using the `yield` keyword.
        For each successor, a pair of the successor state and the operator cost is yielded.
        """
        assert isinstance(state_to_expand, RelaxedDeliveriesState)
        # print('state_to_expand links: ', self.drop_points-state_to_expand.dropped_so_far)
        for junction in self.possible_stop_points - state_to_expand.dropped_so_far:
            #print('cur location:', state_to_expand.current_location.index, ' succ junction index: ', junction.index)
            distance = junction.calc_air_distance_from(state_to_expand.current_location)
            if distance <= state_to_expand.fuel:
                succ_dropped_so_far = set()
                succ_dropped_so_far = succ_dropped_so_far.union(state_to_expand.dropped_so_far)
                succ_dropped_so_far.add(junction)
                successor = RelaxedDeliveriesState(junction, succ_dropped_so_far, state_to_expand.fuel-distance)
                yield [successor, distance]
        for junction in self.gas_stations:
            # print('cur location:', state_to_expand.current_location.index, ' succ junction index: ', junction.index)
            distance = junction.calc_air_distance_from(state_to_expand.current_location)
            if distance <= state_to_expand.fuel:
                successor = RelaxedDeliveriesState(junction, state_to_expand.dropped_so_far, self.gas_tank_capacity)
                yield [successor, distance]


    def is_goal(self, state: GraphProblemState) -> bool:
        """
        This method receives a state and returns whether this state is a goal.
        """
        assert isinstance(state, RelaxedDeliveriesState)
        return state.dropped_so_far <= self.drop_points <= state.dropped_so_far

    def solution_additional_str(self, result: 'SearchResult') -> str:
        """This method is used to enhance the printing method of a found solution."""
        return 'gas-stations: [' + (', '.join(
            str(state) for state in result.make_path() if state.current_location in self.gas_stations)) + ']'
