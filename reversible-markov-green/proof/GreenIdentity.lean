import ReversibleMarkov.Basic

open scoped BigOperators

namespace ReversibleMarkov

/--
Under detailed balance, reversing the two indices in the weighted
generator sum changes the sign of the increment.
-/
theorem reversible_green_identity
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb :
      ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      = -dirichletForm π q f g := by
  classical

  unfold weightedInner generator dirichletForm

  have hleft :
      (∑ x,
          π x * f x *
            (∑ y, q x y * (g y - g x))) =
        ∑ x, ∑ y,
          π x * q x y * f x *
            (g y - g x) := by
    apply Finset.sum_congr rfl
    intro x hx
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro y hy
    ring

  have hswap :
      (∑ x, ∑ y,
          π x * q x y * f x *
            (g y - g x)) =
        -(∑ x, ∑ y,
          π x * q x y * f y *
            (g y - g x)) := by
    calc
      (∑ x, ∑ y,
          π x * q x y * f x *
            (g y - g x))
          =
        ∑ x, ∑ y,
          π y * q y x * f y *
            (g x - g y) := by
              rw [Finset.sum_comm]

      _ =
        ∑ x, ∑ y,
          π x * q x y * f y *
            (g x - g y) := by
              apply Finset.sum_congr rfl
              intro x hx
              apply Finset.sum_congr rfl
              intro y hy
              rw [← hdb x y]

      _ =
        ∑ x, ∑ y,
          -(π x * q x y * f y *
            (g y - g x)) := by
              apply Finset.sum_congr rfl
              intro x hx
              apply Finset.sum_congr rfl
              intro y hy
              ring

      _ =
        -(∑ x, ∑ y,
          π x * q x y * f y *
            (g y - g x)) := by
              simp

  have hsplit :
      (∑ x, ∑ y,
          π x * q x y *
            (f y - f x) *
            (g y - g x)) =
        (∑ x, ∑ y,
          π x * q x y * f y *
            (g y - g x)) -
        (∑ x, ∑ y,
          π x * q x y * f x *
            (g y - g x)) := by
    calc
      (∑ x, ∑ y,
          π x * q x y *
            (f y - f x) *
            (g y - g x))
          =
        ∑ x, ∑ y,
          (π x * q x y * f y *
              (g y - g x) -
           π x * q x y * f x *
              (g y - g x)) := by
                apply Finset.sum_congr rfl
                intro x hx
                apply Finset.sum_congr rfl
                intro y hy
                ring

      _ =
        ∑ x,
          ((∑ y,
              π x * q x y * f y *
                (g y - g x)) -
           (∑ y,
              π x * q x y * f x *
                (g y - g x))) := by
                apply Finset.sum_congr rfl
                intro x hx
                rw [Finset.sum_sub_distrib]

      _ =
        (∑ x, ∑ y,
          π x * q x y * f y *
            (g y - g x)) -
        (∑ x, ∑ y,
          π x * q x y * f x *
            (g y - g x)) := by
              rw [Finset.sum_sub_distrib]

  rw [hleft, hsplit]
  simp only [hswap]
  ring


/--
Detailed balance implies conservation of total weighted mass.
-/
theorem reversible_mass_conservation
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb :
      ∀ x y, π x * q x y = π y * q y x) :
    ∑ x, π x * generator q f x = 0 := by
  have h :=
    reversible_green_identity
      π q (fun _ => (1 : ℝ)) f hdb

  simpa [weightedInner, dirichletForm] using h


/--
The Dirichlet form is symmetric in its two function arguments.
-/
theorem dirichletForm_symmetric
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ) :
    dirichletForm π q f g =
      dirichletForm π q g f := by
  classical

  unfold dirichletForm

  apply congrArg
    (fun z : ℝ => (1 / 2 : ℝ) * z)

  apply Finset.sum_congr rfl
  intro x hx

  apply Finset.sum_congr rfl
  intro y hy

  ring


/--
The weighted pairing is symmetric.
-/
theorem weightedInner_symmetric
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (f g : α → ℝ) :
    weightedInner π f g =
      weightedInner π g f := by
  classical

  unfold weightedInner

  apply Finset.sum_congr rfl
  intro x hx
  ring


/--
A generator satisfying detailed balance is self-adjoint with respect
to the weighted pairing.
-/
theorem reversible_generator_self_adjoint
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f g : α → ℝ)
    (hdb :
      ∀ x y, π x * q x y = π y * q y x) :
    weightedInner π f (generator q g)
      =
    weightedInner π (generator q f) g := by
  calc
    weightedInner π f (generator q g)
        =
      -dirichletForm π q f g :=
        reversible_green_identity
          π q f g hdb

    _ =
      -dirichletForm π q g f := by
        rw [dirichletForm_symmetric]

    _ =
      weightedInner π g (generator q f) :=
        (reversible_green_identity
          π q g f hdb).symm

    _ =
      weightedInner π (generator q f) g :=
        weightedInner_symmetric
          π g (generator q f)


/--
If the weights and transition rates are nonnegative, then the
Dirichlet form is nonnegative on the diagonal.
-/
theorem reversible_dirichlet_nonneg
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    0 ≤ dirichletForm π q f f := by
  classical

  unfold dirichletForm

  apply mul_nonneg
  · norm_num

  · apply Fintype.sum_nonneg
    intro x

    apply Fintype.sum_nonneg
    intro y

    have hpq :
        0 ≤ π x * q x y :=
      mul_nonneg (hπ x) (hq x y)

    calc
      0 ≤
          (π x * q x y) *
            (f y - f x) ^ 2 :=
        mul_nonneg hpq (sq_nonneg _)

      _ =
          π x * q x y *
            (f y - f x) *
            (f y - f x) := by
        ring


/--
For a reversible generator with nonnegative rates and weights,
the quadratic generator energy is nonpositive.
-/
theorem reversible_energy_nonpos
    {α : Type*} [Fintype α]
    (π : α → ℝ)
    (q : α → α → ℝ)
    (f : α → ℝ)
    (hdb :
      ∀ x y, π x * q x y = π y * q y x)
    (hπ : ∀ x, 0 ≤ π x)
    (hq : ∀ x y, 0 ≤ q x y) :
    weightedInner π f (generator q f) ≤ 0 := by
  calc
    weightedInner π f (generator q f)
        =
      -dirichletForm π q f f :=
        reversible_green_identity
          π q f f hdb

    _ ≤ 0 :=
      neg_nonpos.mpr
        (reversible_dirichlet_nonneg
          π q f hπ hq)


#check reversible_green_identity
#check reversible_mass_conservation
#check reversible_generator_self_adjoint
#check reversible_dirichlet_nonneg
#check reversible_energy_nonpos

#print axioms reversible_green_identity
#print axioms reversible_mass_conservation
#print axioms reversible_generator_self_adjoint
#print axioms reversible_dirichlet_nonneg
#print axioms reversible_energy_nonpos

end ReversibleMarkov