#!/usr/bin/env python3

import json
import os
import random
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

P = 1009

SEED = int(
    os.environ.get(
        "FFE_SEED",
        "20260923",
    )
)

N_SOLUTIONS = int(
    os.environ.get(
        "FFE_N_SOLUTIONS",
        "40",
    )
)

RECOVERY_DEGREE = int(
    os.environ.get(
        "FFE_RECOVERY_DEGREE",
        "9",
    )
)

MIXING_ROUNDS = int(
    os.environ.get(
        "FFE_MIXING_ROUNDS",
        "2",
    )
)

SHEAR_PAIRS = int(
    os.environ.get(
        "FFE_SHEAR_PAIRS",
        "1",
    )
)


VARIABLES = [
    "x0",
    "x1",
    "x2",
    "x3",
    "x4",
    "x5",
    "x6",
    "t",
]

T_INDEX = len(VARIABLES) - 1

ROOT = Path(__file__).resolve().parents[1]

if not 1 <= SHEAR_PAIRS <= 3:
    raise ValueError(
        "FFE_SHEAR_PAIRS must be 1, 2, or 3"
    )

if N_SOLUTIONS <= 0:
    raise ValueError(
        "FFE_N_SOLUTIONS must be positive"
    )

if N_SOLUTIONS >= P:
    raise ValueError(
        "FFE_N_SOLUTIONS must be smaller than the field size"
    )

if RECOVERY_DEGREE < 0:
    raise ValueError(
        "FFE_RECOVERY_DEGREE must be nonnegative"
    )

if RECOVERY_DEGREE >= N_SOLUTIONS:
    raise ValueError(
        "FFE_RECOVERY_DEGREE must be smaller than N_SOLUTIONS"
    )

if MIXING_ROUNDS < 0:
    raise ValueError(
        "FFE_MIXING_ROUNDS must be nonnegative"
    )


def mod(x):
    return x % P


# ============================================================================
# Univariate polynomial arithmetic
# Coefficients use ascending-degree order:   [c0, c1, c2]
## means:   c0 + c1*s + c2*s^2
# ============================================================================

def trim_uni(a):
    a = [mod(x) for x in a]

    while len(a) > 1 and a[-1] == 0:
        a.pop()

    return a


def add_uni(a, b):
    n = max(len(a), len(b))
    out = [0] * n

    for i in range(n):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0

        out[i] = mod(ai + bi)

    return trim_uni(out)


def sub_uni(a, b):
    n = max(len(a), len(b))
    out = [0] * n

    for i in range(n):
        ai = a[i] if i < len(a) else 0
        bi = b[i] if i < len(b) else 0

        out[i] = mod(ai - bi)

    return trim_uni(out)


def mul_uni(a, b):
    out = [0] * (len(a) + len(b) - 1)

    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = mod(
                out[i + j] + ai * bj
            )

    return trim_uni(out)


def mod_uni(a, modulus):
    """
    Reduce the univariate polynomial a modulo a monic modulus.
    """

    a = trim_uni(list(a))
    modulus = trim_uni(list(modulus))

    if not modulus:
        raise ValueError("empty modulus")

    if modulus[-1] != 1:
        raise ValueError(
            "modulus must be monic"
        )

    while len(a) >= len(modulus):
        factor = a[-1]
        shift = len(a) - len(modulus)

        if factor != 0:
            for i, c in enumerate(modulus):
                a[i + shift] = mod(
                    a[i + shift]
                    - factor * c
                )

        a = trim_uni(a)

    return a


def eval_uni(coeffs, x):
    """
    Evaluate a univariate polynomial using Horner's rule.
    """

    result = 0

    for c in reversed(coeffs):
        result = mod(
            result * x + c
        )

    return result


# ============================================================================
# Sparse multivariate polynomial arithmetic
# Representation:
# {
#     exponent_tuple: coefficient
# }
# Example for variables [x0, x1, ..., t]: {(2, 0, ..., 3): 17}
# means:  17 * x0^2 * t^3
# ============================================================================
def clean_poly(poly):
    return {
        tuple(exp): mod(coeff)
        for exp, coeff in poly.items()
        if mod(coeff) != 0
    }


