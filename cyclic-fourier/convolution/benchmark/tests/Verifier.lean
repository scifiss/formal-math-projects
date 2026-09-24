import Submission

open scoped BigOperators

namespace CyclicFourier

example
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (c d : ZMod N → ℂ) :
    cyclicDFT ψ (cyclicConvolution c d)
      = fun j => cyclicDFT ψ c j * cyclicDFT ψ d j := by
  exact cyclicDFT_cyclicConvolution ψ c d

end CyclicFourier

#print axioms CyclicFourier.cyclicDFT_cyclicConvolution