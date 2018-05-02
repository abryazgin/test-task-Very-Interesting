from collections import defaultdict


class UniDirectionalGraph:

    def __init__(self):
        self._graph = defaultdict(dict)

    def add_edge(self, node_from, node_to, edge):
        self._graph[node_from][node_to] = edge

    def iter_neighbors(self, node):
        for node_to, edge in self._graph[node].items():
            yield node_to, edge