------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ParityBridge
--
-- THE WEDGE CONSTRUCTS A BRIDGE. The first actual cross-root edge of the
-- foundational sphere: `ℕ-div ↠ F₂-div`, the parity (mod-2) reduction, as a
-- `Bridge`. Founding both roots on the wedge basis (ℕ-div in Wedge.agda,
-- F₂-div in F2.Wedge) is exactly what makes this edge wedge-EXPRESSIBLE: a
-- `Bridge` is a carrier translation that RESPECTS `recon`, and parity does
-- (it is the ℕ → F₂ ring homomorphism). So this is the literal answer to
-- "the wedge constructs bridges, it doesn't bolt them on" — the edge the
-- rank-4 shred found missing, now present and structure-respecting.
--
-- And because a Bridge transports the whole Euclidean apparatus
-- (Bridge.transport-trace), `parity-bridge` carries gcd / Bézout / mod from
-- ℕ onto F₂: the number theory of one root flows along the edge to the other.
-- That is the sphere becoming a LIVING surface — not just coherent (pentagon
-- + triangle) but with content flowing along its geodesics.
--
-- The proof is the standard fact that parity is a ring hom, assembled from
-- two lemmas: parity-+ (additive: parity (x+y) = parity x +₂ parity y) and
-- parity-scale (the quotient's Peano scale: parity (q·b) = scale q (parity b)).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ParityBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; sym)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; +-assoc; ·-distribʳ-+; ·-identityˡ)
  renaming (_+_ to _+₂_; _·_ to _·₂_)
open import Substrate.Algebra.F2.Wedge using (F₂-div)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)

------------------------------------------------------------------------
-- 1. Parity: the mod-2 reduction ℕ → F₂.
------------------------------------------------------------------------

parity : ℕ → F₂
parity zero    = 𝟘
parity (suc n) = 𝟙 +₂ parity n

------------------------------------------------------------------------
-- 2. Parity is a ring hom: additive (parity-+) AND multiplicative (parity-*).
--    parity-* replaces the old parity-scale now that F₂-div's recon uses F₂'s
--    own multiplication (q·b), not the Peano count `scale q b`.
------------------------------------------------------------------------

parity-+ : (x y : ℕ) → parity (x + y) ≡ parity x +₂ parity y
parity-+ zero    y = refl
parity-+ (suc n) y =
  trans (cong (𝟙 +₂_) (parity-+ n y))
        (sym (+-assoc 𝟙 (parity n) (parity y)))

-- parity is multiplicative: parity (x·y) = parity x ·₂ parity y (the ℕ→F₂ ring
-- hom's multiplicative leg). suc-case = distribute, then 𝟙·=id.
parity-* : (x y : ℕ) → parity (x * y) ≡ parity x ·₂ parity y
parity-* zero    y = refl
parity-* (suc n) y =
  trans (parity-+ y (n * y))
  (trans (cong (parity y +₂_) (parity-* n y))
         (sym (trans (·-distribʳ-+ (parity y) 𝟙 (parity n))
                     (cong (_+₂ (parity n ·₂ parity y)) (·-identityˡ (parity y))))))

------------------------------------------------------------------------
-- 3. The bridge: parity respects recon, so it carries the wedge structure.
--    recon ℕ-div q b r = q·b + r ;  recon F₂-div q b r = (parity q)·(parity b) +₂ r.
------------------------------------------------------------------------

parity-bridge : Bridge ℕ-div F₂-div
parity-bridge = record
  { translate = parity
  ; respects  = λ q b r →
      trans (parity-+ (q * b) r) (cong (_+₂ parity r) (parity-* q b))
  ; z-pres    = refl
  }

------------------------------------------------------------------------
-- 4. The payoff: the bridge transports the whole Euclidean apparatus
--    (hence gcd / Bézout / mod) from ℕ onto F₂ — content flowing along the
--    geodesic, the sphere made living.
------------------------------------------------------------------------

parity-transport-trace : {a b g : ℕ} →
  Trace ℕ-div a b g → Trace F₂-div (parity a) (parity b) (parity g)
parity-transport-trace = transport-trace parity-bridge
