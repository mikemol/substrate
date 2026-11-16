------------------------------------------------------------------------
-- Substrate.Algebra.F2.FromBool
--
-- N-1 of M-11.dim4.codeword-bridge. Direct Bool ↔ F₂ bijection.
--
-- Foundational primitive for bridging Bool-based ambient types
-- (e.g., Codeword.agda's Bool⁵ Codeword) to F₂-linear structural
-- forms. Minimal subset of M-10A N-1 (the full M-10A would package
-- this as an F₂-Like universal-property instance +F derived
-- Foundations.Bijection bundle; here we just provide the direct
-- bijection for use by M-11.dim4.codeword-bridge).
--
-- Convention: false ↔ 𝟘, true ↔ 𝟙. Matches the existing convention
-- in M-12 N-4 (Chirality ↔ F₂ with even ↔ 𝟘, odd ↔ 𝟙) and the
-- canonical sign-character convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.FromBool where

open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.OrXorAnd   -- ⟡A5: read the Bool ANF-of-OR

open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

------------------------------------------------------------------------
-- Forward: Bool → F₂.
------------------------------------------------------------------------

bool→F₂ : Bool → F₂
bool→F₂ true  = 𝟙
bool→F₂ false = 𝟘

------------------------------------------------------------------------
-- Backward: F₂ → Bool.
------------------------------------------------------------------------

F₂→bool : F₂ → Bool
F₂→bool 𝟙 = true
F₂→bool 𝟘 = false

------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

bool→F₂→bool : (b : Bool) → F₂→bool (bool→F₂ b) ≡ b
bool→F₂→bool true  = refl
bool→F₂→bool false = refl

F₂→bool→F₂ : (x : F₂) → bool→F₂ (F₂→bool x) ≡ x
F₂→bool→F₂ 𝟙 = refl
F₂→bool→F₂ 𝟘 = refl

------------------------------------------------------------------------
-- ⟡H-lemmas — Bool is the F₂ FIELD plus a graded (∧) RESIDUE: the two op-homomorphism
-- halves (xor ↔ +F, ∧ ↔ ·) and the APEX  OR = recon(XOR, AND).
--
-- The oriented-residue reading: Bool (∨/∧, the ROUTING gauge) and F₂ (+/·, the FIELD gauge)
-- are TWO GAUGES OF ONE CARRIER — they SHARE the multiplication (∧ = ·) and differ only by a
-- graded cross-term. OR is NOT a separate primitive: it is the wedge recon  a = recon q b r
-- = q·b +F r  read as  a ∨ b = (a ⊕ b) ⊕ (a ∧ b), with the ∧ cross-term the ORIENTED RESIDUE the
-- Bool gauge adds to the F₂ field. The `𝟙 ∨ 𝟙 = 𝟙` vs `𝟙 +F 𝟙 = 𝟘` "trap" is the wall-REFLEX
-- this dissolves (cf. SpectralCrossCoherent, which names that reflex an error); the four-gauge
-- split is the guard. Each lemma is refl (case-split on the two Bools) — an unwritten corollary
-- of the already-banked machinery (bool→F₂ +F F2's _+_/_·_), now a TERM.
------------------------------------------------------------------------

-- ∧ ↔ · : the SHARED multiplication (the multiplicative op-homomorphism half).
bool→F₂-and : (a b : Bool) → bool→F₂ (a ∧ b) ≡ bool→F₂ a · bool→F₂ b
bool→F₂-and true  true  = refl
bool→F₂-and true  false = refl
bool→F₂-and false true  = refl
bool→F₂-and false false = refl

-- xor ↔ +F : the additive op-homomorphism (the F₂ field addition = symmetric difference).
bool→F₂-xor : (a b : Bool) → bool→F₂ (a xor b) ≡ bool→F₂ a +F bool→F₂ b
bool→F₂-xor true  true  = refl
bool→F₂-xor true  false = refl
bool→F₂-xor false true  = refl
bool→F₂-xor false false = refl

-- THE APEX:  OR = recon(XOR, AND) = a ⊕ b ⊕ (a ∧ b). Bool ∨ IS the F₂ field XOR reconstructed by the
-- ∧ cross-term (the oriented residue r in  recon q b r = q·b +F r) — the wedge, not a new primitive.
-- (_+F_ is infixl 6, _·_ infixl 7, so the RHS is ((a+b) +F (a·b)).) ⟡A5: DERIVED by reading the Bool-level
-- ANF-of-OR (or-xor-and, Foundation.Bool.Properties) and transporting it through the two op-homomorphisms
-- (bool→F₂-xor on the outer/inner XOR, bool→F₂-and on the ∧) — the F₂ image of the ONE Bool identity, not
-- a re-case-split.
∨-as-xor-recon : (a b : Bool)
               → bool→F₂ (a ∨ b) ≡ (bool→F₂ a +F bool→F₂ b) +F (bool→F₂ a · bool→F₂ b)
∨-as-xor-recon a b =
  trans (cong bool→F₂ (or-xor-and a b))
        (trans (bool→F₂-xor (a xor b) (a ∧ b))
               (cong₂ _+F_ (bool→F₂-xor a b) (bool→F₂-and a b)))
