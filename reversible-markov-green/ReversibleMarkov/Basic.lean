import Mathlib

open scoped BigOperators

namespace ReversibleMarkov

/-- Generator of a finite-state continuous-time Markov-type system. -/
noncomputable def generator
    {α : Type*} [Fintype α]
    (q : α → α → ℝ)
    (f : α → ℝ) :
    α → ℝ :=
  fun x =>
    ∑ y, q x y * (f y - f x)

/-- Weighted inner product associated with a finite measure `π`. -/
noncomputable def weightedInner
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (f g : α → ℝ) :
    ℝ :=
  ∑ x, π x * f x * g x

/-- Dirichlet form associated with the reversible rates `q`. -/
noncomputable def dirichletForm
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ) :
    ℝ :=
  (1 / 2 : ℝ) *
    ∑ x, ∑ y,
      π x * q x y *
        (f y - f x) *
        (g y - g x)

end ReversibleMarkov