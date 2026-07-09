{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSetoidFunctor — SMALL functors and natural transformations
-- between setoid-enriched categories (288). Everything is MODULE-PARAMETERIZED over concrete Sets (no levels,
-- no Set₁, no funext, no postulate): the source/target objects, morphisms, and morphism-equalities are
-- parameters, so the SetoidFunctor / SetoidNaturalTransformation records live in Set. Laws hold at the target
-- _≈_ (the non-funext packaging). This is the enabling piece for the setoid-enriched Monad (io-monad-record).
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: SetoidFunctor (F-obj/F-mor/
-- F-resp/F-id/F-compose at _≈₂_) and SetoidNaturalTransformation (component/naturality at _≈₂_). The framing
-- ('small, parameterized, no levels/funext') is (prose: 288 + Category.Functor/NaturalTransformation).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSetoidFunctor where

------------------------------------------------------------------------
-- ① SetoidFunctor between two setoid-categories (source/target as module params — all Set, small):
------------------------------------------------------------------------
module _ (Obj₁ : Set) (Mor₁ : Obj₁ → Obj₁ → Set)
         (_≈₁_ : {a b : Obj₁} → Mor₁ a b → Mor₁ a b → Set)
         (id₁ : (a : Obj₁) → Mor₁ a a)
         (comp₁ : {a b c : Obj₁} → Mor₁ b c → Mor₁ a b → Mor₁ a c)
         (Obj₂ : Set) (Mor₂ : Obj₂ → Obj₂ → Set)
         (_≈₂_ : {a b : Obj₂} → Mor₂ a b → Mor₂ a b → Set)
         (id₂ : (a : Obj₂) → Mor₂ a a)
         (comp₂ : {a b c : Obj₂} → Mor₂ b c → Mor₂ a b → Mor₂ a c) where

  record SetoidFunctor : Set where
    field
      F-obj     : Obj₁ → Obj₂
      F-mor     : {a b : Obj₁} → Mor₁ a b → Mor₂ (F-obj a) (F-obj b)
      F-resp    : {a b : Obj₁} {f g : Mor₁ a b} → f ≈₁ g → F-mor f ≈₂ F-mor g
      F-id      : (a : Obj₁) → F-mor (id₁ a) ≈₂ id₂ (F-obj a)
      F-compose : {a b c : Obj₁} (g : Mor₁ b c) (f : Mor₁ a b) →
                  F-mor (comp₁ g f) ≈₂ comp₂ (F-mor g) (F-mor f)
  open SetoidFunctor public

------------------------------------------------------------------------
-- ② SetoidNaturalTransformation between two SetoidFunctors F, G (given by their obj/mor actions as params —
--    small): a component at each object + the naturality square at the target _≈₂_.
------------------------------------------------------------------------
module _ (Obj₁ : Set) (Mor₁ : Obj₁ → Obj₁ → Set)
         (Obj₂ : Set) (Mor₂ : Obj₂ → Obj₂ → Set)
         (_≈₂_ : {a b : Obj₂} → Mor₂ a b → Mor₂ a b → Set)
         (comp₂ : {a b c : Obj₂} → Mor₂ b c → Mor₂ a b → Mor₂ a c)
         (F-obj G-obj : Obj₁ → Obj₂)
         (F-mor : {a b : Obj₁} → Mor₁ a b → Mor₂ (F-obj a) (F-obj b))
         (G-mor : {a b : Obj₁} → Mor₁ a b → Mor₂ (G-obj a) (G-obj b)) where

  record SetoidNaturalTransformation : Set where
    field
      component  : (a : Obj₁) → Mor₂ (F-obj a) (G-obj a)
      naturality : {a b : Obj₁} (f : Mor₁ a b) →
                   comp₂ (component b) (F-mor f) ≈₂ comp₂ (G-mor f) (component a)
  open SetoidNaturalTransformation public

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — small setoid functors + natural transformations, parameterized over concrete
-- Sets, laws at the target _≈_, NO levels/Set₁/funext/postulate): 288 gave the small setoid-category; this
-- gives the maps between them. SetoidFunctor (①) carries F-obj/F-mor with F-resp (respects _≈₁_), F-id/
-- F-compose at _≈₂_ (not ≡ — no funext). SetoidNaturalTransformation (②) carries a component + naturality at
-- _≈₂_. All records live in Set (source/target data are module PARAMS), so no levels, no Set₁. These are the
-- pieces the setoid-enriched Monad needs (T a SetoidFunctor endofunctor, η/μ SetoidNaturalTransformations) —
-- io-monad-record. Reusing 288's discipline, no over-assumption. Chain: 288 (setoid-category) → 289a (setoid
-- functor + NT).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = SetoidFunctor + SetoidNaturalTransformation (both small,
-- parameterized, laws at _≈₂_). SCOPED: the composite/identity SetoidFunctor + vertical/horizontal NT
-- composition (⟡extrude-setoid-functor-compose — the 2-categorical structure, small). What's grounded: small
-- setoid functors and natural transformations, the maps between setoid-categories, no levels/funext.
------------------------------------------------------------------------
