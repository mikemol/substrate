------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Core
--
-- The lemmas that complete the Coxeter framework:
--   * power-canonical-bounded: normalize is identity on bounded power
--   * canonical-is-fixed (via canonical-cover-ex + the bounded lemma)
--   * iter / iter-insert-pos / insert-cycle-id-word
--   * normalize-power-prepend
--   * insert-append-lemma
--   * Opens WithLemmas — final layer giving _·_, _≈_, normalize-distrib, etc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _<?_; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r; <-irrefl)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties using (toℕ-bound)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Foundation.Fin.Iterate
  using (σ-iterate)

module Substrate.Groups.Coxeter.Cyclic.Core (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Bridge n using (insert-power-advance; insert-power-eq; not-lt-eq-n; insert-power-wrap)
open import Substrate.Groups.Coxeter.Cyclic.Base n using (power; insert; a; Gen; σ; c-here; σ-HasOrderPerm)
open import Substrate.Groups.Coxeter.Cyclic.Existential n

------------------------------------------------------------------------
-- power-canonical-bounded: normalize fixes power words within bound.
------------------------------------------------------------------------

power-canonical-bounded : (k : ℕ) → k < suc n → normalize (power k) ≡ power k
power-canonical-bounded zero    _         = refl
power-canonical-bounded (suc k) (s≤s k<n) =
  trans (cong (insert a) (power-canonical-bounded k (≤-suc-r k<n)))
        (insert-power-advance k k<n)

------------------------------------------------------------------------
-- canonical-is-fixed for the existential view.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical-ex w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover-ex (λ {w} _ → normalize w ≡ w)
    (λ k → power-canonical-bounded (toℕ k) (toℕ-bound k))

------------------------------------------------------------------------
-- iter / iter-insert-pos / insert-cycle-id-word — the Word-level
-- cycle property derived from σ-HasOrderPerm via insert-power-eq.
------------------------------------------------------------------------

iter : ℕ → (Word Gen → Word Gen) → Word Gen → Word Gen
iter zero    f x = x
iter (suc m) f x = f (iter m f x)

private
  iter-insert-pos : (m : ℕ) (k : Fin (suc n)) →
                    iter m (insert a) (power (toℕ k)) ≡ power (toℕ (σ-iterate m σ k))
  iter-insert-pos zero    k = refl
  iter-insert-pos (suc m) k =
    trans (cong (insert a) (iter-insert-pos m k))
          (insert-power-eq (σ-iterate m σ k))

insert-cycle-id-word : ∀ {w} → Canonical-ex w → iter (suc n) (insert a) w ≡ w
insert-cycle-id-word (k , c-here .k) =
  trans (iter-insert-pos (suc n) k)
        (cong (λ k' → power (toℕ k')) (σ-HasOrderPerm k))

------------------------------------------------------------------------
-- normalize-power-prepend: normalize (power k ++ w₂) ≡ iter k (insert a) (normalize w₂).
------------------------------------------------------------------------

normalize-power-prepend : (k : ℕ) (w₂ : Word Gen) →
                         normalize (power k ++ w₂) ≡ iter k (insert a) (normalize w₂)
normalize-power-prepend zero    w₂ = refl
normalize-power-prepend (suc k) w₂ = cong (insert a) (normalize-power-prepend k w₂)

------------------------------------------------------------------------
-- insert-append-lemma: case-split on whether k is the last position.
------------------------------------------------------------------------

insert-append-lemma : (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical-ex w →
                     normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))

open WithLemmas canonical-is-fixed insert-append-lemma public
insert-append-lemma a w₂ (k , c-here .k) with toℕ k <? n
... | yes p
  rewrite insert-power-advance (toℕ k) p
  = refl
... | no ¬p
  rewrite not-lt-eq-n k ¬p
        | insert-power-wrap
        | normalize-power-prepend n w₂
  = sym (insert-cycle-id-word (normalize-canonical w₂))

------------------------------------------------------------------------
-- Open WithLemmas to inherit the abstract Core surface
-- (_·_, _≈_, ε, normalize-distrib, etc.).
------------------------------------------------------------------------