def add_poly(a, b):
    out = dict(a)

    for exp, coeff in b.items():
        out[exp] = mod(out.get(exp, 0) + coeff)

    return clean_poly(out)


def scale_poly(poly, scalar):
    return clean_poly({
        exp: mod(scalar * coeff)
        for exp, coeff in poly.items()
    })

def mul_monomial(
    poly,
    variable_index,
    power,
    scalar=1,
):
    out = {}

    for exp, coeff in poly.items():

        new_exp = list(exp)
        new_exp[variable_index] += power
        new_exp = tuple(new_exp)

        out[new_exp] = mod(
            out.get(new_exp, 0)
            + scalar * coeff
        )

    return clean_poly(out)														

def mul_poly(a, b):
    out = {}

    for exp_a, coeff_a in a.items():
        for exp_b, coeff_b in b.items():

            exp = tuple(
                ea + eb
                for ea, eb in zip(
                    exp_a,
                    exp_b,
                )
            )

            out[exp] = mod(
                out.get(exp, 0)
                + coeff_a * coeff_b
            )

    return clean_poly(out)

def pow_poly(poly, exponent):
    """
    Integer power of a sparse multivariate polynomial.
    """
    result = constant_poly(1)
    base = poly
    while exponent > 0:
        if exponent & 1:
            result = mul_poly(
                result,
                base,
            )
        exponent >>= 1
        if exponent:
            base = mul_poly(
                base,
                base,
            )

    return result


def constant_poly(c):
    exp = (0,) * len(VARIABLES)

    if mod(c) == 0:
        return {}

    return {
        exp: mod(c)
    }


def variable_poly(index):
    exp = [0] * len(VARIABLES)
    exp[index] = 1

    return {
        tuple(exp): 1
    }


def univariate_hidden_poly(coeffs):
    """
    Before the nonlinear coordinate transformation, the final polynomial-variable slot is used as the hidden parameter s.
    Later we substitute:
        s = t + x0*x1 + x2*x3 + ...
    into these polynomials.
    """
    out = {}
    for degree, coeff in enumerate(coeffs):
        coeff = mod(coeff)
        if coeff == 0:
            continue
        exp = [0] * len(VARIABLES)
        exp[T_INDEX] = degree
        out[tuple(exp)] = coeff
    return clean_poly(out)


# ============================================================================
# Nonlinear coordinate shear#
# The hidden shape parameter is s.
# Public coordinates satisfy:
#   s = t + x0*x1
# or, depending on SHEAR_PAIRS:
#   s = t + x0*x1 + x2*x3 + ...
# This is invertible because:
#   t = s - x0*x1 - x2*x3 - ...
# ============================================================================

def hidden_parameter_poly():
    """
    Return the public-coordinate polynomial representing hidden s.
    """
    out = variable_poly(T_INDEX)
    for pair in range(SHEAR_PAIRS):
        a = 2 * pair
        b = a + 1
        product = mul_poly(
            variable_poly(a),
            variable_poly(b),
        )
        out = add_poly(
            out,
            product,
        )

    return out


def substitute_hidden_parameter(poly):
    """
    Substitute

        s = t + x0*x1 + x2*x3 + ...

    into a polynomial originally expressed using the hidden
    parameter in the final variable slot.
    """

    s_poly = hidden_parameter_poly()

    out = {}

    for exponents, coeff in poly.items():

        s_power = exponents[T_INDEX]

        base_exp = list(exponents)
        base_exp[T_INDEX] = 0

        base_poly = {
            tuple(base_exp): coeff
        }

        s_factor = pow_poly(
            s_poly,
            s_power,
        )

        term = mul_poly(
            base_poly,
            s_factor,
        )

        out = add_poly(
            out,
            term,
        )

    return clean_poly(out)


# ============================================================================
# Serialization
# ============================================================================

