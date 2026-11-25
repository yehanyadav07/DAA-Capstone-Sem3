"""
=============================================================================
MINI-COURIER PLANNER — PHASE 2: SORTING & KNAPSACK
=============================================================================

This module implements:
  A) Three sorting algorithms applied to the parcel dataset
       1. Merge Sort   — by deadline_days (asc), then priority (asc)
       2. Quick Sort   — by value_score / weight_kg ratio (desc)
       3. Insertion Sort — by priority (asc)

  B) Dual-constraint 0/1 Knapsack via Dynamic Programming
       Van capacity : 50 kg weight  &  100 litre volume
       Objective    : maximise total value_score of packed parcels

All algorithms are implemented from scratch (no built-in sort used for
the primary ordering).  Standard library modules only (csv, copy, os).
=============================================================================
"""

import csv
import copy
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PARCEL_CSV = os.path.join(BASE_DIR, "data", "parcels.csv")

# Van capacity constants
MAX_WEIGHT = 50    # kg
MAX_VOLUME = 100   # litres

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def separator(char="=", width=72):
    print(char * width)

def section(title):
    separator()
    print(f"  {title}")
    separator()

def print_parcel_table(parcels, extra_col=None, extra_header=None):
    """Pretty-print a list of parcel dicts.

    Args:
        parcels      : list of parcel dicts
        extra_col    : optional callable(parcel) → formatted string for an
                       extra right-hand column
        extra_header : header text for the extra column
    """
    hdr = (f"{'#':>3}  {'ID':<6} {'Weight':>8} {'Volume':>8}"
           f" {'Pri':>4} {'Deadline':>9} {'Value':>7}")
    if extra_col and extra_header:
        hdr += f"  {extra_header:>12}"
    divider = "-" * len(hdr)
    print(hdr)
    print(divider)
    for idx, p in enumerate(parcels, 1):
        row = (f"{idx:>3}  {p['parcel_id']:<6} {p['weight_kg']:>7.1f}kg"
               f" {p['volume_litre']:>7.1f}L"
               f" {p['priority']:>4} {p['deadline_days']:>8}d"
               f" {p['value_score']:>7}")
        if extra_col:
            row += f"  {extra_col(p):>12}"
        print(row)
    print()


def load_parcels(filepath):
    """Load parcels.csv → list of typed dicts."""
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


# ===========================================================================
# SECTION A — SORTING ALGORITHMS
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. MERGE SORT
#    Key: (deadline_days ASC, priority ASC)
#    Rationale: parcels due soonest and most urgent should be delivered first.
# ---------------------------------------------------------------------------

def _merge(left, right, key_fn):
    """Merge two sorted sublists using key_fn for comparison.

    Merge sort is stable; equal keys preserve original relative order.
    Time complexity: O(n)  |  Space: O(n)
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_fn(left[i]) <= key_fn(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr, key_fn, depth=0, verbose=False):
    """Recursive merge sort.

    Args:
        arr     : list to sort (not mutated; returns a new sorted list)
        key_fn  : callable returning a comparable key per element
        depth   : recursion depth (used for verbose indentation)
        verbose : if True, prints merge operations at depth <= 2
    Returns:
        Sorted list (new object).
    """
    if len(arr) <= 1:
        return list(arr)

    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid],  key_fn, depth + 1, verbose)
    right = merge_sort(arr[mid:],  key_fn, depth + 1, verbose)
    merged = _merge(left, right, key_fn)

    if verbose and depth <= 2:
        ids_left   = [p["parcel_id"] for p in left]
        ids_right  = [p["parcel_id"] for p in right]
        ids_merged = [p["parcel_id"] for p in merged]
        indent = "  " * depth
        print(f"{indent}[depth={depth}] MERGE  "
              f"{ids_left} + {ids_right} → {ids_merged}")

    return merged


def run_merge_sort(parcels):
    section("SORT 1 — MERGE SORT  (deadline_days ASC, then priority ASC)")

    print("""
  Merge sort divides the array in half recursively, then merges sorted
  halves back together.  It guarantees O(n log n) time in all cases and
  is stable — parcels with identical keys keep their original order.

  KEY FUNCTION : (deadline_days, priority)   — both ascending

  Below are selected merge operations at recursion depth ≤ 2:
