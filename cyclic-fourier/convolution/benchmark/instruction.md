# Finite Cyclic Fourier Convolution in Lean 4

> Archived verbatim from the original benchmark prompt, preserved here only
> so the verifier setup in this folder remains reproducible. The completed
> proof and its writeup live in [`../proof/Convolution.lean`](../proof/Convolution.lean)
> and [`../README.md`](../README.md).

Complete the Lean proof of the cyclic convolution theorem for the finite cyclic Fourier transform.

The public project defines:

* `CyclicFourier.cyclicDFT`
* `CyclicFourier.cyclicIDFT`
* `CyclicFourier.cyclicConvolution`

Your submission must be a file named `Submission.lean` containing a proof of this exact theorem:

```lean
import CyclicFourier.Basic

namespace CyclicFourier

theorem cyclicDFT_cyclicConvolution
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (c d : ZMod N → ℂ) :
    cyclicDFT ψ (cyclicConvolution c d)
      = fun j => cyclicDFT ψ c j * cyclicDFT ψ d j := by
  classical
  funext j
  simp only [cyclicDFT, cyclicConvolution]
  -- prove this
  sorry

end CyclicFourier
```

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
