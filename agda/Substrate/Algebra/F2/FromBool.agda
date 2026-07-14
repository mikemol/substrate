------------------------------------------------------------------------
-- Substrate.Algebra.F2.FromBool
--
-- N-1 of M-11.dim4.codeword-bridge. Direct Bool ↔ F₂ bijection.
--
-- Foundational primitive for bridging Bool-based ambient types
-- (e.g., Codeword.agda's Bool⁵ Codeword) to F₂-linear structural
-- forms. Minimal subset of M-10A N-1 (the full M-10A would package
-- this as an F₂-Like universal-property instance + derived
-- Foundations.Bijection bundle; here we just provide the direct
-- bijection for use by M-11.dim4.codeword-bridge).
--
-- Convention: false ↔ 𝟘, true ↔ 𝟙. Matches the existing convention
-- in M-12 N-4 (Chirality ↔ F₂ with even ↔ 𝟘, odd ↔ 𝟙) and the
-- canonical sign-character convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.FromBool where

open import Substrate.Foundation.Bool using (Bool; true; false; _∧_; _∨_; _xor_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2

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
-- halves (xor ↔ +, ∧ ↔ ·) and the APEX  OR = recon(XOR, AND).
--
-- The oriented-residue reading: Bool (∨/∧, the ROUTING gauge) and F₂ (+/·, the FIELD gauge)
-- are TWO GAUGES OF ONE CARRIER — they SHARE the multiplication (∧ = ·) and differ only by a
-- graded cross-term. OR is NOT a separate primitive: it is the wedge recon  a = recon q b r
-- = q·b + r  read as  a ∨ b = (a ⊕ b) ⊕ (a ∧ b), with the ∧ cross-term the ORIENTED RESIDUE the
-- Bool gauge adds to the F₂ field. The `𝟙 ∨ 𝟙 = 𝟙` vs `𝟙 + 𝟙 = 𝟘` "trap" is the wall-REFLEX
-- this dissolves (cf. SpectralCrossCoherent, which names that reflex an error); the four-gauge
-- split is the guard. Each lemma is refl (case-split on the two Bools) — an unwritten corollary
-- of the already-banked machinery (bool→F₂ + F2's _+_/_·_), now a TERM.
------------------------------------------------------------------------

-- ∧ ↔ · : the SHARED multiplication (the multiplicative op-homomorphism half).
bool→F₂-and : (a b : Bool) → bool→F₂ (a ∧ b) ≡ bool→F₂ a · bool→F₂ b
bool→F₂-and true  true  = refl
bool→F₂-and true  false = refl
bool→F₂-and false true  = refl
bool→F₂-and false false = refl

-- xor ↔ + : the additive op-homomorphism (the F₂ field addition = symmetric difference).
bool→F₂-xor : (a b : Bool) → bool→F₂ (a xor b) ≡ bool→F₂ a + bool→F₂ b
bool→F₂-xor true  true  = refl
bool→F₂-xor true  false = refl
bool→F₂-xor false true  = refl
bool→F₂-xor false false = refl

-- THE APEX:  OR = recon(XOR, AND) = a ⊕ b ⊕ (a ∧ b). Bool ∨ IS the F₂ field XOR reconstructed
-- by the ∧ cross-term (the oriented residue r in  recon q b r = q·b + r) — the wedge, not a new
-- primitive. (_+_ is infixl 6, _·_ infixl 7, so the RHS is ((a+b) + (a·b)).)
∨-as-xor-recon : (a b : Bool)
               → bool→F₂ (a ∨ b) ≡ (bool→F₂ a + bool→F₂ b) + (bool→F₂ a · bool→F₂ b)
∨-as-xor-recon true  true  = refl
∨-as-xor-recon true  false = refl
∨-as-xor-recon false true  = refl
∨-as-xor-recon false false = refl
