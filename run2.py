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

    def bfs_shortest_path(self, start: str, target_gateways: Set[str]) -> Tuple[Optional[List[str]], Optional[str]]:
        if start in target_gateways:
            return [start], start

        queue = deque([start])
        distances = {start: 0}
        previous = {start: None}

        while queue:
            current = queue.popleft()
            for neighbour in sorted(self.nodes[current].neighbors):  # лексикографический порядок
                if neighbour not in distances:
                    distances[neighbour] = distances[current] + 1
                    previous[neighbour] = current
                    queue.append(neighbour)

        reachable_gateways = [gw for gw in target_gateways if gw in distances]
        if not reachable_gateways:
            return None, None

        min_dist = min(distances[gw] for gw in reachable_gateways)
        candidates_gateways = [gw for gw in reachable_gateways if distances[gw] == min_dist]
        best_gw = min(candidates_gateways)

        path = []
        current = best_gw
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        return path, best_gw

    def get_all_gateway_edges(self) -> List[Tuple[str, str]]:
        edges = []
        for gw in self.gateways:
            node = self.nodes[gw]
            for neigh in node.neighbors:
                if not self.nodes[neigh].is_gateway:
                    edges.append((gw, neigh))
        edges.sort(key=lambda x: (x[0], x[1]))
        return edges

    def simulate(self, virus_start: str) -> List[str]:
        virus = virus_start
        blocked = []

        while True:
            path, target = self.bfs_shortest_path(virus, self.gateways)
            if path and len(path) == 2:
                gw = path[1]
                edge = f"{gw}-{virus}"
                blocked.append(edge)
                self.nodes[gw].remove_neighbor(virus)
                self.nodes[virus].remove_neighbor(gw)
                continue

            if not path:
                break

            candidates = self.get_all_gateway_edges()
            if not candidates:
                break

            blocked_this_turn = False
            for gw, node in candidates:
                self.nodes[gw].remove_neighbor(node)
                self.nodes[node].remove_neighbor(gw)

                new_path, _ = self.bfs_shortest_path(virus, self.gateways)

                if not new_path or len(new_path) > 2:
                    blocked.append(f"{gw}-{node}")
                    blocked_this_turn = True
                    break
                else:
                    self.nodes[gw].add_neighbor(node)
                    self.nodes[node].add_neighbor(gw)

            if not blocked_this_turn:
                break

            path, _ = self.bfs_shortest_path(virus, self.gateways)
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