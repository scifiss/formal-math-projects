# Reversible Markov Green Identity

A Lean 4 formalization of the basic analytic identities of a finite-state
reversible Markov generator, under detailed balance.

## Mathematics

For a finite state space `α`, a stationary weight `π : α → ℝ`, and
transition rates `q : α → α → ℝ`, [`ReversibleMarkov/Basic.lean`](ReversibleMarkov/Basic.lean)
defines:

```text
generator q f      = fun x => ∑ y, q x y * (f y - f x)
weightedInner π f g = ∑ x, π x * f x * g x
dirichletForm π q f g = (1/2) * ∑ x, ∑ y, π x * q x y * (f y - f x) * (g y - g x)
```

Under the detailed-balance condition `π x * q x y = π y * q y x`, the
following identities are proved:

- `reversible_green_identity` — a discrete Green identity,
  `⟪f, generator q g⟫_π = -dirichletForm π q f g`.
- `reversible_mass_conservation` — the generator conserves total weighted
  mass: `∑ x, π x * generator q f x = 0`.
- `reversible_generator_self_adjoint` — the generator is self-adjoint with
  respect to the weighted inner product.
- `reversible_dirichlet_nonneg` — under nonnegative weights and rates, the
  diagonal Dirichlet form is nonnegative.
- `reversible_energy_nonpos` — under the same nonnegativity assumptions and
  detailed balance, the generator energy `⟪f, generator q f⟫_π` is
  nonpositive.

## Proof strategy

The proof, in [`proof/GreenIdentity.lean`](proof/GreenIdentity.lean),
establishes the Green identity first and derives the remaining results from
it:

1. expand the weighted generator pairing into a double finite sum,
2. reverse the two summation indices using detailed balance, picking up a
   sign change,
3. split the resulting sum to recover the Dirichlet form, giving the Green
   identity,
4. specialize `f` to the constant function `1` to obtain mass conservation
   directly from the Green identity,
5. use symmetry of the Dirichlet form and the weighted inner product,
   together with the Green identity applied in both argument orders, to
   derive self-adjointness of the generator,
6. prove diagonal Dirichlet-form nonnegativity termwise, since each summand
   is a product of nonnegative weights, rates, and a squared difference,
7. combine the Green identity with Dirichlet-form nonnegativity to conclude
   that the generator energy is nonpositive.

## Verification

The proof was checked by compiling it against the pinned Lean/Mathlib
toolchain and auditing the axiom footprint of all five required theorems —
confirming each depends only on the standard `propext`, `Classical.choice`,
and `Quot.sound` axioms, with no `sorry`, `admit`, or user-introduced
axioms. The benchmark packaging used to originally pose and mechanically
check this result is preserved under [`benchmark/`](benchmark) for
reproducibility.
