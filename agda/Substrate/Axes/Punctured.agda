------------------------------------------------------------------------
-- Substrate.Axes.Punctured
--
-- The `Axis`-layer instance of the punctured-finite-set bijection
-- (Substrate.Foundation.Fin.Punctured), made explicit at the carrier
-- both `Substrate.Cardinality` and `Substrate.Groups.Stab-S3` sit above.
--
-- This module materialises one structural fact that was previously
-- duplicated and/or hidden behind hand-enumerations:
--
--   * `axis-↔-fin4` : the canonical Axis ≅ Fin 4 enumeration.  Was a
--     private copy inside Cardinality; now the single source of truth
--     (Cardinality imports it from here — no backward edge, since
--     Cardinality already imports Axes, and Bijection is foundation-only).
--
--   * The anchor-skipping bridge `Axis ↔ (Fin 3 ∖ nothing)` IS the
--     punctured-Fin bijection transported along `axis-↔-fin4`:
--       axis-punchIn  anchor = from ∘ punchIn (to anchor)
--       axis-punchOut anchor = punchOut  (with to-injectivity transport)
--     Stab-S3's `fin3-to-non-anchor` / `non-anchor-to-fin3` are thin
--     aliases of these; their round-trips are now PROVED via the
--     primitive's `punchOut-punchIn` / `punchIn-punchOut`, not by an
--     evaluation-coincidence refl-tuple.
--
-- --safe --without-K; zero postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Punctured where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Fin.Punctured
  using (punchIn; punchIn-≢; punchOut; punchOut-irrelevant; punchOut-cong;
         punchOut-punchIn; punchIn-punchOut)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′)
open import Substrate.Axes using (Axis; D; C; S; W; axis-cover)

------------------------------------------------------------------------
-- 1. The canonical Axis ≅ Fin 4 enumeration (single source of truth).
------------------------------------------------------------------------

a→f : Axis → Fin 4
a→f D = zero
a→f C = suc zero
a→f S = suc (suc zero)
a→f W = suc (suc (suc zero))

f→a : Fin 4 → Axis
f→a zero                         = D
f→a (suc zero)                   = C
f→a (suc (suc zero))             = S
f→a (suc (suc (suc zero)))       = W

f→a→f : (i : Fin 4) → a→f (f→a i) ≡ i
f→a→f = fin-cover _ (refl , refl , refl , refl)

a→f→a : (x : Axis) → f→a (a→f x) ≡ x
a→f→a = axis-cover _ (refl , refl , refl , refl)

axis-↔-fin4 : Axis ↔ Fin 4
axis-↔-fin4 = mk↔ₛ′ a→f f→a f→a→f a→f→a

-- to-injectivity + its ≢-transport (the only structure punchOut needs).
a→f-inj : {x y : Axis} → a→f x ≡ a→f y → x ≡ y
a→f-inj {x} {y} eq = trans (sym (a→f→a x)) (trans (cong f→a eq) (a→f→a y))

a→f-≢ : {anchor x : Axis} → ¬ (x ≡ anchor) → ¬ (a→f x ≡ a→f anchor)
a→f-≢ x≢a eq = x≢a (a→f-inj eq)

------------------------------------------------------------------------
-- 2. The anchor-skipping bridge = punctured-Fin transported along ≅.
------------------------------------------------------------------------

axis-punchIn : Axis → Fin 3 → Axis
axis-punchIn anchor i = f→a (punchIn (a→f anchor) i)

axis-punchIn-≢ : (anchor : Axis) (i : Fin 3) → ¬ (axis-punchIn anchor i ≡ anchor)
axis-punchIn-≢ anchor i eq =
  punchIn-≢ (a→f anchor) i
    (trans (sym (f→a→f (punchIn (a→f anchor) i))) (cong a→f eq))

axis-punchOut : (anchor x : Axis) → ¬ (x ≡ anchor) → Fin 3
axis-punchOut anchor x x≢a = punchOut {k = a→f anchor} {i = a→f x} (a→f-≢ x≢a)

-- proof-irrelevance (subsumes Stab-S3-Restrict's non-anchor-to-fin3-irr).
axis-punchOut-irrelevant :
  (anchor x : Axis) (p q : ¬ (x ≡ anchor)) →
  axis-punchOut anchor x p ≡ axis-punchOut anchor x q
axis-punchOut-irrelevant anchor x p q =
  punchOut-irrelevant (a→f-≢ p) (a→f-≢ q)

------------------------------------------------------------------------
-- 3. Round-trips, PROVED via the primitive (not by refl-coincidence).
------------------------------------------------------------------------

axis-punchOut-punchIn :
  (anchor : Axis) (i : Fin 3) →
  axis-punchOut anchor (axis-punchIn anchor i) (axis-punchIn-≢ anchor i) ≡ i
axis-punchOut-punchIn anchor i =
  trans (punchOut-cong (f→a→f (punchIn (a→f anchor) i))
                       (a→f-≢ (axis-punchIn-≢ anchor i))
                       (punchIn-≢ (a→f anchor) i))
        (punchOut-punchIn (a→f anchor) i)

axis-punchIn-punchOut :
  (anchor x : Axis) (x≢a : ¬ (x ≡ anchor)) →
  axis-punchIn anchor (axis-punchOut anchor x x≢a) ≡ x
axis-punchIn-punchOut anchor x x≢a =
  trans (cong f→a (punchIn-punchOut {k = a→f anchor} {i = a→f x} (a→f-≢ x≢a)))
        (a→f→a x)
