{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.CertifiedPhiStep — ⟡certified-phi-step: the full certified
-- rewire. A Φ-step variant on CertifiedWedge (over ℕ-div) where ADD 165's ω-continuity
-- hypothesis wrem-uniq is BUILT IN — discharged via 166's cwrem-uniq (recon-bounded-
-- unique). So the abstract-limit-postfp holds UNCONDITIONALLY (no wrem-uniq parameter):
-- the certified wedge's smallness makes rem unique, so the descending-chain Limit is
-- a post-fixed-point outright, hence = νΦ-step-cert.
--
-- The either/or "generic Φ-step (needs wrem-uniq hypothesis, 165) vs certified Φ-step"
-- dissolves: the certified wedge INTERNALIZES smallness, so the hypothesis becomes a
-- THEOREM (cwrem-uniq). This is the same smallness the CONSTRUCTIVE ν (divide, 164)
-- builds in — recon-bounded-unique the shared certificate, now wired into the functor.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.CertifiedPhiStep where

open import Substrate.Foundation.Eq  using (_≡_; refl; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≟_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Wedge using (ℕ-div; rem)
open import Substrate.Category.Allegory.Refinement
  using (_⊑ᶠ_; ⊑ᶠ-trans; Refinement; iterate; chain)
open import Substrate.Algebra.Wedge.Certified using (CertifiedWedge; wedge; small; idℕ)
open import Substrate.Algebra.Wedge.NuAbstractLimitInstance using (cwrem-uniq)

-- the index (a, b, g) over ℕ-div.
Idxℕ : Set
Idxℕ = ℕ × ℕ × ℕ

-- a certified wedge over ℕ-div at (a, b).
CW : ℕ → ℕ → Set
CW a b = CertifiedWedge ℕ-div idℕ a b

------------------------------------------------------------------------
-- ① THE CERTIFIED PATTERN FUNCTOR: same shape as Φ-step (158), but the step uses a
-- CERTIFIED wedge (smallness bundled). done ⊎ (certified step).
------------------------------------------------------------------------
Φ-cert : (Idxℕ → Set) → Idxℕ → Set
Φ-cert P (a , b , g) =
    ((b ≡ zero) × (g ≡ a))
  ⊎ (Σ (CW a b) (λ cw → P (b , rem (wedge cw) , g)))

Φ-cert-mono : {P Q : Idxℕ → Set} → P ⊑ᶠ Q → Φ-cert P ⊑ᶠ Φ-cert Q
Φ-cert-mono P⊑Q (a , b , g) (inj₁ eqs)       = inj₁ eqs
Φ-cert-mono P⊑Q (a , b , g) (inj₂ (cw , p))  = inj₂ (cw , P⊑Q (b , rem (wedge cw) , g) p)

cert-refinement : Refinement Idxℕ Φ-cert Φ-cert-mono
cert-refinement = record {}

------------------------------------------------------------------------
-- ② THE DESCENDING CHAIN + LIMIT (re-derived for the certified refinement, generic
-- over Refinement — 162's construction at cert-refinement).
------------------------------------------------------------------------
⊤-cert : Idxℕ → Set
⊤-cert _ = ⊤

⊤-cert-pre : Φ-cert ⊤-cert ⊑ᶠ ⊤-cert
⊤-cert-pre _ _ = tt

descending-cert : (n : ℕ) → iterate cert-refinement (suc n) ⊤-cert ⊑ᶠ iterate cert-refinement n ⊤-cert
descending-cert = chain cert-refinement ⊤-cert-pre

Limit-cert : Idxℕ → Set
Limit-cert i = (n : ℕ) → iterate cert-refinement n ⊤-cert i

-- every coalgebra below the limit (162's universal property at cert-refinement).
below-stage : {X : Idxℕ → Set} → (X ⊑ᶠ Φ-cert X) → (n : ℕ) → X ⊑ᶠ iterate cert-refinement n ⊤-cert
below-stage co zero    i x = tt
below-stage co (suc m) = ⊑ᶠ-trans co (Φ-cert-mono (below-stage co m))

below-limit : {X : Idxℕ → Set} → (X ⊑ᶠ Φ-cert X) → X ⊑ᶠ Limit-cert
below-limit co i x n = below-stage co n i x

------------------------------------------------------------------------
-- ③ THE ABSTRACT LIMIT IS A POST-FIXED-POINT — UNCONDITIONALLY (no wrem-uniq
-- parameter). The certified wedge's rem is unique via cwrem-uniq (166), so the
-- per-stage step-wedges reconcile with NO hypothesis. This is 165's proof with the
-- hypothesis DISCHARGED by the certified structure.
------------------------------------------------------------------------
cert-limit-postfp : Limit-cert ⊑ᶠ Φ-cert Limit-cert
cert-limit-postfp (a , zero  , g) l with g ≟ a
... | yes g≡a = inj₁ (refl , g≡a)
... | no ¬g≡a = extract (l 1)         -- b=0: the step (certified wedge a→0) is empty
  where
    extract : Φ-cert (iterate cert-refinement 0 ⊤-cert) (a , zero , g) → Φ-cert Limit-cert (a , zero , g)
    extract (inj₁ (_ , g≡a)) = ⊥-elim (¬g≡a g≡a)
    extract (inj₂ (cw , _))  = ⊥-elim (absurd (small cw))   -- small : rem < 0, impossible
      where absurd : {r : ℕ} → suc r ≤ zero → ⊥
            absurd ()
cert-limit-postfp (a , suc b , g) l = inj₂ (cw₁ , residual)
  where
    -- b = suc b': ¬done, every stage-witness is a certified step (inj₁ needs b≡0).
    step-at : (m : ℕ) → Σ (CW a (suc b)) (λ cw → iterate cert-refinement m ⊤-cert (suc b , rem (wedge cw) , g))
    step-at m with l (suc m)
    ... | inj₁ (() , _)
    ... | inj₂ (cw , y) = cw , y
    cw₁ : CW a (suc b)
    cw₁ = proj₁ (step-at zero)
    -- reconcile per-stage certified wedges via cwrem-uniq (166) — NO hypothesis.
    residual : Limit-cert (suc b , rem (wedge cw₁) , g)
    residual m =
      subst (λ r → iterate cert-refinement m ⊤-cert (suc b , r , g))
            (cwrem-uniq (proj₁ (step-at m)) cw₁)
            (proj₂ (step-at m))

-- HENCE Limit-cert = νΦ-cert: a post-fixed-point (above) + above every coalgebra
-- (below-limit) = the greatest fixed point — UNCONDITIONALLY.
cert-limit-greatest : {X : Idxℕ → Set} → (X ⊑ᶠ Φ-cert X) → X ⊑ᶠ Limit-cert
cert-limit-greatest = below-limit

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the certified rewire, hypothesis DISCHARGED): the
-- certified Φ-step (Φ-cert, using CertifiedWedge) makes ADD 165's ω-continuity
-- hypothesis wrem-uniq a THEOREM (cwrem-uniq, 166, via recon-bounded-unique) — so the
-- abstract descending-chain Limit-cert IS a post-fixed-point UNCONDITIONALLY (cert-
-- limit-postfp, no parameter), hence the GREATEST fixed point = νΦ-cert. The either/or
-- "generic Φ-step needs the wrem-uniq hypothesis (165) vs the constructive ν needs
-- none (164)" dissolves: the CERTIFIED Φ-step INTERNALIZES smallness (the certified
-- wedge bundles rem < b), so rem is unique (recon-bounded-unique) and the hypothesis
-- is discharged — the SAME smallness the constructive ν (divide) builds in. The b=0
-- case is handled by the certified step being EMPTY (rem < 0 impossible), matching
-- done; the b=suc case reconciles per-stage wedges via cwrem-uniq. So 165's conditional
-- theorem becomes UNCONDITIONAL on the certified functor: recon-bounded-unique is the
-- shared smallness certificate, now wired into the pattern functor itself.
------------------------------------------------------------------------
