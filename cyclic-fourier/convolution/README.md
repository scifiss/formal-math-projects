# Cyclic Fourier Inversion and Convolution

## Overview

This Lean 4 task formalizes basic finite Fourier analysis over `ZMod N` with complex additive characters.

The reference solution proves:

* additive-character orthogonality,
* Fourier inversion,
* injectivity of `cyclicDFT`,
* and the cyclic convolution theorem.

## Reference solution

The solution is in:

```text
solution/Reference.lean
```

It uses finite-sum rearrangement, `ZMod` arithmetic, additive-character identities, and reindexing of cyclic sums.

To compile it:

```bash
cd environment
lake env lean ../solution/Reference.lean
```

## Verification

The verifier checks the required theorem names and types, rejects `sorry`, `admit`, and user-defined axioms, compiles the submission in the pinned Lean/Mathlib environment, and audits the axiom footprint.

A successful verification writes:

```text
1
```

to:

```text
/logs/verifier/reward.txt
```
