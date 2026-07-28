------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductStructural
--
-- ⟡rig-UP-wreath (Step A) — the FOLD-TRANSPARENT structural product on Lehmer
-- paths. Unlike OrientationProductInsert's `_⊗ˡ_` (defined by TRANSPORT across
-- decode/encode — opaque to `fold`), this `_⊗ˢ_` is defined by RECURSION on the
-- first path, so `fold` reduces straight through its rungs. That is exactly what
-- the parametric fold-⊗ catamorphism needs (OrientationRigUniversal).
--
-- The construction realises "THE UNLOCK": the n block-insert digits building
-- (insert-at p σ) ⊗ τ out of σ ⊗ τ are l₂'s OWN Lehmer rungs, replayed with each
-- digit offset by p·n:
--
--     offsetDigit p n q = p·n + toℕ q            (a Fin (suc (k + m·n)), by fromℕ<)
--     replay-aux p n (l ◂ q) base = replay-aux p n l base ◂ offsetDigit p n q
--     (l₁ ◂ p) ⊗ˢ l₂ = replay-aux p n l₂ (l₁ ⊗ˢ l₂)      -- add n rungs per ◂-step
--
-- The GRADE is clean by decoupling: `replay-aux` peels a length-k FRAGMENT of l₂
-- while the base stays at the fixed grade m·n, so the accumulator grows as
-- k + m·n (k on the LEFT, matching `suc m * n = n + m * n` definitionally) — no
-- commutativity transport. The digit VALUES (p·n + toℕ q) are irrelevant to the
-- structural fold homomorphism; they are pinned only for the decode-agreement
-- (the ⊗ˢ ≡ ⊗ correctness link), which is the separate research edge.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductStructural where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _≤_; s≤s; s≤s-injective)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Order using (+-mono-≤; *-monoˡ-≤)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties using (toℕ-bound)
open import Substrate.Foundation.Eq using (_≡_; subst)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)

------------------------------------------------------------------------
-- 1. The offset digit: value p·n + toℕ q, landed in Fin (suc (k + m·n)).
--    (p : Fin (suc m) so toℕ p ≤ m ; q : Fin (suc k) so toℕ q ≤ k ; hence
--     p·n + toℕ q ≤ m·n + k = k + m·n, and fromℕ< builds the Fin.)
------------------------------------------------------------------------

offsetDigit : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ} (q : Fin (suc k)) →
              Fin (suc (k + m * n))
offsetDigit {m} p n {k} q = fromℕ< (s≤s bound)
  where
  p≤m : toℕ p ≤ m
  p≤m = s≤s-injective (toℕ-bound p)
  q≤k : toℕ q ≤ k
  q≤k = s≤s-injective (toℕ-bound q)
  bound : toℕ p * n + toℕ q ≤ k + m * n
  bound = subst (λ z → toℕ p * n + toℕ q ≤ z) (+-comm (m * n) k)
                (+-mono-≤ (*-monoˡ-≤ n p≤m) q≤k)

------------------------------------------------------------------------
-- 2. replay-aux: add one rung per rung of a length-k FRAGMENT of l₂ on top of a
--    base of the FIXED grade m·n, replaying the fragment's digits offset by p·n.
--    The result has grade k + m·n (k on the left — the accumulator grows cleanly).
------------------------------------------------------------------------

replay-aux : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ} →
             LehmerPath k → LehmerPath (m * n) → LehmerPath (k + m * n)
replay-aux p n start   base = base
replay-aux p n (l ◂ q) base = replay-aux p n l base ◂ offsetDigit p n q

------------------------------------------------------------------------
-- 3. replayOffset: the full n-rung block-insert of a ◂-step. Grade
--    n + m·n = suc m * n (definitionally, since suc m * n = n + m * n).
------------------------------------------------------------------------

replayOffset : ∀ {m n} (p : Fin (suc m)) → LehmerPath n →
               LehmerPath (m * n) → LehmerPath (suc m * n)
replayOffset {m} {n} p l₂ base = replay-aux p n l₂ base

------------------------------------------------------------------------
-- 4. THE FOLD-TRANSPARENT STRUCTURAL PRODUCT. Recursion on the first path: each
--    ◂-rung of l₁ contributes one replayOffset block (n rungs replaying l₂). The
--    grade follows ℕ's `*` by the type (m * n), like _⊕_ follows `+`.
------------------------------------------------------------------------

infixr 7 _⊗ˢ_

_⊗ˢ_ : ∀ {m n} → LehmerPath m → LehmerPath n → LehmerPath (m * n)
start    ⊗ˢ l₂ = start
(l₁ ◂ p) ⊗ˢ l₂ = replayOffset p l₂ (l₁ ⊗ˢ l₂)