def serialize_poly(poly):
    terms = []

    for exp, coeff in sorted(
        poly.items()
    ):
        terms.append({
            "coeff": int(mod(coeff)),
            "exponents": list(exp),
        })

    return {
        "terms": terms
    }


def write_json(path, obj):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            obj,
            f,
            indent=2,
        )

        f.write("\n")


# ============================================================================
# Build hidden shape-position system
# ============================================================================

rng = random.Random(SEED)


# --------------------------------------------------------------------------
# Select distinct roots of the eliminant.
# --------------------------------------------------------------------------

roots = sorted(
    rng.sample(
        range(P),
        N_SOLUTIONS,
    )
)


# --------------------------------------------------------------------------
# h(s) = product_j (s - root_j)
# --------------------------------------------------------------------------

h = [1]

for root in roots:

    h = mul_uni(
        h,
        [
            mod(-root),
            1,
        ],
    )


assert len(h) == N_SOLUTIONS + 1
assert h[-1] == 1


# --------------------------------------------------------------------------
# Generate hidden coordinate recovery polynomials
#
# x_i = r_i(s)
# --------------------------------------------------------------------------

coordinates = {}

for name in VARIABLES[:-1]:

    coeffs = [
        rng.randrange(P)
        for _ in range(
            RECOVERY_DEGREE + 1
        )
    ]

    # Force exact requested degree.
    if coeffs[-1] == 0:
        coeffs[-1] = 1

    coordinates[name] = trim_uni(
        coeffs
    )


# ============================================================================
# Recover public t as a polynomial in s
# Since:
#
#   s = t + x0*x1 + x2*x3 + ...
#
# then:
#   t = s - x0*x1 - x2*x3 - ...
# ============================================================================

public_coordinates = dict(
    coordinates
)

# polynomial "s"
t_recovery = [0, 1]

for pair in range(SHEAR_PAIRS):

    a = f"x{2 * pair}"
    b = f"x{2 * pair + 1}"

    product = mul_uni(
        coordinates[a],
        coordinates[b],
    )

    t_recovery = sub_uni(
        t_recovery,
        product,
    )


# Recovery polynomials are canonical modulo h(s).
t_recovery = mod_uni(
    t_recovery,
    h,
)

public_coordinates["t"] = (
    t_recovery
)


# ============================================================================
# Hidden generators
#
# Before shear:
#   h(s)
#   x0 - r0(s)
#   ...
#   x6 - r6(s)
# ============================================================================
generators = []
generators.append(
    univariate_hidden_poly(h)
)


for i, name in enumerate(
    VARIABLES[:-1]
):

    xi = variable_poly(i)

    ri = univariate_hidden_poly(
        coordinates[name]
    )

    generator = add_poly(
        xi,
        scale_poly(
            ri,
            -1,
        ),
    )

    generators.append(
        generator
    )


assert len(generators) == len(
    VARIABLES
)


# ============================================================================
# Hide the primitive parameter using nonlinear shear
# ============================================================================

generators = [
    substitute_hidden_parameter(poly)
    for poly in generators
]


# ============================================================================
# Generator mixing
# Elementary operation:
#   g_i <- g_i + m * g_j
# is invertible and therefore preserves the generated ideal.
# ============================================================================

for _ in range(MIXING_ROUNDS):

    i, j = rng.sample(
        range(len(generators)),
        2,
    )

    variable_index = (
        rng.randrange(
            len(VARIABLES)
        )
    )

    power = rng.choice([
        1,
        1,
        1,
        2,
    ])

    scalar = rng.randrange(
        1,
        P,
    )

    extra = mul_monomial(
        generators[j],
        variable_index,
        power,
        scalar,
    )

    generators[i] = add_poly(
        generators[i],
        extra,
    )


# --------------------------------------------------------------------------
# Mild constant elementary row mixing.

