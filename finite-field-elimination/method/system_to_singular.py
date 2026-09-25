#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SYSTEM_FILE = ROOT / "data/system.json"

OUT_DIR = ROOT / "method/singular"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def monomial_to_singular(exponents, variables):
    factors = []

    for var, exponent in zip(variables, exponents):
        if exponent == 0:
            continue
        elif exponent == 1:
            factors.append(var)
        else:
            factors.append(f"{var}^{exponent}")

    if not factors:
        return "1"

    return "*".join(factors)


def polynomial_to_singular(poly, variables, p):
    pieces = []

    for term in poly["terms"]:
        coeff = int(term["coeff"]) % p
        exponents = term["exponents"]

        if coeff == 0:
            continue

        monomial = monomial_to_singular(
            exponents,
            variables,
        )

        if monomial == "1":
            piece = str(coeff)
        elif coeff == 1:
            piece = monomial
        else:
            piece = f"{coeff}*{monomial}"

        pieces.append(piece)

    if not pieces:
        return "0"

    return " + ".join(pieces)


system = load_json(SYSTEM_FILE)

p = int(system["prime"])
variables = system["variables"]

polynomials = [
    polynomial_to_singular(
        poly,
        variables,
        p,
    )
    for poly in system["polynomials"]
]



variable_list = ",".join(variables)

fglm_lines = [
    f"ring r = {p},({variable_list}),dp;",
    "",
    "ideal I =",
]

for i, poly in enumerate(polynomials):
    suffix = "," if i < len(polynomials) - 1 else ";"
    fglm_lines.append(f"  {poly}{suffix}")

fglm_lines += [
    "",
    'print("=== INPUT GENERATORS ===");',
    "size(I);",
    "",
    # FGLM expects a reduced standard basis.
    "option(redSB);",
    "",
    'print("=== COMPUTING DP GROEBNER BASIS ===");',
    "ideal G = std(I);",
    "",
    'print("=== DP BASIS SIZE ===");',
    "size(G);",
    "",
    'print("=== VECTOR SPACE DIMENSION ===");',
    "vdim(G);",
    "",
    # Same field and variable list; only the monomial order changes.
    f"ring s = {p},({variable_list}),lp;",
    "",
    'print("=== COMPUTING LEX BASIS WITH FGLM ===");',
    "ideal L = fglm(r,G);",
    "",
    'print("=== LEX BASIS SIZE ===");',
    "size(L);",
    "",
    'print("=== LEX GROEBNER BASIS ===");',
    "L;",
    "",
    "quit;",
]


direct_lines = [
    f"ring r = {p},({variable_list}),lp;",
    "",
    "ideal I =",
]

for i, poly in enumerate(polynomials):
    suffix = "," if i < len(polynomials) - 1 else ";"
    direct_lines.append(f"  {poly}{suffix}")

direct_lines += [
    "",
    "option(redSB);",
    "",
    'print("=== COMPUTING DIRECT LEX GROEBNER BASIS ===");',
    "ideal G = std(I);",
    "",
    'print("=== DIRECT LEX BASIS SIZE ===");',
    "size(G);",
    "",
    'print("=== DIRECT LEX GROEBNER BASIS ===");',
    "G;",
    "",
    "quit;",
]


fglm_file = OUT_DIR / "solve_fglm.sing"
direct_file = OUT_DIR / "solve_direct_lex.sing"

fglm_file.write_text(
    "\n".join(fglm_lines) + "\n",
    encoding="utf-8",
)

direct_file.write_text(
    "\n".join(direct_lines) + "\n",
    encoding="utf-8",
)


print(f"prime              : {p}")
print(f"variables          : {variables}")
print(f"public polynomials : {len(polynomials)}")
print()
print(f"wrote: {fglm_file}")
print(f"wrote: {direct_file}")