"""
=============================================================================
MINI-COURIER PLANNER — PHASE 1: DESIGN DOCUMENT
=============================================================================

Project Title  : Mini-Courier Planner (Capstone)
Phase          : 1 — Problem Clarity, Algorithm Selection & Data Design

PROBLEM STATEMENT
-----------------
A local courier company needs an automated system that can:
  1. Prioritise parcels for delivery based on urgency, deadline and value.
  2. Pack a delivery van optimally given fixed weight & volume constraints.
  3. Find the shortest path between any two delivery stops.
  4. Generate an efficient full delivery route visiting all stops once.

Each sub-problem maps to a classical algorithm, and the four algorithms
work together as a pipeline:

  parcels.csv ──► Sorting ──► Knapsack ──► Dijkstra ──► TSP Route
                 (Phase 2)    (Phase 2)    (Phase 3)   (Phase 3)

ALGORITHM SELECTION RATIONALE
------------------------------
  • Merge Sort / Quick Sort / Insertion Sort
        → Phase 2 | Rank parcels by deadline, priority and value density
        → Different sorts serve different business views of the same data

  • 0/1 Knapsack (DP, dual-constraint)
        → Phase 2 | Select the highest-value subset of ranked parcels that
          fits within van capacity (50 kg, 100 L)

  • Dijkstra's Shortest Path
        → Phase 3 | Compute minimum-cost path between any two delivery nodes
          on the weighted, undirected delivery graph

  • Nearest-Neighbour TSP Heuristic
        → Phase 3 | Construct an approximate travelling-salesman tour that
          visits every delivery stop exactly once and returns to warehouse

DATA DESIGN
-----------
  parcels.csv  — 15 records; attributes per parcel:
      parcel_id    : unique identifier (P001–P015)
      weight_kg    : physical weight (0.5–15.0 kg)
      volume_litre : physical volume (1–40 L)
      priority     : urgency level 1 (highest) → 5 (lowest)
      deadline_days: days until delivery must occur (1–7)
      value_score  : business value metric (10–100)

  delivery_graph.json — weighted undirected graph:
      nodes : 8 stops (Warehouse + A … G)
      edges : list of [u, v, distance_km] triples (≥ 15 edges)
      format: adjacency-list built at runtime for O(1) neighbour lookup

=============================================================================
"""

