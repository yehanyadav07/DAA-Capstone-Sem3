# Mini-Courier Planner: Capstone Project Report & Viva Guide
**Course Title & Code:** Design & Analysis of Algorithms (ETCCDA302)  
**Programme & Semester:** B.Tech CSE & Specializations  
**Faculty Name:** Dr. Shweta Agarwal  
**Institution:** K.R. Mangalam University, Gurugram, Haryana  
**Maximum Marks:** 100 (Scaled down to 10 marks)  
**Mapped COs:** CO1, CO2, CO3, CO4 | Bloom's Level: L5 (Create / Evaluate)  

---

## 1. Executive Summary & Problem Formulation
The **Mini-Courier Planner** is an intelligent, integrated routing and logistics optimization system developed in Python. It solves two interdependent core challenges of last-mile delivery:
1. **Van Packing & Prioritization (The Loading Problem):** Selecting the most valuable and urgent subset of parcels from a given shipment list without exceeding the van's physical weight and volumetric constraints.
2. **Delivery Route Optimization (The Routing Problem):** Computing the optimal delivery sequence starting and ending at a central depot (Warehouse) that minimizes total transit distance across a road network.

The system combines four algorithmic paradigms taught across the DAA curriculum:
- **Divide & Conquer / Brute-Force / Incremental Sorting:** Merge Sort, Quick Sort, Insertion Sort
- **Dynamic Programming (DP):** 0/1 Dual-Constraint Knapsack Problem
- **Greedy Graph Algorithms:** Dijkstra's Single-Source Shortest Path Algorithm (using Min-Heaps)
- **Approximation Algorithms for NP-Hard Problems:** Nearest-Neighbor Heuristic for the Traveling Salesperson Problem (TSP)

---

## 2. Phase-by-Phase Architecture & Implementation

### Phase 1: Courier Problem Design and Planning (20 Marks)
- **Data Architecture:**
  - `data/parcels.csv`: 15 parcels with parameters: `parcel_id`, `weight_kg`, `volume_litre`, `priority` (1 = urgent, 5 = low), `deadline_days`, `value_score`.
  - `data/delivery_graph.json`: Weighted undirected graph consisting of 8 vertices (`Warehouse`, `A`, `B`, `C`, `D`, `E`, `F`, `G`) and 16 connecting roads with distance weights in kilometers.
- **Pipeline Flow:**
  $$\text{Parcels Dataset} \xrightarrow{\text{Multi-key Sorting}} \text{Ranked Queue} \xrightarrow{\text{Dual-Constraint 0/1 Knapsack DP}} \text{Loaded Shipment} \xrightarrow{\text{Dijkstra + NN-TSP}} \text{Optimal Tour}$$

### Phase 2: Package Prioritization and Box Filling (20 Marks)
1. **Sorting Implementations:**
   - **Merge Sort (Deadline & Priority):** Sorts stably by `(deadline_days ASC, priority ASC)` in $O(n \log n)$ time.
   - **Quick Sort (Value-to-Weight Ratio):** Sorts by $\frac{\text{value\_score}}{\text{weight\_kg}}$ DESC using Lomuto partitioning in average $O(n \log n)$ time.
   - **Insertion Sort (Priority Urgency):** Incremental sorting by `priority ASC` in $O(n^2)$ time.
2. **Dynamic Programming 0/1 Knapsack:**
   - **Constraints:** Van Weight Limit $W = 50.0\text{ kg}$, Van Volume Limit $V = 100.0\text{ L}$.
   - **State Formulation:**
     $$\text{DP}[w][v] = \max(\text{DP}[w][v], \text{DP}[w - \text{weight}_i][v - \text{volume}_i] + \text{value}_i)$$
   - **Result:** Selects **11 optimal parcels** (P001, P002, P003, P005, P006, P008, P010, P011, P013, P014, P015), achieving an optimal value score of **833**, utilizing **38.0 kg** (76%) and **89.0 L** (89%), while dropping low-value/bulky parcels (P004, P007, P009, P012).

### Phase 3: Route Maker & Graph Processing (20 Marks)
1. **Dijkstra's Shortest Path Algorithm:**
   - Implemented using a min-heap (`heapq`) achieving $O((V + E) \log V)$ time.
   - Computes all-pairs shortest path distance matrix and path trees across all nodes.
2. **Nearest-Neighbor TSP Approximation:**
   - Depot: `Warehouse`
   - Tour sequence:
     $$\text{Warehouse} \xrightarrow{4.2\text{km}} \text{A} \xrightarrow{3.8\text{km}} \text{B} \xrightarrow{4.7\text{km}} \text{D} \xrightarrow{3.3\text{km}} \text{E} \xrightarrow{4.5\text{km}} \text{G} \xrightarrow{3.0\text{km}} \text{F} \xrightarrow{7.1\text{km}} \text{C} \xrightarrow{11.0\text{km}} \text{Warehouse}$$
   - **Total Tour Distance:** **41.6 km**.

