{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSetoidCategory — a SMALL setoid-enriched category: the objects,
-- morphisms, and morphism-equality are MODULE PARAMETERS (all : Set, no universe levels), so the structure
-- record lives in Set (small) — NO Set₁, NO levels, NO funext, NO postulate. This follows the repo's OWN
-- bottom-level classifier discipline (operator: "see lawvere, tarski, ana"): Category.Lawvere's record
-- FixedPointFree (V : Set) : Set (parameterized over a concrete Set, record in Set) and Trace.Unfold's ana
-- (unfold : {S : Set} → …, everything small). Where 287 reached for Level/Set₁, this PARAMETERIZES instead —
-- the natural modularity boundary.
--
-- The morphism-equality _≈_ is a SUPPLIED parameter (an equivalence), and the category laws hold at _≈_ — the
-- non-funext packaging (the repo's groupoid Wedge.IsoGroupoid does exactly this with its pointwise _≈ʷ_). IO's
-- multi-object Kleisli (286c) instantiates it with _≐_ (pointwise/bisimilar), so its category laws are a
-- genuine record, small, no funext.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: IsEquivalence (the
-- refl/sym/trans bundle, in Set), IsSetoidCategory (the record of id/compose + laws-at-≈, in Set, over the
-- Obj/Mor/_≈_ module parameters), and io-kleisli-setoid (IO's Kleisli AS an IsSetoidCategory, via 286c's _≐_).
-- The framing ('small, parameterized, no levels/Set₁/funext; the repo's Lawvere/ana discipline') is (prose:
-- Category.Lawvere + Trace.Unfold + Wedge.IsoGroupoid + 286c).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSetoidCategory where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

------------------------------------------------------------------------
-- ① IsEquivalence (in Set — parameterized over the carrier A : Set and the relation _≈_, both concrete):
------------------------------------------------------------------------
record IsEquivalence {A : Set} (_≈_ : A → A → Set) : Set where
  field
    ≈-refl  : (a : A) → a ≈ a
    ≈-sym   : {a b : A} → a ≈ b → b ≈ a
    ≈-trans : {a b c : A} → a ≈ b → b ≈ c → a ≈ c
open IsEquivalence public

------------------------------------------------------------------------
-- ② THE SMALL SETOID-ENRICHED CATEGORY: Obj/Mor/_≈_ are MODULE PARAMETERS (all : Set — no levels), so the
--    record of operations+laws is : Set (small). The laws hold at the SUPPLIED equivalence _≈_ (no funext).
------------------------------------------------------------------------
module _ (Obj : Set) (Mor : Obj → Obj → Set)
         (_≈_ : {a b : Obj} → Mor a b → Mor a b → Set) where

  record IsSetoidCategory : Set where
    field
      ≈-equiv  : {a b : Obj} → IsEquivalence (_≈_ {a} {b})
      id       : (a : Obj) → Mor a a
      compose  : {a b c : Obj} → Mor b c → Mor a b → Mor a c
      left-id  : {a b : Obj} (f : Mor a b) → (compose (id b) f) ≈ f
      right-id : {a b : Obj} (f : Mor a b) → (compose f (id a)) ≈ f
      assoc    : {a b c d : Obj} (f : Mor a b) (g : Mor b c) (h : Mor c d) →
                 (compose h (compose g f)) ≈ (compose (compose h g) f)
  open IsSetoidCategory public

------------------------------------------------------------------------
-- ③ IO's MULTI-OBJECT KLEISLI AS A SMALL SetoidCategory (the payoff — 286c's _≐_ is the morphism-equality;
--    the record is small, no funext). Parameterized over O/𝕆/⟦_⟧ (all : Set).
------------------------------------------------------------------------
module _ (O : Set) (𝕆 : Set) (⟦_⟧ : 𝕆 → Set) where
  open import Substrate.Category.UniversalProperty.ExtrudeIOKleisli O 𝕆 ⟦_⟧
    using (Kmor; Kid; Kcompose; _≐_; ≐-refl; ≐-sym; ≐-trans; K-left-id; K-right-id; K-assoc)

  io-kleisli-setoid : IsSetoidCategory 𝕆 Kmor _≐_
  io-kleisli-setoid = record
    { ≈-equiv  = record { ≈-refl = ≐-refl ; ≈-sym = ≐-sym ; ≈-trans = ≐-trans }
    ; id       = Kid
    ; compose  = Kcompose
    ; left-id  = K-left-id
    ; right-id = K-right-id
    ; assoc    = K-assoc
    }

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — a SMALL setoid-enriched category: Obj/Mor/_≈_ module PARAMETERS, record in
-- Set, NO levels/Set₁/funext/postulate; the repo's own Lawvere/ana bottom-level discipline): 287 reached for
-- universe levels (record SetoidCategory (ℓO ℓM ℓE) : Set (lsuc …)) — the operator's hard constraint forbids
-- that. The fix, from the repo's bottom-level classifiers (Category.Lawvere's FixedPointFree (V : Set) : Set,
-- parameterized over a concrete Set with the record in Set; Trace.Unfold's ana over {S : Set}): PARAMETERIZE
-- over Obj/Mor/_≈_ (all : Set — the natural modularity boundary), so IsSetoidCategory (②) is a record in Set
-- (small). IsEquivalence (①) likewise. Then IO's multi-object Kleisli (286c) is a genuine SMALL record (③,
-- io-kleisli-setoid : IsSetoidCategory 𝕆 Kmor _≐_) — its _≐_ (pointwise/bisimilar) the morphism-equality, its
-- laws already grounded, NO funext, NO Set₁, NO levels, parameterized. So the funext/level boundary is
-- DISSOLVED by parameterization (the operator's rule), reusing the repo's own small-classifier discipline and
-- the groupoid's setoid move (IsoGroupoid's _≈ʷ_). Chain: 286 (Kleisli laws at _≐_) → 287 (levels — WRONG) →
-- 288 (small, parameterized — the repo's Lawvere/ana discipline).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = IsEquivalence + IsSetoidCategory (both in Set, small, over module
-- params), io-kleisli-setoid (IO's Kleisli as a genuine SMALL record, no funext/levels). SCOPED: packaging IO's
-- Monad (η/μ, 286b) as a Monad over this small setoid-category (⟡extrude-io-monad-record — a small setoid-
-- enriched Monad record, parameterized, no levels); a small SetoidFunctor (⟡extrude-setoid-functor). What's
-- grounded: a small, parameterized, level-free, funext-free, postulate-free setoid-enriched category, with IO's
-- multi-object Kleisli as an instance — the operator's constraints met by parameterization.
------------------------------------------------------------------------
