"""
Mini-Courier Planner — Phase 3: Graph Routing
==============================================
Covers:
  1. Graph building from JSON (or hardcoded fallback)
  2. Dijkstra's Algorithm (from scratch, using heapq)
  3. Nearest-Neighbor TSP Approximation (from scratch)
  4. Formatted Delivery Route Plan summary

Standard-library only: heapq, json, csv, collections
"""

import heapq
import json
import os
import collections

# ─────────────────────────────────────────────────────────────────────────────
# 1.  GRAPH BUILDING
# ─────────────────────────────────────────────────────────────────────────────

# Hardcoded fallback edge list  (u, v, weight) — undirected
FALLBACK_EDGES = [
    ("Warehouse", "A",  4),
    ("Warehouse", "B",  7),
    ("Warehouse", "C", 10),
    ("A",         "B",  2),
    ("A",         "C",  5),
    ("A",         "G", 15),
    ("B",         "C",  3),
    ("B",         "D",  6),
    ("C",         "D",  2),
    ("C",         "E",  8),
    ("D",         "E",  4),
    ("D",         "F",  5),
    ("E",         "F",  2),
    ("E",         "G",  6),
    ("F",         "G",  3),
]

GRAPH_FILE = os.path.join(os.path.dirname(__file__), "data", "delivery_graph.json")


def build_graph(edge_list):
    """
    Build an adjacency-list graph (dict of lists of (neighbor, weight))
    from a list of (u, v, weight) tuples.  The graph is treated as undirected.
    """
    graph = collections.defaultdict(list)
    for u, v, w in edge_list:
        graph[u].append((v, w))
        graph[v].append((u, w))
    return dict(graph)


def load_graph():
    """
    Try to load the graph from delivery_graph.json.
    Expected JSON format:
        { "edges": [{"from": "X", "to": "Y", "weight": N}, ...] }
    Falls back to FALLBACK_EDGES if the file is missing or malformed.
    """
    if os.path.exists(GRAPH_FILE):
        try:
            with open(GRAPH_FILE, "r") as f:
                data = json.load(f)
            # Support two JSON shapes:
            #   {"edges": [{"from": X, "to": Y, "weight": W}, ...]}
            #   [[X, Y, W], ...]
            raw = data["edges"] if isinstance(data, dict) and "edges" in data else data
            if raw and isinstance(raw[0], dict):
                edges = [(e["from"], e["to"], e["weight"]) for e in raw]
            else:
                edges = [(e[0], e[1], e[2]) for e in raw]
            print(f"[INFO] Loaded graph from {GRAPH_FILE}  ({len(edges)} edges)")
            return build_graph(edges), edges
        except (KeyError, ValueError, json.JSONDecodeError, IndexError, TypeError) as exc:
            print(f"[WARN] Could not parse {GRAPH_FILE} ({exc}). Using fallback.")
    else:
        print(f"[INFO] {GRAPH_FILE} not found. Using hardcoded fallback graph.")
    return build_graph(FALLBACK_EDGES), FALLBACK_EDGES


def print_adjacency_list(graph):
    """Pretty-print the adjacency list of the graph."""
    print("\n" + "=" * 60)
    print("  ADJACENCY LIST REPRESENTATION")
    print("=" * 60)
    for node in sorted(graph.keys()):
        neighbours = ", ".join(f"{v}(w={w})" for v, w in sorted(graph[node]))
        print(f"  {node:<12} → {neighbours}")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  DIJKSTRA'S ALGORITHM  (from scratch)
# ─────────────────────────────────────────────────────────────────────────────

INF = float("inf")


def dijkstra(graph, source, verbose=False):
    """
    Single-source shortest paths using Dijkstra's algorithm.

    Parameters
    ----------
    graph   : dict  — adjacency list {node: [(neighbor, weight), ...]}
    source  : str   — starting node
    verbose : bool  — if True, print step-by-step progress

    Returns
    -------
    dist  : dict {node: shortest_distance}
    prev  : dict {node: predecessor_node}  (used to reconstruct paths)
    """
    dist = {node: INF for node in graph}
    dist[source] = 0
    prev = {node: None for node in graph}
    visited = set()

    # Min-heap entries: (distance, node)
    heap = [(0, source)]

    step = 0
    while heap:
        current_dist, u = heapq.heappop(heap)

        # Skip stale entries (lazy deletion)
        if u in visited:
            continue
        visited.add(u)
        step += 1

        if verbose:
            print(f"\n  Step {step}: Visit '{u}'  (dist={current_dist})")
            # Print current distance table
            row = "  Distances: " + " | ".join(
                f"{n}={'∞' if d == INF else d}"
                for n, d in sorted(dist.items())
            )
            print(row)

        # Relax neighbours
        for v, weight in graph.get(u, []):
            if v in visited:
                continue
            new_dist = current_dist + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    return dist, prev