### Phase 4: Performance Testing & Optimization (20 Marks)
- Benchmarked across synthetic datasets ($n = 10, 100, 1000$ elements for sorting; $V = 10, 50, 200$ nodes for Dijkstra; $n = 10, 50, 100, 200$ items for Knapsack).
- **Sorting Runtimes ($n = 1000$):**
  - Insertion Sort: $15.08\text{ ms}$ ($O(n^2)$ degradation)
  - Merge Sort: $3.87\text{ ms}$ ($O(n \log n)$ stable)
  - Quick Sort: $1.71\text{ ms}$ ($O(n \log n)$ cache-efficient)
  - Python Timsort: $0.11\text{ ms}$ (C-optimized adaptive hybrid)
- **Optimization Recommendations:**
  - 2-Opt local search post-processing for TSP (reduces tour distance by 10-15%).
  - 1-D space-optimized DP array for knapsack ($O(W \cdot V)$ space reduction).
  - A* search with Euclidean heuristic for real-world GPS road networks.

### Phase 5: Final Report & Demonstration (20 Marks)
- Full end-to-end command line CLI with color-coded trace outputs (`main.py`).
- Exported text output reports and generated high-resolution PNG visualizations in `outputs/`.

---

## 3. Algorithm Complexity Matrix

| Algorithm | Paradigm | Time (Best) | Time (Average) | Time (Worst) | Space | Stability |
|---|---|---|---|---|---|---|
| **Insertion Sort** | Incremental | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes |
| **Merge Sort** | Divide & Conquer | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Yes |
| **Quick Sort** | Divide & Conquer | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ | $O(\log n)$ | No |
| **0/1 Knapsack DP** | Dynamic Prog. | $O(n \cdot W \cdot V)$ | $O(n \cdot W \cdot V)$ | $O(n \cdot W \cdot V)$ | $O(W \cdot V)$ | N/A |
| **Dijkstra's Algorithm** | Greedy / Heap | $O((V+E)\log V)$ | $O((V+E)\log V)$ | $O((V+E)\log V)$ | $O(V)$ | N/A |
| **Nearest-Neighbor TSP** | Greedy Approx. | $O(V^2)$ | $O(V^2)$ | $O(V^2)$ | $O(V)$ | N/A |

---

## 4. Comprehensive Viva Voce Questions & Model Answers

### Q1: Why use 0/1 Knapsack Dynamic Programming instead of a Greedy approach?
**Answer:** The Greedy approach (selecting items by highest value-to-weight ratio) is only optimal for the *Fractional Knapsack* problem, where items can be divided. In 0/1 Knapsack, an item must either be fully taken or left behind. Greedy fails because taking a high-ratio item can leave unused capacity that could have accommodated multiple items yielding a higher combined value. Dynamic Programming guarantees finding the global optimum by evaluating overlapping subproblems through memoization.

### Q2: What is the recurrence relation for the dual-constraint 0/1 Knapsack?
**Answer:**
$$\text{DP}[i][w][v] = \begin{cases} \text{DP}[i-1][w][v] & \text{if } w < \text{wt}_i \text{ or } v < \text{vol}_i \\ \max(\text{DP}[i-1][w][v], \text{DP}[i-1][w-\text{wt}_i][v-\text{vol}_i] + \text{val}_i) & \text{otherwise} \end{cases}$$
We reduced the space complexity by maintaining a 2D table $\text{DP}[w][v]$ and iterating $w$ and $v$ backwards from maximum capacity down to the item's requirements.

### Q3: Why is Dijkstra's algorithm preferred over Bellman-Ford or Floyd-Warshall here?
**Answer:** Road distances between physical delivery locations are strictly non-negative ($w(u, v) \ge 0$). Dijkstra's algorithm with a binary min-heap runs in $O((V+E)\log V)$, which is significantly faster than Bellman-Ford ($O(V \cdot E)$) and Floyd-Warshall ($O(V^3)$).

### Q4: Does Nearest-Neighbor heuristic always produce the optimal TSP tour?
**Answer:** No. TSP is NP-Hard. The Nearest-Neighbor heuristic is a greedy approximation algorithm. While it runs in $O(V^2)$ time, it makes locally optimal choices that can force the courier to make an unusually long final jump back to the warehouse. In metric graphs obeying the triangle inequality, 2-Opt or Christofides algorithm ($1.5$-approximation) can further refine the route.

### Q5: Why is Merge Sort preferred for deadline prioritization while Quick Sort is used for ratio ranking?
**Answer:** Merge Sort is **stable**—it preserves the relative ordering of elements with identical keys. This ensures that when sorting primarily by deadline, equal deadline items retain their secondary priority order. Quick Sort is in-place and has better cache locality, making it faster when stability is not required.

---

## 5. Execution Steps
To execute the complete application:
```bash
# Navigate to the project root
cd /home/tushar/Downloads/mini_courier_planner

# Run the complete automated pipeline
python3 main.py

# Run specific phases independently
python3 phase1_design.py
python3 phase2_sorting_knapsack.py
python3 phase3_graph_routing.py
python3 phase4_performance.py
python3 phase5_report.py

# Regenerate all visual charts and output reports
python3 generate_visualizations.py
```
