
LAB 1 - MODULAR ARITHMETIC AND EXTENDED EUCLIDEAN ALGORITHM
============================================================

FILES
-----
main.cpp
    C++ implementation of:
    1. Euclidean GCD
    2. Extended Euclidean Algorithm
    3. Bezout coefficients x,y where ax+by=gcd(a,b)
    4. Modular inverse
    5. Modular addition
    6. Modular multiplication
    7. Modular exponentiation by square-and-multiply
    8. Naive modular exponentiation for the experiment

ui.py
    Python Tkinter graphical user interface. It starts the C++
    executable and displays the results.

verify_external.py
    OPTIONAL verification script. It uses Python's native integer
    arithmetic ONLY as an external trusted reference. It is NOT used
    by the C++ calculator.

CAPACITY
--------
The C++ BigInt uses 40 x 32-bit words = 1280 bits of internal storage.
This is larger than the required 512-bit input size and also leaves
space for products and Euclidean intermediates.

The decimal input/output conversion is implemented manually.

NO BIG-INTEGER LIBRARY
----------------------
The C++ arithmetic does NOT use:
    std::gcd
    std::pow
    Boost.Multiprecision
    any standard big-integer class
    a built-in modular inverse

The algorithms are implemented using fixed arrays, arithmetic,
comparison, subtraction, shifts and binary long division.

HOW TO COMPILE
--------------

Windows (MinGW g++):

    g++ -std=c++17 -O2 main.cpp -o calculator.exe

Then:

    python ui.py


Linux/macOS:

    g++ -std=c++17 -O2 main.cpp -o calculator
    python3 ui.py


COMMAND LINE EXAMPLES
---------------------

GCD:
    calculator gcd 48 18

Extended GCD:
    calculator egcd 48 18

Modular inverse:
    calculator inverse 3 11

Modular addition:
    calculator modadd 100 50 7

Modular multiplication:
    calculator modmul 123 456 1000

Square-and-multiply:
    calculator powfast 5 117 19

Naive:
    calculator pownaive 5 117 19


IMPORTANT
---------
The naive exponentiation method is intentionally slow because it
performs one modular multiplication for each unit of the exponent.
Use it for small/medium exponents in the timing experiment.

The square-and-multiply method reduces the number of multiplications
to O(log e), so it is suitable for very large exponents.

LAB TASK MAPPING
----------------
Task 1 -> gcd
Task 2 -> egcd
Task 3 -> egcd output x and y
Task 4 -> inverse
Task 5 -> modadd and modmul
Task 6 -> powfast
Task 7 -> verify_external.py (optional external trusted reference)

EXPERIMENT
----------
The Python UI has an Experiment tab.

Enter:
    Base
    Modulus
    Exponents such as:
        10,100,500,1000,2000

It measures:
    naive modular exponentiation
    square-and-multiply

It also checks that both algorithms return the same result.
