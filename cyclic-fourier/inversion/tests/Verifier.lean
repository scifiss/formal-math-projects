import Submission

open scoped BigOperators

namespace CyclicFourier

example
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (c : ZMod N → ℂ) :
    cyclicIDFT ψ (cyclicDFT ψ c) = c := by
  exact cyclicIDFT_cyclicDFT ψ hψ c

example
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive) :
    Function.Injective (cyclicDFT ψ) := by
  exact cyclicDFT_injective ψ hψ

end CyclicFourier

#print axioms CyclicFourier.cyclicIDFT_cyclicDFT
#print axioms CyclicFourier.cyclicDFT_injective