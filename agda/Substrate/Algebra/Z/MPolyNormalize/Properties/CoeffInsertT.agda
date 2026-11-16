------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffInsertT
--
-- Defines: coeff-insertT
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffInsertT where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.List
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Properties.Add
open import Substrate.Algebra.Z.JacobianResidue
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Z.MPolyNormalize
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.MPolyNormalize.Properties.EqMSound
open import Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToNeq
open import Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffCons
open import Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffConsNZ



coeff-insertT : (j m : Mono) (k : ℤ) (p : MPoly) →
                coeff j (insertT m k p) ≡ coeff j (term m k ∷ p)
coeff-insertT j m k [] = coeff-consNZ j m k []
coeff-insertT j m k (term n d ∷ p) with triM m n
... | ltM _ = coeff-consNZ j m k (term n d ∷ p)
... | eqM≡ refl =
      trans (coeff-consNZ j m (k +ℤ d) p)
      (trans (coeff-cons j m (k +ℤ d) p)
      (trans mid (sym (coeff-cons j m k (term m d ∷ p)))))
  where
    mid : Bcase (eqM j m) ((k +ℤ d) +ℤ coeff j p) (coeff j p)
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term m d ∷ p)) (coeff j (term m d ∷ p))
    mid rewrite coeff-cons j m d p with eqM j m
    ... | tt = +ℤ-assoc k d (coeff j p)
    ... | ff = refl
coeff-insertT j m k (term n d ∷ p) | gtM n<m =
      trans (coeff-cons j n d (insertT m k p))
      (trans mid
             (sym (coeff-cons j m k (term n d ∷ p))))
  where
    m≢n : ¬ (m ≡ n)
    m≢n e = <M→≢ n<m (sym e)
    mid : Bcase (eqM j n) (d +ℤ coeff j (insertT m k p)) (coeff j (insertT m k p))
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term n d ∷ p))  (coeff j (term n d ∷ p))
    mid rewrite coeff-insertT j m k p | coeff-cons j m k p | coeff-cons j n d p
              with eqM j m in ejm | eqM j n in ejn
    ... | tt | tt = ⊥-elim (m≢n (trans (sym (eqM-sound {j} {m} ejm)) (eqM-sound {j} {n} ejn)))
    ... | tt | ff = refl
    ... | ff | tt = refl
    ... | ff | ff = refl
