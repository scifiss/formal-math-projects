# Finite-Field Elimination Certificate

An exact elimination certificate for a custom zero-dimensional multivariate
polynomial system over the prime field `F_1009`, verified using exact
finite-field arithmetic rather than floating-point approximation.

## Mathematics

The public system, in [`data/system.json`](data/system.json), is a
zero-dimensional ideal in the variables `x0, ..., x6, t` over `F_1009`. It
is constructed to admit a shape-position representation in an auxiliary
elimination parameter `s`, related to the public variables by
`s = t + x0*x1`:

```text
h(s) = 0
x_i  = r_i(s)   for i = 0, ..., 6
t    = r_t(s)
```

where `h` is monic, splits into distinct linear factors over `F_1009`, and
each root of `h` determines exactly one solution of the public system.

## Method

The design and generation of the instance, and the routine that solves it,
are in [`method/`](method):

- [`generate_instance.py`](method/generate_instance.py) builds the hidden
  shape-position system, applies invertible generator mixing and a
  nonlinear coordinate shear to hide the triangular structure, and emits
  the public system together with the sealed ground truth.
- [`system_to_singular.py`](method/system_to_singular.py) converts the
  public system into Singular scripts for both a degree-order Gröbner
  basis + FGLM elimination route and a direct lexicographic route.
- [`tune_instances.py`](method/tune_instances.py) searches over solution
  count, recovery degree, shear strength, and mixing rounds to select an
  instance where the FGLM route is tractable but direct lexicographic
  elimination is substantially slower.
- [`INSTANCE_DESIGN.md`](method/INSTANCE_DESIGN.md) records the final
  parameters, timing measurements, and frozen artifact hashes.

The certificate itself — a monic univariate eliminant together with one
recovery polynomial per public variable — is in
[`certificate/reference_certificate.json`](certificate/reference_certificate.json).
The final instance was calibrated so that degree-order Gröbner computation followed by FGLM recovers the elimination structure in about 4 seconds, while direct lexicographic elimination exceeded 60 seconds in local benchmarks, making algorithm selection materially important.

## Verification

The verifier, preserved under [`benchmark/tests/verifier.py`](benchmark/tests/verifier.py),
is semantic rather than textual: it enumerates the roots of the submitted
eliminant in `F_1009`, reconstructs every public-variable tuple, checks the
auxiliary parameter relation, evaluates every public polynomial exactly
modulo 1009, checks distinctness and completeness, and compares the
represented solution set against the sealed ground truth. Adversarial
checks against the verifier itself are in
[`method/test_verifier.py`](method/test_verifier.py). The remaining
benchmark packaging (`instruction.md`, `task.toml`, Dockerfiles, and the
oracle `solve.sh`) is preserved under [`benchmark/`](benchmark) for
reproducibility.
