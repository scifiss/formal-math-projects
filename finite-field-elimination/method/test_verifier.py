#!/usr/bin/env python3

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REFERENCE = (
    ROOT
    / "certificate"
    / "reference_certificate.json"
)

VERIFIER = (
    ROOT
    / "benchmark"
    / "tests"
    / "verifier.py"
)


with open(
    REFERENCE,
    "r",
    encoding="utf-8",
) as f:
    reference = json.load(f)


# Helpers

def run_certificate(cert):
    """
    Write a temporary certificate, run the verifier,
    and return its final stdout result.
    """

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as f:

        json.dump(
            cert,
            f,
            indent=2,
        )

        f.write("\n")

        path = Path(f.name)


    try:
        result = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                str(path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

    except subprocess.TimeoutExpired:
        path.unlink(
            missing_ok=True
        )

        return "TIMEOUT"


    path.unlink(
        missing_ok=True
    )


    lines = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


    if not lines:
        return "NO_RESULT"


    return lines[-1]


def expect(
    name,
    cert,
    expected,
):
    actual = run_certificate(
        cert
    )

    if actual != expected:
        print(
            f"FAIL: {name}"
        )

        print(
            f"  expected: {expected}"
        )

        print(
            f"  actual:   {actual}"
        )

        raise SystemExit(1)

    print(
        f"PASS: {name}"
    )



# Valid reference
expect(
    "reference certificate",
    reference,
    "1",
)

# Basic metadata attacks
bad = copy.deepcopy(
    reference
)

bad["prime"] = (
    bad["prime"] + 2
)

expect(
    "wrong prime",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["parameter"] = "t"

expect(
    "wrong parameter",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["solution_count"] += 1

expect(
    "wrong solution count",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["solution_count"] = 0

expect(
    "zero solution count",
    bad,
    "0",
)

# Eliminant attacks
bad = copy.deepcopy(
    reference
)

bad["eliminant"][-1] = 2

expect(
    "nonmonic eliminant",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["eliminant"] = [0]

expect(
    "zero eliminant",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["eliminant"] = (
    bad["eliminant"][:-1]
)

expect(
    "truncated eliminant",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["eliminant"][0] = (
    bad["eliminant"][0] + 1
)

expect(
    "wrong eliminant coefficient",
    bad,
    "0",
)


# Coordinate schema attacks
bad = copy.deepcopy(
    reference
)

del bad[
    "coordinates"
]["x0"]

expect(
    "missing x0 coordinate",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

del bad[
    "coordinates"
]["t"]

expect(
    "missing t coordinate",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["fake"] = [1]

expect(
    "extra coordinate",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x0"] = []

expect(
    "empty coordinate polynomial",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x0"] = [
    "not-an-integer"
]

expect(
    "noninteger coordinate coefficient",
    bad,
    "0",
)

# Coordinate-value attacks
bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x0"][0] += 1

expect(
    "wrong x0 recovery polynomial",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x3"][0] += 1

expect(
    "wrong x3 recovery polynomial",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["t"][0] += 1

expect(
    "wrong t recovery polynomial",
    bad,
    "0",
)


# ============================================================================
# Shear-relation attacks
# These are important after introducing:
#   s = t + x0*x1 + x2*x3 + ...
# A certificate may still look superficially plausible,
# but the auxiliary parameter relation must hold exactly.
# ============================================================================

bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["t"] = [0]

expect(
    "break auxiliary parameter relation",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x1"][0] += 7

expect(
    "break shear product relation",
    bad,
    "0",
)


# Degree-bound attacks
bad = copy.deepcopy(
    reference
)

degree_h = (
    len(
        bad["eliminant"]
    )
    - 1
)

bad[
    "coordinates"
]["x0"] = (
    bad[
        "coordinates"
    ]["x0"]
    + [0] * (
        degree_h
        - len(
            bad[
                "coordinates"
            ]["x0"]
        )
    )
    + [1]
)

expect(
    "coordinate degree too large",
    bad,
    "0",
)

# Type attacks
bad = copy.deepcopy(
    reference
)

bad["solution_count"] = True

expect(
    "boolean solution count",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["eliminant"][0] = True

expect(
    "boolean eliminant coefficient",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad[
    "coordinates"
]["x0"][0] = False

expect(
    "boolean coordinate coefficient",
    bad,
    "0",
)


# Structural attacks
bad = copy.deepcopy(
    reference
)

bad["coordinates"] = []

expect(
    "coordinates not an object",
    bad,
    "0",
)


bad = copy.deepcopy(
    reference
)

bad["eliminant"] = "not-a-list"

expect(
    "eliminant not a list",
    bad,
    "0",
)

print()
print(
    "All verifier attack tests passed."
)