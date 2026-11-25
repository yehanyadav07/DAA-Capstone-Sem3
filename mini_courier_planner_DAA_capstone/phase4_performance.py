"""
Mini-Courier Planner — Phase 4: Performance Analysis
=====================================================
Covers:
  1. Sorting algorithm comparisons  (Merge, Quick, Insertion, Built-in)
  2. Knapsack DP runtime scaling
  3. Dijkstra runtime scaling on randomly generated graphs
  4. ASCII horizontal bar chart of sorting runtimes
  5. Detailed Big-O analysis printed to console

Standard-library only: time, random, heapq, collections, copy, math, statistics
"""

import time
import random
import heapq
import copy
import math
import statistics
import collections

# Reproducible randomness
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# How many timing repetitions per experiment
REPS = 5

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def timed_runs(func, *args, reps=REPS):
    """
    Call func(*args) `reps` times and return (avg_seconds, all_times_list).
    Uses time.perf_counter() for high-resolution timing.
    A fresh deep-copy of each argument is passed so sorting doesn't mutate
    the original list between runs.
    """
    times = []
    for _ in range(reps):
        args_copy = tuple(copy.deepcopy(a) for a in args)
        t0 = time.perf_counter()
        func(*args_copy)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    avg = statistics.mean(times)
    return avg, times


def ms(seconds):
    """Convert seconds → milliseconds string."""
    return f"{seconds * 1000:.4f} ms"


def section(title):
    """Print a bold section header."""
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


# ─────────────────────────────────────────────────────────────────────────────
# SORTING ALGORITHMS  (implemented from scratch)
# ─────────────────────────────────────────────────────────────────────────────

def merge_sort(arr):
    """
    Merge Sort — O(n log n) time, O(n) auxiliary space.
    Divide-and-conquer: split in half, sort halves, merge.
    """
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    """Merge two sorted sublists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr, low=None, high=None):
    """
    Quick Sort — O(n log n) average, O(n²) worst, O(log n) stack space.
    Lomuto partition scheme with median-of-three pivot for better average perf.
    In-place sort: modifies `arr` directly.
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1
    if low < high:
        pivot_idx = _partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)


def _median_of_three(arr, low, high):
    """Pick median of first, middle, last as pivot index."""
    mid = (low + high) // 2
    triple = [(arr[low], low), (arr[mid], mid), (arr[high], high)]
    triple.sort()
    return triple[1][1]  # median index


def _partition(arr, low, high):
    """Lomuto partition; pivot placed at correct sorted position."""
    pivot_idx = _median_of_three(arr, low, high)
    # Swap pivot to end
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def insertion_sort(arr):
    """
    Insertion Sort — O(n²) time, O(1) space.
    Efficient for small or nearly sorted arrays.
    In-place sort.
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def builtin_sort(arr):
    """Python's Timsort — O(n log n) time, O(n) space."""
    arr.sort()


# ─────────────────────────────────────────────────────────────────────────────
# KNAPSACK  (0/1 DP)
# ─────────────────────────────────────────────────────────────────────────────

def knapsack_01(weights, values, capacity):
    """
    0/1 Knapsack via bottom-up DP.
    Time:  O(n * W)
    Space: O(n * W)  — full table kept for clarity
    """
    n = len(weights)
    # dp[i][w] = max value using first i items with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi = weights[i - 1]
        vi = values[i - 1]
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]  # don't take item i
            if wi <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - wi] + vi)
    return dp[n][capacity]


