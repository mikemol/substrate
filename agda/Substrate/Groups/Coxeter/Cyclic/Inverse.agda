------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse
--
-- Generic inverse: inv-pos at the Fin level, inv at the Word level
-- (via length-check + power), and inv-canonical at the Fin-indexed
-- Canonical level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _∸_; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)

module Substrate.Groups.Coxeter.Cyclic.Inverse (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Bridge n public

------------------------------------------------------------------------
-- inv-pos: the inverse position via (suc n ∸ toℕ k) mod-suc n.
------------------------------------------------------------------------

inv-pos : Fin (suc n) → Fin (suc n)
inv-pos k = fromℕ< (mod-suc-bound (suc n ∸ toℕ k) n)

------------------------------------------------------------------------
-- inv: Word-level inverse via length-check + power composition.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv w with length w <? suc n
... | yes p = power (toℕ (inv-pos (fromℕ< p)))
... | no  _ = w

------------------------------------------------------------------------
-- inv-canonical (Fin-indexed): bridged via the inv-power-eq lemma.
------------------------------------------------------------------------

private
  fromℕ<-toℕ-id : ∀ {m} (k : Fin m) (p : toℕ k < m) → fromℕ< p ≡ k
  fromℕ<-toℕ-id {suc _} zero    (s≤s _)   = refl
  fromℕ<-toℕ-id {suc _} (suc k) (s≤s p')  = cong suc (fromℕ<-toℕ-id k p')

  fromℕ<-power-toℕ : (k : Fin (suc n))
                   → (p : length (power (toℕ k)) < suc n)
                   → fromℕ< p ≡ k
  fromℕ<-power-toℕ k p
    rewrite length-power (toℕ k) = fromℕ<-toℕ-id k p

-- inv on `power (toℕ k)` reduces to `power (toℕ (inv-pos k))`. Exposed
-- so downstream proofs (InvCanonical.{Left, Right, InvInv}) can use it
-- without re-deriving the length-check + fromℕ<-roundtrip dance.
inv-power-eq : (k : Fin (suc n)) →
               inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))
inv-power-eq k with length (power (toℕ k)) <? suc n | length-power (toℕ k)
... | yes p | _    = cong (λ x → power (toℕ (inv-pos x))) (fromℕ<-power-toℕ k p)
... | no ¬p | l≡tk = ⊥-elim (¬p (subst (λ x → x < suc n) (sym l≡tk) (toℕ-bound k)))

inv-canonical : ∀ {w} {k : Fin (suc n)} → Canonical w k → Canonical (inv w) (inv-pos k)
inv-canonical (c-here k) =
  subst (λ w → Canonical w (inv-pos k)) (sym (inv-power-eq k)) (c-here (inv-pos k))
