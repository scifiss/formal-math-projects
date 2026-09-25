#!/usr/bin/env python3

import csv
import itertools
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

GENERATOR = ROOT / "method/generate_instance.py"
CONVERTER = ROOT / "method/system_to_singular.py"
VERIFIER = ROOT / "benchmark/tests/verifier.py"

FGLM = ROOT / "method/singular/solve_fglm.sing"
DIRECT = ROOT / "method/singular/solve_direct_lex.sing"

SYSTEM = ROOT / "data/system.json"
REFERENCE = ROOT / "certificate/reference_certificate.json"

RESULTS = ROOT / "method/tuning_results.csv"
CANDIDATES = ROOT / "method/candidates"

CANDIDATES.mkdir(
    parents=True,
    exist_ok=True,
)

RNG = random.Random(20260922)


parameter_grid = list(
    itertools.product(
        [24, 28, 32, 36, 40, 44],    # solutions
        [5, 7, 9],                     # recovery degree
        [0, 2, 4, 6],                  # mixing rounds
        [1, 2],                         # shear pairs
        [
            20260922,
            20260923,
            20260924,
            20260925,
        ],
    )
)

RNG.shuffle(parameter_grid)

# Don't search the entire Cartesian product initially.
parameter_grid = parameter_grid[:40]


def run_quiet(args, env=None, timeout=None):
    start = time.perf_counter()

    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )

        elapsed = (
            time.perf_counter() - start
        )

        return (
            result.returncode,
            elapsed,
            result.stdout,
            result.stderr,
        )

    except subprocess.TimeoutExpired:
        elapsed = (
            time.perf_counter() - start
        )

        return (
            124,
            elapsed,
            "",
            "TIMEOUT",
        )


def system_stats():
    with open(
        SYSTEM,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    counts = [
        len(poly["terms"])
        for poly in data["polynomials"]
    ]

    degrees = []

    for poly in data["polynomials"]:
        degrees.append(
            max(
                sum(term["exponents"])
                for term in poly["terms"]
            )
        )

    return {
        "size_mb": (
            SYSTEM.stat().st_size
            / (1024 * 1024)
        ),
        "terms": sum(counts),
        "max_degree": max(degrees),
    }


def singular_runtime(script, timeout):
    code, seconds, _, _ = run_quiet(
        [
            "Singular",
            str(script),
        ],
        timeout=timeout,
    )

    return code, seconds


def save_candidate(
    candidate_id,
    params,
    metrics,
):
    out = CANDIDATES / candidate_id
    out.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        SYSTEM,
        out / "system.json",
    )

    shutil.copy2(
        ROOT / "data/spec.json",
        out / "spec.json",
    )

    shutil.copy2(
        REFERENCE,
        out / "reference_certificate.json",
    )

    shutil.copy2(
        ROOT / "benchmark/tests/data/ground_truth.json",
        out / "ground_truth.json",
    )

    with open(
        out / "metrics.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {
                "parameters": params,
                "metrics": metrics,
            },
            f,
            indent=2,
        )


rows = []


