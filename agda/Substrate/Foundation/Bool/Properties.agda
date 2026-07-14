------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties
--
-- Substrate-native Bool properties. Replaces stdlib Data.Bool.Properties
-- for the xor lemmas used downstream (F₂³ group, F₂ structures).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties where

open import Substrate.Foundation.Bool using (Bool; true; false; _xor_; _∧_; _∨_; not)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- ⟡A5: the ANF-of-OR (OR = XOR ⊕ AND at the Bool level) — the canonical foundational home for the
-- identity, read by CayleyDickson/Grade (∨-anf) and Algebra.F2.FromBool (∨-as-xor-recon derives from it).
or-xor-and : (a b : Bool) → (a ∨ b) ≡ (a xor b) xor (a ∧ b)
or-xor-and true  true  = refl
or-xor-and true  false = refl
or-xor-and false true  = refl
or-xor-and false false = refl

------------------------------------------------------------------------
-- xor lemmas (case-analytical proofs).
------------------------------------------------------------------------

xor-identityˡ : (b : Bool) → false xor b ≡ b
xor-identityˡ true  = refl
xor-identityˡ false = refl

xor-identityʳ : (b : Bool) → b xor false ≡ b
xor-identityʳ true  = refl
xor-identityʳ false = refl

xor-same : (b : Bool) → b xor b ≡ false
xor-same true  = refl
xor-same false = refl

xor-comm : (a b : Bool) → a xor b ≡ b xor a
xor-comm true  true  = refl
xor-comm true  false = refl
xor-comm false true  = refl
xor-comm false false = refl

xor-assoc : (a b c : Bool) → (a xor b) xor c ≡ a xor (b xor c)
xor-assoc true  true  true  = refl
xor-assoc true  true  false = refl
xor-assoc true  false true  = refl
xor-assoc true  false false = refl
xor-assoc false true  true  = refl
xor-assoc false true  false = refl
xor-assoc false false true  = refl
xor-assoc false false false = refl

------------------------------------------------------------------------
-- ∧ / ∨ semilattice laws. Added for the dual-rail evidence connectives
-- (Substrate.Logic.Evidence.Verdict.Connectives), which lift each rail's
-- Bool operations; reusable for any F₂ / Boolean lattice structure.
-- `_∧_` and `_∨_` match on their first argument, so assoc and identityʳ
-- need only split that one (b, c stay free).
------------------------------------------------------------------------

∧-comm : (a b : Bool) → a ∧ b ≡ b ∧ a
∧-comm true  true  = refl
∧-comm true  false = refl
∧-comm false true  = refl
∧-comm false false = refl

∨-comm : (a b : Bool) → a ∨ b ≡ b ∨ a
∨-comm true  true  = refl
∨-comm true  false = refl
∨-comm false true  = refl
∨-comm false false = refl

∧-assoc : (a b c : Bool) → (a ∧ b) ∧ c ≡ a ∧ (b ∧ c)
∧-assoc true  b c = refl
∧-assoc false b c = refl

∨-assoc : (a b c : Bool) → (a ∨ b) ∨ c ≡ a ∨ (b ∨ c)
∨-assoc true  b c = refl
∨-assoc false b c = refl

∧-idem : (a : Bool) → a ∧ a ≡ a
∧-idem true  = refl
∧-idem false = refl

∨-idem : (a : Bool) → a ∨ a ≡ a
∨-idem true  = refl
∨-idem false = refl

∧-identityʳ : (a : Bool) → a ∧ true ≡ a
∧-identityʳ true  = refl
∧-identityʳ false = refl

∨-identityʳ : (a : Bool) → a ∨ false ≡ a
∨-identityʳ true  = refl
∨-identityʳ false = refl

-- Ⓓ: left-identity / distributivity / annihilator Bool laws, relocated here
-- from Algebra.Semiring.Instances (where they were proven "for lack of a prior
-- home"). Their carrier home is Bool's properties. The identityˡ pair also
-- completes the chirality with the identityʳ above.
∧-identityˡ : (a : Bool) → true ∧ a ≡ a
∧-identityˡ _ = refl

∨-identityˡ : (a : Bool) → false ∨ a ≡ a
∨-identityˡ _ = refl

-- ∧ distributes over ∨.
∧-distribˡ-∨ : (a b c : Bool) → a ∧ (b ∨ c) ≡ (a ∧ b) ∨ (a ∧ c)
∧-distribˡ-∨ true  _ _ = refl
∧-distribˡ-∨ false _ _ = refl

∧-distribʳ-∨ : (a b c : Bool) → (a ∨ b) ∧ c ≡ (a ∧ c) ∨ (b ∧ c)
∧-distribʳ-∨ true  true  true  = refl
∧-distribʳ-∨ true  true  false = refl
∧-distribʳ-∨ true  false true  = refl
∧-distribʳ-∨ true  false false = refl
∧-distribʳ-∨ false true  true  = refl
∧-distribʳ-∨ false true  false = refl
∧-distribʳ-∨ false false true  = refl
∧-distribʳ-∨ false false false = refl

-- false (the ∨-identity) annihilates ∧.
∧-zeroˡ : (a : Bool) → false ∧ a ≡ false
∧-zeroˡ _ = refl

∧-zeroʳ : (a : Bool) → a ∧ false ≡ false
∧-zeroʳ true  = refl
∧-zeroʳ false = refl

-- Ⓓ: ∧ reflection eliminators (a ∧ b ≡ true ⟹ each conjunct ≡ true), relocated
-- here from Realizability.Charter and …Wedge.GUnit (both re-proved them; the
-- carrier home is Bool's properties).
∧-elimˡ : {a b : Bool} → (a ∧ b) ≡ true → a ≡ true
∧-elimˡ {true}  _ = refl
∧-elimˡ {false} ()

∧-elimʳ : {a b : Bool} → (a ∧ b) ≡ true → b ≡ true
∧-elimʳ {true}  h = h
∧-elimʳ {false} ()
