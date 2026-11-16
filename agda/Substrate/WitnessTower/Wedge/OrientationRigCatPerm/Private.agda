------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private
--
-- Defines: Braid, B⊕, B⊗
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Vec.Properties.LookupComptabulate
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationSumComm
open import Substrate.WitnessTower.Wedge.OrientationProductComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstSymL
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFinUip
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LookupSubst



------------------------------------------------------------------------
-- S2 — THE BRAIDINGS. Generic over the grading (op, comm) and its Fin-level
-- swap (sw, sw-invol): blockSwap over (ℕ+) and factorSwap over (*) are ONE
-- structure. The braiding MORPHISM is the swap made a single-grade Perm
-- endomorphism (tabulate ∘ sw ∘ reindex); its involution is the swap's own
-- order-2 law, discharged pointwise through SnGroup faithfulness.
------------------------------------------------------------------------

module Braid
  (op : ℕ → ℕ → ℕ)
  (comm : (a b : ℕ) → op a b ≡ op b a)
  (sw : (m n : ℕ) → Fin (op m n) → Fin (op n m))
  (sw-invol : (m n : ℕ) (k : Fin (op m n)) → sw n m (sw m n k) ≡ k)
  where

  -- the braiding permutation at grades (i,j): a genuine endo of Fin (op j i).
  swPerm : (i j : ℕ) → Perm (op j i)
  swPerm i j = tabulate (λ k → sw i j (subst Fin (comm j i) k))

  private
    -- readout of swPerm at the swapped grade.
    lookup-swPerm : (i j : ℕ) (y : Fin (op i j)) →
                    lookup (swPerm j i) y ≡ sw j i (subst Fin (comm i j) y)
    lookup-swPerm i j y = lookup∘tabulate (λ k → sw j i (subst Fin (comm i j) k)) y

    -- readout of the transported braiding (the second composition factor).
    lookup-γ : (i j : ℕ) (x : Fin (op i j)) →
               lookup (subst Perm (comm j i) (swPerm i j)) x
               ≡ subst Fin (comm j i) (sw i j x)
    lookup-γ i j x =
      trans (lookup-subst (comm j i) (swPerm i j) x)
            (cong (subst Fin (comm j i))
                  (trans (lookup∘tabulate (λ k → sw i j (subst Fin (comm j i) k))
                                          (subst Fin (sym (comm j i)) x))
                         (cong (sw i j) (subst-symˡ (comm j i) x))))

  -- THE INVOLUTION (perm component): swap-then-swap = identity, pointwise.
  swPerm-invol : (i j : ℕ) →
                 compose (swPerm j i) (subst Perm (comm j i) (swPerm i j))
                 ≡ id-perm (op i j)
  swPerm-invol i j = apply-injective (λ x →
    trans (apply-compose (swPerm j i) (subst Perm (comm j i) (swPerm i j)) x)
    (trans (cong (lookup (swPerm j i)) (lookup-γ i j x))
    (trans (lookup-swPerm i j (subst Fin (comm j i) (sw i j x)))
    (trans (cong (sw j i) (subst-fuse Fin (comm j i) (comm i j) (sw i j x)))
    (trans (cong (sw j i) (subst-Fin-uip (trans (comm j i) (comm i j)) (sw i j x)))
    (trans (sw-invol i j x)
           (sym (apply-id x))))))))

module B⊕ = Braid _ℕ+_ +ℕ-comm blockSwap blockSwap-invol
module B⊗ = Braid _*_ *-comm factorSwap factorSwap-invol
