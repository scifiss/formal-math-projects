import Submission

open scoped BigOperators

namespace ReversibleMarkov

example
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      = -dirichletForm π q f g := by
  exact reversible_green_identity π q f g hdb

example
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    ∑ x, π x * generator q f x = 0 := by
  exact reversible_mass_conservation π q f hdb

example
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      =
    weightedInner π (generator q f) g := by
  exact reversible_generator_self_adjoint π q f g hdb

example
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    0 ≤ dirichletForm π q f f := by
  exact reversible_dirichlet_nonneg π q f hπ hq

example
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb : ∀ x y, π x * q x y = π y * q y x)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    weightedInner π f (generator q f) ≤ 0 := by
  exact reversible_energy_nonpos π q f hdb hπ hq

end ReversibleMarkov

#print axioms ReversibleMarkov.reversible_green_identity
#print axioms ReversibleMarkov.reversible_mass_conservation
#print axioms ReversibleMarkov.reversible_generator_self_adjoint
#print axioms ReversibleMarkov.reversible_dirichlet_nonneg
#print axioms ReversibleMarkov.reversible_energy_nonpos