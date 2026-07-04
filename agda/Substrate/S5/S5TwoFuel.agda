{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5TwoFuel: the two fuels as TWO FOLDS OF ONE KEPT TRACE.
--
-- Extends S5Verdict. Disciplines carried forward:
--   * no absurdity pattern; every arm returns; ε retained everywhere.
--   * one trace, many folds (EEAFoldTable): the runner KEEPS its trace
--     (the states stepped through); traversal-fuel and calculation-fuel
--     are two catamorphisms over that one list —
--         traversal   = length
--         calculation = length ∘ dedupe
--     and calc ≤ trav holds for ANY boolean "equality" (even a wrong
--     one): filtering never lengthens. With a correct eqb, dedupe-length
--     is exactly the distinct-classes count (memo misses from cold).
--   * ε's TWO HATS, related and never identified:
--       unit hat  — the zero window is the unit of BOTH monoids in
--                   sight (fuel-sum and trace-append), and runTrace is
--                   a morphism between them (traces concatenate under
--                   window composition: T-compose below);
--       nilpotent hat — an unresolved suspension is a graded
--                   obstruction; Resolves is upward-closed in fuel
--                   ("dies at power n ⟹ dead at every higher power"),
--                   a one-line corollary of L1, the stability law of
--                   nilpotency proved rather than imposed.
------------------------------------------------------------------------

module Substrate.S5.S5TwoFuel where

open import Substrate.S5.S5Verdict
open import Substrate.Foundation.Bool    using (Bool; true; false)
open import Substrate.Foundation.Product using (Σ; _×_; _,_) renaming (proj₁ to fst; proj₂ to snd)
open import Substrate.Foundation.List    using (_++_)
open import Substrate.Foundation.Nat     using (_≤_; z≤n; s≤s)

length : {A : Set} → List A → ℕ
length []       = zero
length (x ∷ xs) = suc (length xs)

≤-up : ∀ {m n} → m ≤ n → m ≤ suc n
≤-up z≤n       = z≤n
≤-up (s≤s le)  = s≤s (≤-up le)

-- dedupe: keep first occurrences, judged by an arbitrary boolean eqb ----

module Dedupe {A : Set} (eqb : A → A → Bool) where

  member : A → List A → Bool
  member a []       = false
  member a (x ∷ xs) = memb (eqb a x)
    where
      memb : Bool → Bool
      memb true  = true
      memb false = member a xs

  go     : List A → List A → List A
  branch : List A → A → List A → Bool → List A

  go seen []       = []
  go seen (x ∷ xs) = branch seen x xs (member x seen)

  branch seen x xs true  = go seen xs
  branch seen x xs false = x ∷ go (x ∷ seen) xs

  dedupe : List A → List A
  dedupe = go []

  -- calc ≤ trav, for ANY eqb: filtering never lengthens.
  go-≤     : ∀ (seen : List A) (xs : List A) → length (go seen xs) ≤ length xs
  branch-≤ : ∀ (seen : List A) (x : A) (xs : List A) (b : Bool)
           → length (branch seen x xs b) ≤ suc (length xs)

  go-≤ seen []       = z≤n
  go-≤ seen (x ∷ xs) = branch-≤ seen x xs (member x seen)

  branch-≤ seen x xs true  = ≤-up (go-≤ seen xs)
  branch-≤ seen x xs false = s≤s (go-≤ (x ∷ seen) xs)

  dedupe-≤ : ∀ (xs : List A) → length (dedupe xs) ≤ length xs
  dedupe-≤ = go-≤ []

-- the trace-keeping runner ----------------------------------------------

module TwoFuel (S : Set) (next : S → Progress S) (eqb : S → S → Bool) where

  module M = Machine S next
  open Dedupe {S} eqb using (dedupe; dedupe-≤)

  -- the runner keeps its trace: the states ARRIVED AT by real steps.
  -- ε-window: zero steps, empty trace — [] is the unit of ++ as zero is
  -- the unit of +; the two unit hats, side by side.
  handleT : ℕ → Progress S → Verdict S × List S
  runT    : ℕ → S → Verdict S × List S

  runT zero    s = (suspended s , [])
  runT (suc n) s = handleT n (next s)

  consT : S → Verdict S × List S → Verdict S × List S
  consT s (v , t) = (v , s ∷ t)

  handleT n (final v)    = (value v , [])
  handleT n (stepped s') = consT s' (runT n s')

  -- projections: the two fuels, as folds of the ONE kept trace
  trace : ℕ → S → List S
  trace n s = snd (runT n s)

  trav : ℕ → S → ℕ
  trav n s = length (trace n s)

  calc : ℕ → S → ℕ
  calc n s = length (dedupe (trace n s))

  -- L3, machine-checked, for any eqb whatsoever
  calc≤trav : ∀ (n : ℕ) (s : S) → calc n s ≤ trav n s
  calc≤trav n s = dedupe-≤ (trace n s)

  -- the verdict component agrees with the plain machine ------------------
  verdict-agrees : ∀ (n : ℕ) (s : S) → fst (runT n s) ≡ M.run n s
  handle-agrees  : ∀ (n : ℕ) (p : Progress S)
                 → fst (handleT n p) ≡ M.handle n p

  verdict-agrees zero    s = refl
  verdict-agrees (suc n) s = handle-agrees n (next s)

  handle-agrees n (final v)    = refl
  handle-agrees n (stepped s') = verdict-agrees n s'

  ----------------------------------------------------------------------
  -- T-compose: traces CONCATENATE under window composition — runT is a
  -- monoid morphism from (fuel, +, zero) to (traces, ++, []).
  -- The ε-window is the unit on BOTH sides; the base case of the
  -- induction is, once again, ε.
  ----------------------------------------------------------------------

  resumeT : ℕ → Verdict S × List S → Verdict S × List S
  resumeT m (value v     , t) = (value v , t)
  resumeT m (suspended s , t) = attach t (runT m s)
    where
      attach : List S → Verdict S × List S → Verdict S × List S
      attach t (v , t') = (v , t ++ t')

  -- resumption commutes with prefixing an emission
  resumeT-consT : ∀ (m : ℕ) (s : S) (p : Verdict S × List S)
                → resumeT m (consT s p) ≡ consT s (resumeT m p)
  resumeT-consT m s (value v     , t) = refl
  resumeT-consT m s (suspended u , t) = refl

  T-compose      : ∀ (m n : ℕ) (s : S)
                 → resumeT m (runT n s) ≡ runT (n + m) s
  T-compose-hand : ∀ (m n : ℕ) (p : Progress S)
                 → resumeT m (handleT n p) ≡ handleT (n + m) p

  T-compose m zero    s = refl                          -- ε, the unit
  T-compose m (suc n) s = T-compose-hand m n (next s)

  T-compose-hand m n (final v)    = refl
  T-compose-hand m n (stepped s') =
    trans (resumeT-consT m s' (runT n s'))
          (cong (consT s') (T-compose m n s'))

  ----------------------------------------------------------------------
  -- ε's NILPOTENT hat: resolution degree, and its stability law.
  -- Resolves n s: the obstruction carried by s dies at power n.
  -- Upward closure — dead at n ⟹ dead at n + m — is nilpotency's
  -- defining stability, here a corollary of L1 (value-monotone),
  -- proved in one line, no case analysis, no absurdity.
  ----------------------------------------------------------------------

  Resolves : ℕ → S → Set
  Resolves n s = Σ S (λ v → M.run n s ≡ value v)

  resolves-up : ∀ (m n : ℕ) (s : S) → Resolves n s → Resolves (n + m) s
  resolves-up m n s (v , eq) = (v , M.value-monotone m n s v eq)
