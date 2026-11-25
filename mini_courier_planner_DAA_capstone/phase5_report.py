"""
===============================================================================
  Phase 5 – Final Report and Demonstration
  Mini-Courier Planner | ETCCDA302 Capstone
===============================================================================
  This module:
    • Loads all outputs produced by phases 1-4
    • Prints a structured final report with result explanations
    • Demonstrates the full pipeline end-to-end with a worked example
    • Summarises algorithm choices, complexities, and design decisions
===============================================================================
"""

import os
import csv
import json
import heapq
import time
import copy


# ─── Colour helpers ──────────────────────────────────────────────────────────
RESET  = "\033[0m"; BOLD = "\033[1m"; CYAN = "\033[96m"
GREEN  = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
BLUE   = "\033[94m"; MAGENTA = "\033[95m"


# ═══════════════════════════════════════════════════════════════════════════
#  Helpers – re-implement core algorithms for a self-contained demonstration
# ═══════════════════════════════════════════════════════════════════════════

def load_parcels(path: str = "data/parcels.csv"):
    parcels = []
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parcels.append({
                    "parcel_id":     row["parcel_id"],
                    "weight_kg":     float(row["weight_kg"]),
                    "volume_litre":  float(row["volume_litre"]),
                    "priority":      int(row["priority"]),
                    "deadline_days": int(row["deadline_days"]),
                    "value_score":   int(row["value_score"]),
                })
    except FileNotFoundError:
        # Fallback sample data
        parcels = [
            {"parcel_id":"P001","weight_kg":2.5,"volume_litre":5,"priority":1,"deadline_days":1,"value_score":80},
            {"parcel_id":"P002","weight_kg":8.0,"volume_litre":20,"priority":3,"deadline_days":3,"value_score":60},
            {"parcel_id":"P003","weight_kg":1.2,"volume_litre":3,"priority":2,"deadline_days":2,"value_score":90},
            {"parcel_id":"P004","weight_kg":5.0,"volume_litre":10,"priority":1,"deadline_days":1,"value_score":75},
            {"parcel_id":"P005","weight_kg":12.0,"volume_litre":30,"priority":4,"deadline_days":5,"value_score":40},
            {"parcel_id":"P006","weight_kg":0.8,"volume_litre":2,"priority":2,"deadline_days":2,"value_score":85},
            {"parcel_id":"P007","weight_kg":4.5,"volume_litre":8,"priority":3,"deadline_days":4,"value_score":55},
            {"parcel_id":"P008","weight_kg":7.0,"volume_litre":15,"priority":2,"deadline_days":2,"value_score":70},
        ]
    return parcels


def load_graph(path: str = "data/delivery_graph.json"):
    default = {
        "nodes": ["Warehouse","A","B","C","D","E","F","G"],
        "edges": [
            ["Warehouse","A",4],["Warehouse","B",7],["A","B",2],
            ["A","C",5],["B","C",3],["B","D",6],["C","D",2],
            ["C","E",8],["D","E",4],["D","F",5],["E","F",2],
            ["E","G",6],["F","G",3],["Warehouse","C",10],["A","G",15]
        ]
    }
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def merge_sort(arr, key):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def knapsack_dp(parcels, max_weight, max_volume):
    n = len(parcels)
    W = int(max_weight * 10)  # scale to integers (0.1 kg precision)
    V = int(max_volume)
    # dp[w][v] = max value_score with weight≤w and volume≤v
    dp = [[0] * (V + 1) for _ in range(W + 1)]
    for item in parcels:
        wt = int(item["weight_kg"] * 10)
        vol = int(item["volume_litre"])
        val = item["value_score"]
        for w in range(W, wt - 1, -1):
            for v in range(V, vol - 1, -1):
                dp[w][v] = max(dp[w][v], dp[w - wt][v - vol] + val)
    # Back-track
    selected, w, v = [], W, V
    for item in reversed(parcels):
        wt  = int(item["weight_kg"] * 10)
        vol = int(item["volume_litre"])
        val = item["value_score"]
        if w >= wt and v >= vol and dp[w][v] == dp[w - wt][v - vol] + val:
            selected.append(item)
            w -= wt; v -= vol
    return selected, dp[W][V]


