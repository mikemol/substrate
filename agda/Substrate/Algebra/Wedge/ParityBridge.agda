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

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.IdentityL
-- ⚑ THE OPERATORS THEMSELVES WERE NEVER BOUND (Ⓕ-ALIAS-RESTORE).  This file
-- reached F₂'s `_·_`/`_+F_` through `open import Substrate.Algebra.F2 …
-- renaming (_+_ to _+₂_; _·_ to _·₂_)` — a barrel alias introduced in 97e567f2.
-- The barrel was decomposed into per-lemma siblings and the ban paydown replaced
-- that line with the plain sibling opens above, DROPPING the renaming without
-- rewriting the eight use sites; `·₂`/`+₂` then named nothing anywhere in the
-- tree.  The laws already imported here (`·-distribʳ-+`, `·-identityˡ`) are
-- stated in `·`/`+F`, so those are the spellings, and `F₂-div`'s own
-- `recon = λ q b r → q · b +F r` (F2/Wedge.agda:52) fixes them as the only ones
-- that discharge the `respects` obligation below.
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.Wedge using (F₂-div)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)
-- ⚑ `public` RETIRED (Ⓑ2c).  The removed trailing comment read *"⟡A2: single
-- source, re-exported (IntParityBridge/Registry consume parity via this
-- bridge)"* — it named the two consumers the forward existed for, and both now
-- bind `N-to-F2-Parity` themselves.  "Single source" is preserved by the HOME,
-- not by a second route to it; the re-export was the second route.
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym

------------------------------------------------------------------------
-- 1. Parity: the mod-2 reduction ℕ → F₂.
------------------------------------------------------------------------

-- parity / parity-+ are imported from N-to-F2-Parity (single source, ⟡A2) — the mod-2 map lives
-- ONCE there; this module keeps only the bridge-specific parity-* / parity-bridge / transport.

------------------------------------------------------------------------
-- 2. Parity is a ring hom: additive (parity-+) AND multiplicative (parity-*).
--    parity-* replaces the old parity-scale now that F₂-div's recon uses F₂'s
--    own multiplication (q·b), not the Peano count `scale q b`.
------------------------------------------------------------------------

-- (parity-+ : the additive ring-hom leg is imported from N-to-F2-Parity — ⟡A2)

-- parity is multiplicative: parity (x·y) = parity x · parity y (the ℕ→F₂ ring
-- hom's multiplicative leg). suc-case = distribute, then 𝟙·=id.
parity-* : (x y : ℕ) → parity (x * y) ≡ parity x · parity y
parity-* zero    y = refl
parity-* (suc n) y =
  trans (parity-+ y (n * y))
  (trans (cong (parity y +F_) (parity-* n y))
         (sym (trans (·-distribʳ-+ (parity y) 𝟙 (parity n))
                     (cong (_+F (parity n · parity y)) (·-identityˡ (parity y))))))

------------------------------------------------------------------------
-- 3. The bridge: parity respects recon, so it carries the wedge structure.
--    recon ℕ-div q b r = q·b + r ;  recon F₂-div q b r = (parity q)·(parity b) +F r.
------------------------------------------------------------------------

parity-bridge : Bridge ℕ-div F₂-div
parity-bridge = record
  { translate = parity
  ; respects  = λ q b r →
      trans (parity-+ (q * b) r) (cong (_+F parity r) (parity-* q b))
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
