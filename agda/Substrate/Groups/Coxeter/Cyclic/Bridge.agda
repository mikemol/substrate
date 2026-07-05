------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge
--
-- The algebraic bridge between insert (length-check) and σ (mod-suc).
-- Provides insert-power-eq + insert-canonical (Fin-indexed) + the
-- per-case helpers (insert-power-advance / insert-power-wrap) for
-- downstream use in Inverse + Core.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r; <-irrefl)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; suc-mod-suc-lt; suc-mod-suc-self)
open import Substrate.Algebra.Nat.CyclicSuc
  using (cyclic-suc; cyclic-suc-toℕ)

module Substrate.Groups.Coxeter.Cyclic.Bridge (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n public

------------------------------------------------------------------------
-- For k : Fin (suc n) where ¬ (toℕ k < n), toℕ k must equal n.
------------------------------------------------------------------------

private
  not-lt-aux : (x y : ℕ) → x < suc y → ¬ (x < y) → x ≡ y
  not-lt-aux zero    zero    _              _      = refl
  not-lt-aux zero    (suc y) _              ¬0<sy  = ⊥-elim (¬0<sy (s≤s z≤n))
  not-lt-aux (suc x) zero    (s≤s ())       _
  not-lt-aux (suc x) (suc y) (s≤s x<sy)     ¬sx<sy = cong suc
    (not-lt-aux x y x<sy (λ x<y → ¬sx<sy (s≤s x<y)))

not-lt-eq-n : (k : Fin (suc n)) → ¬ (toℕ k < n) → toℕ k ≡ n
not-lt-eq-n k ¬k<n = not-lt-aux (toℕ k) n (toℕ-bound k) ¬k<n

------------------------------------------------------------------------
-- Bridge: insert a (power (toℕ k)) ≡ power (toℕ (σ k)).
------------------------------------------------------------------------

private
  insert-power-eq-yes : (k : Fin (suc n)) → toℕ k < n →
                        insert a (power (toℕ k)) ≡ power (toℕ (σ k))
  insert-power-eq-yes k k<n
    rewrite cyclic-suc-toℕ k
          | suc-mod-suc-lt (toℕ k) n k<n
    with length (power (toℕ k)) <? n | length-power (toℕ k)
  ... | yes _  | _     = refl
  ... | no  ¬p | l≡tk  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡tk) k<n))

  insert-power-eq-no : (k : Fin (suc n)) → ¬ (toℕ k < n) →
                       insert a (power (toℕ k)) ≡ power (toℕ (σ k))
  insert-power-eq-no k ¬k<n
    rewrite cyclic-suc-toℕ k
          | not-lt-eq-n k ¬k<n
          | suc-mod-suc-self n
    with length (power n) <? n | length-power n
  ... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
  ... | no  _  | _    = refl

insert-power-eq : (k : Fin (suc n)) →
                  insert a (power (toℕ k)) ≡ power (toℕ (σ k))
insert-power-eq k with toℕ k <? n
... | yes p  = insert-power-eq-yes k p
... | no  ¬p = insert-power-eq-no k ¬p

------------------------------------------------------------------------
-- insert-canonical at the Fin-indexed level.
------------------------------------------------------------------------

insert-canonical : (g : Gen) {w : Word Gen} {k : Fin (suc n)} →
                   Canonical w k → Canonical (insert g w) (σ k)
insert-canonical a (c-here k) =
  subst (λ w → Canonical w (σ k)) (sym (insert-power-eq k)) (c-here (σ k))

------------------------------------------------------------------------
-- Per-case insert helpers (used by Core for power-canonical-bounded
-- and insert-append-lemma).
------------------------------------------------------------------------

insert-power-advance : (k : ℕ) → k < n → insert a (power k) ≡ a ∷ power k
insert-power-advance k k<n
  with length (power k) <? n | length-power k
... | yes _  | _    = refl
... | no  ¬p | l≡k  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡k) k<n))

insert-power-wrap : insert a (power n) ≡ []
insert-power-wrap
  with length (power n) <? n | length-power n
... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
... | no  _  | _    = refl
