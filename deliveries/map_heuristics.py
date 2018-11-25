from framework.graph_search import *
from .map_problem import MapProblem, MapState


class AirDistHeuristic(HeuristicFunction):
    heuristic_name = 'AirDist'

    def estimate(self, state: GraphProblemState) -> float:
        """
        The air distance between the geographic location represented
         by `state` and the geographic location of the problem's target.

        Use `self.problem` to access the problem.
        Use `self.problem.roads` to access the map.
        Given a junction index, use `roads[junction_id]` to find the
         junction instance (of type Junction).
        Use the method `calc_air_distance_from()` to calculate the
        air distance between two junctions.
        """
        assert isinstance(self.problem, MapProblem)
        assert isinstance(state, MapState)
        if self.problem.target_junction_id== state.junction_id:
            return 0
        else:
            return self.problem.roads[state.junction_id].\
                        calc_air_distance_from(self.problem.roads[self.problem.target_junction_id])



        """
        
        for multiple targets
        estimation = 0
        valid = False
        for id,junction in self.problem.roads.items():
            if self.problem.target_junction_id== id:
                if valid==False or estimation > self.problem.road[state.junction_id].\
                        calc_air_distance_from(junction):
                    estimation=self.problem.road[state.junction_id].\
                        calc_air_distance_from(junction)
                    valid= True
        assert valid == True
        return estimation
        """