import csv
import json
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
PARCEL_CSV = os.path.join(DATA_DIR, "parcels.csv")
GRAPH_JSON = os.path.join(DATA_DIR, "delivery_graph.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def separator(char="=", width=72):
    print(char * width)

def section(title):
    separator()
    print(f"  {title}")
    separator()


def load_parcels(filepath):
    """Load parcels.csv and return a list of dicts with typed values."""
    parcels = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parcels.append({
                "parcel_id"    : row["parcel_id"],
                "weight_kg"    : float(row["weight_kg"]),
                "volume_litre" : float(row["volume_litre"]),
                "priority"     : int(row["priority"]),
                "deadline_days": int(row["deadline_days"]),
                "value_score"  : int(row["value_score"]),
            })
    return parcels


def load_graph(filepath):
    """Load delivery_graph.json and build an adjacency list."""
    with open(filepath) as f:
        raw = json.load(f)

    nodes = raw["nodes"]
    edges = raw["edges"]

    adj = {n: [] for n in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    return nodes, edges, adj


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_parcels(parcels):
    header = (f"{'ID':<6} {'Weight':>8} {'Volume':>8} {'Priority':>9}"
              f" {'Deadline':>9} {'Value':>7}")
    divider = "-" * len(header)
    print(header)
    print(divider)
    for p in parcels:
        print(f"{p['parcel_id']:<6} {p['weight_kg']:>7.1f}kg"
              f" {p['volume_litre']:>7.1f}L"
              f" {p['priority']:>9}"
              f" {p['deadline_days']:>8}d"
              f" {p['value_score']:>7}")


def print_adjacency_list(adj):
    for node, neighbours in sorted(adj.items()):
        nbr_str = "  |  ".join(f"{n} ({w:.1f} km)" for n, w in
                                sorted(neighbours, key=lambda x: x[1]))
        print(f"  {node:<12} → {nbr_str}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    separator("=")
    print("        MINI-COURIER PLANNER  —  PHASE 1: DESIGN OVERVIEW")
    separator("=")
    print()

    # ── Problem Statement ──────────────────────────────────────────────────
    section("1. PROBLEM STATEMENT")
    print("""
  A courier company wants a data-driven system to:
    (a) Rank parcels by urgency and value                (Sorting)
    (b) Pack the van within weight/volume limits         (0/1 Knapsack DP)
    (c) Find the shortest inter-stop distance            (Dijkstra)
    (d) Build a complete delivery tour                   (Nearest-Neighbour TSP)

  All four modules connect as a sequential pipeline — output from each
  stage feeds the next.
""")

    # ── Parcel Dataset ─────────────────────────────────────────────────────
    section("2. PARCEL DATASET  (parcels.csv)")
    parcels = load_parcels(PARCEL_CSV)
    print(f"\n  Loaded {len(parcels)} parcels:\n")
    print_parcels(parcels)
    print(f"""
  Attribute notes:
    weight_kg     → Van max: 50 kg   (physical constraint)
    volume_litre  → Van max: 100 L   (physical constraint)
    priority      → 1 = most urgent; drives Insertion Sort ordering
    deadline_days → Days until cutoff; primary key for Merge Sort
    value_score   → Business value; value/weight ratio drives Quick Sort
""")

    # ── Delivery Graph ─────────────────────────────────────────────────────
    section("3. DELIVERY GRAPH  (delivery_graph.json)")
    nodes, edges, adj = load_graph(GRAPH_JSON)
    print(f"\n  Nodes ({len(nodes)}): {', '.join(nodes)}")
    print(f"  Edges ({len(edges)}): undirected, weighted in km\n")
    print("  Adjacency List:")
    print_adjacency_list(adj)
    print(f"""
  Graph format:
    JSON schema  → {{"nodes": [...], "edges": [[u, v, km], ...]}}
    Runtime repr → Python dict: node → list of (neighbour, distance) tuples
    Undirected   → each edge stored in both directions for O(degree) lookup
""")

    # ── Algorithm Map ──────────────────────────────────────────────────────
    section("4. ALGORITHM SELECTION MAP")
    print("""
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Phase  │  Algorithm              │  Purpose                        │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  2      │  Merge Sort             │  Sort by deadline (asc) then    │
  │         │                         │  priority (asc)                 │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  2      │  Quick Sort             │  Sort by value/weight ratio     │
  │         │                         │  (desc) — highest value density │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  2      │  Insertion Sort         │  Sort by priority (asc) —       │
  │         │                         │  simplest, good for small n     │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  2      │  0/1 Knapsack DP        │  Select parcels maximising      │
  │         │  (dual-constraint)      │  value_score within 50 kg/100 L │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  3      │  Dijkstra's Algorithm   │  Minimum distance between any   │
  │         │                         │  two stops in the graph         │
  ├─────────┼─────────────────────────┼─────────────────────────────────┤
  │  3      │  Nearest-Neighbour TSP  │  Greedy tour visiting all       │
  │         │                         │  selected stops once            │
  └─────────┴─────────────────────────┴─────────────────────────────────┘
""")

    # ── Integration Pipeline ───────────────────────────────────────────────
    section("5. INTEGRATION PIPELINE")
    print("""
  Step 1 — SORTING (Phase 2)
    Input  : All 15 parcels from parcels.csv
    Process: Apply Merge Sort (deadline/priority), Quick Sort (value density),
             Insertion Sort (priority) to produce ranked lists.
    Output : Ordered parcel lists showing delivery preference.

  Step 2 — KNAPSACK (Phase 2)
    Input  : Ranked parcel list + van capacity (50 kg, 100 L)
    Process: 0/1 DP over weight × volume dimensions.
    Output : Selected subset — highest feasible value_score load.

  Step 3 — SHORTEST PATHS (Phase 3)
    Input  : delivery_graph.json + selected delivery stops
    Process: Dijkstra from Warehouse to each stop.
    Output : Distance matrix / shortest-path dictionary.

  Step 4 — TSP ROUTE (Phase 3)
    Input  : Distance matrix from Step 3
    Process: Nearest-Neighbour heuristic starting at Warehouse.
    Output : Ordered tour → Warehouse → … → Warehouse
""")

    separator()
    print("  Phase 1 design complete. Proceed to phase2_sorting_knapsack.py")
    separator()


if __name__ == "__main__":
    main()
