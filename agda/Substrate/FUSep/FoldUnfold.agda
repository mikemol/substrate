{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.FUSep.FoldUnfold — the free-unfold / aggressive-fold MATCHED PAIR,
-- machine-checked. [Conformed from the z47 self-contained prototype: the inlined
-- _≡_ / Σ / _×_ are replaced by Foundation.*; the domain content is unchanged.]
--
--   THE FOLD   = behavioral dedup, one representative per ~-class (the SPPF
--                quotient). Sound as an equality iff ~ is a CONGRUENCE.
--   THE UNFOLD = the free closure under application, INCLUDING self-application
--                (the powerset closure): every partial completion interned and kept
--                combinable, Earley-style.
--
-- A MATCHED PAIR: an aggressive fold is COMPLETE only when paired with a FREE
-- unfold, sound exactly when ~ is a congruence (ADD 96). The coalgebraic dual of the
-- substrate's initial-algebra centre: the unfold is the FREE construction (initial
-- algebra, induction); the fold is behavioral OBSERVATION (final coalgebra); hinged
-- by Lawvere (ADD 92).
------------------------------------------------------------------------

module Substrate.FUSep.FoldUnfold where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.Magma using (Magma)   -- the canonical magma (carrier param + _·_)

-- a magma: a carrier with application (the SKI applicative structure). The carrier
-- is the module parameter below; the canonical Algebra.Magma provides _·_.
Pred : Set → Set₁
Pred A = A → Set

module _ {Carrier : Set} (M : Magma Carrier) where
  open Magma M

  --------------------------------------------------------------------
  -- THE FREE UNFOLD: closure of X under application, INCLUDING self-
  -- application. Each Gen node IS a partial completion, kept combinable.
  --------------------------------------------------------------------
  data Gen (X : Pred Carrier) : Carrier → Set where
    gen : ∀ {x}   → X x → Gen X x
    app : ∀ {a b} → Gen X a → Gen X b → Gen X (a · b)

  -- self-combination is a corollary (the diagonal of app): a term combined
  -- WITH ITSELF — the powerset closure the operator flagged.
  self : ∀ {X a} → Gen X a → Gen X (a · a)
  self g = app g g

  --------------------------------------------------------------------
  -- THE AGGRESSIVE FOLD is sound (as an equality) exactly when the
  -- behavioral ~ RESPECTS application — i.e. is a CONGRUENCE.
  --------------------------------------------------------------------
  record Congruence : Set₁ where
    field
      _~_     : Carrier → Carrier → Set
      ~-refl  : ∀ {a}         → a ~ a
      ~-sym   : ∀ {a b}       → a ~ b → b ~ a
      ~-trans : ∀ {a b c}     → a ~ b → b ~ c → a ~ c
      ~-cong  : ∀ {a a' b b'} → a ~ a' → b ~ b' → (a · b) ~ (a' · b')

  --------------------------------------------------------------------
  -- THE FILTER (coalgebra by constraint, ADD 93): a law P proven true in the
  -- coalgebra; its contrapositive ¬P is OUTSIDE. If the law is a SUBALGEBRA
  -- (closed under application) and the seeds satisfy it, the free unfold emits
  -- ONLY P. Generation-under-the-filter is SOUND.
  --------------------------------------------------------------------
  filter-sound :
    ∀ {P : Pred Carrier} →
    (∀ {a b} → P a → P b → P (a · b)) →
    ∀ {X} → (∀ {x} → X x → P x) →
    ∀ {t} → Gen X t → P t
  filter-sound pc x⊆P (gen x)     = x⊆P x
  filter-sound pc x⊆P (app ga gb) = pc (filter-sound pc x⊆P ga)
                                        (filter-sound pc x⊆P gb)

  module _ (Cg : Congruence) where
    open Congruence Cg

    -- a REP MAP: each generator has a ~-equivalent representative in X'
    -- (the fold picking one term per behavior class — the SPPF chart).
    RepMap : Pred Carrier → Pred Carrier → Set
    RepMap X X' = ∀ {x} → X x → Σ Carrier (λ x' → (X' x') × (x ~ x'))

    ------------------------------------------------------------------
    -- THE MATCHED-PAIR THEOREM (SPPF reuse soundness): closing over the
    -- REPRESENTATIVES reaches a ~-equivalent of EVERYTHING closing over the full
    -- set reaches. The aggressive fold loses NOTHING — provided the unfold is free
    -- (Gen closed under app, incl self) and ~ is a congruence.
    ------------------------------------------------------------------
    rep-closure-complete :
      ∀ {X X'} → RepMap X X' →
      ∀ {t} → Gen X t →
      Σ Carrier (λ t' → (Gen X' t') × (t ~ t'))
    rep-closure-complete rm (gen x) with rm x
    ... | (x' , (x'∈X' , x~x')) = x' , (gen x'∈X' , x~x')
    rep-closure-complete rm (app ga gb)
      with rep-closure-complete rm ga | rep-closure-complete rm gb
    ... | (a' , (ga' , a~a')) | (b' , (gb' , b~b')) =
          (a' · b') , (app ga' gb' , ~-cong a~a' b~b')
