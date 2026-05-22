------------------------------------------------------------------------
-- Substrate.Algebra.F2.AsField
--
-- M9 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- Packages F₂ as a Field instance. The substrate's existing F₂
-- infrastructure (Substrate.Algebra.F2 + F2-CommutativeMonoid) is
-- already discharged at the operational level; this slice wires
-- it into the M-arc records.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]] applied
-- coalgebraically: each tower level's instance is a packaging
-- move, not a re-derivation. The operational laws were proven
-- at the F₂ module already.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AsField where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; cong; trans)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.F2
  using (F₂; 𝟘; 𝟙; _+_; _·_; -_;
         +-assoc; +-comm; +-identityˡ; +-identityʳ;
         +-inverseˡ; +-inverseʳ;
         ·-assoc; ·-comm; ·-identityˡ; ·-identityʳ;
         ·-absorbˡ; ·-absorbʳ;
         +-self-inverse;
         ·-distribˡ-+; ·-distribʳ-+;
         𝟘≢𝟙; 𝟙≢𝟘)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Field using (Field)

------------------------------------------------------------------------
-- 1. F₂'s additive structure: Magma → Semigroup → Monoid → Group
-- → AbelianGroup.
------------------------------------------------------------------------

F₂-+-Magma : Magma F₂
F₂-+-Magma = record { _·_ = _+_ }

F₂-+-Semigroup : Semigroup F₂
F₂-+-Semigroup = record
  { magma   = F₂-+-Magma
  ; ·-assoc = +-assoc
  }

F₂-+-Monoid : Monoid F₂
F₂-+-Monoid = record
  { semigroup = F₂-+-Semigroup
  ; ε         = 𝟘
  ; ε-left    = +-identityˡ
  ; ε-right   = +-identityʳ
  }

F₂-+-Group : Group F₂
F₂-+-Group = record
  { monoid    = F₂-+-Monoid
  ; inv       = -_
  ; inv-left  = +-inverseˡ
  ; inv-right = +-inverseʳ
  }

F₂-+-AbelianGroup : AbelianGroup F₂
F₂-+-AbelianGroup = record
  { group  = F₂-+-Group
  ; ·-comm = +-comm
  }

------------------------------------------------------------------------
-- 2. F₂'s multiplicative structure: Monoid.
------------------------------------------------------------------------

F₂-·-Magma : Magma F₂
F₂-·-Magma = record { _·_ = _·_ }

F₂-·-Semigroup : Semigroup F₂
F₂-·-Semigroup = record
  { magma   = F₂-·-Magma
  ; ·-assoc = ·-assoc
  }

F₂-·-Monoid : Monoid F₂
F₂-·-Monoid = record
  { semigroup = F₂-·-Semigroup
  ; ε         = 𝟙
  ; ε-left    = ·-identityˡ
  ; ε-right   = ·-identityʳ
  }

------------------------------------------------------------------------
-- 3. F₂ as Semiring: combine additive + multiplicative monoids.
------------------------------------------------------------------------

F₂-Semiring : Semiring F₂
F₂-Semiring = record
  { +-monoid          = F₂-+-Monoid
  ; *-monoid          = F₂-·-Monoid
  ; distrib-left      = ·-distribˡ-+
  ; distrib-right     = λ a b c → ·-distribʳ-+ c a b
  ; zero-absorb-left  = ·-absorbˡ
  ; zero-absorb-right = ·-absorbʳ
  }

------------------------------------------------------------------------
-- 4. F₂ as Ring: Semiring + additive AbelianGroup.
------------------------------------------------------------------------

F₂-Ring : Ring F₂
F₂-Ring = record
  { semiring   = F₂-Semiring
  ; +-abelian  = F₂-+-AbelianGroup
  ; +-coherent = refl
  }

------------------------------------------------------------------------
-- 5. F₂ as Field: Ring + multiplicative inverse + 0 ≠ 1.
--
-- In F₂, the only non-zero element is 𝟙, and its multiplicative
-- inverse is itself (𝟙 · 𝟙 = 𝟙). The inverse function is the
-- identity on non-zero elements.
------------------------------------------------------------------------

F₂-Field : Field F₂
F₂-Field = record
  { ring        = F₂-Ring
  ; 0≢1         = 𝟘≢𝟙
  ; mul-inv     = λ { 𝟘 0≢0 → 𝟙   -- vacuous; 0≢0 is absurd
                    ; 𝟙 _   → 𝟙
                    }
  ; mul-inv-law = λ { 𝟘 0≢0 → 𝟘≢0-absurd 0≢0
                    ; 𝟙 _   → refl
                    }
  }
  where
    𝟘≢0-absurd : ¬ (𝟘 ≡ 𝟘) → _
    𝟘≢0-absurd 0≢0 with 0≢0 refl
    ... | ()

------------------------------------------------------------------------
-- 6. Capstone for M9.
--
-- F₂ now sits as a Field instance. All F₂ ring-laws are accessible
-- via Field-accessor projections (ring → semiring → +-monoid →
-- semigroup → ·-assoc, etc.). M10 supplies ℚ similarly.
------------------------------------------------------------------------
