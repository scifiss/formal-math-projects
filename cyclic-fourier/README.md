# Cyclic Fourier Analysis in Lean 4

Formalizations of finite Fourier analysis over `ZMod N` using complex-valued
additive characters. Both projects build on the same small library
(`CyclicFourier.Basic`), which defines the discrete Fourier transform, its
normalized inverse, and cyclic convolution.

- [`inversion/`](inversion) — Fourier inversion and injectivity of the
  discrete Fourier transform.
- [`convolution/`](convolution) — the cyclic convolution theorem: the
  Fourier transform turns convolution into pointwise multiplication.

Each project is a self-contained Lean package at its own root (`lakefile.toml`,
`lean-toolchain`, `CyclicFourier/`), with the completed proof under `proof/`.
Benchmark packaging originally used to pose and mechanically verify each
result is preserved under each project's `benchmark/` directory for
reproducibility.
