------------------------------------------------------------------------
-- Substrate.Category.Allegory.Power  (ALG-8 — the topos capstone)
--
-- Closes the allegory→topos loop: the MAP sub-category of the relation
-- allegory (ALG-5) is the category of types & functions, which carries a
-- (subobject-classifier) Topos skeleton; and the relation allegory is a
-- POWER allegory (every relation transposes to a map into a power object).
--
-- PROVEN HERE (--safe --without-K):
--   * `Set-Category : CategoryOf` — types & functions form a STRICT category:
--     every law is `refl` by η.  This is the structural reason maps are better
--     behaved than relations: the full Rel allegory is only poset-enriched (up
--     to ≈, no strict-≡ — see `Category/Allegory`), but its MAPS (= functions,
--     ALG-5 `graph`) recover a strict category.
--   * `Set-Topos : Topos Set-Category` — the map category carries the (thin)
--     Topos skeleton, with Ω = Bool the classical (decidable-subobject)
--     classifier.  This closes the loop with the substrate's `Category/Topos`.
--   * POWER ALLEGORY: power object `P A = A → Set` (= the fiber family `Fam A`),
--     and the power transpose `name`/`unname : Rel A B ≃ (A → P B)` — for
--     Set-valued relations CURRYING, an IDENTITY: a relation IS a map into its
--     power object, definitionally.  Plus membership `_∈_`.
--
-- RESEARCH-GRADE REMAINDER (honest deferral — the full `Map(unitary tabular
-- power allegory) ≃ Topos`): the `SubobjectClassifier` True-arrow + pullback
-- characterization, finite limits, cartesian-closure, and tabularity are the
-- `Topos`/`SubobjectClassifier` records' explicit user-obligations.  The
-- proof-relevant classifier Ω = Set (vs Bool here) lives one universe up.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Power where

open import Substrate.Foundation.Level using (Level; _⊔_; 0ℓ) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Universe using (U; ⌜bool⌝; El)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.SubobjectClassifier using (SubobjectClassifier)
open import Substrate.Category.Topos using (Topos)
open import Substrate.Category.Allegory using (Rel)

-- ⟡rc-tarski-universe: the category of "types & functions" ranges over the
-- Set₀ Tarski universe U (decoded by El), NOT raw `Set` — so it lands in Set₀
-- (the generative representation; the "category of all Sets is Set₁" claim was
-- the wall-reflex — you represent the universe, like CF-streams represent
-- reals). Objects are type-CODES; morphisms El a → El b. η still makes every
-- law refl.
Set-Category : CategoryOf U (λ a b → El a → El b)
Set-Category = record
  { id       = λ A x → x
  ; compose  = λ g f x → g (f x)
  ; left-id  = λ f → refl
  ; right-id = λ f → refl
  ; assoc    = λ f g h → refl
  }

-- the (classical) subobject classifier Ω = the ⌜bool⌝ code (El ⌜bool⌝ = Bool);
-- decidable subobjects. True/pullback = obligations.
Set-SubobjectClassifier : SubobjectClassifier Set-Category
Set-SubobjectClassifier = record { Ω = ⌜bool⌝ }

-- the MAP category carries a Topos skeleton — closes the allegory→topos loop.
Set-Topos : Topos Set-Category
Set-Topos = record { Ω-data = Set-SubobjectClassifier }

-- POWER ALLEGORY: power object A → Set (= the fiber family), and the power
-- transpose Rel A B ≃ (A → (B → Set)).  For Set-valued relations this is
-- CURRYING — an IDENTITY: a relation IS a map into its power object,
-- DEFINITIONALLY. ⟡rc-local-respell: the `P A = A → Set` alias (Set₁) is
-- inlined + deleted (used only here).
name : {A B : Set} → Rel A B → A → B → Set
name R = R

unname : {A B : Set} → (A → (B → Set)) → A → B → Set
unname f = f

-- membership relation a ∈ S.
_∈_ : {A : Set} → A → (A → Set) → Set
a ∈ S = S a