def generate_knapsack_instance(n, seed=RANDOM_SEED):
    """Generate a random knapsack problem of n items."""
    rng = random.Random(seed)
    weights  = [rng.randint(1, 20) for _ in range(n)]
    values   = [rng.randint(1, 100) for _ in range(n)]
    capacity = max(1, sum(weights) // 2)
    return weights, values, capacity


# ─────────────────────────────────────────────────────────────────────────────
# DIJKSTRA  (reused from phase 3, self-contained copy)
# ─────────────────────────────────────────────────────────────────────────────

INF = float("inf")


def dijkstra_perf(graph, source):
    """
    Dijkstra using a min-heap (lazy deletion).
    Time:  O((V + E) log V)
    Space: O(V)
    """
    dist = {node: INF for node in graph}
    dist[source] = 0
    visited = set()
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist


def generate_random_graph(n_nodes, seed=RANDOM_SEED):
    """
    Generate a random connected undirected weighted graph with n_nodes nodes.
    Strategy:
      1. Create a random spanning tree (guarantees connectivity).
      2. Add extra random edges to make it denser.
    """
    rng = random.Random(seed)
    nodes = [str(i) for i in range(n_nodes)]
    graph = collections.defaultdict(list)

    # Step 1: random spanning tree via shuffled node insertion
    shuffled = nodes[:]
    rng.shuffle(shuffled)
    for i in range(1, len(shuffled)):
        u = shuffled[i]
        v = shuffled[rng.randint(0, i - 1)]
        w = rng.randint(1, 20)
        graph[u].append((v, w))
        graph[v].append((u, w))

    # Step 2: add ~1.5*n extra random edges
    extra = int(1.5 * n_nodes)
    for _ in range(extra):
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v:
            w = rng.randint(1, 20)
            graph[u].append((v, w))
            graph[v].append((u, w))

    return dict(graph), nodes


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: SORTING COMPARISONS
# ─────────────────────────────────────────────────────────────────────────────

def run_sorting_benchmarks():
    section("SORTING ALGORITHM RUNTIME COMPARISON")

    sizes = [10, 100, 1000]

    # Pre-generate data once so all algorithms face the same input
    datasets = {}
    rng = random.Random(RANDOM_SEED)
    for n in sizes:
        datasets[n] = [rng.randint(0, 10_000) for _ in range(n)]

    algorithms = [
        ("Merge Sort",     merge_sort,     False),   # (name, func, in_place)
        ("Quick Sort",     quick_sort,     True),
        ("Insertion Sort", insertion_sort, True),
        ("Built-in Sort",  builtin_sort,   True),
    ]

    # results[algo_name][size] = avg_seconds
    results = {name: {} for name, _, _ in algorithms}

    col_w = 16
    size_cols = [f"n={n}" for n in sizes]
    header = f"  {'Algorithm':<{col_w}}" + "".join(f"  {c:>14}" for c in size_cols)
    print(header)
    print("  " + "-" * (col_w + 2 + 16 * len(sizes)))

    for name, func, in_place in algorithms:
        row = f"  {name:<{col_w}}"
        for n in sizes:
            data = datasets[n]

            if in_place:
                # func mutates arr in-place; wrap it so timed_runs works
                avg, _ = timed_runs(func, data)
            else:
                # merge_sort returns new list; pass arr as-is
                avg, _ = timed_runs(func, data)

            results[name][n] = avg
            row += f"  {ms(avg):>14}"
        print(row)

    return results, sizes


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: KNAPSACK RUNTIME SCALING
# ─────────────────────────────────────────────────────────────────────────────

def run_knapsack_benchmarks():
    section("KNAPSACK DP RUNTIME SCALING")

    item_counts = [10, 50, 100, 200]
    print(f"  {'Items (n)':<12}  {'Capacity':>10}  {'Avg Time':>14}")
    print("  " + "-" * 42)

    knapsack_results = {}
    for n in item_counts:
        weights, values, cap = generate_knapsack_instance(n)
        avg, _ = timed_runs(knapsack_01, weights, values, cap)
        knapsack_results[n] = avg
        print(f"  {n:<12}  {cap:>10}  {ms(avg):>14}")

    return knapsack_results


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: DIJKSTRA RUNTIME SCALING
# ─────────────────────────────────────────────────────────────────────────────

def run_dijkstra_benchmarks():
    section("DIJKSTRA RUNTIME SCALING (randomly generated graphs)")

    node_counts = [10, 50, 200]
    print(f"  {'Nodes (V)':<12}  {'Edges (≈)':>10}  {'Avg Time':>14}")
    print("  " + "-" * 42)

    dijkstra_results = {}
    for n in node_counts:
        graph, nodes = generate_random_graph(n)
        edge_count = sum(len(v) for v in graph.values()) // 2
        source = nodes[0]
        avg, _ = timed_runs(dijkstra_perf, graph, source)
        dijkstra_results[n] = avg
        print(f"  {n:<12}  {edge_count:>10}  {ms(avg):>14}")

    return dijkstra_results


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: ASCII BAR CHART
# ─────────────────────────────────────────────────────────────────────────────

def print_ascii_bar_chart(results, sizes):
    """
    Horizontal ASCII bar chart: one row per algorithm, one chart per dataset size.
    Bar length is proportional to the slowest algorithm's time.
    """
    section("ASCII RUNTIME BAR CHART  (sorting algorithms)")

    BAR_WIDTH = 40   # max number of '#' characters

    for n in sizes:
        print(f"\n  Dataset size n={n}:")
        print(f"  {'Algorithm':<17} | {'Bar (relative)':<{BAR_WIDTH}} | Time")
        print("  " + "-" * (17 + BAR_WIDTH + 20))

        algo_times = {name: results[name][n] for name in results}
        max_time = max(algo_times.values()) or 1e-9  # guard div-by-zero

        for name, t in algo_times.items():
            bar_len = max(1, int(round((t / max_time) * BAR_WIDTH)))
            bar = "#" * bar_len
            print(f"  {name:<17} | {bar:<{BAR_WIDTH}} | {ms(t)}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: ANALYSIS & OPTIMIZATION COMMENTARY
# ─────────────────────────────────────────────────────────────────────────────

ANALYSIS = """
╔══════════════════════════════════════════════════════════════════╗
║           ALGORITHM ANALYSIS & OPTIMIZATION NOTES               ║
╚══════════════════════════════════════════════════════════════════╝

─── SORTING ALGORITHMS ─────────────────────────────────────────────

│ Algorithm     │ Time (avg) │ Time (worst) │ Space  │ Stable? │
│ Merge Sort    │ O(n log n) │ O(n log n)   │ O(n)   │ Yes     │
│ Quick Sort    │ O(n log n) │ O(n²)        │ O(logn)│ No      │
│ Insertion Sort│ O(n²)      │ O(n²)        │ O(1)   │ Yes     │
│ Timsort(built)│ O(n log n) │ O(n log n)   │ O(n)   │ Yes     │

Observations:
  • Insertion Sort is fastest for tiny arrays (n=10) due to negligible overhead;
    its O(n²) becomes a severe bottleneck at n=1000.
  • Quick Sort with median-of-three beats naive Quick Sort and often beats Merge
    Sort in practice because of better cache locality (in-place).
  • Merge Sort guarantees O(n log n) even on adversarial inputs, making it
    preferable when worst-case guarantees matter.
  • Python's built-in sort (Timsort) is fastest overall because it's implemented
    in C and exploits natural runs in the data; it should be the default choice.

Suggested improvements:
  • Hybrid approach: use Insertion Sort for sub-arrays of size ≤ 16 inside
    Merge/Quick Sort (this is what Timsort does internally).
  • Intro Sort (std::sort in C++): Quick Sort → Heap Sort fallback when
    recursion depth exceeds 2·log₂(n) to guarantee O(n log n) worst-case.

─── KNAPSACK (0/1 DP) ──────────────────────────────────────────────

  Time Complexity:  O(n × W)   — pseudo-polynomial (W = capacity)
  Space Complexity: O(n × W)   — full DP table

Observations:
  • Runtime grows with both n and W.  For large capacities (e.g. W=10000)
    even n=50 can be slow.
  • Memory can be halved to O(W) by keeping only the previous DP row
    (space-optimised 1-D DP).

Suggested improvements:
  • Space optimisation: use a single 1-D array iterated in reverse.
  • For fractional items, use a greedy (sort by value/weight ratio) approach
    which is O(n log n) — far faster.
  • Branch-and-bound or meet-in-the-middle for exact solutions on larger n
    when W is huge.

─── DIJKSTRA'S ALGORITHM ───────────────────────────────────────────

  Time Complexity:  O((V + E) log V)  with binary heap (heapq)
  Space Complexity: O(V)

Observations:
  • The heap-based implementation scales well up to hundreds/thousands of nodes.
  • For dense graphs (E ~ V²), a Fibonacci heap reduces the time to O(E + V log V),
    but the constant factor is large; in practice the binary-heap version wins.
  • For unweighted graphs, BFS is O(V + E) — strictly faster.

Suggested improvements:
  • Bidirectional Dijkstra: run from both source and target simultaneously;
    terminates as soon as the frontiers meet — roughly halves the search space.
  • A* with an admissible heuristic (e.g. Euclidean distance for spatial graphs)
    can dramatically reduce explored nodes.
  • For TSP specifically, replace the naive O(n²) nearest-neighbor scan with a
    priority queue (heap) keyed on current shortest distance — reduces inner
    loop from O(n) to O(log n) per step.

─── OVERALL TAKEAWAYS ──────────────────────────────────────────────

  1. Always profile before optimising — Timsort is hard to beat in Python.
  2. Choose the right data structure: a heap makes Dijkstra and TSP faster.
  3. Space-time trade-offs matter: DP can be memory-heavy for large inputs.
  4. Algorithmic improvements (better Big-O) beat micro-optimisations for
     large n; for small n, constant factors dominate.
  5. Memoization / caching (functools.lru_cache) can convert exponential
     recursive algorithms to polynomial with zero change to logic.
"""


def print_analysis():
    section("ANALYSIS, BIG-O COMPLEXITIES & OPTIMIZATION SUGGESTIONS")
    print(ANALYSIS)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "#" * 65)
    print("  MINI-COURIER PLANNER — PHASE 4: PERFORMANCE ANALYSIS")
    print(f"  Random seed: {RANDOM_SEED} | Repetitions per experiment: {REPS}")
    print("#" * 65)

    # 1. Sorting
    sort_results, sizes = run_sorting_benchmarks()

    # 2. Knapsack
    run_knapsack_benchmarks()

    # 3. Dijkstra
    run_dijkstra_benchmarks()

    # 4. ASCII chart
    print_ascii_bar_chart(sort_results, sizes)

    # 5. Analysis
    print_analysis()

    print("\n[Phase 4 complete]\n")


if __name__ == "__main__":
    main()
