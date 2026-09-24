import Mathlib.NumberTheory.LegendreSymbol.AddCharacter

open scoped BigOperators

namespace CyclicFourier

/-- The unnormalized discrete Fourier transform on `ZMod N`. -/
noncomputable def cyclicDFT {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (c : ZMod N → ℂ) :
    ZMod N → ℂ :=
  fun j => ∑ k, c k * ψ (j * k)

/-- The normalized inverse discrete Fourier transform on `ZMod N`. -/
noncomputable def cyclicIDFT {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (y : ZMod N → ℂ) :
    ZMod N → ℂ :=
  fun q =>
    (N : ℂ)⁻¹ * ∑ j, y j * ψ (-(j * q))

#check cyclicDFT
#check cyclicIDFT

end CyclicFourier
