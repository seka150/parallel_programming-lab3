
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS_FILE = ROOT / "results.csv"

if not RESULTS_FILE.exists():
    print("Error: results.csv not found. Run experiment.py first.")
    sys.exit(1)

results = []

with open(RESULTS_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        results.append({
            "size": int(row["size"]),
            "processes": int(row["processes"]),
            "sequential": float(row["sequential_time_ms"]),
            "parallel": float(row["parallel_time_ms"]),
            "speedup": float(row["speedup"]),
            "efficiency": float(row["efficiency_percent"])
        })

if not results:
    print("Error: no experiment results")
    sys.exit(1)

process_counts = sorted(set(
    item["processes"] for item in results
))

# Execution time

for count in process_counts:
    selected = [
        item for item in results
        if item["processes"] == count
    ]

    plt.plot(
        [item["size"] for item in selected],
        [item["parallel"] for item in selected],
        marker="o",
        label=f"{count} process(es)"
    )

plt.xlabel("Matrix size (N x N)")
plt.ylabel("Execution time (ms)")
plt.title("MPI matrix multiplication performance")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(ROOT / "performance.png", dpi=150)
plt.close()

# Speedup

for count in process_counts:
    selected = [
        item for item in results
        if item["processes"] == count
    ]

    plt.plot(
        [item["size"] for item in selected],
        [item["speedup"] for item in selected],
        marker="o",
        label=f"{count} process(es)"
    )

plt.xlabel("Matrix size (N x N)")
plt.ylabel("Speedup")
plt.title("MPI speedup")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(ROOT / "speedup.png", dpi=150)
plt.close()

# Efficiency

for count in process_counts:
    selected = [
        item for item in results
        if item["processes"] == count
    ]

    plt.plot(
        [item["size"] for item in selected],
        [item["efficiency"] for item in selected],
        marker="o",
        label=f"{count} process(es)"
    )

plt.xlabel("Matrix size (N x N)")
plt.ylabel("Efficiency (%)")
plt.title("MPI parallel efficiency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(ROOT / "efficiency.png", dpi=150)
plt.close()

print("Graphs successfully created:")
print("performance.png")
print("speedup.png")
print("efficiency.png")
