------------------------------------------------------------------------
-- Substrate.Groups.F2Cubed
--
-- F_2³ — the elementary abelian group of order 8 (three copies of
-- Z/2Z under componentwise XOR). Substrate-native (no stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.F2Cubed where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _xor_)
open import Substrate.Foundation.Bool.Properties
  using (xor-assoc; xor-identityˡ; xor-identityʳ; xor-same)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

import Substrate.Algebra.Magma     as SM
import Substrate.Algebra.Semigroup as SS
import Substrate.Algebra.Monoid    as SMo
import Substrate.Algebra.Group     as SG

------------------------------------------------------------------------
-- Carrier.
------------------------------------------------------------------------

F₂³ : Set
F₂³ = Bool × Bool × Bool

------------------------------------------------------------------------
-- Group operations.
------------------------------------------------------------------------

infixl 6 _+_

_+_ : F₂³ → F₂³ → F₂³
(a₁ , a₂ , a₃) + (b₁ , b₂ , b₃) = (a₁ xor b₁ , a₂ xor b₂ , a₃ xor b₃)

ε : F₂³
ε = false , false , false

-_ : F₂³ → F₂³
- x = x

------------------------------------------------------------------------
-- Group axioms, lifted componentwise.
------------------------------------------------------------------------

+-assoc : (x y z : F₂³) → (x + y) + z ≡ x + (y + z)
+-assoc (a₁ , a₂ , a₃) (b₁ , b₂ , b₃) (c₁ , c₂ , c₃) =
  cong₂ _,_ (xor-assoc a₁ b₁ c₁)
   (cong₂ _,_ (xor-assoc a₂ b₂ c₂)
              (xor-assoc a₃ b₃ c₃))

+-identityˡ : (x : F₂³) → ε + x ≡ x
+-identityˡ (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-identityˡ a₁)
   (cong₂ _,_ (xor-identityˡ a₂) (xor-identityˡ a₃))

+-identityʳ : (x : F₂³) → x + ε ≡ x
+-identityʳ (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-identityʳ a₁)
   (cong₂ _,_ (xor-identityʳ a₂) (xor-identityʳ a₃))

+-self : (x : F₂³) → x + x ≡ ε
+-self (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-same a₁)
   (cong₂ _,_ (xor-same a₂) (xor-same a₃))

-inverseˡ : (x : F₂³) → (- x) + x ≡ ε
-inverseˡ x = +-self x

-inverseʳ : (x : F₂³) → x + (- x) ≡ ε
-inverseʳ x = +-self x

------------------------------------------------------------------------
-- Substrate-native group bundle.
------------------------------------------------------------------------

F₂³-Magma : SM.Magma F₂³
F₂³-Magma = record { _·_ = _+_ }

F₂³-Semigroup : SS.Semigroup F₂³
F₂³-Semigroup = record
  { magma   = F₂³-Magma
  ; ·-assoc = +-assoc
  }

F₂³-Monoid : SMo.Monoid F₂³
F₂³-Monoid = record
  { semigroup = F₂³-Semigroup
  ; ε         = ε
  ; ε-left    = +-identityˡ
  ; ε-right   = +-identityʳ
  }

F₂³-Group : SG.Group F₂³
F₂³-Group = record
  { monoid    = F₂³-Monoid
  ; inv       = -_
  ; inv-left  = -inverseˡ
  ; inv-right = -inverseʳ
  }

-- Backward-compat alias for files that already used the
-- `-substrate` suffixed name.
F₂³-Group-substrate : SG.Group F₂³
F₂³-Group-substrate = F₂³-Group