""")

    key_fn = lambda p: (p["deadline_days"], p["priority"])
    data   = copy.deepcopy(parcels)
    sorted_parcels = merge_sort(data, key_fn, depth=0, verbose=True)

    print("\n  ── Final Sorted Result ──")
    print_parcel_table(
        sorted_parcels,
        extra_col=lambda p: f"({p['deadline_days']}d, pri={p['priority']})",
        extra_header="Sort Key"
    )

    print("  ✔ ANALYSIS: Merge Sort is ideal here because the dataset may")
    print("    arrive pre-sorted by other criteria. Its O(n log n) worst-case")
    print("    and stability make it the safest choice for multi-key ordering.")
    print()
    return sorted_parcels


# ---------------------------------------------------------------------------
# 2. QUICK SORT
#    Key: value_score / weight_kg  DESCENDING  (highest value density first)
#    Rationale: load the most profit per kg first when space is limited.
# ---------------------------------------------------------------------------

def _partition(arr, low, high, key_fn, pivot_log):
    """Lomuto partition scheme.

    Chooses arr[high] as pivot; places it in its correct sorted position.
    Elements with key ≥ pivot (descending) go to the left partition.
    """
    pivot     = arr[high]
    pivot_key = key_fn(pivot)
    i         = low - 1          # boundary of "greater-than-pivot" region

    pivot_log.append(
        f"    Pivot={pivot['parcel_id']} (ratio={pivot_key:.3f})"
        f"  range=[{low}..{high}]"
    )

    for j in range(low, high):
        if key_fn(arr[j]) >= pivot_key:   # descending: keep larger left
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quick_sort(arr, low, high, key_fn, pivot_log):
    """In-place recursive quick sort (Lomuto)."""
    if low < high:
        pi = _partition(arr, low, high, key_fn, pivot_log)
        _quick_sort(arr, low,     pi - 1, key_fn, pivot_log)
        _quick_sort(arr, pi + 1,  high,   key_fn, pivot_log)


def run_quick_sort(parcels):
    section("SORT 2 — QUICK SORT  (value_score / weight_kg  DESC)")

    print("""
  Quick sort picks a pivot, partitions elements into two groups (those
  with key ≥ pivot on the left for descending order, rest on the right),
  then recursively sorts each partition.  Average O(n log n), O(n²) worst.

  KEY FUNCTION : value_score ÷ weight_kg  — descending (best density first)

  Pivot selections (Lomuto scheme, pivot = last element of sub-array):
""")

    key_fn    = lambda p: p["value_score"] / p["weight_kg"]
    data      = copy.deepcopy(parcels)
    pivot_log = []

    _quick_sort(data, 0, len(data) - 1, key_fn, pivot_log)

    for line in pivot_log:
        print(line)

    print("\n  ── Final Sorted Result ──")
    print_parcel_table(
        data,
        extra_col=lambda p: f"{p['value_score']/p['weight_kg']:.2f}",
        extra_header="val/kg ratio"
    )

    print("  ✔ ANALYSIS: Quick Sort excels at value-density ranking because")
    print("    the in-place partitioning uses O(log n) stack space and is")
    print("    cache-friendly — faster in practice than Merge Sort for this")
    print("    single numeric key on a small-to-medium dataset.")
    print()
    return data


# ---------------------------------------------------------------------------
# 3. INSERTION SORT
#    Key: priority  ASCENDING  (priority 1 = most urgent)
#    Rationale: list is likely nearly sorted by priority already; insertion
#               sort shines on nearly-sorted data with O(n) best-case.
# ---------------------------------------------------------------------------

def run_insertion_sort(parcels):
    section("SORT 3 — INSERTION SORT  (priority ASC)")

    print("""
  Insertion sort builds the sorted list one element at a time by inserting
  each new element into its correct position among already-sorted elements.
  Best case O(n) when already sorted; worst O(n²) — good for small n.

  KEY FUNCTION : priority   — ascending (1 = highest urgency)

  Showing each insertion step:
