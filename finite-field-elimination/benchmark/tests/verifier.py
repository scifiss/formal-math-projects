#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

# Paths
TEST_ROOT = Path(__file__).resolve().parent

SYSTEM_FILE = (
    TEST_ROOT
    / "data"
    / "system.json"
)

GROUND_TRUTH_FILE = (
    TEST_ROOT
    / "data"
    / "ground_truth.json"
)

# Utilities
def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def valid_int(value):
    """
    JSON booleans are Python ints, so explicitly reject them.
    """
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
    )


def fail(message):
    """
    Diagnostics go to stderr.
    The final verifier result is always exactly 0 or 1
    on stdout.
    """
    print(
        f"verification failed: {message}",
        file=sys.stderr,
    )

    print("0")
    raise SystemExit(0)

# Polynomial evaluation
def eval_univariate(
    coefficients,
    x,
    p,
):
    """
    Evaluate  c0 + c1*x + c2*x^2 + ...
    modulo p using Horner's rule.
    """
    result = 0
    for coefficient in reversed(
        coefficients
    ):
        result = (
            result * x
            + coefficient
        ) % p

    return result

def eval_multivariate(
    polynomial,
    point,
    p,
    variable_count,
):
    """
    Evaluate one sparse public polynomial.
    Each term is encoded as:
        {
            "coeff": c,
            "exponents": [e0, ..., en]
        }
    """
    total = 0
    terms = polynomial.get(
        "terms"
    )

    if not isinstance(terms, list):
        fail(
            "public polynomial has invalid terms"
        )

    for term in terms:

        if not isinstance(term, dict):
            fail(
                "public polynomial contains "
                "an invalid term"
            )

        coefficient = term.get(
            "coeff"
        )

        exponents = term.get(
            "exponents"
        )

        if not valid_int(coefficient):
            fail(
                "public polynomial has "
                "a non-integer coefficient"
            )

        if (
            not isinstance(exponents, list)
            or len(exponents)
            != variable_count
        ):
            fail(
                "public polynomial has "
                "an invalid exponent vector"
            )

        if not all(
            valid_int(e) and e >= 0
            for e in exponents
        ):
            fail(
                "public polynomial has "
                "an invalid exponent"
            )

        value = coefficient % p

        for coordinate, exponent in zip(
            point,
            exponents,
        ):
            value = (
                value
                * pow(
                    coordinate,
                    exponent,
                    p,
                )
            ) % p

        total = (
            total + value
        ) % p

    return total

# Certificate normalization
def normalize_univariate(
    coefficients,
    p,
    name,
):
    """
    Validate and normalize a submitted coefficient array.
    """
    if not isinstance(
        coefficients,
        list,
    ):
        fail(
            f"{name} must be a coefficient list"
        )

    if len(coefficients) == 0:
        fail(
            f"{name} cannot be empty"
        )

    if not all(
        valid_int(c)
        for c in coefficients
    ):
        fail(
            f"{name} contains "
            "a non-integer coefficient"
        )

    result = [
        c % p
        for c in coefficients
    ]

    # Remove trailing zero coefficients.
    while (
        len(result) > 1
        and result[-1] == 0
    ):
        result.pop()

    return result


