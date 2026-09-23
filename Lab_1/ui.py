
import os
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox

# ------------------------------------------------------------
# Python UI only.
# All number-theory calculations are performed by the C++ program.
# No Python math/gcd/pow is used for the calculator algorithms.
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.name == "nt":
    EXE = os.path.join(BASE_DIR, "calculator.exe")
else:
    EXE = os.path.join(BASE_DIR, "calculator")


def run_cpp(operation, *args):
    if not os.path.exists(EXE):
        raise RuntimeError(
            "C++ executable not found.\n\n"
            "Compile main.cpp first:\n"
            "Windows: g++ -std=c++17 -O2 main.cpp -o calculator.exe\n"
            "Linux/macOS: g++ -std=c++17 -O2 main.cpp -o calculator"
        )

    command = [EXE, operation]
    for value in args:
        command.append(str(value).strip())

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        error = result.stdout.strip()
        if result.stderr.strip():
            error += "\n" + result.stderr.strip()
        raise RuntimeError(error if error else "C++ program returned an error.")

    return result.stdout.strip()


def show_result(box, text):
    box.config(state="normal")
    box.delete("1.0", tk.END)
    box.insert(tk.END, text)
    box.config(state="disabled")


def get_value(entry, name):
    value = entry.get().strip()
    if not value:
        raise ValueError(name + " is required.")
    if value.startswith("+"):
        value = value[1:]
    if not value.isdigit():
        raise ValueError(name + " must contain decimal digits only.")
    return value

def get_signed_value(entry, name):
    s = entry.get().strip()

    if not s:
        raise ValueError(name + " cannot be empty.")

    start = 0

    # Allow + or - at the beginning
    if s[0] == '+' or s[0] == '-':
        start = 1

    # Input is only a sign, such as "-"
    if start == len(s):
        raise ValueError(name + " must contain digits.")

    # Check the remaining characters
    for i in range(start, len(s)):
        if s[i] < '0' or s[i] > '9':
            raise ValueError(name + " must contain a valid decimal integer.")

    return s


def execute(operation, fields, output_box, signed=False):
    try:
        values = []

        for entry, name in fields:
            if signed:
                values.append(get_signed_value(entry, name))
            else:
                values.append(get_value(entry, name))

        start = time.perf_counter()

        answer = run_cpp(operation, *values)

        elapsed = time.perf_counter() - start

        show_result(
            output_box,
            answer + "\n\nExecution time: "
            + format(elapsed, ".6f")
            + " seconds"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def clear_entries(entries):
    for entry in entries:
        entry.delete(0, tk.END)
    show_result("")


# ---------------- Main window ----------------

root = tk.Tk()
root.title("Modular Arithmetic & Extended Euclidean Calculator")
root.geometry("1000x720")
root.minsize(850, 600)

style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

title = ttk.Label(
    root,
    text="LAB 1 — Modular Arithmetic & Extended Euclidean Algorithm",
    font=("Segoe UI", 18, "bold")
)
title.pack(pady=(15, 4))

subtitle = ttk.Label(
    root,
    text="C++ arithmetic engine + Python GUI | Decimal inputs up to the implemented fixed capacity",
    font=("Segoe UI", 10)
)
subtitle.pack(pady=(0, 12))

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=10)

# ============================================================
# Basic operations tab
# ============================================================

basic = ttk.Frame(notebook)
notebook.add(basic, text="GCD / Extended GCD")

left = ttk.Frame(basic)
left.pack(side="left", fill="both", expand=True, padx=(15, 8), pady=15)

right = ttk.Frame(basic)
right.pack(side="right", fill="both", expand=True, padx=(8, 15), pady=15)

ttk.Label(left, text="a", font=("Segoe UI", 11, "bold")).pack(anchor="w")
a_entry = ttk.Entry(left, font=("Consolas", 12))
a_entry.pack(fill="x", pady=(3, 12))

ttk.Label(left, text="b", font=("Segoe UI", 11, "bold")).pack(anchor="w")
b_entry = ttk.Entry(left, font=("Consolas", 12))
b_entry.pack(fill="x", pady=(3, 12))

ttk.Button(
    left,
    text="Euclidean GCD",
    command=lambda: execute(
    "gcd",
    [(a_entry, "a"), (b_entry, "b")],
    result_box, signed=True
)
).pack(fill="x", pady=4)

ttk.Button(
    left,
    text="Extended Euclidean Algorithm",
    command=lambda: execute(
    "egcd",
    [(a_entry, "a"), (b_entry, "b")],
    result_box, signed= True
)
).pack(fill="x", pady=4)

ttk.Label(
    left,
    text="Extended GCD returns x and y such that\n"
         "a*x + b*y = gcd(a,b).",
    justify="left"
).pack(anchor="w", pady=15)

result_box = tk.Text(
    right,
    height=18,
    font=("Consolas", 12),
    wrap="word"
)
result_box.pack(fill="both", expand=True)
result_box.config(state="disabled")

entries_basic = [a_entry, b_entry]

