------------------------------------------------------------------------
-- Σ-SEAM-GLUE / ΞG — the gauge-invariance side-condition.
--
-- SEAM_GLUE: "centrality must survive the sign-convention flip (even↔odd),
-- or the verdict is an artifact of one fixed gauge." The honest discharge:
-- the centrality verdict does NOT depend on the even/odd labeling.
--
--   central-sign : EVERY pure-sign element (mk s e z0) is central — for BOTH
--     labels s, with the SAME proof (it never privileges `odd`). This is
--     ΞB2i's `central-χ` generalised over the sign: the verdict is uniform
--     over the gauge.
--   gauge-flip-invariant : centrality holds at the EVEN↔ODD-FLIPPED label
--     (oflip s) too — the verdict in the other sign convention. = the
--     equivariance the SPPF torsor verifies for spans, here for the sign gauge.
--
-- (NB the naive even↔odd swap is NOT a group automorphism — oflip(a*c b) ≠
-- oflip a *c oflip b, and Aut(ℤ₂) is trivial — so "flip is the ℤ₂ factor's
-- automorphism" is loose. The real content is label-uniformity, below.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Gauge where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; _·_)
open import Substrate.Groups.V4.Axioms using (ε-left; ε-identity)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (_×_; _,_; proj₂)
open import Substrate.WitnessTower.M40Closure
  using (Chir; even; odd; _*c_; *c-comm; Z3; z0; +₃-idʳ; σ; σ-fixes-e;
         A4Z2; mk; compose; a4z2-≡; central-χ)
open A4Z2
open import Substrate.WitnessTower.M40Iso using (oflip; oflip-invol)

ε-right : (x : V₄) → (x · e) ≡ x
ε-right = proj₂ ε-identity

------------------------------------------------------------------------
-- Centrality is UNIFORM over the sign label (the gauge-invariant verdict).
-- This is `central-χ`'s proof with the sign abstracted: `odd` is never used,
-- so the centrality of the ℤ₂ factor does not depend on which label is which.
------------------------------------------------------------------------

central-sign : (s : Chir) (g : A4Z2) → compose (mk s e z0) g ≡ compose g (mk s e z0)
central-sign s g =
  a4z2-≡ (*c-comm s (chir g))
         (trans (ε-left (mask g))
                (trans (sym (ε-right (mask g)))
                       (cong (mask g ·_) (sym (σ-fixes-e (zee g))))))
         (sym (+₃-idʳ (zee g)))

-- ΞB2i's central-χ is the s = odd instance — so the original verdict is just
-- one gauge representative of the uniform fact.
central-χ-is-an-instance : (g : A4Z2) → compose (mk odd e z0) g ≡ compose g (mk odd e z0)
central-χ-is-an-instance = central-sign odd

-- and it agrees with the committed central-χ (mk odd e z0 = χ).
central-χ-agrees : (g : A4Z2) → compose (mk odd e z0) g ≡ compose g (mk odd e z0)
central-χ-agrees = central-χ

------------------------------------------------------------------------
-- ΞG: centrality SURVIVES the even↔odd flip — the verdict in the flipped
-- sign convention holds, for every g. (The gauge transformation oflip is an
-- involution: oflip-invol — gauge moves are invertible. Centrality is FIXED
-- under it: central at s ⟹ central at oflip s, both inhabited ∀ s.)
------------------------------------------------------------------------

-- the gauge transformation is an involution (gauge moves are invertible).
gauge-involution : (s : Chir) → oflip (oflip s) ≡ s
gauge-involution = oflip-invol

gauge-flip-invariant : (s : Chir) (g : A4Z2) →
                       compose (mk (oflip s) e z0) g ≡ compose g (mk (oflip s) e z0)
gauge-flip-invariant s g = central-sign (oflip s) g

-- equivariance: the verdict transports across the gauge flip in BOTH directions
-- (oflip is an involution), so it is not an artifact of the fixed even/odd choice.
gauge-equivariance : (s : Chir) (g : A4Z2) →
                     (compose (mk s e z0) g ≡ compose g (mk s e z0)) ×
                     (compose (mk (oflip s) e z0) g ≡ compose g (mk (oflip s) e z0))
gauge-equivariance s g = central-sign s g , central-sign (oflip s) g
