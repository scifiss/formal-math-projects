# Cyclic Fourier Inversion

A Lean 4 formalization of Fourier inversion for the discrete Fourier
transform on the finite cyclic group `ZMod N`, using a primitive complex
additive character.

## Mathematics

Given a primitive additive character `ψ` on `ZMod N`, the (unnormalized)
discrete Fourier transform and its normalized inverse are defined in
[`CyclicFourier/Basic.lean`](CyclicFourier/Basic.lean) as

```text
cyclicDFT  ψ c = fun j => ∑ k, c k * ψ (j * k)
cyclicIDFT ψ y = fun q => N⁻¹ * ∑ j, y j * ψ (-(j * q))
```

The two results proved here are:

- `cyclicIDFT_cyclicDFT` — applying the inverse transform to the forward
  transform recovers the original function exactly.
- `cyclicDFT_injective` — the forward transform is injective, as an
  immediate consequence of the first result.

## Proof strategy

The proof, in [`proof/Inversion.lean`](proof/Inversion.lean), proceeds by:

1. establishing orthogonality of the additive character over `ZMod N`
   (the sum of `ψ(j·b)` is `N` when `b = 0` and `0` otherwise),
2. expanding the inverse kernel applied to the forward transform and
   exchanging the two finite sums,
3. using character orthogonality to collapse the resulting kernel onto the
   diagonal frequency,
4. cancelling the nonzero cardinality factor `N` to recover the original
   function,
5. deriving injectivity of the forward transform directly from the
   inversion identity.

The proof relies on finite-sum rearrangement, `ZMod` indexing, and
normalization of complex additive characters; it does not introduce any
additional axioms.

## Verification

The proof was checked by compiling it against the pinned Lean/Mathlib
toolchain and auditing its axiom footprint — confirming it depends only on
the standard `propext`, `Classical.choice`, and `Quot.sound` axioms, with no
`sorry`, `admit`, or user-introduced axioms. The benchmark packaging used to
originally pose and mechanically check this result is preserved under
[`benchmark/`](benchmark) for reproducibility.