# ============================================================
# Modular operations tab
# ============================================================

modtab = ttk.Frame(notebook)
notebook.add(modtab, text="Modular Arithmetic")

form = ttk.Frame(modtab)
form.pack(fill="x", padx=30, pady=25)

ttk.Label(form, text="a").grid(row=0, column=0, sticky="w", pady=7)
ma = ttk.Entry(form, font=("Consolas", 12))
ma.grid(row=0, column=1, sticky="ew", padx=10, pady=7)

ttk.Label(form, text="b").grid(row=1, column=0, sticky="w", pady=7)
mb = ttk.Entry(form, font=("Consolas", 12))
mb.grid(row=1, column=1, sticky="ew", padx=10, pady=7)

ttk.Label(form, text="modulus m").grid(row=2, column=0, sticky="w", pady=7)
mm = ttk.Entry(form, font=("Consolas", 12))
mm.grid(row=2, column=1, sticky="ew", padx=10, pady=7)

form.columnconfigure(1, weight=1)

buttons = ttk.Frame(modtab)
buttons.pack(fill="x", padx=30)

ttk.Button(
    buttons,
    text="Modular Addition  (a + b) mod m",
    command=lambda: execute(
        "modadd",
        [(ma, "a"), (mb, "b"), (mm, "modulus")],
        mod_result_box
    )
).pack(fill="x", pady=5)


ttk.Button(
    buttons,
    text="Modular Multiplication  (a × b) mod m",
    command=lambda: execute(
        "modmul",
        [(ma, "a"), (mb, "b"), (mm, "modulus")],
        mod_result_box
    )
).pack(fill="x", pady=5)


ttk.Label(
    modtab,
    text="Result:",
    font=("Segoe UI", 11, "bold")
).pack(anchor="w", padx=30, pady=(20, 5))


mod_result_box = tk.Text(
    modtab,
    height=8,
    font=("Consolas", 12),
    wrap="word"
)

mod_result_box.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(0, 20)
)

mod_result_box.config(state="disabled")

# ============================================================
# Modular inverse tab
# ============================================================

invtab = ttk.Frame(notebook)
notebook.add(invtab, text="Modular Inverse")

invform = ttk.Frame(invtab)
invform.pack(fill="x", padx=30, pady=30)

ttk.Label(invform, text="a").grid(row=0, column=0, sticky="w", pady=8)
ia = ttk.Entry(invform, font=("Consolas", 12))
ia.grid(row=0, column=1, sticky="ew", padx=10, pady=8)

ttk.Label(invform, text="modulus m").grid(row=1, column=0, sticky="w", pady=8)
im = ttk.Entry(invform, font=("Consolas", 12))
im.grid(row=1, column=1, sticky="ew", padx=10, pady=8)

invform.columnconfigure(1, weight=1)

ttk.Button(
    invtab,
    text="Find Modular Inverse",
    command=lambda: execute(
        "inverse",
        [(ia, "a"), (im, "modulus")],
        inv_result_box
    )
).pack(fill="x", padx=30, pady=10)

ttk.Label(
    invtab,
    text="Result:",
    font=("Segoe UI", 11, "bold")
).pack(anchor="w", padx=30, pady=(20, 5))


inv_result_box = tk.Text(
    invtab,
    height=8,
    font=("Consolas", 12),
    wrap="word"
)

inv_result_box.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(0, 20)
)

inv_result_box.config(state="disabled")

# ============================================================
# Modular exponentiation tab
# ============================================================

powtab = ttk.Frame(notebook)
notebook.add(powtab, text="Modular Exponentiation")

powform = ttk.Frame(powtab)
powform.pack(fill="x", padx=30, pady=25)

ttk.Label(powform, text="base a").grid(row=0, column=0, sticky="w", pady=7)
pa = ttk.Entry(powform, font=("Consolas", 12))
pa.grid(row=0, column=1, sticky="ew", padx=10, pady=7)

ttk.Label(powform, text="exponent e").grid(row=1, column=0, sticky="w", pady=7)
pe = ttk.Entry(powform, font=("Consolas", 12))
pe.grid(row=1, column=1, sticky="ew", padx=10, pady=7)

ttk.Label(powform, text="modulus m").grid(row=2, column=0, sticky="w", pady=7)
pm = ttk.Entry(powform, font=("Consolas", 12))
pm.grid(row=2, column=1, sticky="ew", padx=10, pady=7)

powform.columnconfigure(1, weight=1)

ttk.Button(
    powtab,
    text="Square-and-Multiply / Repeated Squaring",
    command=lambda: execute(
    "powfast",
    [(pa, "base"), (pe, "exponent"), (pm, "modulus")],
    pow_result_box
)
).pack(fill="x", padx=30, pady=5)

ttk.Button(
    powtab,
    text="Naive Modular Exponentiation",
    command=lambda: execute(
    "pownaive",
    [(pa, "base"), (pe, "exponent"), (pm, "modulus")],
    pow_result_box
)
).pack(fill="x", padx=30, pady=5)