# Main verification
def main():    
    # Locate submission.
    if len(sys.argv) >= 2:
        certificate_path = Path(
            sys.argv[1]
        )
    else:
        app_root = Path(
            os.environ.get(
                "APP_ROOT",
                "/app",
            )
        )

        certificate_path = (
            app_root
            / "certificate.json"
        )


    if not certificate_path.is_file():
        fail(
            "certificate.json is missing"
        )    
    # Load private/public verifier data.   
    try:
        system = load_json(
            SYSTEM_FILE
        )

        truth = load_json(
            GROUND_TRUTH_FILE
        )

        certificate = load_json(
            certificate_path
        )

    except Exception as exc:
        fail(
            f"cannot load JSON: {exc}"
        )


    if not isinstance(
        certificate,
        dict,
    ):
        fail(
            "certificate must be "
            "a JSON object"
        )
    
    # Public system metadata.
    p = system.get("prime")
    variables = system.get(
        "variables"
    )
    shear_pairs = system.get(
        "shear_pairs"
    )

    public_polynomials = (
        system.get(
            "polynomials"
        )
    )

    if (
        not valid_int(p)
        or p <= 2
    ):
        fail(
            "invalid verifier field prime"
        )


    if (
        not isinstance(
            variables,
            list,
        )
        or len(variables) == 0
        or not all(
            isinstance(name, str)
            for name in variables
        )
    ):
        fail(
            "invalid public variable list"
        )


    if (
        not valid_int(
            shear_pairs
        )
        or shear_pairs < 1
    ):
        fail(
            "invalid shear-pair count"
        )


    if not isinstance(
        public_polynomials,
        list,
    ):
        fail(
            "invalid public polynomial system"
        )


    variable_count = len(
        variables
    )

    variable_index = {
        name: i
        for i, name in enumerate(
            variables
        )
    }


    if "t" not in variable_index:
        fail(
            "public system is missing t"
        )


    # Verify that all shear variables exist.
    for pair in range(
        shear_pairs
    ):
        a = f"x{2 * pair}"
        b = f"x{2 * pair + 1}"

        if (
            a not in variable_index
            or b not in variable_index
        ):
            fail(
                "public system has "
                "invalid shear metadata"
            )


    
    # Certificate metadata.
    if certificate.get(
        "prime"
    ) != p:
        fail(
            "certificate uses wrong prime"
        )

    if certificate.get(
        "parameter"
    ) != "s":
        fail(
            "certificate parameter "
            "must be s"
        )


    solution_count = (
        certificate.get(
            "solution_count"
        )
    )


    if not valid_int(
        solution_count
    ):
        fail(
            "solution_count must "
            "be an integer"
        )


    if solution_count <= 0:
        fail(
            "solution_count must "
            "be positive"
        )


    if solution_count >= p:
        fail(
            "solution_count is "
            "too large for the field"
        )


    # ----------------------------------------------------------------------
    # Eliminant.
    # ----------------------------------------------------------------------

    eliminant = normalize_univariate(
        certificate.get(
            "eliminant"
        ),
        p,
        "eliminant",
    )
    if len(eliminant) < 2:
        fail(
            "eliminant must have "
            "positive degree"
        )
    degree_h = (
        len(eliminant) - 1
    )


    # Our certificate convention uses a monic eliminant.
    if eliminant[-1] != 1:
        fail(
            "eliminant must be monic"
        )


    # We require the eliminant degree to equal the number of represented solutions.
    if degree_h != solution_count:
        fail(
            "degree(eliminant) must equal "
            "solution_count"
        )

    
    # Recovery polynomials.    
    coordinates = certificate.get(
        "coordinates"
    )
    if not isinstance(
        coordinates,
        dict,
    ):
        fail(
            "coordinates must be "
            "a JSON object"
        )

    expected_coordinate_names = set(
        variables
    )

    if set(
        coordinates.keys()
    ) != expected_coordinate_names:
        fail(
            "coordinate polynomial names "
            "do not match public variables"
        )


    normalized_coordinates = {}


    for name in variables:

        coefficients = (
            normalize_univariate(
                coordinates[name],
                p,
                f"coordinate {name}",
            )
        )

        # Canonical representative modulo h(s): degree(r_i) < degree(h)
        if len(coefficients) > degree_h:
            fail(
                f"degree of recovery "
                f"polynomial {name} "
                f"must be less than "
                f"degree(eliminant)"
            )

        normalized_coordinates[
            name
        ] = coefficients
    
    # Enumerate roots of h(s) in F_p. p = 1009, so exact enumeration is cheap.
    roots = []
    for s in range(p):

        if (
            eval_univariate(
                eliminant,
                s,
                p,
            )
            == 0
        ):
            roots.append(s)


    # Since degree(h) equals the number of distinct field roots, h splits completely into distinct linear factors.
    if len(roots) != degree_h:
        fail(
            "eliminant does not have "
            "the required number of "
            "distinct roots in F_p"
        )


    if len(roots) != solution_count:
        fail(
            "eliminant root count "
            "does not match "
            "solution_count"
        )
    
    # Reconstruct public solution points.
    reconstructed_points = []
    for s in roots:

        point = []
        for name in variables:
            coordinate = (
                eval_univariate(
                    normalized_coordinates[
                        name
                    ],
                    s,
                    p,
                )
            )

            point.append(
                coordinate
            )

        
        # Verify auxiliary parameter relation:
        #   s = t + x0*x1 + x2*x3 + ...        
        # modulo p.        
        reconstructed_s = (
            point[
                variable_index["t"]
            ]
        )

        for pair in range(
            shear_pairs
        ):

            a_name = (
                f"x{2 * pair}"
            )

            b_name = (
                f"x{2 * pair + 1}"
            )

            a_value = point[
                variable_index[
                    a_name
                ]
            ]

            b_value = point[
                variable_index[
                    b_name
                ]
            ]

            reconstructed_s = (
                reconstructed_s
                + a_value * b_value
            ) % p


        if reconstructed_s != s:
            fail(
                "coordinate recovery "
                "violates the auxiliary "
                "parameter relation"
            )


        reconstructed_points.append(
            tuple(point)
        )


    # Distinctness.
    submitted_point_set = set(
        reconstructed_points
    )

    if (
        len(submitted_point_set)
        != solution_count
    ):
        fail(
            "reconstructed solutions "
            "are not distinct"
        )

   
    # Every reconstructed point must satisfy every original public polynomial.
    for point_number, point in enumerate(
        reconstructed_points
    ):
        for polynomial_number, polynomial in enumerate(
            public_polynomials
        ):

            value = eval_multivariate(
                polynomial,
                point,
                p,
                variable_count,
            )

            if value != 0:
                fail(
                    "reconstructed point "
                    f"{point_number} fails "
                    "public polynomial "
                    f"{polynomial_number}"
                )
    
    # Sealed ground truth.
    truth_points_raw = truth.get(
        "points"
    )

    if not isinstance(
        truth_points_raw,
        list,
    ):
        fail(
            "invalid sealed ground truth"
        )


    truth_point_set = set()
    for point in truth_points_raw:
        if (
            not isinstance(
                point,
                list,
            )
            or len(point)
            != variable_count
        ):
            fail(
                "invalid sealed "
                "ground-truth point"
            )

        if not all(
            valid_int(value)
            for value in point
        ):
            fail(
                "invalid sealed "
                "ground-truth coordinate"
            )

        truth_point_set.add(
            tuple(
                value % p
                for value in point
            )
        )


    
    # Completeness.
    if (
        submitted_point_set
        != truth_point_set
    ):
        fail(
            "certificate does not "
            "describe the complete "
            "sealed solution set"
        )

    if (
        solution_count
        != len(
            truth_point_set
        )
    ):
        fail(
            "solution_count does not "
            "match sealed ground truth"
        )
    
    # Success  
    print("1")


if __name__ == "__main__":
    main()