def reconstruct_path(prev, source, target):
    """Walk the predecessor map backwards to rebuild the full path."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    # Return empty list if path doesn't start at source (unreachable)
    if path[0] != source:
        return []
    return path


def print_dijkstra_results(graph, source="Warehouse"):
    """Run Dijkstra from `source`, print step-by-step and final table."""
    print("\n" + "=" * 60)
    print(f"  DIJKSTRA'S ALGORITHM  (source = '{source}')")
    print("=" * 60)
    print("\n--- Step-by-step execution ---")
    dist, prev = dijkstra(graph, source, verbose=True)

    print("\n--- Final shortest distances & paths ---")
    print(f"  {'Destination':<14} {'Distance':>8}   Path")
    print("  " + "-" * 55)
    for dest in sorted(dist.keys()):
        if dest == source:
            continue
        d = dist[dest]
        path = reconstruct_path(prev, source, dest)
        path_str = " → ".join(path) if path else "unreachable"
        d_str = str(d) if d != INF else "∞"
        print(f"  {dest:<14} {d_str:>8}   {path_str}")

    # Specific pair examples
    pairs = [("A", "G"), ("B", "F"), ("C", "G")]
    print("\n--- Specific pair shortest paths ---")
    for s, t in pairs:
        # Run Dijkstra from s
        d2, p2 = dijkstra(graph, s)
        path = reconstruct_path(p2, s, t)
        path_str = " → ".join(path) if path else "unreachable"
        d_str = str(d2[t]) if d2[t] != INF else "∞"
        print(f"  {s} → {t}: distance={d_str},  path={path_str}")

    return dist, prev


# ─────────────────────────────────────────────────────────────────────────────
# 3.  NEAREST-NEIGHBOR TSP APPROXIMATION  (from scratch)
# ─────────────────────────────────────────────────────────────────────────────

def build_cost_matrix(graph, nodes):
    """
    Compute all-pairs shortest-path costs between the given nodes.
    Uses Dijkstra from each node as the source.

    Returns
    -------
    cost : dict  cost[u][v] = shortest distance from u to v
    """
    cost = {}
    for node in nodes:
        d, _ = dijkstra(graph, node)
        cost[node] = d
    return cost


def nearest_neighbor_tsp(cost, stops, start="Warehouse"):
    """
    Greedy nearest-neighbor TSP heuristic.

    Parameters
    ----------
    cost  : dict  cost[u][v] = travel cost between u and v
    stops : list  all nodes that must be visited (including start)
    start : str   depot / starting node

    Returns
    -------
    route         : list of nodes in visit order (start → ... → start)
    total_dist    : total route distance
    leg_distances : list of distances for each consecutive leg
    """
    unvisited = set(stops) - {start}
    route = [start]
    leg_distances = []
    total_dist = 0

    current = start
    while unvisited:
        # Find the nearest unvisited node
        nearest = min(unvisited, key=lambda v: cost[current].get(v, INF))
        leg = cost[current].get(nearest, INF)
        route.append(nearest)
        leg_distances.append(leg)
        total_dist += leg
        unvisited.remove(nearest)
        current = nearest

    # Return to depot
    return_leg = cost[current].get(start, INF)
    route.append(start)
    leg_distances.append(return_leg)
    total_dist += return_leg

    return route, total_dist, leg_distances


def print_tsp_results(graph, delivery_stops):
    """Build cost matrix, run TSP, print route."""
    print("\n" + "=" * 60)
    print("  NEAREST-NEIGHBOR TSP APPROXIMATION")
    print("=" * 60)
    print(f"  Stops to visit: {delivery_stops}")

    cost = build_cost_matrix(graph, delivery_stops)

    route, total_dist, legs = nearest_neighbor_tsp(cost, delivery_stops, start="Warehouse")

    print(f"\n  Computed Route:  {' → '.join(route)}")
    print(f"  Total Distance:  {total_dist}")
    print("\n  Leg breakdown:")
    for i, (leg_dist) in enumerate(legs):
        frm = route[i]
        to  = route[i + 1]
        print(f"    Leg {i+1}: {frm:<12} → {to:<12}  dist={leg_dist}")

    return route, total_dist, legs, cost


# ─────────────────────────────────────────────────────────────────────────────
# 4.  FORMATTED DELIVERY ROUTE PLAN
# ─────────────────────────────────────────────────────────────────────────────

def print_route_summary(route, leg_distances):
    """
    Print a clean tabular delivery route plan.

    Columns: Stop # | Location | Leg Distance | Running Total
    """
    print("\n" + "=" * 60)
    print("  DELIVERY ROUTE PLAN — FORMATTED SUMMARY")
    print("=" * 60)
    header = f"  {'Stop':>4}  {'Location':<14}  {'Leg Dist':>9}  {'Running Total':>13}"
    print(header)
    print("  " + "-" * 55)

    running = 0
    # First stop (depot, leg distance = 0 by definition)
    print(f"  {'1':>4}  {'Warehouse':<14}  {'0':>9}  {'0':>13}  ← DEPOT START")

    for i, leg in enumerate(leg_distances):
        location = route[i + 1]
        running += leg
        stop_num = i + 2
        label = "← RETURN TO DEPOT" if location == "Warehouse" and i == len(leg_distances) - 1 else ""
        print(f"  {stop_num:>4}  {location:<14}  {leg:>9}  {running:>13}  {label}")

    print("  " + "-" * 55)
    print(f"  {'':>4}  {'TOTAL':.<14}  {'':>9}  {running:>13}")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "#" * 60)
    print("  MINI-COURIER PLANNER — PHASE 3: GRAPH ROUTING")
    print("#" * 60)

    # ── 1. Load / build graph ───────────────────────────────────────────────
    graph, edges = load_graph()
    print_adjacency_list(graph)

    # ── 2. Dijkstra from Warehouse ──────────────────────────────────────────
    dist, prev = print_dijkstra_results(graph, source="Warehouse")

    # ── 3. TSP approximation ────────────────────────────────────────────────
    delivery_stops = ["Warehouse", "A", "B", "C", "D", "E", "F", "G"]
    route, total_dist, legs, cost = print_tsp_results(graph, delivery_stops)

    # ── 4. Route summary ────────────────────────────────────────────────────
    print_route_summary(route, legs)

    print("\n[Phase 3 complete]\n")


if __name__ == "__main__":
    main()
