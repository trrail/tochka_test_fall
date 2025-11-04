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

def bfs_path(start, target_gateways, graph):
    queue = deque([[start]])
    visited = {start}
    best_path = None
    best_gateway = None

    while queue:
        path = queue.popleft()
        current_node = path[-1]
        if current_node in target_gateways:
            if (best_path is None or
                len(path) < len(best_path) or
                (len(path) == len(best_path) and current_node < best_gateway)):
                best_path = path
                best_gateway = current_node
            continue
        for neighbor in sorted(graph[current_node]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return best_path, best_gateway

def next_step_towards(current, target, graph):
    path, _ = bfs_path(current, {target}, graph)
    return path[1] if path and len(path) > 1 else current

def simulate(graph, gateways, virus_start):
    blocked_edges = []
    virus_position = virus_start

    while True:
        path_to_gateway, nearest_gateway = bfs_path(virus_position, gateways, graph)
        if not path_to_gateway or not nearest_gateway:
            break

        adjacent_gateways = sorted([g for g in graph[virus_position] if g in gateways])
        if adjacent_gateways:
            gateway_to_block = adjacent_gateways[0]
            blocked_edges.append(f"{gateway_to_block}-{virus_position}")
            graph[gateway_to_block].remove(virus_position)
            graph[virus_position].remove(gateway_to_block)
            continue

        prev_node = path_to_gateway[-2]
        gateway_node = path_to_gateway[-1]
        blocked_edges.append(f"{gateway_node}-{prev_node}")
        graph[gateway_node].remove(prev_node)
        graph[prev_node].remove(gateway_node)

        virus_position = next_step_towards(virus_position, nearest_gateway, graph)

    return blocked_edges

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
