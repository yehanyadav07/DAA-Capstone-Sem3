"""
===============================================================================
  Mini-Courier Planner - Visualization & Output Generator
  Generates graphical plots and exports all phase logs for submission
===============================================================================
"""

import os
import sys
import json
import subprocess
import matplotlib.pyplot as plt
import numpy as np

def generate_charts():
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Sorting Runtimes Comparison Chart
    # -------------------------------------------------------------
    sizes = [10, 100, 1000]
    merge_sort_times = [0.0311, 0.3447, 3.8680]
    quick_sort_times = [0.0227, 0.1332, 1.7053]
    insertion_sort_times = [0.0061, 0.2038, 15.0788]
    builtin_sort_times = [0.0039, 0.0056, 0.1077]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart for n=1000
    x = np.arange(4)
    algorithms = ['Merge Sort', 'Quick Sort', 'Insertion Sort', 'Python Timsort']
    times_1000 = [3.8680, 1.7053, 15.0788, 0.1077]
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']

    bars = ax1.bar(algorithms, times_1000, color=colors, edgecolor='black', alpha=0.85)
    ax1.set_ylabel('Execution Time (milliseconds)', fontsize=11, fontweight='bold')
    ax1.set_title('Sorting Runtime Comparison at n = 1,000 Elements', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height:.2f} ms',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

    # Line chart across sizes (log scale)
    ax2.plot(sizes, merge_sort_times, marker='o', label='Merge Sort O(n log n)', color='#3498db', linewidth=2)
    ax2.plot(sizes, quick_sort_times, marker='s', label='Quick Sort O(n log n)', color='#2ecc71', linewidth=2)
    ax2.plot(sizes, insertion_sort_times, marker='^', label='Insertion Sort O(n²)', color='#e74c3c', linewidth=2)
    ax2.plot(sizes, builtin_sort_times, marker='d', label='Python Timsort', color='#9b59b6', linewidth=2)

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Input Size (n) [Log Scale]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Execution Time (ms) [Log Scale]', fontsize=11, fontweight='bold')
    ax2.set_title('Scalability Comparison across Input Sizes', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', frameon=True)
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    plt.suptitle('Mini-Courier Planner: Algorithm Performance Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    chart_path = os.path.join(outputs_dir, "runtime_comparison_chart.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[OK] Generated: {chart_path}")

    # -------------------------------------------------------------
    # 2. Delivery Route Map (Graph & Tour Visualisation)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 8))

    # Coordinates for nodes
    coords = {
        "Warehouse": (0, 0),
        "A": (2, 3),
        "B": (5, 4),
        "C": (8, 2),
        "D": (4, 1),
        "E": (5, -3),
        "F": (8, -1),
        "G": (9, -4)
    }

    # Load graph edges
    graph_path = os.path.join(os.path.dirname(__file__), "data", "delivery_graph.json")
    with open(graph_path, 'r') as f:
        graph_data = json.load(f)

    # Plot all graph edges in light gray
    for u, v, w in graph_data["edges"]:
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        ax.plot([x1, x2], [y1, y2], color='#bdc3c7', linestyle='--', linewidth=1.5, zorder=1)
        # edge label
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my, f"{w}km", color='#7f8c8d', fontsize=8, ha='center', va='center')

    # TSP Route: Warehouse → A → B → D → E → G → F → C → Warehouse
    route = ["Warehouse", "A", "B", "D", "E", "G", "F", "C", "Warehouse"]
    for i in range(len(route)-1):
        u, v = route[i], route[i+1]
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color='#e67e22', lw=2.5, mutation_scale=15),
                    zorder=2)
        # Annotate step number
        step_x = x1 + (x2 - x1) * 0.4
        step_y = y1 + (y2 - y1) * 0.4
        ax.text(step_x, step_y + 0.2, f"#{i+1}", color='#d35400', fontweight='bold', fontsize=10, zorder=4)

    # Draw nodes
    for node, (nx, ny) in coords.items():
        node_color = '#e74c3c' if node == "Warehouse" else '#3498db'
        node_size = 700 if node == "Warehouse" else 550
        ax.scatter(nx, ny, s=node_size, color=node_color, edgecolors='black', linewidth=1.5, zorder=3)
        ax.text(nx, ny, node, color='white', fontweight='bold', ha='center', va='center', fontsize=9, zorder=4)

    ax.set_title("Mini-Courier Delivery Route: Nearest-Neighbor TSP Tour (41.6 km)", fontsize=13, fontweight='bold')
    ax.axis('off')
    route_path = os.path.join(outputs_dir, "delivery_route_map.png")
    plt.savefig(route_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Generated: {route_path}")

def export_text_outputs():
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    scripts = {
        "phase1_design_spec.txt": "phase1_design.py",
        "phase2_sorting_knapsack_output.txt": "phase2_sorting_knapsack.py",
        "phase3_routes_output.txt": "phase3_graph_routing.py",
        "phase4_performance_report.txt": "phase4_performance.py",
        "phase5_final_report.txt": "phase5_report.py"
    }

    for out_file, script in scripts.items():
        out_path = os.path.join(outputs_dir, out_file)
        script_path = os.path.join(os.path.dirname(__file__), script)
        res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        with open(out_path, "w") as f:
            f.write(res.stdout)
        print(f"[OK] Exported: {out_path}")

if __name__ == "__main__":
    generate_charts()
    export_text_outputs()
    print("\n[SUCCESS] All submission artifacts & visual charts generated in outputs/ folder.")
