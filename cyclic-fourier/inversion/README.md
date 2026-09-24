# Cyclic Fourier Inversion

## Difficulty

This is a Lean 4 formalization task. The mathematics is classical, but the
formal proof requires finite-sum rearrangement, primitive additive-character
orthogonality, ZMod indexing, complex normalization, and function extensionality.
The expected expert time is approximately four hours.

## Reference solution

The reference solution expands the inverse transform applied to the forward
transform, applies character orthogonality, collapses the resulting diagonal
kernel, cancels the nonzero cardinality factor, and derives injectivity of the
forward transform.

## Verification

The verifier checks the exact required theorem names and types, rejects
`sorry`, `admit`, and user-defined axioms, compiles the submission with the
pinned Lean/Mathlib project, and audits the axiom footprint of the required
declarations.