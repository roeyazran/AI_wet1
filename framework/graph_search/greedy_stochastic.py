from .graph_problem_interface import *
from .best_first_search import BestFirstSearch
from typing import Optional
import numpy as np


class GreedyStochastic(BestFirstSearch):
    def __init__(self, heuristic_function_type: HeuristicFunctionType,
                 T_init: float = 1.0, N: int = 5, T_scale_factor: float = 0.95):
        # GreedyStochastic is a graph search algorithm. Hence, we use close set.
        super(GreedyStochastic, self).__init__(use_close=True)
        self.heuristic_function_type = heuristic_function_type
        self.T = T_init
        self.N = N
        self.T_scale_factor = T_scale_factor
        self.solver_name = 'GreedyStochastic (h={heuristic_name})'.format(
            heuristic_name=heuristic_function_type.heuristic_name)

    def _init_solver(self, problem: GraphProblem):
        super(GreedyStochastic, self)._init_solver(problem)
        self.heuristic_function = self.heuristic_function_type(problem)

    def _open_successor_node(self, problem: GraphProblem, successor_node: SearchNode):
        """
        TODO: implement this method!
        """
        if self.close.has_state(successor_node.state):
            if self.close.get_node_by_state(successor_node.state).expanding_priority <= successor_node.expanding_priority:
                return
            else:
                self.close.remove_node(self.close.get_node_by_state(successor_node.state));
        if self.open.has_state(successor_node.state):
            if successor_node.expanding_priority < self.open.get_node_by_state(successor_node.state).expanding_priority:
                self.open.extract_node(self.open.get_node_by_state(successor_node.state))
            else:
                return
        self.open.push_node(successor_node)


    def _calc_node_expanding_priority(self, search_node: SearchNode) -> float:
        """
        TODO: implement this method!
        Remember: `GreedyStochastic` is greedy.
        """
        return self.heuristic_function.estimate(search_node.state);

    def _extract_next_search_node_to_expand(self) -> Optional[SearchNode]:
        """
        Extracts the next node to expand from the open queue,
         using the stochastic method to choose out of the N
         best items from open.
        TODO: implement this method!
        Use `np.random.choice(...)` whenever you need to randomly choose
         an item from an array of items given a probabilities array `p`.
        You can read the documentation of `np.random.choice(...)` and
         see usage examples by searching it in Google.
        Notice: You might want to pop min(N, len(open) items from the
                `open` priority queue, and then choose an item out
                of these popped items. The other items have to be
                pushed again into that queue.
        """
        if self.open.is_empty():
            return
        bestFiveList = []
        toreturnQ = []

        while  not self.open.is_empty():
            popedFromOpen = self.open.pop_next_node()
            if len(bestFiveList) < self.N:
                bestFiveList.append(popedFromOpen)
            else:
                i_replace = 0
                max = bestFiveList[i_replace].expanding_priority
                for i in range (1, len(bestFiveList)):
                    if bestFiveList[i].expanding_priority > max:
                        i_replace = i
                        max = bestFiveList[i].expanding_priority
                if popedFromOpen.expanding_priority < max:
                    bestFiveList[i_replace] = popedFromOpen

            toreturnQ.append(popedFromOpen)

        for retrunNode in toreturnQ:
            self.open.push_node(retrunNode)

        bestFiveArr = np.empty(shape=0, dtype=SearchNode)
        bestFiveArrCheck = np.empty(shape=0, dtype=SearchNode)
        costArr = []
        pArr = np.empty(shape=0, dtype=float)
        for node in bestFiveList:
            bestFiveArr = np.append(bestFiveArr,node)
            costArr.append(node.expanding_priority)
        if costArr.count(0) != 0:
            for node in bestFiveArr:
                if node.expanding_priority == 0:
                    bestFiveArrCheck = np.append(bestFiveArrCheck,node)
            pArr = None
        else:
            bestFiveArrCheck = bestFiveArr
            denominator = 0
            for x_mechane in costArr:
                denominator += (x_mechane ** (-1 / self.T))
            for cost in costArr:
                pArr = np.append(pArr, ((cost ** (-1 / self.T)) / denominator))
        chosenNode = np.random.choice(bestFiveArrCheck,None,True,pArr)
        self.open.extract_node(chosenNode)
        self.close.add_node(chosenNode)
        self.T = self.T *0.95

        return chosenNode
