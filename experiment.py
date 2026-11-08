
import csv
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PROGRAM = ROOT / "build" / "matrix"
GENERATOR = ROOT / "gen.py"

SIZES = [200, 400, 800, 1200, 1600, 2000]
PROCESS_COUNTS = [1, 2, 4, 8]

REPEATS = 3

MPI_COMMAND = shlex.split(
    os.environ.get("MPI_COMMAND", "mpirun")
)
MPI_NUMPROC_FLAG = os.environ.get(
    "MPI_NUMPROC_FLAG", "-np"
)

if not PROGRAM.exists():
    print("Error: MPI program not found.")
    print("Build the project first using CMake.")
    sys.exit(1)

if not GENERATOR.exists():
    print("Error: gen.py not found.")
    sys.exit(1)

if not MPI_COMMAND:
    print("Error: MPI command is empty.")
    sys.exit(1)

results = []

for n in SIZES:

    print(f"\nGenerating matrices: {n}x{n}")

    subprocess.run(
        [sys.executable, str(GENERATOR), str(n)],
        cwd=ROOT,
        check=True
    )

    for process_count in PROCESS_COUNTS:

        sequential_times = []
        parallel_times = []

        print(f"\nRunning with {process_count} MPI process(es)")

        for repeat in range(REPEATS):

            command = (
                MPI_COMMAND
                + [
                    MPI_NUMPROC_FLAG,
                    str(process_count),
                    str(PROGRAM)
                ]
            )

            try:
                process = subprocess.run(
                    command,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as error:
                print("Error: MPI execution failed.")
                print(error.stdout or "")
                print(error.stderr or "")
                sys.exit(1)

            sequential_match = re.search(
                r"Sequential time:\s*([\d.]+)\s*ms",
                process.stdout
            )

            parallel_match = re.search(
                r"Parallel time:\s*([\d.]+)\s*ms",
                process.stdout
            )

            if sequential_match is None or parallel_match is None:
                print("Error: execution times not found.")
                print(process.stdout)
                print(process.stderr)
                sys.exit(1)

            sequential_times.append(
                float(sequential_match.group(1))
            )

            parallel_times.append(
                float(parallel_match.group(1))
            )

            print(
                f"  Run {repeat + 1}/{REPEATS}: "
                f"{parallel_times[-1]:.3f} ms"
            )

        sequential_average = (
            sum(sequential_times) / REPEATS
        )

        parallel_average = (
            sum(parallel_times) / REPEATS
        )

        speedup = (
            sequential_average / parallel_average
            if parallel_average > 0 else 0.0
        )

        efficiency = speedup / process_count * 100

        results.append((
            n,
            process_count,
            sequential_average,
            parallel_average,
            speedup,
            efficiency
        ))

        print(
            f"Size: {n}x{n}, "
            f"processes: {process_count}, "
            f"sequential: {sequential_average:.3f} ms, "
            f"parallel: {parallel_average:.3f} ms, "
            f"speedup: {speedup:.3f}x, "
            f"efficiency: {efficiency:.2f}%"
        )

# Save results to CSV

with open(ROOT / "results.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "size",
        "processes",
        "sequential_time_ms",
        "parallel_time_ms",
        "speedup",
        "efficiency_percent"
    ])

    writer.writerows(results)

print("\nExperiments completed!")
print("Saved results.csv")
print("\nRun plot.py to generate graphs.")
