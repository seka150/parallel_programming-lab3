
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if len(sys.argv) != 2:
    print("Usage: python gen.py <size>")
    sys.exit(1)

try:
    n = int(sys.argv[1])
except ValueError:
    print("Error: size must be an integer")
    sys.exit(1)

if n <= 0:
    print("Error: size must be positive")
    sys.exit(1)

rng = np.random.default_rng()

A = rng.integers(0, 10, size=(n, n))
B = rng.integers(0, 10, size=(n, n))

with open(ROOT / "A.txt", "w") as file:
    file.write(f"{n}\n")
    np.savetxt(file, A, fmt="%d")

with open(ROOT / "B.txt", "w") as file:
    file.write(f"{n}\n")
    np.savetxt(file, B, fmt="%d")

print(f"Generated two {n}x{n} matrices")
