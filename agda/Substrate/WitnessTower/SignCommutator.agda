------------------------------------------------------------------------
-- Substrate.WitnessTower.SignCommutator
--
-- ◆ip-abel-easy — the EASY containment [Sₙ,Sₙ] ⊆ Aₙ: every commutator is
-- EVEN (sign false). This is one direction of the sign-abelianisation
-- terminality (SignAbelianization): the sign KILLS commutators, so it
-- factors through Sₙ^ab. The HARD direction (Aₙ ⊆ [Sₙ,Sₙ], every even perm
-- a product of commutators) is the CoxGen-native crux ◆ip-hard-A*.
--
-- The Perm INVERSE is NOT unbuilt (the SnGroup:21 note is stale): it is the
-- two-sided `Iso` witness `IsPerm→Iso σ pf`
-- (OrientationRigCatSym), and its round-trips are the projections. So:
--
--   · inverse σ pf         = proj₁ (IsPerm→Iso σ pf)            — the inverse vector
--   · inverse-right / left = the two round-trips (projections)
--   · inverse-is-perm      = left-inv→isperm on the right round-trip
--   · sign-inv             : sign (inverse σ) ≡ sign σ         — sign is inversion-invariant
--   · commutator           = (a·b)·(a⁻¹·b⁻¹)
--   · commutator-even      : sign [a,b] ≡ false                — THE deliverable
--
-- sign-inv is the sign homomorphism applied to σ·σ⁻¹ = id, cancelled in Z/2
-- (sign σ xor sign σ⁻¹ = false ⟹ sign σ⁻¹ = sign σ). commutator-even then
-- collapses (sa xor sb) xor (sa xor sb) = false (xor-same), reusing sign-inv
-- for the two inverses. Nothing new is proven about permutations — this is
-- the inverse (Iso) + the sign homomorphism, assembled.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignCommutator where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; false; _xor_)
open import Substrate.Foundation.Bool.Properties
  using (xor-identityˡ; xor-identityʳ; xor-same; xor-assoc)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.SnGroup using (compose-is-perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym
  using (IsPerm→Iso; left-inv→isperm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; sign-id; sign-hom)

------------------------------------------------------------------------
-- 1. THE PERM INVERSE — the Iso witness, projected. (SnGroup:21's "inverse
--    unbuilt" note is stale: IsPerm→Iso IS it, both round-trips proven.)
------------------------------------------------------------------------

inverse : {n : ℕ} (σ : Perm n) → IsPerm σ → Perm n
inverse σ pf = proj₁ (IsPerm→Iso σ pf)

inverse-right : {n : ℕ} (σ : Perm n) (pf : IsPerm σ) →
                compose σ (inverse σ pf) ≡ id-perm n
inverse-right σ pf = proj₁ (proj₂ (IsPerm→Iso σ pf))

inverse-left : {n : ℕ} (σ : Perm n) (pf : IsPerm σ) →
               compose (inverse σ pf) σ ≡ id-perm n
inverse-left σ pf = proj₂ (proj₂ (IsPerm→Iso σ pf))

inverse-is-perm : {n : ℕ} (σ : Perm n) (pf : IsPerm σ) → IsPerm (inverse σ pf)
inverse-is-perm σ pf = left-inv→isperm σ (inverse σ pf) (inverse-right σ pf)

------------------------------------------------------------------------
-- 2. sign is INVERSION-INVARIANT: sign σ⁻¹ = sign σ. From sign-hom on
--    σ·σ⁻¹ = id and the Z/2 cancellation a xor b = false ⟹ b = a.
------------------------------------------------------------------------

sign-inv : {n : ℕ} (σ : Perm n) (pf : IsPerm σ) → sign (inverse σ pf) ≡ sign σ
sign-inv {n} σ pf =
  trans (sym (xor-identityˡ b))
    (trans (cong (λ z → z xor b) (sym (xor-same a)))
      (trans (xor-assoc a a b)
        (trans (cong (λ z → a xor z) e0)
               (xor-identityʳ a))))
  where
    a = sign σ
    b = sign (inverse σ pf)
    e0 : (a xor b) ≡ false
    e0 = trans (sym (sign-hom σ (inverse σ pf) pf (inverse-is-perm σ pf)))
               (trans (cong sign (inverse-right σ pf)) (sign-id {n}))

------------------------------------------------------------------------
-- 3. THE COMMUTATOR and its evenness. [a,b] = (a·b)·(a⁻¹·b⁻¹).
------------------------------------------------------------------------

commutator : {n : ℕ} (a b : Perm n) → IsPerm a → IsPerm b → Perm n
commutator a b pa pb =
  compose (compose a b) (compose (inverse a pa) (inverse b pb))

commutator-is-perm : {n : ℕ} (a b : Perm n) (pa : IsPerm a) (pb : IsPerm b) →
                     IsPerm (commutator a b pa pb)
commutator-is-perm a b pa pb =
  compose-is-perm (compose a b) (compose (inverse a pa) (inverse b pb))
    (compose-is-perm a b pa pb)
    (compose-is-perm (inverse a pa) (inverse b pb)
                     (inverse-is-perm a pa) (inverse-is-perm b pb))

-- THE DELIVERABLE: every commutator is even ([Sₙ,Sₙ] ⊆ Aₙ at the generator).
commutator-even : {n : ℕ} (a b : Perm n) (pa : IsPerm a) (pb : IsPerm b) →
                  sign (commutator a b pa pb) ≡ false
commutator-even a b pa pb =
  trans (sign-hom (compose a b) (compose (inverse a pa) (inverse b pb))
           (compose-is-perm a b pa pb)
           (compose-is-perm (inverse a pa) (inverse b pb)
                            (inverse-is-perm a pa) (inverse-is-perm b pb)))
    (trans (cong₂ _xor_
              (sign-hom a b pa pb)
              (trans (sign-hom (inverse a pa) (inverse b pb)
                               (inverse-is-perm a pa) (inverse-is-perm b pb))
                     (cong₂ _xor_ (sign-inv a pa) (sign-inv b pb))))
           (xor-same (sign a xor sign b)))
