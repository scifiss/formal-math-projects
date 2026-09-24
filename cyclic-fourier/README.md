# Cyclic Fourier Formalization

Two Lean 4 projects over `ZMod N` with complex additive characters:

- `inversion/` proves Fourier inversion and injectivity of the cyclic DFT.
- `convolution/` proves that the cyclic DFT turns convolution into pointwise multiplication.

Each subproject is self-contained with its pinned Lean environment, reference proof, instructions, and verifier.

The convolution reference uses the same character-orthogonality and inversion lemmas as the inversion project, but the two task packages remain separate for independent study and verification.
