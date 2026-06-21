------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.CrossMulGraded
--
-- ⊙.c5b — a CrossMix witness whose cross-term nilpotency degree GENUINELY VARIES
-- across pairs, the graded half of conjecture #5. `CrossMul.coherent-everywhere`
-- only exhibits the degenerate extreme (every cross term = z, degree 0, via the
-- square-zero carrier two-mul); the comment there notes "GRADED coherence (degree
-- genuinely varying) needs a richer common carrier". M₂ over F₂ (Wedderburn) is
-- that carrier.
--
-- Embed Two → M₂ so the cross term varies: ε ↦ e₁₁ (idempotent) on the LEFT,
-- ε ↦ e₁₂ (the corner) on the RIGHT. Then cross(ε,ε) = e₁₁·e₁₂ = e₁₂, a NONZERO
-- degree-2 nilpotent (e₁₂² = 𝟎) — a genuine graded obstruction — while every other
-- pair gives 𝟎 (clean, degree 0). Still coherent everywhere (all cross terms
-- nilpotent), but the degree is now 0 OR 2, not uniformly 0. (Ties ⊙.assoc: the
-- varying degree is the cross-mixer's graded cost, the same shape as dε.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.CrossMulGraded where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Vec using (_∷_)
open import Substrate.Algebra.F2 using (F₂; 𝟙; 𝟙≢𝟘)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
open import Substrate.Algebra.Wedge.Mul using (Two; ε; two-div) renaming (𝟘 to t0)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)
open import Substrate.Algebra.Wedge.Wedderburn
  using (M2; M2-div; M2-mul-str; 𝟎; e₁₁; e₁₂)

-- Two → M₂: the zero goes to 𝟎; the live element goes to e₁₁ (left) / e₁₂ (right).
tA tB : Two → M2
tA t0 = 𝟎
tA ε  = e₁₁
tB t0 = 𝟎
tB ε  = e₁₂

embA-M2 embB-M2 : Bridge two-div M2-div
embA-M2 = record { translate = tA ; respects = λ _ _ _ → refl ; z-pres = refl }
embB-M2 = record { translate = tB ; respects = λ _ _ _ → refl ; z-pres = refl }

mix-M2 : CrossMix two-div two-div M2-mul-str
mix-M2 = record { embA = embA-M2 ; embB = embB-M2 }

------------------------------------------------------------------------
-- Coherent everywhere, but the nilpotency degree VARIES: (ε,ε) needs degree 2
-- (n = 1), every other pair is clean (degree 0, n = 0).
------------------------------------------------------------------------

coherent-graded : (a b : Two) → Coherent mix-M2 a b
coherent-graded t0 t0 = 0 , refl                 -- 𝟎·𝟎  = 𝟎 (clean)
coherent-graded t0 ε  = 0 , refl                 -- 𝟎·e₁₂ = 𝟎 (clean)
coherent-graded ε  t0 = 0 , refl                 -- e₁₁·𝟎 = 𝟎 (clean)
coherent-graded ε  ε  = 1 , refl                 -- e₁₁·e₁₂ = e₁₂, e₁₂² = 𝟎 (degree 2)

-- The (ε,ε) cross term is the named corner e₁₂ — a NONZERO degree-2 obstruction.
cross-εε : cross mix-M2 ε ε ≡ e₁₂
cross-εε = refl

-- second matrix entry (e₁₂ has 𝟙 here, 𝟎 has 𝟘) — distinguishes the obstruction.
entry₂ : M2 → F₂
entry₂ (_ ∷ x ∷ _) = x

-- the degree GENUINELY varies: the (ε,ε) cross term is NOT z, so it cannot be
-- witnessed clean (degree 0) — unlike coherent-everywhere's uniform degree 0.
cross-εε-not-clean : cross mix-M2 ε ε ≡ 𝟎 → ⊥
cross-εε-not-clean p = 𝟙≢𝟘 (cong entry₂ p)
