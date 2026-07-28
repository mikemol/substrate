------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Punctured
--
-- The punctured-finite-set bijection  Fin (suc n) ∖ {k} ≅ Fin n.
--
-- This is the reusable substructure behind every hand-enumerated
-- "skip one element" finite bijection in the substrate (Stab-S3's
-- anchor-skipping Axis↔Fin 3 bridge; the Axes v-of-axis/axis-of-v
-- torsor; the per-Zₙ Fin index work).  The two halves are the standard
-- `punchIn` / `punchOut` of finite combinatorics:
--
--   punchIn  k : Fin n → Fin (suc n)      -- insert, skipping slot k
--   punchOut   : i ≢ k → Fin n            -- remove slot k (given i ≠ k)
--
-- punchIn k is the injection whose image is exactly Fin (suc n) ∖ {k};
-- punchOut is its inverse on that complement.  Together they witness
-- the bijection.  No decidable equality is needed: the "i = k" case of
-- punchOut is genuinely impossible and is discharged by ⊥-elim against
-- the supplied i ≢ k.
--
-- Carrier-generic; --safe --without-K; zero postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Punctured where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Sucinjective

private
  variable
    n : ℕ

------------------------------------------------------------------------
-- 1. punchIn k : Fin n ↪ Fin (suc n) — insert, skipping slot k.
--
-- punchIn zero    j = suc j           (skip the first slot)
-- punchIn (suc k) zero    = zero      (keep the first slot)
-- punchIn (suc k) (suc j) = suc (punchIn k j)
------------------------------------------------------------------------

punchIn : Fin (suc n) → Fin n → Fin (suc n)
punchIn zero    j       = suc j
punchIn (suc k) zero    = zero
punchIn {suc _} (suc k) (suc j) = suc (punchIn k j)

------------------------------------------------------------------------
-- 2. punchIn never hits k: punchIn k j ≢ k.  (The image avoids k.)
------------------------------------------------------------------------

punchIn-≢ : (k : Fin (suc n)) (j : Fin n) → ¬ (punchIn k j ≡ k)
punchIn-≢ zero    j       ()
punchIn-≢ (suc k) zero    ()
punchIn-≢ {suc _} (suc k) (suc j) eq =
  punchIn-≢ k j (fin-suc-injective eq)

------------------------------------------------------------------------
-- 3. punchOut : i ≢ k → Fin n — remove slot k (given i ≠ k).
--
-- The i = k case is impossible and discharged by ⊥-elim.
------------------------------------------------------------------------

punchOut : {k i : Fin (suc n)} → ¬ (i ≡ k) → Fin n
punchOut {n}     {zero}   {zero}  i≢k = ⊥-elim (i≢k refl)
punchOut {suc _} {zero}   {suc i} _   = i
punchOut {suc _} {suc k}  {zero}  _   = zero
punchOut {suc _} {suc k}  {suc i} i≢k =
  suc (punchOut {k = k} {i = i} (λ e → i≢k (cong suc e)))

------------------------------------------------------------------------
-- 3b. punchOut is proof-irrelevant: its value does not depend on WHICH
-- disequality witness is supplied.  (Companion lemma; also the honest
-- statement that the bijection is canonical, not proof-sensitive.)
------------------------------------------------------------------------

punchOut-irrelevant :
  {k i : Fin (suc n)} (p q : ¬ (i ≡ k)) →
  punchOut {k = k} {i = i} p ≡ punchOut {k = k} {i = i} q
punchOut-irrelevant {n}     {zero}  {zero}  p q = ⊥-elim (p refl)
punchOut-irrelevant {suc _} {zero}  {suc i} p q = refl
punchOut-irrelevant {suc _} {suc k} {zero}  p q = refl
punchOut-irrelevant {suc _} {suc k} {suc i} p q =
  cong suc (punchOut-irrelevant {k = k} {i = i}
              (λ e → p (cong suc e)) (λ e → q (cong suc e)))

-- punchOut respects a path in its index i (transport companion of
-- punchOut-irrelevant; needed whenever the index is only propositionally,
-- not definitionally, in the expected form — e.g. after a carrier
-- bijection transport).
punchOut-cong :
  {k i i′ : Fin (suc n)} (eq : i ≡ i′)
  (p : ¬ (i ≡ k)) (p′ : ¬ (i′ ≡ k)) →
  punchOut {k = k} {i = i} p ≡ punchOut {k = k} {i = i′} p′
punchOut-cong refl p p′ = punchOut-irrelevant p p′

------------------------------------------------------------------------
-- 4. Round-trip A:  punchOut ∘ punchIn = id  on Fin n.
--
-- Removing slot k after inserting at-skip-k returns the original index.
-- (punchIn k j ≢ k holds by punchIn-≢, so punchOut applies.)
------------------------------------------------------------------------

punchOut-punchIn :
  (k : Fin (suc n)) (j : Fin n) →
  punchOut {k = k} {i = punchIn k j} (punchIn-≢ k j) ≡ j
punchOut-punchIn zero    zero    = refl
punchOut-punchIn zero    (suc j) = refl
punchOut-punchIn (suc k) zero    = refl
punchOut-punchIn (suc k) (suc j) =
  cong suc (trans (punchOut-irrelevant _ (punchIn-≢ k j))
                  (punchOut-punchIn k j))

------------------------------------------------------------------------
-- 5. Round-trip B:  punchIn ∘ punchOut = id  on Fin (suc n) ∖ {k}.
--
-- Re-inserting at-skip-k the index obtained by removing slot k returns
-- the original i (for any i ≢ k).
------------------------------------------------------------------------

punchIn-punchOut :
  {k i : Fin (suc n)} (i≢k : ¬ (i ≡ k)) →
  punchIn k (punchOut {k = k} {i = i} i≢k) ≡ i
punchIn-punchOut {n}     {zero}   {zero}  i≢k = ⊥-elim (i≢k refl)
punchIn-punchOut {suc _} {zero}   {suc i} _   = refl
punchIn-punchOut {suc _} {suc k}  {zero}  _   = refl
punchIn-punchOut {suc _} {suc k}  {suc i} i≢k =
  cong suc (punchIn-punchOut {k = k} {i = i} (λ e → i≢k (cong suc e)))
