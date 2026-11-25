# Mini-Courier Planner
### Capstone Project — Design & Analysis of Algorithms (ETCCDA302)
**K.R. Mangalam University, Gurugram, Haryana**
**Faculty:** Dr. Shweta Agarwal

---

## Project Overview

This project is a **Mini-Courier Planner** prototype that integrates four key algorithmic paradigms:
- **Sorting Algorithms** – to prioritise parcels
- **Dynamic Programming (0/1 Knapsack)** – to optimise van loading
- **Dijkstra's Algorithm** – to find shortest delivery paths
- **Nearest-Neighbor TSP** – to generate an efficient delivery route

---

## Project Structure

```
mini_courier_planner/
├── main.py                      # Runs all phases in sequence
├── phase1_design.py             # Phase 1: Design & Planning
├── phase2_sorting_knapsack.py   # Phase 2: Sorting + Knapsack DP
├── phase3_graph_routing.py      # Phase 3: Dijkstra + TSP
├── phase4_performance.py        # Phase 4: Runtime benchmarks
├── phase5_report.py             # Phase 5: Final report & demo
├── data/
│   ├── parcels.csv              # 15 sample parcels
│   └── delivery_graph.json      # Road network (8 nodes, 15 edges)
├── outputs/                     # Generated results
└── README.md                    # This file
```

---

## Setup & Execution

### Requirements
- Python 3.8 or higher
- No external libraries required (only standard library)

### Run the Full Pipeline
```bash
cd mini_courier_planner
python main.py
```

### Run a Single Phase
```bash
python main.py --phase 1    # Design & Planning
python main.py --phase 2    # Sorting + Knapsack
python main.py --phase 3    # Graph + Routes
python main.py --phase 4    # Performance Testing
python main.py --phase 5    # Final Report
```

### Run Individual Phase Files Directly
```bash
python phase1_design.py
python phase2_sorting_knapsack.py
python phase3_graph_routing.py
python phase4_performance.py
python phase5_report.py
```

---

## Phase Descriptions

### Phase 1 – Courier Problem Design and Planning (20 marks)
- Defines parcel attributes and delivery graph format
- Explains the integration of all four algorithms
- Visualises the graph structure as an adjacency list

### Phase 2 – Package Prioritization and Box Filling (20 marks)
- **Sorting:** Implements Merge Sort, Quick Sort, and Insertion Sort from scratch
  - Merge Sort: sort by deadline then priority
  - Quick Sort: sort by value-to-weight ratio
  - Insertion Sort: sort by priority
- **Knapsack DP:** Dual-constraint 0/1 knapsack (50 kg / 100 L van capacity)
  - Selects optimal parcel subset to maximise value_score

### Phase 3 – Route Maker and Graph Processing (20 marks)
- Builds adjacency list from delivery_graph.json
- **Dijkstra's Algorithm:** Finds shortest paths from Warehouse to all nodes
- **Nearest-Neighbor TSP:** Greedy route covering all delivery stops

### Phase 4 – Performance Testing and Optimization (20 marks)
- Benchmarks sorting algorithms on small/medium/large datasets
- Times Dijkstra on graphs of various sizes
- Displays ASCII runtime bar chart
- Provides Big-O complexity analysis and improvement suggestions

### Phase 5 – Final Report and Demonstration (20 marks)
- Comprehensive final report with algorithm analysis
- Complexity summary table
- Design decisions and reflections
- Full submission checklist

---

## Algorithms Used

| Algorithm      | Phase | Time Complexity   | Space Complexity |
|----------------|-------|-------------------|-----------------|
| Insertion Sort | 2     | O(n²)             | O(1)            |
| Merge Sort     | 2     | O(n log n)        | O(n)            |
| Quick Sort     | 2     | O(n log n) avg    | O(log n)        |
| 0/1 Knapsack   | 2     | O(n·W·V)          | O(W·V)          |
| Dijkstra       | 3     | O((V+E) log V)    | O(V)            |
| Nearest-Nbr TSP| 3     | O(V²)             | O(V)            |

---

## Sample Data

**parcels.csv** – 15 parcels with attributes: `parcel_id, weight_kg, volume_litre, priority, deadline_days, value_score`

**delivery_graph.json** – Road network: 8 nodes (Warehouse, A–G), 15 weighted edges

---

## Submission
- Source code: all `.py` files in this folder
- Data: `data/` directory
- Documentation: this `README.md`
- Phase 5 produces the final demonstration output
