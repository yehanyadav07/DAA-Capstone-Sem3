"""
===============================================================================
  Mini-Courier Planner - Main Entry Point
  Capstone Project: Design & Analysis of Algorithms (ETCCDA302)
  K.R. Mangalam University, Gurugram
===============================================================================
  This script orchestrates all 5 phases of the capstone project in sequence.
  Run this file to execute the complete courier planning pipeline.

  Usage:
      python main.py [--phase 1|2|3|4|5|all]

  Phases:
      Phase 1 - Design and Planning
      Phase 2 - Package Prioritization and Box Filling (Sorting + Knapsack)
      Phase 3 - Route Maker and Graph Processing (Dijkstra + TSP)
      Phase 4 - Performance Testing and Optimization
      Phase 5 - Final Report and Demonstration
===============================================================================
"""

import sys
import os
import time

# ─── Colour helpers (works on most terminals) ───────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"

def banner(title: str, color: str = CYAN) -> None:
    """Print a full-width banner."""
    width = 78
    print()
    print(color + "═" * width + RESET)
    print(color + BOLD + f"  {title}".center(width) + RESET)
    print(color + "═" * width + RESET)

def section(msg: str) -> None:
    print(f"\n{YELLOW}{BOLD}▶  {msg}{RESET}")

def run_phase(phase_num: int, module_name: str, phase_title: str, color: str) -> None:
    """Import and run a phase module."""
    banner(f"PHASE {phase_num}  –  {phase_title}", color)
    start = time.perf_counter()
    try:
        # Dynamically import the phase module
        import importlib
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            mod.main()
        elapsed = time.perf_counter() - start
        print(f"\n{GREEN}✔  Phase {phase_num} completed in {elapsed:.3f}s{RESET}")
    except ModuleNotFoundError:
        print(f"{RED}✘  Module '{module_name}' not found. "
              f"Ensure '{module_name}.py' exists in the project folder.{RESET}")
    except Exception as exc:
        print(f"{RED}✘  Error in Phase {phase_num}: {exc}{RESET}")
        import traceback; traceback.print_exc()

def main() -> None:
    # Ensure we run from the project root so relative imports work
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Determine which phases to run
    if len(sys.argv) >= 3 and sys.argv[1] == "--phase":
        selected = sys.argv[2].strip().lower()
        phases = [int(selected)] if selected != "all" else [1, 2, 3, 4, 5]
    else:
        phases = [1, 2, 3, 4, 5]

    banner("MINI-COURIER PLANNER  –  Capstone Project", MAGENTA)
    print(f"""
  {BOLD}Course  :{RESET} Design & Analysis of Algorithms (ETCCDA302)
  {BOLD}Faculty :{RESET} Dr. Shweta Agarwal
  {BOLD}Uni     :{RESET} K.R. Mangalam University, Gurugram, Haryana
  {BOLD}Running :{RESET} Phases {phases}
""")

    phase_map = {
        1: ("phase1_design",           "Courier Problem Design and Planning",          BLUE),
        2: ("phase2_sorting_knapsack", "Package Prioritization and Box Filling",       GREEN),
        3: ("phase3_graph_routing",    "Route Maker and Graph Processing",             CYAN),
        4: ("phase4_performance",      "Performance Testing and Optimization",         YELLOW),
        5: ("phase5_report",           "Final Report and Demonstration",               MAGENTA),
    }

    for p in phases:
        if p in phase_map:
            mod, title, col = phase_map[p]
            run_phase(p, mod, title, col)
            time.sleep(0.3)   # small pause between phases for readability
        else:
            print(f"{RED}Unknown phase: {p}{RESET}")

    banner("ALL SELECTED PHASES COMPLETE", MAGENTA)

if __name__ == "__main__":
    main()
