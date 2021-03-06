from framework.graph_search import *
from .relaxed_deliveries_problem import RelaxedDeliveriesState, RelaxedDeliveriesProblem
from .strict_deliveries_problem import StrictDeliveriesState, StrictDeliveriesProblem
from .deliveries_problem_input import DeliveriesProblemInput
from framework.ways import *

import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree as mst
from typing import Set, Dict, FrozenSet


class MaxAirDistHeuristic(HeuristicFunction):
    heuristic_name = 'MaxAirDist'

    def estimate(self, state: GraphProblemState) -> float:
        """
        Calculates the maximum among air distances between the location
         represented by `state` and the locations of the waiting deliveries.
        """
        assert isinstance(self.problem, RelaxedDeliveriesProblem)
        assert isinstance(state, RelaxedDeliveriesState)
        if self.problem.is_goal(state):
            return 0
        max_dist=0
        drop_points_left = self.problem.drop_points.difference(state.dropped_so_far)
        for destination in drop_points_left:
            if destination.calc_air_distance_from(state.current_location)> max_dist:
                max_dist=destination.calc_air_distance_from(state.current_location)
        return max_dist


class MSTAirDistHeuristic(HeuristicFunction):
    heuristic_name = 'MSTAirDist'

    def __init__(self, problem: GraphProblem):
        super(MSTAirDistHeuristic, self).__init__(problem)
        assert isinstance(self.problem, RelaxedDeliveriesProblem)
        self._junctions_distances_cache: Dict[FrozenSet[Junction], float] = dict()

    def estimate(self, state: GraphProblemState) -> float:
        assert isinstance(self.problem, RelaxedDeliveriesProblem)
        assert isinstance(state, RelaxedDeliveriesState)

        remained_drop_points = set(self.problem.drop_points - state.dropped_so_far)
        remained_drop_points.add(state.current_location)
        return self._calculate_junctions_air_dist_mst_weight(remained_drop_points)

    def _get_distance_between_junctions(self, junction1: Junction, junction2: Junction):
        junctions_pair = frozenset({junction1, junction2})
        if junctions_pair in self._junctions_distances_cache:
            return self._junctions_distances_cache[junctions_pair]
        dist = junction1.calc_air_distance_from(junction2)
        self._junctions_distances_cache[junctions_pair] = dist
        return dist

    def _calculate_junctions_air_dist_mst_weight(self, junctions: Set[Junction]) -> float:
        nr_junctions = len(junctions)
        idx_to_junction = {idx: junction for idx, junction in enumerate(junctions)}
        distances_matrix = np.zeros((nr_junctions, nr_junctions), dtype=np.float)
        for j1_idx in range(nr_junctions):
            for j2_idx in range(nr_junctions):
                if j1_idx == j2_idx:
                    continue
                dist = self._get_distance_between_junctions(idx_to_junction[j1_idx], idx_to_junction[j2_idx])
                distances_matrix[j1_idx, j2_idx] = dist
                distances_matrix[j2_idx, j1_idx] = dist
        return mst(distances_matrix).sum()


class RelaxedDeliveriesHeuristic(HeuristicFunction):
    heuristic_name = 'RelaxedProb'

    def estimate(self, state: GraphProblemState) -> float:
        """
        Solve the appropriate relaxed problem in order to
         evaluate the distance to the goal.
        TODO: implement this method!
        """

        assert isinstance(self.problem, StrictDeliveriesProblem)
        assert isinstance(state, StrictDeliveriesState)
        if self.problem.is_goal(state):
            return 0
        sub_prob_drop_pnts = set()
        sub_prob_drop_pnts = sub_prob_drop_pnts.union(self.problem.drop_points-state.dropped_so_far)-{state.current_location}
        #sub_prob_drop_pnts -= state.dropped_so_far
        reduced_in = DeliveriesProblemInput('relaxed_reduced',state.current_location,
                                            sub_prob_drop_pnts.copy(),
                                            self.problem.gas_stations, self.problem.gas_tank_capacity, state.fuel)
        relaxed_problem = RelaxedDeliveriesProblem(reduced_in)
        # print('solving inner problem for init junction: ', state.current_location.index, 'dropping points:')
        # for junction in relaxed_problem.drop_points:
        #     print(junction.index)
        # print('dropped so far:')
        # for junction in state.dropped_so_far:
        #     print(junction.index)
        # print('fuel: ', state.fuel)
        assert relaxed_problem.initial_state is not None
        assert relaxed_problem.initial_state.current_location == state.current_location
        astar_Mst = AStar(MSTAirDistHeuristic)
        res = astar_Mst.solve_problem(relaxed_problem)
        if res.final_search_node is None:
            return np.inf
        else:
            return res.final_search_node.cost
