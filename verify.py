import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent

try:
    A = np.loadtxt(ROOT / "A.txt", skiprows=1, dtype=np.int64)
    B = np.loadtxt(ROOT / "B.txt", skiprows=1, dtype=np.int64)
    C = np.loadtxt(ROOT / "C.txt", skiprows=1, dtype=np.int64)

    if A.shape != B.shape:
        raise ValueError("Input matrices have different dimensions")

    if A.shape != C.shape:
        raise ValueError("Result matrix has incorrect dimensions")

    expected = A @ B

    if np.array_equal(C, expected):
        print("OK: matrices match")
    else:
        print("ERROR: matrices do not match")

except (OSError, ValueError) as error:
    print(f"Verification error: {error}")
