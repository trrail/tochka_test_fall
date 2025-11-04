import sys
from collections import deque, defaultdict

VIRUS_START = 'a'

def build_graph(edges):
    graph = defaultdict(set)
    gateways = set()

    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
        if left.isupper():
            gateways.add(left)
        if right.isupper():
            gateways.add(right)

    return graph, gateways


def bfs_path(start, gateways, graph):
    queue = deque([[start]])
    visited = {start}
    best_path = None
    best_gateway = None

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node in gateways:
            if (
                best_gateway is None
                or len(path) < len(best_path)
                or (len(path) == len(best_path) and node < best_gateway)
            ):
                best_path, best_gateway = path, node
            continue

        for neighbor in sorted(graph[node]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return best_path, best_gateway


def move_towards_gateway(current, target, graph):
    path, _ = bfs_path(current, {target}, graph)
    return path[1] if path and len(path) > 1 else current


def simulate(graph, gateways, virus_start):
    blocked_paths = []
    virus = virus_start

    while True:
        path, target_gateway = bfs_path(virus, gateways, graph)
        if not path or not target_gateway:
            break

        nearby_gw = sorted([g for g in graph[virus] if g in gateways])
        if nearby_gw:
            gateway = nearby_gw[0]
            blocked_paths.append(f"{gateway}-{virus}")
            graph[gateway].remove(virus)
            graph[virus].remove(gateway)
            continue

        *_, prev_node, gateway_node = path
        blocked_paths.append(f"{gateway_node}-{prev_node}")
        graph[gateway_node].remove(prev_node)
        graph[prev_node].remove(gateway_node)

        virus = move_towards_gateway(virus, target_gateway, graph)

    return blocked_paths


def solve(edges):
    graph, gateways = build_graph(edges)
    return simulate(graph, gateways, VIRUS_START)


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