""")

    data = copy.deepcopy(parcels)
    n    = len(data)

    print(f"  {'Step':>5}  {'Inserting':>10}  {'pri':>4}  Action")
    print("  " + "-" * 50)

    for i in range(1, n):
        key_item = data[i]
        key_val  = key_item["priority"]
        j = i - 1

        # Count how many positions we shift
        shifts = 0
        while j >= 0 and data[j]["priority"] > key_val:
            data[j + 1] = data[j]
            j -= 1
            shifts += 1

        data[j + 1] = key_item
        action = f"shifted {shifts} element(s) left" if shifts else "already in place"
        print(f"  {i:>5}  {key_item['parcel_id']:>10}  {key_val:>4}  {action}")

    print("\n  ── Final Sorted Result ──")
    print_parcel_table(
        data,
        extra_col=lambda p: f"priority={p['priority']}",
        extra_header="Sort Key"
    )

    print("  ✔ ANALYSIS: Insertion Sort is ideal for small datasets (n=15)")
    print("    and nearly-sorted sequences.  It sorts in-place with O(1)")
    print("    extra space.  For this 15-parcel list it is fast enough and")
    print("    the step-by-step trace is intuitive for demonstration.")
    print()
    return data


# ===========================================================================
# SECTION B — DUAL-CONSTRAINT 0/1 KNAPSACK (DYNAMIC PROGRAMMING)
# ===========================================================================

def knapsack_dual(parcels, max_weight, max_volume):
    """0/1 Knapsack with dual constraints: weight AND volume.

    State: dp[i][w][v] = maximum value_score using first i items,
                         with at most w kg weight and v litres volume.

    Because storing the full 3-D table uses O(n * W * V) memory, we keep
    only the current and previous layers (rolling array trick).

    Args:
        parcels    : list of parcel dicts (order matters for DP trace)
        max_weight : int, van weight capacity in kg
        max_volume : int, van volume capacity in litres

    Returns:
        (selected_ids, total_weight, total_volume, total_value, dp_prev)
        where dp_prev is the final DP layer for the snippet display.
    """
    n = len(parcels)

    # Integer-scale weights & volumes for DP indices (already integers here)
    weights  = [int(round(p["weight_kg"]))    for p in parcels]
    volumes  = [int(round(p["volume_litre"])) for p in parcels]
    values   = [p["value_score"]               for p in parcels]

    W = max_weight
    V = max_volume

    # Initialise DP table: (W+1) x (V+1) grid of zeros
    # We use two layers: prev (item i-1) and curr (item i)
    prev = [[0] * (V + 1) for _ in range(W + 1)]

    # --- Forward pass -------------------------------------------------------
    for i in range(n):
        curr = [[0] * (V + 1) for _ in range(W + 1)]
        wi, vi, val = weights[i], volumes[i], values[i]

        for w in range(W + 1):
            for v in range(V + 1):
                # Option 1: skip item i
                curr[w][v] = prev[w][v]
                # Option 2: take item i (if it fits)
                if w >= wi and v >= vi:
                    take = prev[w - wi][v - vi] + val
                    if take > curr[w][v]:
                        curr[w][v] = take
        prev = curr

    best_value = prev[W][V]

    # --- Back-track to find which items were selected -----------------------
    selected = []
    w, v = W, V
    for i in range(n - 1, -1, -1):
        wi, vi, val = weights[i], volumes[i], values[i]
        # Reconstruct previous layer for item i (re-run the DP for that item)
        # We compare current cell with what it would have been without item i.
        # Efficient reconstruction: check if value changed from skipping.
        if w >= wi and v >= vi:
            # Value if we did NOT include item i
            # We need prev_prev[w - wi][v - vi] + val == prev[w][v]
            # Recompute by running DP again up to i-1 — simpler: use the
            # inclusion indicator: selected if prev[w][v] != prev[w-wi][v-vi]+val
            # We'll re-derive by rebuilding one column.
            pass

        selected.append(i)   # placeholder; replaced below

    # Cleaner back-track: rebuild all layers and store them
    layers = [[[0] * (V + 1) for _ in range(W + 1)]]
    for i in range(n):
        prev_layer = layers[-1]
        curr_layer = [[0] * (V + 1) for _ in range(W + 1)]
        wi, vi, val = weights[i], volumes[i], values[i]
        for w2 in range(W + 1):
            for v2 in range(V + 1):
                curr_layer[w2][v2] = prev_layer[w2][v2]
                if w2 >= wi and v2 >= vi:
                    take = prev_layer[w2 - wi][v2 - vi] + val
                    if take > curr_layer[w2][v2]:
                        curr_layer[w2][v2] = take
        layers.append(curr_layer)

    # Back-track using stored layers
    selected = []
    w, v = W, V
    for i in range(n - 1, -1, -1):
        wi, vi, val = weights[i], volumes[i], values[i]
        if layers[i + 1][w][v] != layers[i][w][v]:
            selected.append(i)
            w -= wi
            v -= vi

    selected.reverse()
    return selected, layers[-1], weights, volumes, values


def run_knapsack(parcels):
    section("DP KNAPSACK  —  Dual-Constraint 0/1 (weight ≤ 50 kg, volume ≤ 100 L)")

    print(f"""
  Van capacity  : {MAX_WEIGHT} kg weight   |   {MAX_VOLUME} litres volume
  Objective     : maximise total value_score of selected parcels
  Algorithm     : 0/1 Knapsack via Dynamic Programming
  State space   : dp[item][weight][volume]
  Table size    : {len(parcels)+1} items × {MAX_WEIGHT+1} weight states × {MAX_VOLUME+1} volume states
                  = {(len(parcels)+1) * (MAX_WEIGHT+1) * (MAX_VOLUME+1):,} cells

  Transition:
    dp[i][w][v] = max( dp[i-1][w][v],                              ← skip
                       dp[i-1][w-wi][v-vi] + value_i  if fits )    ← take
