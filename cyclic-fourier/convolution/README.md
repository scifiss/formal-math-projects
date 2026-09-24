# Cyclic Fourier Convolution

A Lean 4 formalization of the cyclic convolution theorem for the discrete
Fourier transform on the finite cyclic group `ZMod N`.

## Mathematics

Building on the same character-based Fourier transform used in the
companion [`inversion`](../inversion) project, `CyclicFourier.Basic` also
defines cyclic convolution:

```text
cyclicConvolution c d = fun x => ∑ k, c k * d (x - k)
```

The result proved here is the convolution theorem:

```text
cyclicDFT ψ (cyclicConvolution c d) = fun j => cyclicDFT ψ c j * cyclicDFT ψ d j
```

i.e. the Fourier transform turns cyclic convolution into pointwise
multiplication of the transformed sequences.

## Proof strategy

The proof, in [`proof/Convolution.lean`](proof/Convolution.lean), first
re-establishes the character-orthogonality and Fourier-inversion lemmas from
the companion project as local building blocks, then proves the convolution
theorem itself by:

1. expanding the transform of the convolution as a double finite sum,
2. exchanging the order of summation,
3. reindexing the inner sum by translation in `ZMod N`,
4. using additivity of the character to split the character factor across
   the translated and untranslated frequency terms,
5. factoring the resulting double sum into the product of the two
   individual Fourier transforms.

## Verification

The proof was checked by compiling it against the pinned Lean/Mathlib
toolchain and auditing its axiom footprint — confirming it depends only on
the standard `propext`, `Classical.choice`, and `Quot.sound` axioms, with no
`sorry`, `admit`, or user-introduced axioms. The benchmark packaging used to
originally pose and mechanically check this result is preserved under
[`benchmark/`](benchmark) for reproducibility.
