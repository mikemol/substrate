{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.CertGenericProjection — ⟡cert-generic-projection: the
-- forgetful natural transformation Φ-cert ⟹ Φ-step (ℕ-div), relating the CERTIFIED
-- pattern functor (ADD 167, on CertifiedWedge) to the GENERIC one (ADD 158, on Wedge)
-- via the CertifiedWedge → Wedge forgetful map (the `wedge` accessor, forgetting
-- smallness). Lifts stage-wise (iterate) to Limit-cert ⊑ Limit — the certified limit
-- is below the generic limit.
--
-- The done cases MATCH definitionally (z ℕ-div = zero, so both done = (b≡0)×(g≡a));
-- the step case forgets smallness (cw ↦ wedge cw), rem (wedge cw) unchanged. So the
-- certified functor is a SUBFUNCTOR of the generic one — the smallness is the extra
-- structure the forgetful map drops. This is the honest bridge: 167's UNCONDITIONAL
-- certified result maps into 158/162's generic frame (where 165's hypothesis lived).
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.CertGenericProjection where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Wedge using (ℕ-div; rem)
open import Substrate.Category.Allegory.Refinement using (_⊑ᶠ_; ⊑ᶠ-trans; iterate)
open import Substrate.Algebra.Wedge.Certified using (wedge)
open import Substrate.Foundation.Sum using (inj₁; inj₂)
open import Substrate.Foundation.Product using (_,_)
-- the generic functor (158) + its Limit (162), at ℕ-div.
open import Substrate.Algebra.Wedge.TraceMuStep using (Φ-step; Φ-step-mono; step-refinement)
open import Substrate.Algebra.Wedge.TraceNuColimit using (⊤-fam; Limit)
-- the certified functor (167).
open import Substrate.Algebra.Wedge.CertifiedPhiStep
  using (Idxℕ; Φ-cert; cert-refinement; ⊤-cert; Limit-cert)

------------------------------------------------------------------------
-- ① THE FORGETFUL NATURAL TRANSFORMATION Φ-cert ⟹ Φ-step ℕ-div. done ↦ done
-- (identical, z ℕ-div = zero); certified step (cw, p) ↦ generic step (wedge cw, p)
-- — forget smallness, rem (wedge cw) is the same so p fits.
------------------------------------------------------------------------
cert→generic : (P : Idxℕ → Set) → Φ-cert P ⊑ᶠ Φ-step ℕ-div P
cert→generic P (a , b , g) (inj₁ eqs)      = inj₁ eqs
cert→generic P (a , b , g) (inj₂ (cw , p)) = inj₂ (wedge cw , p)

------------------------------------------------------------------------
-- ② STAGE-WISE: iterate cert-refinement n ⊤ ⊑ iterate step-refinement n ⊤. By
-- induction — stage 0 both ⊤ (⊤-cert = ⊤-fam definitionally); stage suc n via the
-- projection then Φ-step-mono on the IH.
------------------------------------------------------------------------
iter-proj : (n : ℕ) →
  iterate cert-refinement n ⊤-cert ⊑ᶠ iterate (step-refinement ℕ-div) n (⊤-fam ℕ-div)
iter-proj zero    i x = x
iter-proj (suc n) =
  ⊑ᶠ-trans (cert→generic (iterate cert-refinement n ⊤-cert))
           (Φ-step-mono ℕ-div (iter-proj n))

------------------------------------------------------------------------
-- ③ THE LIMIT PROJECTION: Limit-cert ⊑ Limit ℕ-div. A certified-limit element
-- (present at every certified stage) maps to a generic-limit element (present at
-- every generic stage) via iter-proj at each n.
------------------------------------------------------------------------
limit-proj : Limit-cert ⊑ᶠ Limit ℕ-div
limit-proj i l n = iter-proj n i (l n)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the CERTIFIED pattern functor (Φ-cert, ADD 167) is
-- a SUBFUNCTOR of the GENERIC one (Φ-step ℕ-div, ADD 158) via the forgetful map
-- CertifiedWedge → Wedge (cert→generic: done ↦ done, (cw,p) ↦ (wedge cw, p), forget
-- smallness). This lifts stage-wise (iter-proj, via the projection + Φ-step-mono) to
-- Limit-cert ⊑ Limit ℕ-div — the certified limit is BELOW the generic limit. The
-- either/or "certified functor (167, unconditional) vs generic functor (158/162,
-- needs 165's hypothesis)" dissolves into ONE forgetful map: the certified functor
-- carries the smallness (making the ω-continuity hypothesis a theorem, 166/167), and
-- forgetting it lands in the generic functor (where the hypothesis was assumed, 165).
-- So 167's UNCONDITIONAL certified greatest-fixed-point maps into the generic frame:
-- the smallness is EXACTLY the structure separating "hypothesis needed" (generic) from
-- "hypothesis built in" (certified). The forgetful map names the difference precisely.
------------------------------------------------------------------------
