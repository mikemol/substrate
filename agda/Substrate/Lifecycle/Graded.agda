------------------------------------------------------------------------
-- Substrate.Lifecycle.Graded
--
-- Defines: lifecycle-graded, lifecycle-step
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Graded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
-- ⚑ THE BARREL, NOT THE LEAF — and the distinction is load-bearing.
-- `GradedDivStr` resolves to TWO homes (`agda_defs`): the leaf
-- `Wedge.Graded.DivStr` and the barrel `Wedge.Graded`. They are DIFFERENT
-- records, so importing the leaf here while `Graded.Adjunction` expects the
-- barrel's produced `[UnequalTerms]` — two types with the same name failing
-- to unify, four frames from the cause. `WitnessTower.Wedge.Graded:31` (the
-- working precedent) imports the barrel; matching it is the fix.
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; recon; gcell; gforget)
open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Path


------------------------------------------------------------------------
-- THE LIFECYCLE IS A LEHMER ALGEBRA — the `GradedDivStr` instance.
--
--     C n = LifecyclePath n        the pipeline state after n boundaries
--     R n = Fin (suc n)            the ORIENTATION at that boundary
--     recon n p r = p ◂ r          extend the path by one oriented step
--
-- ⚑ THIS IS THE INSTANTIATION, NOT A RESEMBLANCE. Everything the adjunction
-- provides is uniform in `G : GradedDivStr C R` — the hom-iso
-- (`GradedWedge G n a b ≅ gTerm G n a b`, definitional), the triangle law,
-- `reorient` — so supplying `recon` is the whole obligation and the rest
-- follows with no further proof. `Algebra.Wedge.Graded.Adjunction` is
-- explicit that the Free⊣Forgetful core is uniform across all three wedge
-- carriers.
--
-- ⚑ AND IT MIRRORS `WitnessTower.Wedge.Graded` EXACTLY, which is the
-- generative tower's own instance:
--     tower-graded : GradedDivStr Perm (λ n → Fin (suc n))
--     tower-graded = record { recon = λ n σ p → insert-at p σ }
-- Same residue family, same shape. The lifecycle and the permutation tower
-- are two carriers of ONE algebra — which is what makes a codegen path from
-- an extracted `.agdai` mechanical rather than bespoke.
------------------------------------------------------------------------

lifecycle-graded : GradedDivStr LifecyclePath (λ n → Fin (suc n))
lifecycle-graded = record
  { recon = λ _ p r → p ◂ r
  }

-- the canonical wedge at each step: the path `p ◂ r` decomposes against its
-- base `p` with residue `r`, by `refl` — the orientation is recorded, not
-- reconstructed.
lifecycle-step : (n : ℕ) (p : LifecyclePath n) (r : Fin (suc n)) →
                 GradedWedge lifecycle-graded n (p ◂ r) p
lifecycle-step n p r = record { rem = r ; wedge-eq = refl }
