# Finite Cyclic Fourier Inversion in Lean 4

> Archived verbatim from the original benchmark prompt, preserved here only
> so the verifier setup in this folder remains reproducible. The completed
> proof and its writeup live in [`../proof/Inversion.lean`](../proof/Inversion.lean)
> and [`../README.md`](../README.md).

Complete the Lean proof for Fourier inversion on a finite cyclic group.

The public project defines:

- `CyclicFourier.cyclicDFT`
- `CyclicFourier.cyclicIDFT`

Your submission must be a file named `Submission.lean` containing proofs of these two exact theorems.

```lean
import CyclicFourier.Basic

namespace CyclicFourier

theorem cyclicIDFT_cyclicDFT
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive)
    (c : ZMod N → ℂ) :
    cyclicIDFT ψ (cyclicDFT ψ c) = c := by
  -- prove this
  sorry

theorem cyclicDFT_injective
    {N : ℕ} [NeZero N]
    (ψ : AddChar (ZMod N) ℂ)
    (hψ : ψ.IsPrimitive) :
    Function.Injective (cyclicDFT ψ) := by
  -- prove this
  sorry

end CyclicFourier

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
