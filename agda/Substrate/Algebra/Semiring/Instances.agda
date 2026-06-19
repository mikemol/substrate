------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.Instances
--
-- Concrete instantiations of the dormant `Semiring` record at the
-- four "job gauges" of the semiring-VM layer (conjecture #6,
-- scratch/commuting_sphere.md):  one tensor over a chosen semiring
-- *is* the job gauge.
--
--   * ℕ            — the COUNTING gauge   (+ , * , 0 , 1)
--   * F₂           — the GF(2)/CARRIER gauge (XOR , AND , 𝟘 , 𝟙)
--   * Bool         — the ROUTING gauge   (∨ , ∧ , false , true)
--   * ℕ∞ (tropical)— the COST/PLACEMENT gauge (min , + , ∞ , fin 0)
--
-- The semiring records are *packaging* moves over laws proven
-- elsewhere (Foundation.Nat.Properties.*, Algebra.F2, and — for the
-- Bool routing laws, which had no prior home — small exhaustive
-- case-splits in §3 below).  Nothing is postulated.
--
-- F₂'s Semiring already lives at Substrate.Algebra.F2.AsField
-- (F₂-Semiring); it is re-exported here so that all four gauges sit
-- behind one import.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.Instances where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Semiring using (Semiring)

------------------------------------------------------------------------
-- 0. The shared costructure: build a Monoid from carrier + op + ε
--    + the three laws.  Used 6× below (one additive + one
--    multiplicative monoid for each of ℕ, Bool, ℕ∞).
------------------------------------------------------------------------

mk-monoid :
  {A : Set}
  (op : A → A → A)
  (e  : A)
  (assoc : (a b c : A) → op (op a b) c ≡ op a (op b c))
  (idˡ : (a : A) → op e a ≡ a)
  (idʳ : (a : A) → op a e ≡ a)
  → Monoid A
mk-monoid op e assoc idˡ idʳ = record
  { semigroup = record { magma = record { _·_ = op } ; ·-assoc = assoc }
  ; ε         = e
  ; ε-left    = idˡ
  ; ε-right   = idʳ
  }

------------------------------------------------------------------------
-- 1. ℕ — the counting gauge.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-assoc; +-identityˡ; +-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-identityˡ; *-identityʳ;
         *-distribˡ-+; *-distribʳ-+; *-zeroˡ; *-zeroʳ)

ℕ-+-Monoid : Monoid ℕ
ℕ-+-Monoid = mk-monoid _+_ zero +-assoc +-identityˡ +-identityʳ

ℕ-*-Monoid : Monoid ℕ
ℕ-*-Monoid = mk-monoid _*_ (suc zero) *-assoc *-identityˡ *-identityʳ

ℕ-semiring : Semiring ℕ
ℕ-semiring = record
  { +-monoid          = ℕ-+-Monoid
  ; *-monoid          = ℕ-*-Monoid
  ; distrib-left      = *-distribˡ-+
  ; distrib-right     = λ a b c → *-distribʳ-+ c a b
  ; zero-absorb-left  = *-zeroˡ
  ; zero-absorb-right = *-zeroʳ
  }

------------------------------------------------------------------------
-- 2. F₂ — the GF(2)/carrier gauge.
--
-- The full Semiring (in fact Field) instance already exists; we
-- simply re-export it so all four gauges are reachable here.
------------------------------------------------------------------------

open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.AsField using () renaming (F₂-Semiring to F₂-semiring) public

------------------------------------------------------------------------
-- 3. Bool — the routing gauge.
--
-- additive = ∨ (ε = false), multiplicative = ∧ (ε = true).  (Ⓓ: these Bool
-- laws now live at the Bool carrier home, Foundation.Bool.Properties — they
-- were proven here "for lack of a prior home", but 4 already lived there and
-- the other 6 belong there too. Imported below, then packaged into the records.)
------------------------------------------------------------------------

open import Substrate.Foundation.Bool using (Bool; true; false; _∨_; _∧_)
open import Substrate.Foundation.Bool.Properties
  using ( ∨-assoc; ∨-identityˡ; ∨-identityʳ; ∧-assoc; ∧-identityˡ; ∧-identityʳ
        ; ∧-distribˡ-∨; ∧-distribʳ-∨; ∧-zeroˡ; ∧-zeroʳ )

Bool-∨-Monoid : Monoid Bool
Bool-∨-Monoid = mk-monoid _∨_ false ∨-assoc ∨-identityˡ ∨-identityʳ

Bool-∧-Monoid : Monoid Bool
Bool-∧-Monoid = mk-monoid _∧_ true ∧-assoc ∧-identityˡ ∧-identityʳ

Bool-semiring : Semiring Bool
Bool-semiring = record
  { +-monoid          = Bool-∨-Monoid
  ; *-monoid          = Bool-∧-Monoid
  ; distrib-left      = ∧-distribˡ-∨
  ; distrib-right     = ∧-distribʳ-∨
  ; zero-absorb-left  = ∧-zeroˡ
  ; zero-absorb-right = ∧-zeroʳ
  }

------------------------------------------------------------------------
-- 4. ℕ∞ tropical (min-plus) — the cost/placement gauge.
--
-- additive = min (ε = ∞), multiplicative = ⊕ = +∞ (ε = fin 0).
-- Carrier + laws live in Substrate.Algebra.Semiring.NatInf.
------------------------------------------------------------------------

open import Substrate.Algebra.Semiring.NatInf
  using (ℕ∞; fin; ∞; _⊓_; _⊕_;
         ⊓-assoc; ⊓-identityˡ; ⊓-identityʳ;
         ⊕-identityˡ; ⊕-distribˡ-⊓; ⊕-absorbˡ; ⊕-absorbʳ)
open import Substrate.Algebra.Semiring.NatInf.Properties
  using (⊕-assoc; ⊕-identityʳ; ⊕-distribʳ-⊓)
open import Substrate.Foundation.Nat using () renaming (zero to ℕzero)

ℕ∞-⊓-Monoid : Monoid ℕ∞
ℕ∞-⊓-Monoid = mk-monoid _⊓_ ∞ ⊓-assoc ⊓-identityˡ ⊓-identityʳ

ℕ∞-⊕-Monoid : Monoid ℕ∞
ℕ∞-⊕-Monoid = mk-monoid _⊕_ (fin ℕzero) ⊕-assoc ⊕-identityˡ ⊕-identityʳ

tropical-semiring : Semiring ℕ∞
tropical-semiring = record
  { +-monoid          = ℕ∞-⊓-Monoid
  ; *-monoid          = ℕ∞-⊕-Monoid
  ; distrib-left      = ⊕-distribˡ-⊓
  ; distrib-right     = ⊕-distribʳ-⊓
  ; zero-absorb-left  = ⊕-absorbˡ
  ; zero-absorb-right = ⊕-absorbʳ
  }