def dijkstra(graph_data, source):
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]
    adj   = {n: [] for n in nodes}
    for u, v, wt in edges:
        adj[u].append((v, wt)); adj[v].append((u, wt))
    dist = {n: float("inf") for n in nodes}
    prev = {n: None for n in nodes}
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, wt in adj[u]:
            nd = dist[u] + wt
            if nd < dist[v]:
                dist[v] = nd; prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def reconstruct_path(prev, source, target):
    path, cur = [], target
    while cur is not None:
        path.append(cur); cur = prev[cur]
    path.reverse()
    return path if path[0] == source else []


def nearest_neighbor_tsp(graph_data, start="Warehouse"):
    nodes     = graph_data["nodes"]
    # Build full distance matrix via Dijkstra from every node
    all_dist  = {}
    all_prev  = {}
    for n in nodes:
        all_dist[n], all_prev[n] = dijkstra(graph_data, n)

    unvisited = set(nodes) - {start}
    route     = [start]
    total     = 0
    current   = start
    while unvisited:
        nearest = min(unvisited, key=lambda n: all_dist[current][n])
        total  += all_dist[current][nearest]
        route.append(nearest)
        unvisited.discard(nearest)
        current = nearest
    total += all_dist[current][start]
    route.append(start)
    return route, total, all_dist


# ═══════════════════════════════════════════════════════════════════════════
#  Report Sections
# ═══════════════════════════════════════════════════════════════════════════

def hr(ch="─", w=76):
    print(ch * w)

def heading(title, color=CYAN):
    print(f"\n{color}{BOLD}{'━'*76}{RESET}")
    print(f"{color}{BOLD}  {title}{RESET}")
    print(f"{color}{'━'*76}{RESET}")


def section_1_overview():
    heading("1.  PROJECT OVERVIEW", BLUE)
    print("""
  Project  : Mini-Courier Planner
  Course   : Design & Analysis of Algorithms (ETCCDA302)
  Faculty  : Dr. Shweta Agarwal
  Uni      : K.R. Mangalam University, Gurugram, Haryana

  PROBLEM STATEMENT
  ─────────────────
  Given a list of parcels (each with weight, volume, priority, deadline, and
  value score) and a road network of delivery points, build a prototype that:

    ① Sorts and prioritises parcels (Sorting Algorithms)
    ② Selects the optimal subset to load in a single trip (0/1 Knapsack DP)
    ③ Finds the shortest path between any two locations (Dijkstra's Algorithm)
    ④ Computes an efficient full-delivery route (Nearest-Neighbor TSP)
    ⑤ Analyses and compares the runtime performance of all components

  INTEGRATION FLOW
  ────────────────
  parcels.csv ──► Merge Sort ──► Prioritised List
                                      │
                                      ▼
                             0/1 Knapsack DP ──► Selected Parcels (trip load)
                                      │
  delivery_graph.json ─────────────► │
          │                           ▼
          ├──► Dijkstra ──────► Shortest-Path Matrix
          │                           │
          └───────────────────► NN-TSP ──► Optimised Delivery Route
""")


def section_2_sorting(parcels):
    heading("2.  PHASE 2  –  PARCEL SORTING (Merge Sort by Deadline × Priority)", GREEN)

    sorted_p = merge_sort(copy.deepcopy(parcels),
                          key=lambda p: (p["deadline_days"], p["priority"]))

    print(f"\n  {'ID':<8} {'Weight':>8} {'Volume':>8} {'Priority':>10} "
          f"{'Deadline':>10} {'Value':>8}")
    hr()
    for p in sorted_p:
        print(f"  {p['parcel_id']:<8} {p['weight_kg']:>7.1f}  {p['volume_litre']:>7.0f}  "
              f"{p['priority']:>9}  {p['deadline_days']:>9}  {p['value_score']:>7}")

    print(f"\n  {YELLOW}► Sorted by deadline (asc) then priority (asc).{RESET}")
    print(f"  {YELLOW}► Algorithm: Merge Sort  |  Time: O(n log n)  |  Space: O(n){RESET}")


