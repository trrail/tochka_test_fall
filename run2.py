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
        for node1, node2 in edges:
            if node1 not in self.nodes:
                self.nodes[node1] = Node(node1)
            if node2 not in self.nodes:
                self.nodes[node2] = Node(node2)
            self.nodes[node1].add_neighbor(node2)
            self.nodes[node2].add_neighbor(node1)
        self.gateways = {name for name, node in self.nodes.items() if node.is_gateway}

    def bfs_shortest_path(self, start, target_gateways):
        queue = deque([[start]])
        visited = {start}
        best_path = None
        best_gateway = None

        while queue:
            path = queue.popleft()
            node_name = path[-1]
            node = self.nodes[node_name]

            if node.is_gateway and node_name in target_gateways:
                if (best_path is None or
                    len(path) < len(best_path) or
                    (len(path) == len(best_path) and node_name < best_gateway)):
                    best_path = path
                    best_gateway = node_name
                continue

            for neighbor_name in sorted(node.neighbors):
                if neighbor_name not in visited:
                    visited.add(neighbor_name)
                    queue.append(path + [neighbor_name])

        return best_path, best_gateway

    def next_step(self, current, target):
        path, _ = self.bfs_shortest_path(current, {target})
        return path[1] if path and len(path) > 1 else current

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
                continue

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
