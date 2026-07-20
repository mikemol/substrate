------------------------------------------------------------------------
-- Substrate.WitnessTower.CommutatorSubgroup
--
-- ◆ip-comm-subgroup — the commutator subgroup [Sₙ,Sₙ] as an inductive family
-- over Perm n, and its containment in Aₙ (the even permutations): the FIRST
-- brick of ◆ip-abel-cap.
--
--   data InComm  — the derived subgroup: id, every commutator [a,b],
--                  closed under compose (finite ⇒ inverse-free, like CoxGen)
--   InComm→isperm — every member is a genuine permutation
--   InComm→even  — every member is EVEN (sign ≡ false)  = [Sₙ,Sₙ] ⊆ Aₙ
--
-- InComm→even lifts SignCommutator.commutator-even from a SINGLE commutator to
-- the whole SUBGROUP (a fold: id even by sign-id, commutators even by
-- commutator-even, products even by sign-hom + false xor false = false). This
-- is the EASY containment as a genuine subgroup statement.
--
-- The REVERSE containment Aₙ ⊆ [Sₙ,Sₙ] (even→InComm — every even perm is a
-- product of commutators) is the deep half: it routes through α-Sₙ
-- (SignGrade2Generated: even ⟹ grade-2-generated) + a per-pair classification
-- whose disjoint double-transposition case is the one genuinely-new hard proof;
-- the categorical Sₙ^ab ≅ Z/2 iso is a further separate infra layer. Neither is
-- this module (◆ip-cap-reverse / ◆ip-cap-categorical).
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CommutatorSubgroup where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; trans; cong₂)
open import Substrate.Foundation.Bool using (Bool; false; _xor_)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.SnGroup using (compose-is-perm)
open import Substrate.WitnessTower.SignCommutator
  using (commutator; commutator-is-perm; commutator-even)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; sign-id; sign-hom; id-perm-is-perm)

------------------------------------------------------------------------
-- 1. THE COMMUTATOR SUBGROUP as an inductive family (mirrors CoxGen/BraidGen).
------------------------------------------------------------------------

data InComm : {n : ℕ} → Perm n → Set where
  ic-id   : {n : ℕ} → InComm (id-perm n)
  ic-comm : {n : ℕ} (a b : Perm n) (pa : IsPerm a) (pb : IsPerm b) →
            InComm (commutator a b pa pb)
  ic-∘    : {n : ℕ} {σ τ : Perm n} → InComm σ → InComm τ → InComm (compose σ τ)

------------------------------------------------------------------------
-- 2. Every member is a permutation.
------------------------------------------------------------------------

InComm→isperm : {n : ℕ} {σ : Perm n} → InComm σ → IsPerm σ
InComm→isperm {n} ic-id            = id-perm-is-perm {n}
InComm→isperm (ic-comm a b pa pb)  = commutator-is-perm a b pa pb
InComm→isperm (ic-∘ {σ = σ} {τ} x y) =
  compose-is-perm σ τ (InComm→isperm x) (InComm→isperm y)

------------------------------------------------------------------------
-- 3. [Sₙ,Sₙ] ⊆ Aₙ — every member of the commutator subgroup is EVEN.
------------------------------------------------------------------------

InComm→even : {n : ℕ} {σ : Perm n} → InComm σ → sign σ ≡ false
InComm→even {n} ic-id           = sign-id {n}
InComm→even (ic-comm a b pa pb) = commutator-even a b pa pb
InComm→even (ic-∘ {σ = σ} {τ} x y) =
  trans (sign-hom σ τ (InComm→isperm x) (InComm→isperm y))
        (cong₂ _xor_ (InComm→even x) (InComm→even y))