ttk.Label(
    powtab,
    text="Result:",
    font=("Segoe UI", 11, "bold")
).pack(anchor="w", padx=30, pady=(20, 5))


pow_result_box = tk.Text(
    powtab,
    height=8,
    font=("Consolas", 12),
    wrap="word"
)

pow_result_box.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(0, 20)
)

pow_result_box.config(state="disabled")

# ============================================================
# Experiment / timing tab
# ============================================================

exptab = ttk.Frame(notebook)
notebook.add(exptab, text="Experiment")

expform = ttk.Frame(exptab)
expform.pack(fill="x", padx=30, pady=20)

ttk.Label(expform, text="Base a").grid(row=0, column=0, sticky="w", pady=6)
ea = ttk.Entry(expform, font=("Consolas", 12))
ea.insert(0, "5")
ea.grid(row=0, column=1, sticky="ew", padx=10, pady=6)

ttk.Label(expform, text="Modulus m").grid(row=1, column=0, sticky="w", pady=6)
em = ttk.Entry(expform, font=("Consolas", 12))
em.insert(0, "1000000007")
em.grid(row=1, column=1, sticky="ew", padx=10, pady=6)

ttk.Label(
    expform,
    text="Exponents (comma separated)"
).grid(row=2, column=0, sticky="w", pady=6)

exponents_entry = ttk.Entry(expform, font=("Consolas", 12))
exponents_entry.insert(0, "10,100,500,1000,2000")
exponents_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=6)

expform.columnconfigure(1, weight=1)

columns = ("exponent", "naive", "square")
tree = ttk.Treeview(exptab, columns=columns, show="headings", height=12)

tree.heading("exponent", text="Exponent")
tree.heading("naive", text="Naive time (s)")
tree.heading("square", text="Square-and-multiply time (s)")

tree.column("exponent", width=150, anchor="center")
tree.column("naive", width=220, anchor="center")
tree.column("square", width=280, anchor="center")

tree.pack(fill="both", expand=True, padx=30, pady=10)


def run_experiment():
    try:
        base = get_value(ea, "Base")
        modulus = get_value(em, "Modulus")

        raw = exponents_entry.get().strip()
        if not raw:
            raise ValueError("Enter at least one exponent.")

        exponent_strings = raw.split(",")

        for item in tree.get_children():
            tree.delete(item)

        for item in exponent_strings:
            e = item.strip()
            if not e.isdigit():
                raise ValueError("Every exponent must contain digits only.")

            # Naive method is intentionally run first.
            t1 = time.perf_counter()
            fast_naive = run_cpp("pownaive", base, e, modulus)
            naive_time = time.perf_counter() - t1

            t2 = time.perf_counter()
            fast_result = run_cpp("powfast", base, e, modulus)
            square_time = time.perf_counter() - t2

            if fast_naive != fast_result:
                raise RuntimeError(
                    "Verification failed: both exponentiation methods "
                    "returned different answers for exponent " + e
                )

            tree.insert(
                "",
                "end",
                values=(
                    e,
                    format(naive_time, ".6f"),
                    format(square_time, ".6f")
                )
            )

    except Exception as e:
        messagebox.showerror("Experiment error", str(e))


ttk.Button(
    exptab,
    text="Run Timing Experiment",
    command=run_experiment
).pack(fill="x", padx=30, pady=8)

ttk.Label(
    exptab,
    text="The experiment also checks that both algorithms produce the same result.",
    font=("Segoe UI", 9)
).pack(anchor="w", padx=30, pady=4)

# ============================================================
# Help tab
# ============================================================

helptab = ttk.Frame(notebook)
notebook.add(helptab, text="About / Lab Mapping")

help_text = tk.Text(
    helptab,
    font=("Segoe UI", 11),
    wrap="word"
)
help_text.pack(fill="both", expand=True, padx=20, pady=20)

help_text.insert(
    tk.END,
    """LAB 1 TASK MAPPING

1. Implement Euclidean GCD
   → GCD / Extended GCD tab → Euclidean GCD

2. Implement Extended Euclidean Algorithm
   → GCD / Extended GCD tab → Extended Euclidean Algorithm

3. Find x and y satisfying
      ax + by = gcd(a,b)
   → Extended GCD output gives gcd, x and y.

4. Implement modular inverse
   → Modular Inverse tab

5. Implement modular addition and multiplication
   → Modular Arithmetic tab

6. Implement modular exponentiation using repeated squaring
   → Modular Exponentiation tab → Square-and-Multiply

Experiment
   → Compare naive modular exponentiation with
     square-and-multiply for increasing exponents.

IMPORTANT IMPLEMENTATION RULE
The C++ program does not use:
   • std::gcd
   • std::pow
   • Boost multiprecision
   • any standard big-integer library
   • std::vector for big integers
   • a built-in modular inverse

The arithmetic is implemented manually using fixed arrays
of 32-bit words.

The Python program is only the graphical interface and process
launcher. It does not perform the number-theory calculations.
"""
)

help_text.config(state="disabled")

root.mainloop()
