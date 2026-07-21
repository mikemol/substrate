------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CanonicalRec
--
-- ⟡quotient-elim-apex — the CANONICAL-FORM QUOTIENT RECURSOR, and the
-- CO-APEX tie that makes it a witness of the pre-existing `QuotientUP`.
--
-- THIS IS A CO-APEX, NOT NEW CONTENT. The recursor SHAPE and its three laws
-- already exist, named, in `Category.UniversalProperty.Quotient`: `Respects`
-- and `QuotientUP` (whose `factor` / `factor-≡-f` / `factor-respects` /
-- `factor-unique` are record PARAMETERS). What was missing is the
-- `Canonical`-instantiated WITNESS — the only inhabitant on record is
-- `trivial-QuotientUP`, the IDENTITY factorisation (`factor = λ _ f _ → f`),
-- which discharges the UP without computing anything.
--
-- That file's own header PROMISES this witness IN PROSE:
--   "When a `Canonical Q` extension is in scope (Coxeter, ℚ, V4-Cosets, F₂),
--    factorisation IS computational: f̃ a = f (canonical a)."
-- and notes that its `factor-unique` is "uniqueness GIVEN agreement, not the
-- representative-level uniqueness of a quotient; the latter needs the
-- canonical-form layer." This module IS that canonical-form layer: it turns
-- the prose pointer into a checkable term.
--
-- ⚑ LAW → FIELD DISCHARGE (corrected against the record's ACTUAL parameters):
--   the map            `factor`          ← Canonical.canonical
--   computation        `factor-≡-f`      ← Canonical.≈-canonical          (+ sym)
--   respect            `factor-respects` ← Canonical.canonical-respects-≈  (+ cong)
--   uniqueness         `factor-unique`   ← Canonical.≈-canonical           (+ trans)
-- so THREE of `Canonical`'s four fields are load-bearing for the UP — NOT
-- four. `QuotientUP` has no stability parameter, and `factor-unique` needs
-- only `≈-canonical` in its given direction (no `≈-sym`). The fourth field,
-- `canonical-idempotent`, discharges the SEPARATE stability lemma below,
-- which is a genuine property of the recursor but NOT a QuotientUP field —
-- it is recorded as such rather than folded in.
--
-- HOME: sited in `Algebra/Quotient/` (sibling of `F2Parity`, the established
-- home for Quotient+Canonical instances) rather than appended to the
-- `Category` layer — that layer already imports `Algebra.Quotient`, so
-- appending there would invert the dependency. This module is a leaf
-- importing both; no cycle.
--
-- Every `Canonical` instance in the tree therefore now has a computational
-- quotient eliminator for free: Coxeter's `normalize`, `split-Canonical`'s
-- image (`UPTerm-Canonical`, `TmDB-Canonical`, `factor-Canonical`,
-- `wedge-Canonical`, `sign-Canonical`), `idem-Canonical`, ℕ/parity.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CanonicalRec where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Quotient
  using (Quotient; canonical; canonical-idempotent; canonical-respects-≈; ≈-canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)   -- shape-specialize the ambiguous name
open import Substrate.Category.UniversalProperty.Quotient
  using (Respects; QuotientUP)

module _ {A : Set} {_≈_ : A → A → Set} {Q : Quotient A _≈_}
         (C : Canonical⟦de760d07⟧ Q) where

  ------------------------------------------------------------------------
  -- 1. THE RECURSOR — eliminate out of the quotient by evaluating the
  --    representative. This is the promised `f̃ a = f (canonical a)`.
  ------------------------------------------------------------------------

  canonical-rec : (B : Set) (f : A → B) (f-resp : Respects _≈_ f) → A → B
  canonical-rec B f _ a = f (canonical C a)

  ------------------------------------------------------------------------
  -- 2. The three UP laws, each read off one `Canonical` field.
  ------------------------------------------------------------------------

  -- COMPUTATION: the recursor agrees with f everywhere (f respects _≈_, and
  -- a is ≈-related to its own canonical form).
  canonical-rec-β : (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
                    (a : A) → canonical-rec B f f-resp a ≡ f a
  canonical-rec-β B f f-resp a = sym (f-resp (≈-canonical C a))

  -- RESPECT: ≈-related inputs have EQUAL canonical forms, so the recursor is
  -- well-defined on classes — by `cong f`, with no hypothesis on f used.
  canonical-rec-respects : (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
                           Respects _≈_ (canonical-rec B f f-resp)
  canonical-rec-respects B f _ p = cong f (canonical-respects-≈ C p)

  -- UNIQUENESS (given agreement): any respecting g that agrees with f
  -- everywhere already agrees with the recursor — move g along a ≈ canonical a,
  -- then swap g for f at the representative.
  canonical-rec-unique :
    (B : Set) (f : A → B) (f-resp : Respects _≈_ f)
    (g : A → B) (g-resp : Respects _≈_ g) →
    ((a : A) → g a ≡ f a) →
    (a : A) → g a ≡ canonical-rec B f f-resp a
  canonical-rec-unique B f _ g g-resp g≡f a =
    trans (g-resp (≈-canonical C a)) (g≡f (canonical C a))

  ------------------------------------------------------------------------
  -- 3. THE CO-APEX TIE — the `Canonical`-instantiated witness of the
  --    pre-existing `QuotientUP`. This is the whole point of the module:
  --    the shape was already named; this inhabits it computationally.
  ------------------------------------------------------------------------

  canonical-QuotientUP :
    QuotientUP A _≈_ Q
      canonical-rec canonical-rec-β canonical-rec-respects canonical-rec-unique
  canonical-QuotientUP = record {}

  ------------------------------------------------------------------------
  -- 4. STABILITY — ⚑ NOT a `QuotientUP` field (the record has no stability
  --    parameter). Recorded separately because it is the property that
  --    `canonical-idempotent` exists to give: the recursor cannot be moved
  --    by re-normalizing its argument.
  ------------------------------------------------------------------------

  canonical-rec-stable : (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
                         (a : A) → canonical-rec B f f-resp (canonical C a)
                                   ≡ canonical-rec B f f-resp a
  canonical-rec-stable B f _ a = cong f (canonical-idempotent C a)
