------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Warrant.Properties
--
-- The warrants form a BOUNDED MEET-SEMILATTICE under `_⊓w_`: commutative
-- (combination order-independent), associative (combining three claims is
-- unambiguous), idempotent (a claim combined with itself is unchanged),
-- with identity W (a witnessed premise never weakens) and zero U (an
-- unwitnessed premise makes the whole undetermined). All by refl after the
-- chain reductions.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Warrant.Properties where

open import Substrate.Foundation.Eq using (_≡_; refl; trans)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)

open import Substrate.Logic.Evidence.Warrant

⊓w-idem : (a : Warrant) → a ⊓w a ≡ a
⊓w-idem W = refl
⊓w-idem S = refl
⊓w-idem C = refl
⊓w-idem U = refl

⊓w-comm : (a b : Warrant) → a ⊓w b ≡ b ⊓w a
⊓w-comm W W = refl
⊓w-comm W S = refl
⊓w-comm W C = refl
⊓w-comm W U = refl
⊓w-comm S W = refl
⊓w-comm S S = refl
⊓w-comm S C = refl
⊓w-comm S U = refl
⊓w-comm C W = refl
⊓w-comm C S = refl
⊓w-comm C C = refl
⊓w-comm C U = refl
⊓w-comm U W = refl
⊓w-comm U S = refl
⊓w-comm U C = refl
⊓w-comm U U = refl

-- W and U rows are uniform in b, c; only the S and C rows split on c.
⊓w-assoc : (a b c : Warrant) → (a ⊓w b) ⊓w c ≡ a ⊓w (b ⊓w c)
⊓w-assoc W b c = refl
⊓w-assoc U b c = refl
⊓w-assoc S W c = refl
⊓w-assoc S U c = refl
⊓w-assoc S S W = refl
⊓w-assoc S S S = refl
⊓w-assoc S S C = refl
⊓w-assoc S S U = refl
⊓w-assoc S C W = refl
⊓w-assoc S C S = refl
⊓w-assoc S C C = refl
⊓w-assoc S C U = refl
⊓w-assoc C W c = refl
⊓w-assoc C U c = refl
⊓w-assoc C S W = refl
⊓w-assoc C S S = refl
⊓w-assoc C S C = refl
⊓w-assoc C S U = refl
⊓w-assoc C C W = refl
⊓w-assoc C C S = refl
⊓w-assoc C C C = refl
⊓w-assoc C C U = refl

⊓w-identityʳ : (a : Warrant) → a ⊓w W ≡ a
⊓w-identityʳ W = refl
⊓w-identityʳ S = refl
⊓w-identityʳ C = refl
⊓w-identityʳ U = refl

⊓w-zeroʳ : (a : Warrant) → a ⊓w U ≡ U
⊓w-zeroʳ W = refl
⊓w-zeroʳ S = refl
⊓w-zeroʳ C = refl
⊓w-zeroʳ U = refl

------------------------------------------------------------------------
-- GROUNDED: the warrant meet (⊓w, identity ⊤w = W) IS a substrate-named
-- `Category.CommutativeMonoid`. The bare laws above now witness the named
-- categorical structure rather than standing as a hand-rolled re-proof;
-- identityˡ is derived (comm ∘ identityʳ).
------------------------------------------------------------------------

⊓w-CommutativeMonoid : CommutativeMonoid _
⊓w-CommutativeMonoid = record
  { R            = Warrant
  ; _+R_         = _⊓w_
  ; 0R           = ⊤w
  ; +R-assoc     = ⊓w-assoc
  ; +R-identityˡ = λ a → trans (⊓w-comm ⊤w a) (⊓w-identityʳ a)
  ; +R-identityʳ = ⊓w-identityʳ
  ; +R-comm      = ⊓w-comm
  }
