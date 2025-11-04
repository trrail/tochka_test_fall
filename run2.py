import sys
from collections import deque

VIRUS_START = 'a'

class Node:
    def __init__(self, name):
        self.name = name
        self.neighbors = set()
        self.is_gateway = name.isupper()

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)

    def remove_neighbor(self, neighbor):
        self.neighbors.discard(neighbor)

class Graph:
    def __init__(self, edges):
        self.nodes = {}
        self._setup_nodes(edges)
        self.gateways = {name for name, node in self.nodes.items() if node.is_gateway}

    def _setup_nodes(self, edges):
        for node1, node2 in edges:
            if node1 not in self.nodes:
                self.nodes[node1] = Node(node1)
            if node2 not in self.nodes:
                self.nodes[node2] = Node(node2)
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)

    def bfs_shortest_path(self, start, target_gateways):
        distances = {start: 0}
        previous = {start: None}
        queue = deque([start])

        while queue:
            current = queue.popleft()
            for neighbor in sorted(self.nodes[current].neighbors):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    previous[neighbor] = current
                    queue.append(neighbor)

        reachable_gateways = [gw for gw in target_gateways if gw in distances]
        if not reachable_gateways:
            return None, None

        min_distance = min(distances[gw] for gw in reachable_gateways)
        candidate_gateways = [gw for gw in reachable_gateways if distances[gw] == min_distance]
        best_gateway = min(candidate_gateways)

        path = []
        current = best_gateway
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path, best_gateway

    def next_step(self, current, target):
        path, _ = self.bfs_shortest_path(current, {target})
        if path and len(path) > 1:
            return path[1]
        return current

    def simulate(self, virus_start):
        virus = virus_start
        blocked = []

        while True:
            path, gateway = self.bfs_shortest_path(virus, self.gateways)
            if not path or not gateway:
                break

            node = self.nodes[virus]
            adjacent_gateways = sorted([n for n in node.neighbors if self.nodes[n].is_gateway])
            if adjacent_gateways:
                gw_to_block = adjacent_gateways[0]
                blocked.append(f"{gw_to_block}-{virus}")
                node.remove_neighbor(gw_to_block)
                self.nodes[gw_to_block].remove_neighbor(virus)
            else:
                prev_node = path[-2]
                gw_node = path[-1]
                blocked.append(f"{gw_node}-{prev_node}")
                self.nodes[gw_node].remove_neighbor(prev_node)
                self.nodes[prev_node].remove_neighbor(gw_node)

                virus = self.next_step(virus, gateway)

        return blocked

def solve(edges: list[tuple[str, str]]) -> list[str]:
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
