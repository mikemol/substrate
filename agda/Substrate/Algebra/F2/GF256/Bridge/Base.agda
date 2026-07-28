{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Bridge.Base
--
-- ⟡cap128-bridge-split: the SHARED KERNEL of the field/GF256 seam, split off so
-- the three ★ transports (`reduce-eq`, `*P-eq`, `hsum-bridge`) elaborate in a
-- separate unit.  An elaboration peak is per-MODULE; this half carries the
-- element bridge (`ring-+ ≡ +` / `ring-* ≡ ·`, 4-way case-split), its lifts
-- through `+P`/`·c`, the one irreducible `ytime ≡ xtime` obligation, and the
-- generic `gfold`/`gfold-cong` schema both fold-shapes instantiate.
--
-- ⟡public-policy: binds `Mod`'s parts (Core / Expand) DIRECTLY — `ytime` lives
-- in Core — rather than siphoning them through the `Mod` tip.
------------------------------------------------------------------------
module Substrate.Algebra.F2.GF256.Bridge.Base where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base using (m-lo)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod.Core as ModCore

open ModCore.Over F₂-CommRing 7 m-lo using (ytime)
open F.Over F₂-CommRing using (_+P_; _·c_) renaming (_+_ to _+r_; _*_ to _·r_)

------------------------------------------------------------------------
-- The element bridge: the field's CommutativeRing-projected ops are F₂'s.

+e : (a b : F₂) → (a +r b) ≡ (a + b)
+e 𝟘 𝟘 = refl
+e 𝟘 𝟙 = refl
+e 𝟙 𝟘 = refl
+e 𝟙 𝟙 = refl

·e : (a b : F₂) → (a ·r b) ≡ (a · b)
·e 𝟘 𝟘 = refl
·e 𝟘 𝟙 = refl
·e 𝟙 𝟘 = refl
·e 𝟙 𝟙 = refl

-- lifted to vectors (the graded +P / ·c are the vector +ⱽ / *ₛ).
+P≡+ⱽ : ∀ {n} (u v : Vec F₂ n) → u +P v ≡ u +ⱽ v
+P≡+ⱽ []      []      = refl
+P≡+ⱽ (a ∷ u) (b ∷ v) = cong₂ _∷_ (+e a b) (+P≡+ⱽ u v)

·c≡*ₛ : ∀ {n} (c : F₂) (v : Vec F₂ n) → c ·c v ≡ c *ₛ v
·c≡*ₛ c []      = refl
·c≡*ₛ c (a ∷ v) = cong₂ _∷_ (·e c a) (·c≡*ₛ c v)

------------------------------------------------------------------------
-- The one irreducible obligation: the ·x kernels agree on a byte.

ytime-is-xtime : (r : Vector 8) → ytime r ≡ xtime r
ytime-is-xtime (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
  trans (+P≡+ⱽ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ []) (b7 ·c m-lo))
        (cong (_+ⱽ_ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ [])) (·c≡*ₛ b7 m-lo))

------------------------------------------------------------------------
-- ⋈-CONG.  The generic Vec F₂ fold and its congruence — proved once, for an
-- ARBITRARY result type R and an ARBITRARY relation _≈_ on it.  `fold` (reduce)
-- and `thread` (hsum) below are the SAME `gfold`, into C and into C→C; their
-- congruences are this ONE `gfold-cong`, instantiated at _≡_ and at pointwise-≡.
-- This is the schema ⋈-STRUCT generalizes: a graded↔F₂ transport IS a `gfold-cong`
-- fed the element bridge.  (The Fin-indexed `sum-cong` in Idempotent is the same
-- idea over a different functor — a container-fold would absorb it too; → STRUCT.)

gfold : {R : Set} (e : R) (c : F₂ → R → R) → ∀ {n} → Vec F₂ n → R
gfold e c []      = e
gfold e c (a ∷ q) = c a (gfold e c q)

gfold-cong : {R : Set} (_≈_ : R → R → Set) {e₁ e₂ : R} {c₁ c₂ : F₂ → R → R}
           → e₁ ≈ e₂ → (∀ a {r₁ r₂} → r₁ ≈ r₂ → c₁ a r₁ ≈ c₂ a r₂)
           → ∀ {n} (v : Vec F₂ n) → gfold e₁ c₁ v ≈ gfold e₂ c₂ v
gfold-cong _≈_ ee ec []      = ee
gfold-cong _≈_ ee ec (a ∷ q) = ec a (gfold-cong _≈_ ee ec q)
