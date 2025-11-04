import sys
from collections import deque
from typing import List, Tuple, Set, Dict, Optional

VIRUS_START = 'a'


class Node:
    def __init__(self, name: str):
        self.name = name
        self.neighbors: Set[str] = set()
        self.is_gateway = name.isupper()

    def add_neighbor(self, neighbor: str):
        self.neighbors.add(neighbor)

    def remove_neighbor(self, neighbor: str):
        self.neighbors.discard(neighbor)


class Graph:
    def __init__(self, edges: List[Tuple[str, str]]):
        self.nodes: Dict[str, Node] = {}
        self._build_graph(edges)
        self.gateways = {name for name, node in self.nodes.items() if node.is_gateway}

    def _build_graph(self, edges: List[Tuple[str, str]]):
        for node1, node2 in edges:
            if node1 not in self.nodes:
                self.nodes[node1] = Node(node1)
            if node2 not in self.nodes:
                self.nodes[node2] = Node(node2)
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)

    def bfs_shortest_path(self, virus_start_node: str, target_gateways: Set[str]) -> Tuple[Optional[List[str]], Optional[str]]:
        queue = deque([virus_start_node])
        distances: dict[str, Optional[int]]= {virus_start_node: 0}
        previous_node: dict[str, Optional[str]] = {virus_start_node: None}

        while queue:
            current_node = queue.popleft()
            for neighbour in sorted(self.nodes[current_node].neighbors):
                if neighbour not in distances:  # Вычисляем сколько идти до узла
                    distances[neighbour] = distances[current_node] + 1
                    previous_node[neighbour] = current_node
                    queue.append(neighbour)

        # Шлюзы, до которых можно дойти
        reachable_gateways = [gw for gw in target_gateways if gw in distances]
        if not reachable_gateways:
            return None, None

        min_dist = min(distances[gw] for gw in reachable_gateways)
        candidates_gateways = [gw for gw in reachable_gateways if distances[gw] == min_dist]
        best_gw = min(candidates_gateways)

        path = []
        current_node = best_gw
        while current_node is not None:
            path.append(current_node)
            current_node = previous_node.get(current_node)
        path.reverse()
        return path, best_gw

    def simulate(self, virus_start: str) -> List[str]:
        virus = virus_start
        blocked = []

        while True:
            path, target = self.bfs_shortest_path(virus, self.gateways)
            if path:
                if len(path) == 2:
                    gw = path[1]
                    edge = f"{gw}-{virus}"
                    blocked.append(edge)
                    self.nodes[gw].remove_neighbor(virus)
                    self.nodes[virus].remove_neighbor(gw)
                else:
                    gw = path[-1]
                    node = path[-2]
                    edge = f"{gw}-{node}"
                    blocked.append(edge)
                    self.nodes[gw].remove_neighbor(node)
                    self.nodes[node].remove_neighbor(gw)
            else:
                break
            path, target = self.bfs_shortest_path(virus, self.gateways)
            if path and len(path) > 1:
                virus = path[1]
            else:
                break

        return blocked


def solve(edges: List[Tuple[str, str]]) -> List[str]:
    graph = Graph(edges)
    return graph.simulate(VIRUS_START)


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()