for index, (
    n_solutions,
    recovery_degree,
    mixing_rounds,
    shear_pairs,
    seed,
) in enumerate(parameter_grid, 1):

    params = {
        "solutions": n_solutions,
        "recovery_degree": recovery_degree,
        "mixing_rounds": mixing_rounds,
        "shear_pairs": shear_pairs,
        "seed": seed,
    }

    candidate_id = (
        f"n{n_solutions}"
        f"_r{recovery_degree}"
        f"_m{mixing_rounds}"
        f"_s{shear_pairs}"
        f"_seed{seed}"
    )

    print(
        f"[{index:02d}/{len(parameter_grid)}] "
        f"{candidate_id}",
        flush=True,
    )

    env = os.environ.copy()

    env.update({
        "FFE_N_SOLUTIONS":
            str(n_solutions),
        "FFE_RECOVERY_DEGREE":
            str(recovery_degree),
        "FFE_MIXING_ROUNDS":
            str(mixing_rounds),
        "FFE_SHEAR_PAIRS":
            str(shear_pairs),
        "FFE_SEED":
            str(seed),
    })

    # Generate.
    code, _, _, _ = run_quiet(
        [
            sys.executable,
            str(GENERATOR),
        ],
        env=env,
        timeout=120,
    )

    if code != 0:
        print("  generator failed")
        continue

    stats = system_stats()

    # Reject bloated candidates immediately.
    if (
        stats["size_mb"] > 6.0
        or stats["terms"] > 35000
    ):
        print(
            "  rejected: too large "
            f"({stats['size_mb']:.2f} MB, "
            f"{stats['terms']} terms)"
        )
        continue

    # Exact reference verification.
    code, verify_seconds, stdout, _ = run_quiet(
        [
            sys.executable,
            str(VERIFIER),
            str(REFERENCE),
        ],
        timeout=10,
    )

    verify_ok = (
        code == 0
        and stdout.strip().splitlines()[-1:]
        == ["1"]
    )

    if not verify_ok:
        print("  rejected: verifier failed")
        continue

    # Generate Singular scripts.
    code, _, _, _ = run_quiet(
        [
            sys.executable,
            str(CONVERTER),
        ],
        timeout=60,
    )

    if code != 0:
        print("  converter failed")
        continue

    fglm_code, fglm_quick = (
        singular_runtime(
            FGLM,
            timeout=5,
        )
    )

    if fglm_code == 0:
        fglm_seconds = fglm_quick

        if fglm_seconds < 1.0:
            print(
                f"  too easy: "
                f"FGLM {fglm_seconds:.3f}s"
            )

            rows.append({
                **params,
                **stats,
                "verify_seconds":
                    verify_seconds,
                "fglm_seconds":
                    fglm_seconds,
                "fglm_status":
                    "easy",
                "direct_seconds":
                    "",
                "direct_status":
                    "",
            })

            continue

    else:
        fglm_code, fglm_seconds = (
            singular_runtime(
                FGLM,
                timeout=90,
            )
        )

    if fglm_code != 0:
        print(
            "  too hard: "
            "FGLM > 90s"
        )

        rows.append({
            **params,
            **stats,
            "verify_seconds":
                verify_seconds,
            "fglm_seconds":
                90.0,
            "fglm_status":
                "timeout",
            "direct_seconds":
                "",
            "direct_status":
                "",
        })

        continue

    print(
        f"  FGLM: {fglm_seconds:.3f}s"
    )

    if not 1.0 <= fglm_seconds <= 90.0:
        continue

    # Direct lex gets at most 30 seconds.
    direct_code, direct_seconds = (
        singular_runtime(
            DIRECT,
            timeout=30,
        )
    )

    direct_status = (
        "ok"
        if direct_code == 0
        else "timeout"
    )

    if direct_code != 0:
        direct_seconds = 30.0

    print(
        f"  direct: {direct_status} "
        f"{direct_seconds:.3f}s"
    )

    metrics = {
        **stats,
        "verify_seconds":
            verify_seconds,
        "fglm_seconds":
            fglm_seconds,
        "direct_seconds":
            direct_seconds,
        "direct_status":
            direct_status,
    }

    # Save genuinely interesting candidates.
    if (
        fglm_seconds >= 3.0
        and (
            direct_status == "timeout"
            or direct_seconds
            >= 5 * fglm_seconds
        )
    ):
        print("  *** SAVING CANDIDATE ***")

        save_candidate(
            candidate_id,
            params,
            metrics,
        )

    rows.append({
        **params,
        **stats,
        "verify_seconds":
            verify_seconds,
        "fglm_seconds":
            fglm_seconds,
        "fglm_status":
            "ok",
        "direct_seconds":
            direct_seconds,
        "direct_status":
            direct_status,
    })


if rows:
    columns = sorted({
        key
        for row in rows
        for key in row
    })

    with open(
        RESULTS,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=columns,
        )

        writer.writeheader()
        writer.writerows(rows)


print()
print("Search complete.")
print(f"Results: {RESULTS}")
print(f"Candidates: {CANDIDATES}")