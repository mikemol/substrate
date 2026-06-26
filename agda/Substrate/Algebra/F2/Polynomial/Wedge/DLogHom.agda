------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DLogHom
--
-- The GENERAL discrete-log homomorphism and inverse law, STRUCTURALLY (no
-- per-element `*Q` reflection) — so it scales to GF(2⁸) and stays low-memory.
--
-- The antilog is `gpow n = xpow n oneC = ytimeⁿ oneC` (multiply-by-x, bounded
-- magnitude — the division regime that doesn't OOM). The homomorphism
-- `g^(a+b) ≡ gᵃ · gᵇ` is then proven from the substrate's existing reduce-laws,
-- NOT by computing field products: the key step is that `ytime` (multiply-by-x)
-- COMMUTES with `*Q` —
--     p *Q ytime r ≡ ytime (p *Q r)
-- because both sides reduce to `hsum p (ytime r)` (via `reduce-*P-expand`, the
-- `reduce`/`*P`/`hsum` bridge; `reduce-idempotent`; and `hsum-ytime`).
--
-- With the homomorphism, the dlog inverse is general: `gᵏ · gʲ ≡ 1` whenever
-- `k+j = order`, parametric on the single field fact `g^order ≡ 1` — which is a
-- cheap `refl` in the division regime (`order15` below; GF(2⁸)'s `order255`
-- likewise). This is the scalable form of `GF16DLog`'s per-element witness, and
-- the resolution of the `g^order` wall the user diagnosed (change regime; the
-- log/exp codec licenses computing the order fact in the cheap chart).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DLogHom where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as D

module Over (d : ℕ) (m-lo : Vec F2.F₂ (suc d)) where
  open D.Over F₂-CommRing d m-lo using
    ( Poly ; _*Q_ ; oneC ; xpow ; ytime
    ; reduce-*P-expand ; reduce-idempotent ; hsum ; hsum-ytime ; xpow-ytime
    ; *Q-comm ; *Q-identityˡ )

  -- the antilog in the bounded-magnitude (division) regime.
  gpow : ℕ → Poly (suc d)
  gpow n = xpow n oneC

  -- ytime commutes through *Q on the right (both sides ≡ hsum p (ytime r)).
  ytime-*Q : (p r : Poly (suc d)) → (p *Q ytime r) ≡ ytime (p *Q r)
  ytime-*Q p r =
    trans (trans (reduce-*P-expand p (ytime r))
                 (cong (hsum p) (reduce-idempotent (ytime r))))
          (sym (trans (cong ytime (trans (reduce-*P-expand p r)
                                         (cong (hsum p) (reduce-idempotent r))))
                      (hsum-ytime p r)))

  -- ...and on the left, by commutativity.
  ytime-*Qˡ : (p r : Poly (suc d)) → ytime (p *Q r) ≡ (ytime p *Q r)
  ytime-*Qˡ p r =
    trans (cong ytime (*Q-comm p r))
          (trans (sym (ytime-*Q r p)) (*Q-comm r (ytime p)))

  -- multiplying by x^a is *Q by gpow a:  xpow a r ≡ (xpow a oneC) *Q r.
  xpow-*Q : (a : ℕ) (r : Poly (suc d)) → xpow a r ≡ (xpow a oneC *Q r)
  xpow-*Q zero    r = sym (*Q-identityˡ r)
  xpow-*Q (suc a) r =
    trans (xpow-*Q a (ytime r))
    (trans (ytime-*Q (xpow a oneC) r)
    (trans (ytime-*Qˡ (xpow a oneC) r)
           (sym (cong (_*Q r) (xpow-ytime a oneC)))))

  -- exponent-additivity of the antilog iterator.
  xpow-add : (a b : ℕ) (r : Poly (suc d)) → xpow (a + b) r ≡ xpow a (xpow b r)
  xpow-add zero    b r = refl
  xpow-add (suc a) b r =
    trans (xpow-add a b (ytime r)) (cong (xpow a) (xpow-ytime b r))

  -- THE HOMOMORPHISM: g^(a+b) ≡ gᵃ · gᵇ — structural, no field-mult reflection.
  gpow-hom : (a b : ℕ) → gpow (a + b) ≡ (gpow a *Q gpow b)
  gpow-hom a b = trans (xpow-add a b oneC) (xpow-*Q a (gpow b))

  -- THE GENERAL DISCRETE-LOG INVERSE: gᵏ · gʲ ≡ 1 whenever k+j = order.
  dlog-inv-law : (ord : ℕ) → gpow ord ≡ oneC →
                 (k j : ℕ) → k + j ≡ ord → (gpow k *Q gpow j) ≡ oneC
  dlog-inv-law ord g k j kj = trans (sym (gpow-hom k j)) (trans (cong gpow kj) g)

------------------------------------------------------------------------
-- GF(2⁴) instance: order 15. The anchor is the one reflection — cheap in the
-- division regime — and discharges the general law for ALL elements at once.
------------------------------------------------------------------------

m-lo₄ : Vec F2.F₂ 4
m-lo₄ = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

module GF16 = Over 3 m-lo₄
open D.Over F₂-CommRing 3 m-lo₄ using (_*Q_; oneC)

order15 : GF16.gpow 15 ≡ oneC
order15 = refl

-- the GENERAL GF(2⁴) dlog inverse law — covers every nonzero element, no
-- per-element reflections: gᵏ · g^(15−k) ≡ 1 for all k+j=15.
dlog-inv₄ : (k j : ℕ) → k + j ≡ 15 → (GF16.gpow k *Q GF16.gpow j) ≡ oneC
dlog-inv₄ = GF16.dlog-inv-law 15 order15