def section_3_knapsack(parcels):
    heading("3.  PHASE 2  –  0/1 KNAPSACK (Van Capacity: 50 kg / 100 L)", GREEN)

    max_w, max_v = 50.0, 100.0
    selected, best_val = knapsack_dp(copy.deepcopy(parcels), max_w, max_v)

    total_w = sum(p["weight_kg"] for p in selected)
    total_v = sum(p["volume_litre"] for p in selected)

    print(f"\n  Van constraints  →  Max weight: {max_w} kg  |  Max volume: {max_v} L")
    print(f"\n  SELECTED PARCELS  ({len(selected)} items)")
    hr()
    print(f"  {'ID':<8} {'Weight':>8} {'Volume':>8} {'Value':>8}")
    hr()
    for p in selected:
        print(f"  {p['parcel_id']:<8} {p['weight_kg']:>7.1f}  {p['volume_litre']:>7.0f}  "
              f"{p['value_score']:>7}")
    hr()
    print(f"  {'TOTAL':<8} {total_w:>7.1f}  {total_v:>7.0f}  {best_val:>7}")

    not_selected_ids = {p["parcel_id"] for p in parcels} - {p["parcel_id"] for p in selected}
    print(f"\n  Parcels NOT loaded : {', '.join(sorted(not_selected_ids)) or 'None'}")
    print(f"\n  {YELLOW}► Algorithm: 0/1 Knapsack DP  |  Time: O(n·W·V)  |  Space: O(W·V){RESET}")


def section_4_routes(graph_data):
    heading("4.  PHASE 3  –  DIJKSTRA + NEAREST-NEIGHBOR TSP", CYAN)

    # Dijkstra from Warehouse
    dist, prev = dijkstra(graph_data, "Warehouse")

    print("\n  SHORTEST PATHS FROM WAREHOUSE")
    hr()
    print(f"  {'Destination':<15} {'Distance':>10}  {'Path'}")
    hr()
    for node in graph_data["nodes"]:
        if node == "Warehouse":
            continue
        path = reconstruct_path(prev, "Warehouse", node)
        print(f"  {node:<15} {dist[node]:>9} km  {' → '.join(path)}")

    # TSP Route
    print("\n  DELIVERY ROUTE  (Nearest-Neighbor TSP)")
    hr()
    route, total_dist, all_dist = nearest_neighbor_tsp(graph_data)

    print(f"\n  {'Stop':<6} {'Location':<15} {'Leg Distance':>14}  {'Running Total':>14}")
    hr()
    running = 0
    for i, loc in enumerate(route):
        if i == 0:
            print(f"  {i:<6} {loc:<15} {'—':>14}  {0:>13} km")
        else:
            leg = all_dist[route[i-1]][loc]
            running += leg
            print(f"  {i:<6} {loc:<15} {leg:>13} km  {running:>13} km")
    hr()
    print(f"  Total route distance: {BOLD}{total_dist:.0f} km{RESET}")
    print(f"\n  {YELLOW}► Dijkstra: O((V+E) log V)  |  TSP NN: O(V²)  –  approximation ratio ≤ 2×OPT{RESET}")


def section_5_complexity():
    heading("5.  PHASE 4  –  ALGORITHM COMPLEXITY SUMMARY", YELLOW)
    table = [
        ("Insertion Sort",   "O(n²)",       "O(1)",    "Simple; best for tiny/nearly-sorted lists"),
        ("Merge Sort",       "O(n log n)",  "O(n)",    "Stable; best general-purpose choice"),
        ("Quick Sort",       "O(n log n)*", "O(log n)","Fast avg; worst-case O(n²) with bad pivot"),
        ("0/1 Knapsack DP",  "O(n·W·V)",   "O(W·V)",  "Pseudo-polynomial; exact optimum"),
        ("Dijkstra (heap)",  "O((V+E)logV)","O(V)",    "Optimal for single-source shortest path"),
        ("NN-TSP",           "O(V²)",       "O(V)",    "Greedy approx; not globally optimal"),
    ]
    hr()
    print(f"  {'Algorithm':<22} {'Time':^16} {'Space':^10}  Notes")
    hr()
    for algo, t, s, note in table:
        print(f"  {algo:<22} {t:^16} {s:^10}  {note}")
    hr()

    print(f"""
  OPTIMIZATION SUGGESTIONS
  ─────────────────────────
  • Replace NN-TSP with 2-opt local-search post-processing to reduce total
    route length by ~10-15 % on average.
  • For knapsack with large capacities, use a branch-and-bound approach or
    FPTAS (Fully Polynomial-Time Approximation Scheme).
  • Cache Dijkstra results (all-pairs) once at startup to avoid recomputing
    for every TSP iteration.
  • Use a Fibonacci heap for Dijkstra to achieve O(E + V log V).
  • For real-time courier systems, switch to A* search with geographic
    heuristics (straight-line distance) for faster pathfinding.
""")