CONSTANT_MIXING_ROUNDS = 12
for _ in range(
    CONSTANT_MIXING_ROUNDS
):

    i, j = rng.sample(
        range(len(generators)),
        2,
    )

    scalar = rng.randrange(
        1,
        P,
    )

    generators[i] = add_poly(
        generators[i],
        scale_poly(
            generators[j],
            scalar,
        ),
    )


# Randomize generator ordering.
rng.shuffle(generators)


# ============================================================================
# Exact public solution points
# Every root s_j determines:
#   x_i = r_i(s_j)
# and
#   t = s_j - x0*x1 - ...
# ============================================================================
points = []
for s in roots:

    point = [
        eval_uni(
            public_coordinates[name],
            s,
        )
        for name in VARIABLES
    ]

    # Internal consistency check: s == t + x0*x1 + x2*x3 + ...
    index = {
        name: i
        for i, name in enumerate(
            VARIABLES
        )
    }

    reconstructed_s = (
        point[index["t"]]
    )

    for pair in range(
        SHEAR_PAIRS
    ):

        xa = point[
            index[f"x{2 * pair}"]
        ]

        xb = point[
            index[f"x{2 * pair + 1}"]
        ]

        reconstructed_s = mod(
            reconstructed_s
            + xa * xb
        )

    assert reconstructed_s == s

    points.append(point)


assert len(points) == N_SOLUTIONS

assert len({
    tuple(point)
    for point in points
}) == N_SOLUTIONS



# Public files
system = {
    "prime": P,
    "variables": VARIABLES,
    "monomial_order": "lex",
    "shear_pairs": SHEAR_PAIRS,
    "polynomials": [
        serialize_poly(poly)
        for poly in generators
    ],
}


parameter_relation_terms = [
    f"x{2 * pair}*x{2 * pair + 1}"
    for pair in range(
        SHEAR_PAIRS
    )
]


spec = {
    "prime": P,
    "variables": VARIABLES,
    "parameter": "s",
    "parameter_relation": (
        "s = t + "
        + " + ".join(
            parameter_relation_terms
        )
    ),
    "shear_pairs": SHEAR_PAIRS,
    "monomial_order": "lex",
    "coefficient_order":
        "ascending_degree",
    "coefficient_range": [
        0,
        P - 1,
    ],
    "certificate_file":
        "certificate.json",
}


ground_truth = {
    "points": points,
}


reference_certificate = {
    "prime": P,
    "parameter": "s",
    "solution_count": N_SOLUTIONS,
    "eliminant": h,
    "coordinates": (
        public_coordinates
    ),
}

# Write files
write_json(
    ROOT
    / "data/system.json",
    system,
)

write_json(
    ROOT
    / "data/spec.json",
    spec,
)

write_json(
    ROOT
    / "benchmark/tests/data/system.json",
    system,
)

write_json(
    ROOT
    / "benchmark/tests/data/spec.json",
    spec,
)

write_json(
    ROOT
    / "benchmark/tests/data/ground_truth.json",
    ground_truth,
)

write_json(
    ROOT
    / "certificate/reference_certificate.json",
    reference_certificate,
)


total_terms = sum(
    len(poly)
    for poly in generators
)

max_total_degree = max(
    max(
        sum(exp)
        for exp in poly
    )
    for poly in generators
)


print(
    "Generated finite-field instance"
)

print(
    f"seed               : {SEED}"
)

print(
    f"prime              : {P}"
)

print(
    f"variables          : {len(VARIABLES)}"
)

print(
    f"solutions          : {N_SOLUTIONS}"
)

print(
    f"degree(h)          : {len(h) - 1}"
)

print(
    f"recovery degree    : {RECOVERY_DEGREE}"
)

print(
    f"mixing rounds      : {MIXING_ROUNDS}"
)

print(
    f"constant mixing    : {CONSTANT_MIXING_ROUNDS}"
)

print(
    f"shear pairs        : {SHEAR_PAIRS}"
)

print(
    f"public polynomials : {len(generators)}"
)

print(
    f"total terms        : {total_terms}"
)

print(
    f"max total degree   : {max_total_degree}"
)