------------------------------------------------------------------------
-- Substrate.Groups.V4.Bundle
--
-- V₄ group bundle (substrate-native). Phase-2: stdlib `Algebra.Bundles`
-- + `Algebra.Structures` + `Relation.Binary.PropositionalEquality.Properties`
-- imports REMOVED. The substrate-native `V₄-Group : Substrate.Algebra.
-- Group.Group V₄` is the canonical export.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bundle where
open import Substrate.Groups.V4.Operations using (_·_; ε; inv)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.EpsilonRight using (ε-right)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)
open import Substrate.Groups.V4.Axioms.InvRight using (inv-right)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
import Substrate.Algebra.Magma     as SM
import Substrate.Algebra.Semigroup as SS
import Substrate.Algebra.Monoid    as SMo
import Substrate.Algebra.Group     as SG

------------------------------------------------------------------------
-- Substrate-native V₄-Group bundle.
------------------------------------------------------------------------

V₄-Magma : SM.Magma V₄
V₄-Magma = record { _·_ = _·_ }

V₄-Semigroup : SS.Semigroup V₄
V₄-Semigroup = record
  { magma   = V₄-Magma
  ; ·-assoc = ·-assoc
  }

V₄-Monoid : SMo.Monoid V₄
V₄-Monoid = record
  { semigroup = V₄-Semigroup
  ; ε         = ε
  ; ε-left    = ε-left
  ; ε-right   = ε-right
  }

V₄-Group : SG.Group V₄
V₄-Group = record
  { monoid    = V₄-Monoid
  ; inv       = inv
  ; inv-left  = inv-left
  ; inv-right = inv-right
  }

------------------------------------------------------------------------
-- Backwards-compatibility alias: V₄-Group-substrate was the
-- old name during the dual-bundle transition. Now the
-- substrate-native version IS V₄-Group; the alias is retained for
-- downstream code that still uses the longer name.
------------------------------------------------------------------------

V₄-Group-substrate : SG.Group V₄
V₄-Group-substrate = V₄-Group

------------------------------------------------------------------------
-- Sanity check: canonical 4-product.
------------------------------------------------------------------------

V₄-canonical-4-product : e · α · β · γ ≡ e
V₄-canonical-4-product = refl
