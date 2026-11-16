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
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.MLo
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod.Core as ModCore

open ModCore.Over F₂-CommRing 7 m-lo using (ytime)
-- ⚑ Ⓑ6ᶜ: WAS `using (_+P_; _·c_) renaming (_+F_ to _+r_; _*_ to _·r_)`, and that
-- `renaming` was MECHANICALLY MANGLED, not merely stripped. Archaeology
-- (`git show 771283c8^`) shows the original:
--
--     open F.Over F₂-CommRing using (_+P_; _·c_) renaming (_+_ to _+r_; _*_ to _·r_)
--
-- The sweep's blind `+` → `+F` substitution rewrote the rename's SOURCE, so it
-- named `_+F_` — a name `Over` does not export. A `renaming` whose source does not
-- exist binds NOTHING and is only a WARNING at the import, so `+r` dangled until
-- the use site at :38. That is the prose-corruption class (Ⓕ-PROSE-DECORRUPT)
-- landing in live code rather than in a comment.
--
-- ⚑ AND THE COLLISION THE RENAME EXISTED FOR IS GONE. `_+r_` distinguished the
-- ring-projected addition from F₂'s own `_+_`; the sweep renamed F₂'s at source to
-- `_+F_`, so `Over`'s `_+_` no longer collides and needs no alias. The directive
-- is dropped rather than repaired — which is what the ban wants anyway.
--
-- ⚑ AND DROPPING THE FILTER ENTIRELY OVER-WIDENED, WHICH IS ITS OWN FINDING.
-- A bare `open F.Over` brings in `Over.𝟘`, colliding with `F2.F2`'s CONSTRUCTOR
-- `𝟘` — `[AmbiguousName]` at :86, the exact ⟡AMBIG35 shape, and the reason the
-- original reached for a `using` filter in the first place. Removing a banned
-- directive is not the same as removing the collision it was masking.
--
-- ⚑ THE Ⓐ1 SPLIT IS WHAT MAKES THE BAN-COMPLIANT FIX POSSIBLE. `FromCommRing.Over`
-- is now 22 one-definition leaves, so this file takes the operators it needs BY
-- NAME instead of a bundle it must filter. That is the operator's ruling realised:
-- once bare imports carry individual symbols, the filter becomes UNNECESSARY
-- rather than merely forbidden.
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus F₂-CommRing
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Times F₂-CommRing
-- `_+P_` / `_·c_` — the graded vector ops, used by `+P≡+ⱽ` and `·c≡*ₛ` below.
-- Still reached through `F.Over`, which supplies the coefficient arguments
-- `Graded.Defs.Over` needs; only the two colliding OPERATORS moved to leaves.
open F.Over F₂-CommRing using (_+P_; _·c_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans

------------------------------------------------------------------------
-- The element bridge: the field's CommutativeRing-projected ops are F₂'s.

-- ⚑ Ⓑ6ᶜ: `+r` → `_+_` (the ring-projected addition, now unaliased); `+F` stays
-- F₂'s own. The theorem is unchanged — it is exactly the claim the module header
-- makes, that the two agree — but both sides now spell the operator they mean.
+e : (a b : F₂) → (a + b) ≡ (a +F b)
+e 𝟘 𝟘 = refl
+e 𝟘 𝟙 = refl
+e 𝟙 𝟘 = refl
+e 𝟙 𝟙 = refl

-- ⚑ Ⓑ6ᶜ: `·r` → `_*_`. Unlike the addition pair, F₂'s multiplication kept its
-- spelling (`F2.Op` exports `_·_`), so the two sides are `*` and `·` — genuinely
-- different operators, which is what makes this a theorem rather than a tautology.
·e : (a b : F₂) → (a * b) ≡ (a · b)
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
