# Reversible Markov Green Identity in Lean 4

> Archived verbatim from the original benchmark prompt, preserved here only
> so the verifier setup in this folder remains reproducible. The completed
> proof and its writeup live in [`../proof/GreenIdentity.lean`](../proof/GreenIdentity.lean)
> and [`../README.md`](../README.md).

Formalize a finite-state reversible Markov generator and prove its basic analytic identities.

The public project defines:

* `ReversibleMarkov.generator`
* `ReversibleMarkov.weightedInner`
* `ReversibleMarkov.dirichletForm`

Your submission must be a file named `Submission.lean` containing proofs of the following exact theorems:

```lean
import ReversibleMarkov.Basic

open scoped BigOperators

namespace ReversibleMarkov

theorem reversible_green_identity
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      = -dirichletForm π q f g := by
  sorry

theorem reversible_mass_conservation
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    ∑ x, π x * generator q f x = 0 := by
  sorry

theorem reversible_generator_self_adjoint
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      =
    weightedInner π (generator q f) g := by
  sorry

theorem reversible_dirichlet_nonneg
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    0 ≤ dirichletForm π q f f := by
  sorry

theorem reversible_energy_nonpos
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    weightedInner π f (generator q f) ≤ 0 := by
  sorry

end ReversibleMarkov
```

The submission must contain complete kernel-checked proofs. Do not use `sorry`, `admit`, or introduce additional axioms.

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