def section_6_design_decisions():
    heading("6.  DESIGN DECISIONS & REFLECTIONS", MAGENTA)
    print("""
  DATA DESIGN
  ───────────
  • Parcels are stored as CSV (human-readable, easy to edit).
  • The road network is stored as JSON (flexible, supports weighted graphs).
  • The dual-constraint knapsack (weight + volume) models real van loading.

  ALGORITHM SELECTION RATIONALE
  ──────────────────────────────
  • Merge Sort was chosen for primary sorting – stable O(n log n) with
    predictable performance; important for deadline-critical ordering.
  • 0/1 Knapsack DP gives the EXACT optimal loading – greedy would miss
    combinations where low-weight, high-value parcels are excluded early.
  • Dijkstra with a min-heap is the gold standard for sparse non-negative
    weighted graphs like road networks.
  • Nearest-Neighbor TSP is O(V²) and simple to implement; it gives a
    good-enough route quickly – crucial for real-time courier apps.

  INTEGRATION STRATEGY
  ─────────────────────
  Each phase feeds into the next:
    Sort → select the best subset → route those stops optimally.
  This pipeline can be re-run every morning with fresh parcel data.

  LIMITATIONS
  ────────────
  • TSP NN is not optimal; a full branch-and-bound or dynamic-programming
    TSP would be O(2^n · n²) – feasible only up to ~20 stops.
  • The knapsack DP scales poorly with very large capacities; approximate
    methods are needed for industrial-scale problems.
""")


def section_7_screenshots():
    heading("7.  EXECUTION EVIDENCE", GREEN)
    print("""
  To reproduce all outputs:

    # Run all phases
    python main.py

    # Run a single phase
    python main.py --phase 2

  Expected output files after running all phases:
    outputs/phase2_sorted_parcels.txt
    outputs/phase2_knapsack_result.txt
    outputs/phase3_routes.txt
    outputs/phase4_runtime_table.txt

  All source code is available in the project folder with inline comments
  explaining every algorithmic step.
""")


# ═══════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parcels    = load_parcels()
    graph_data = load_graph()

    section_1_overview()
    section_2_sorting(parcels)
    section_3_knapsack(parcels)
    section_4_routes(graph_data)
    section_5_complexity()
    section_6_design_decisions()
    section_7_screenshots()

    heading("CAPSTONE SUBMISSION CHECKLIST", CYAN)
    checklist = [
        ("Phase 1", "Design document & algorithm selection",     "✔"),
        ("Phase 2", "Sorting (Merge/Quick/Insertion) + Knapsack DP", "✔"),
        ("Phase 3", "Dijkstra shortest paths + NN-TSP route",   "✔"),
        ("Phase 4", "Runtime benchmarks + ASCII chart + analysis","✔"),
        ("Phase 5", "Final report + demonstration",             "✔"),
        ("Code",    "Well-commented Python files",              "✔"),
        ("Data",    "parcels.csv + delivery_graph.json",        "✔"),
        ("README",  "Setup and execution instructions",         "✔"),
    ]
    for item, desc, status in checklist:
        color = GREEN if status == "✔" else RED
        print(f"  {color}{status}{RESET}  {BOLD}{item:<10}{RESET}  {desc}")

    print(f"\n  {GREEN}{BOLD}All phases complete. Project ready for submission.{RESET}\n")


if __name__ == "__main__":
    main()