""")

    # Integer weights/volumes for DP
    weights  = [int(round(p["weight_kg"]))    for p in parcels]
    volumes  = [int(round(p["volume_litre"])) for p in parcels]
    values   = [p["value_score"]               for p in parcels]

    n = len(parcels)
    W = MAX_WEIGHT
    V = MAX_VOLUME

    # Build all layers (kept for back-tracking + snippet display)
    print("  Running DP... (this may store up to {:,} integers)".format(
        (n + 1) * (W + 1) * (V + 1)))

    layers = [[[0] * (V + 1) for _ in range(W + 1)]]
    for i in range(n):
        prev_layer = layers[-1]
        curr_layer = [[0] * (V + 1) for _ in range(W + 1)]
        wi, vi, val = weights[i], volumes[i], values[i]
        for w in range(W + 1):
            for v in range(V + 1):
                curr_layer[w][v] = prev_layer[w][v]
                if w >= wi and v >= vi:
                    take = prev_layer[w - wi][v - vi] + val
                    if take > curr_layer[w][v]:
                        curr_layer[w][v] = take
        layers.append(curr_layer)

    best_value = layers[n][W][V]

    # Back-track
    selected_indices = []
    w, v = W, V
    for i in range(n - 1, -1, -1):
        wi, vi = weights[i], volumes[i]
        if layers[i + 1][w][v] != layers[i][w][v]:
            selected_indices.append(i)
            w -= wi
            v -= vi
    selected_indices.reverse()

    selected_parcels  = [parcels[i] for i in selected_indices]
    excluded_parcels  = [parcels[i] for i in range(n) if i not in selected_indices]

    total_weight = sum(weights[i] for i in selected_indices)
    total_volume = sum(volumes[i] for i in selected_indices)
    total_value  = sum(values[i]  for i in selected_indices)

    # ── DP Snippet ─────────────────────────────────────────────────────────
    print("\n  ── DP Table Snippet  (weight axis 0–10, volume axis 0–20) ──")
    print("     Showing dp after each of the first 5 items processed.")
    print()

    snippet_w = min(10, W)
    snippet_v = min(20, V)

    for layer_idx in range(1, min(6, n + 1)):
        pid = parcels[layer_idx - 1]["parcel_id"]
        print(f"     After item {layer_idx} ({pid},"
              f" w={weights[layer_idx-1]}kg, v={volumes[layer_idx-1]}L,"
              f" val={values[layer_idx-1]}):")
        # Print volume header
        hdr = "       w\\v |" + "".join(f"{vv:4}" for vv in range(0, snippet_v + 1, 4))
        print(hdr)
        print("       " + "-" * (len(hdr) - 7))
        for ww in range(0, snippet_w + 1, 2):
            row = f"       {ww:>4}  |" + "".join(
                f"{layers[layer_idx][ww][vv]:4}"
                for vv in range(0, snippet_v + 1, 4)
            )
            print(row)
        print()

    # ── Results ────────────────────────────────────────────────────────────
    separator("-")
    print("  SELECTED PARCELS  (packed into van)")
    separator("-")
    print_parcel_table(selected_parcels)
    print(f"  Total weight : {total_weight} kg  (capacity {MAX_WEIGHT} kg,"
          f" used {100*total_weight/MAX_WEIGHT:.1f}%)")
    print(f"  Total volume : {total_volume} L   (capacity {MAX_VOLUME} L,"
          f" used {100*total_volume/MAX_VOLUME:.1f}%)")
    print(f"  Total value  : {total_value}  (sum of value_score)")
    print()

    separator("-")
    print("  EXCLUDED PARCELS  (did not fit or not worth packing)")
    separator("-")
    if excluded_parcels:
        print_parcel_table(excluded_parcels)
    else:
        print("  (none — all parcels fit!)\n")

    print(f"  ✔ Optimal value_score = {best_value}")
    print("    The DP guarantees this is the global optimum for 0/1 knapsack.")
    print()

    return selected_parcels


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    separator("=")
    print("      MINI-COURIER PLANNER  —  PHASE 2: SORTING & KNAPSACK DP")
    separator("=")
    print()

    # Load data
    parcels = load_parcels(PARCEL_CSV)
    print(f"  Loaded {len(parcels)} parcels from parcels.csv\n")

    # ── SORTING ─────────────────────────────────────────────────────────────
    merge_sorted    = run_merge_sort(parcels)
    quick_sorted    = run_quick_sort(parcels)
    insertion_sorted = run_insertion_sort(parcels)

    # ── SORTING COMPARISON ──────────────────────────────────────────────────
    section("SORTING ALGORITHM COMPARISON SUMMARY")
    print("""
  ┌──────────────────┬──────────────┬────────────┬──────────────────────────┐
  │ Algorithm        │ Time (avg)   │ Space      │ Best Use Case            │
  ├──────────────────┼──────────────┼────────────┼──────────────────────────┤
  │ Merge Sort       │ O(n log n)   │ O(n)       │ Stable multi-key sort;   │
  │                  │ always       │ extra       │ deadline + priority here  │
  ├──────────────────┼──────────────┼────────────┼──────────────────────────┤
  │ Quick Sort       │ O(n log n)   │ O(log n)   │ Single numeric key;      │
  │                  │ average      │ stack       │ value-density ranking     │
  ├──────────────────┼──────────────┼────────────┼──────────────────────────┤
  │ Insertion Sort   │ O(n)  best   │ O(1)       │ Small / nearly-sorted    │
  │                  │ O(n²) worst  │ in-place   │ data; priority list here  │
  └──────────────────┴──────────────┴────────────┴──────────────────────────┘

  RECOMMENDATION: Merge Sort for final production use — O(n log n) guaranteed,
  stable, and handles compound keys cleanly.  Quick Sort wins on single-key
  numeric sorts in practice.  Insertion Sort is a good educational choice for
  the tiny n=15 dataset.
""")

    # ── KNAPSACK ─────────────────────────────────────────────────────────────
    # Use the merge-sorted order as input to the knapsack (deadline priority)
    selected = run_knapsack(merge_sorted)

    separator("=")
    print("  Phase 2 complete.")
    print(f"  → {len(selected)} parcels selected for loading.")
    print(f"  → Pass selected parcel IDs to Phase 3 (Dijkstra + TSP).")
    separator("=")


if __name__ == "__main__":
    main()
