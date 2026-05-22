------------------------------------------------------------------------
-- Substrate.Category.TwoCategory
--
-- Q1 of the Q-arc. 2-category primitive: 0-cells (objects), 1-cells
-- (morphisms), 2-cells (morphisms of morphisms) + horizontal + vertical
-- composition + coherence.
--
-- Per [[grothendieck-coherence-rule]] + EMERGENT N-arc audit: the
-- substrate's prior layers had 0-cells (categories), 1-cells (functors,
-- M1), 2-cells (nat-trans, M2) packaged separately; Q1 names the
-- universal carrier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TwoCategory where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ0 ℓ1 ℓ2 : Level

------------------------------------------------------------------------
-- The TwoCategory record.
------------------------------------------------------------------------

record TwoCategory : Set (lsuc (ℓ0 ⊔ ℓ1 ⊔ ℓ2)) where
  field
    Obj   : Set ℓ0
    Mor   : Obj → Obj → Set ℓ1
    TwoCell : {a b : Obj} → Mor a b → Mor a b → Set ℓ2
    id-1  : (a : Obj) → Mor a a
    comp-1 : {a b c : Obj} → Mor b c → Mor a b → Mor a c
    id-2  : {a b : Obj} (f : Mor a b) → TwoCell f f
    comp-2-vertical :
      {a b : Obj} {f g h : Mor a b} →
      TwoCell g h → TwoCell f g → TwoCell f h

------------------------------------------------------------------------
-- Coherence (interchange, associativity, units) supplied by concrete
-- consumers per substrate-pragmatic minimum.
------------------------------------------------------------------------
