
"""
OPTIONAL EXTERNAL VERIFIER

This file is NOT part of the C++ implementation.
It uses Python's arbitrary-precision integers as a trusted external
reference for Task 7 of the lab.

The C++ implementation itself does not use these Python functions.
"""

import math
import random
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.name == "nt":
    EXE = os.path.join(BASE_DIR, "calculator.exe")
else:
    EXE = os.path.join(BASE_DIR, "calculator")


def run(*args):
    result = subprocess.run(
        [EXE] + [str(x) for x in args],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def check_gcd(a, b):
    cpp = int(run("gcd", a, b))
    reference = math.gcd(a, b)
    return cpp == reference


def check_inverse(a, m):
    if math.gcd(a, m) != 1:
        return run("inverse", a, m) == "NO_INVERSE"

    cpp = int(run("inverse", a, m))
    return (a * cpp) % m == 1


def check_pow(a, e, m):
    cpp = int(run("powfast", a, e, m))
    reference = pow(a, e, m)
    return cpp == reference


def main():
    for i in range(10):
        a = random.getrandbits(512)
        b = random.getrandbits(512)
        print(a)
        print()
        print(b)

        if b == 0:
            b = 1

        if not check_gcd(a, b):
            print("GCD verification FAILED")
            return

    for i in range(10):
        m = random.getrandbits(512) | 1
        a = random.randrange(1, m)

        if math.gcd(a, m) == 1:
            if not check_inverse(a, m):
                print("Inverse verification FAILED")
                return

    for i in range(10):
        m = random.getrandbits(512) | 1
        a = random.getrandbits(512)
        e = random.getrandbits(64)

        if not check_pow(a, e, m):
            print("Modular exponentiation verification FAILED")
            return

    print("All external verification tests passed.")


if __name__ == "__main__":
    main()
