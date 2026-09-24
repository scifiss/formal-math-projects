import CyclicFourier.Basic

open scoped BigOperators

namespace CyclicFourier

/--
Orthogonality of a primitive additive character on `ZMod N`.
The sum is `N` when the multiplicative shift is zero, and zero otherwise.
-/
theorem character_orthogonality
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (b : ZMod N) :
    ∑ j : ZMod N, ψ (j * b) =
      if b = 0 then (N : ℂ) else 0 := by
  simpa using (AddChar.sum_mulShift (ψ := ψ) b hψ)

/--
The form of character orthogonality needed by Fourier inversion.
-/
theorem character_orthogonality_sub
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (k q : ZMod N) :
    ∑ j : ZMod N, ψ (j * (k - q)) =
      if k = q then (N : ℂ) else 0 := by
  simpa [sub_eq_zero] using
    (character_orthogonality ψ hψ (k - q))


/--
The forward and inverse character factors combine into the
difference-frequency character.
-/
theorem character_mul_neg
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (j k q : ZMod N) :
    ψ (j * k) * ψ (-(j * q)) =
      ψ (j * (k - q)) := by
  rw [← ψ.map_add_eq_mul]
  congr 1
  ring

/--
The complete character kernel is `N` on the diagonal and zero away
from the diagonal.
-/
theorem character_kernel_sum
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (k q : ZMod N) :
    ∑ j : ZMod N, ψ (j * k) * ψ (-(j * q)) =
      if k = q then (N : ℂ) else 0 := by
  calc
    ∑ j : ZMod N, ψ (j * k) * ψ (-(j * q))
        = ∑ j : ZMod N, ψ (j * (k - q)) := by
            apply Finset.sum_congr rfl
            intro j _
            exact character_mul_neg ψ j k q
    _ = if k = q then (N : ℂ) else 0 :=
      character_orthogonality_sub ψ hψ k q

/--
Expanding the DFT inside the inverse kernel and exchanging the two
finite summations.
-/
theorem dft_kernel_expansion
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (c : ZMod N → ℂ)
    (q : ZMod N) :
    ∑ j : ZMod N,
        cyclicDFT ψ c j * ψ (-(j * q)) =
      ∑ k : ZMod N,
        c k * ∑ j : ZMod N,
          ψ (j * k) * ψ (-(j * q)) := by
  simp only [cyclicDFT]
  simp_rw [Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k _
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j _
  ring

/--
After character orthogonality, only the diagonal frequency `k = q`
survives.
-/
theorem dft_kernel_collapse
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (c : ZMod N → ℂ)
    (q : ZMod N) :
    ∑ j : ZMod N,
        cyclicDFT ψ c j * ψ (-(j * q)) =
      (N : ℂ) * c q := by
  rw [dft_kernel_expansion ψ c q]
  simp_rw [character_kernel_sum ψ hψ]
  simp [mul_comm]

/--
The normalized inverse Fourier transform recovers the original
coefficient vector.
-/
theorem cyclicIDFT_cyclicDFT
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (c : ZMod N → ℂ) :
    cyclicIDFT ψ (cyclicDFT ψ c) = c := by
  funext q
  simp only [cyclicIDFT]
  rw [dft_kernel_collapse ψ hψ c q]

  have hN : (N : ℂ) ≠ 0 := by
    exact_mod_cast (NeZero.ne N)

  calc
    (N : ℂ)⁻¹ * ((N : ℂ) * c q)
        = ((N : ℂ)⁻¹ * (N : ℂ)) * c q :=
          (mul_assoc _ _ _).symm
    _ = c q := by
      simp [hN]

/--
The cyclic Fourier transform associated with a primitive additive
character is injective.
-/
theorem cyclicDFT_injective
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive) :
    Function.Injective (cyclicDFT ψ) := by
  intro c d hcd
  calc
    c = cyclicIDFT ψ (cyclicDFT ψ c) :=
      (cyclicIDFT_cyclicDFT ψ hψ c).symm
    _ = cyclicIDFT ψ (cyclicDFT ψ d) :=
      congrArg (cyclicIDFT ψ) hcd
    _ = d :=
      cyclicIDFT_cyclicDFT ψ hψ d



#check cyclicDFT_injective
#check cyclicIDFT_cyclicDFT
#check dft_kernel_collapse
#check dft_kernel_expansion
#check character_mul_neg
#check character_kernel_sum
#check character_orthogonality
#check character_orthogonality_sub


#print axioms cyclicIDFT_cyclicDFT
#print axioms cyclicDFT_injective
end CyclicFourier