------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedNode
--
-- THE SELF-BALANCING SPPF CELL. A packed node holds entries up to the ARTIN
-- BOUND — any two entries span an associative/flat subalgebra, so a node seats
-- at most two; the third forces a quote. That bound is IN THE TYPE (empty /
-- one / full), so capacity is structural, not a runtime counter.
--
-- `pack` routes an arriving entry in ONE PASS, and the same decision both
-- balances and detects fullness (the user's observation: the self-balancer
-- acts on the packed node and concurrently identifies when it is full):
--
--   * dependent (the detector reads 𝟘 — same direction) → `shared`: absorbed,
--     node unchanged. This is the in-grade balancing.
--   * new flat direction (detector 𝟙) with room → `packed`: seated.
--   * new flat direction AT capacity → `split`: the node is FULL; the overflow
--     is promoted up a grade (the orthogonal move = quote = grade-lift =
--     Cayley–Dickson doubling = reintern). The node is KEPT and the overflow
--     is RETAINED in the result — nothing discarded (never-annihilate).
--
-- The routing is `_≟A_` (the alphabet's decidable equality), which is exactly
-- what the A2 detector grade is built from (AxisWord.Detector): so the one
-- comparison that seats/shares an entry is the same one that, at capacity,
-- fires the split. Balancing and fullness-detection are literally one reading.
-- `pack-full-distinct` / `pack-full-shared` certify the tie to `detect`:
-- `split` fires exactly when the entry is detector-𝟙 against both seats (a
-- genuine new distinction, hence promoted not annihilated); `shared` exactly
-- when it is detector-𝟘.
--
-- The promote step itself (reinterning the split overflow into a grade-(n+1)
-- node = building the tree) is the next brick; here we found the cell and its
-- routing. See scratch/dent_system_primer.md §4/§5; the overflow is the kept
-- residue.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedNode where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; _≟_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.Wedge.AxisWord.Detector using (module Detector)

module PackedNode {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open Detector _≟A_   -- detect, detect-refl, detect-distinct (the A2 sensor)

  ------------------------------------------------------------------------
  -- 1. The node: capacity 2 BY CONSTRUCTION (the Artin bound). `full` carries
  --    the distinctness of its two seats — the two flat directions are real.
  ------------------------------------------------------------------------

  data Node : Set where
    empty : Node
    one   : A → Node
    full  : (a b : A) → ¬ (a ≡ b) → Node

  -- the routing outcome — one constructor per role of the detector reading.
  data PackOutcome : Set where
    shared : Node → PackOutcome       -- detector 𝟘: dependent, absorbed
    packed : Node → PackOutcome       -- detector 𝟙: seated in a free slot
    split  : Node → A → PackOutcome   -- FULL: node kept, overflow promoted

  ------------------------------------------------------------------------
  -- 2. pack — one pass: the same `_≟A_` that shares a dependent also, at
  --    capacity, fires the split. Balance and fullness, concurrently.
  ------------------------------------------------------------------------

  pack : A → Node → PackOutcome
  pack x empty = packed (one x)
  pack x (one a) with x ≟A a
  ... | yes _  = shared (one a)
  ... | no ¬p = packed (full a x (λ eq → ¬p (sym eq)))
  pack x (full a b d) with x ≟A a | x ≟A b
  ... | yes _ | _     = shared (full a b d)
  ... | no _  | yes _ = shared (full a b d)
  ... | no _  | no _  = split (full a b d) x

  ------------------------------------------------------------------------
  -- 3. The routing IS the detector grade (A2). detect reads 𝟘 on equals…
  ------------------------------------------------------------------------

  detect-eq-𝟘 : {x a : A} → x ≡ a → detect x a ≡ 𝟘
  detect-eq-𝟘 {x} {a} p = trans (cong (λ z → detect z a) p) (detect-refl a)

  -- SPLIT fires exactly on a genuine new distinction at capacity: the overflow
  -- is detector-𝟙 against BOTH seats, so it is a real new direction — promoted
  -- up a grade, never annihilated. (The node is kept; the overflow is retained.)
  pack-full-distinct : (x a b : A) (d : ¬ (a ≡ b)) →
                       ¬ (x ≡ a) → ¬ (x ≡ b) →
                       (pack x (full a b d) ≡ split (full a b d) x)
                       × (detect x a ≡ 𝟙) × (detect x b ≡ 𝟙)
  pack-full-distinct x a b d xa xb =
    eq , detect-distinct {x} {a} xa , detect-distinct {x} {b} xb
    where
      eq : pack x (full a b d) ≡ split (full a b d) x
      eq with x ≟A a | x ≟A b
      ... | yes p | _     = ⊥-elim (xa p)
      ... | no _  | yes q = ⊥-elim (xb q)
      ... | no _  | no _  = refl

  -- SHARED fires on a dependent entry: detector 𝟘, node unchanged (balanced).
  pack-full-shared : (x a b : A) (d : ¬ (a ≡ b)) → x ≡ a →
                     (pack x (full a b d) ≡ shared (full a b d))
                     × (detect x a ≡ 𝟘)
  pack-full-shared x a b d p = eq , detect-eq-𝟘 p
    where
      eq : pack x (full a b d) ≡ shared (full a b d)
      eq with x ≟A a | x ≟A b
      ... | yes _ | _ = refl
      ... | no ¬p | _ = ⊥-elim (¬p p)

------------------------------------------------------------------------
-- 4. Instantiated at the bare axis alphabet (Fin k), as AxisWord uses.
------------------------------------------------------------------------

module PNFin (k : ℕ) = PackedNode {Fin k} (λ a b → a ≟ b)
