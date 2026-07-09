{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimUptoLimit — ⟡extrude-upto-limit: the COINDUCTIVE
-- COMPLETENESS of the bounded bisimilarity. 281 proved SOUNDNESS (≈ ⟹ bisim-upto n ≡ true, ∀ n); this proves
-- COMPLETENESS (bisim-upto n ≡ true ∀ n ⟹ ≈). Together: ≈ ⟺ (∀ n, bisim-upto n ≡ true) — bisimilarity IS the
-- LIMIT of the bounded observations.
--
-- Crucially, this limit is reached by CORECURSION, NOT by "running out of output" — you do NOT check ∀ n by
-- exhausting a finite bound (that would be the verdict = running out of output); the ≈ is the coinductive
-- object built step by step. So completeness is NOT decidable — that is the point. The verdict (a total
-- decision) is what you'd get by truncating; ≈ is what you get by NOT truncating.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: head-eq-complete (head-eq a
-- b ≡ true ⟹ a ≡ b), ∧-true-left/right (Bool conjunction lemmas), and upto-limit (the coinductive
-- completeness). The framing ('≈ is the limit reached by corecursion not truncation; not decidable') is
-- (prose: 281 + the operator's "verdict = run out of output"; the decidability of ∀ n is NOT claimed — it is
-- the coinductive limit).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimUptoLimit where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape; isS; isK; isI; isApp)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun
  using (RedTrace; obs; more; _≈_; obs≈; more≈)
open import Substrate.Category.UniversalProperty.ExtrudeBisimDetect using (bisim-upto; head-eq)

------------------------------------------------------------------------
-- ① COMPLETENESS of the head observation: head-eq a b ≡ true ⟹ a ≡ b (the converse of 281's head-eq-sound).
------------------------------------------------------------------------
head-eq-complete : {a b : HeadShape} → head-eq a b ≡ true → a ≡ b
head-eq-complete {isS}   {isS}   _ = refl
head-eq-complete {isK}   {isK}   _ = refl
head-eq-complete {isI}   {isI}   _ = refl
head-eq-complete {isApp} {isApp} _ = refl
head-eq-complete {isS}   {isK}   ()
head-eq-complete {isS}   {isI}   ()
head-eq-complete {isS}   {isApp} ()
head-eq-complete {isK}   {isS}   ()
head-eq-complete {isK}   {isI}   ()
head-eq-complete {isK}   {isApp} ()
head-eq-complete {isI}   {isS}   ()
head-eq-complete {isI}   {isK}   ()
head-eq-complete {isI}   {isApp} ()
head-eq-complete {isApp} {isS}   ()
head-eq-complete {isApp} {isK}   ()
head-eq-complete {isApp} {isI}   ()

------------------------------------------------------------------------
-- ② Bool conjunction lemmas: extract each conjunct from a ∧ that is true.
------------------------------------------------------------------------
∧-true-left : {a b : Bool} → a ≡ true → (a ∧ b) ≡ true → b ≡ true
∧-true-left {true}  _ eq = eq
∧-true-left {false} () _

∧-true-right : {a : Bool} → (a ∧ true) ≡ true → a ≡ true
∧-true-right {true}  _  = refl
∧-true-right {false} ()

------------------------------------------------------------------------
-- ③ COMPLETENESS (the coinductive limit): if the traces agree on the first n observations for EVERY n, they
--    are bisimilar. Built by CORECURSION — obs≈ from n=1, more≈ from the (suc n) tails — NOT by running out.
------------------------------------------------------------------------
upto-limit : (s t : RedTrace) → ((n : ℕ) → bisim-upto n s t ≡ true) → s ≈ t
obs≈  (upto-limit s t h) = head-eq-complete (∧-true-right (h 1))
more≈ (upto-limit s t h) =
  upto-limit (more s) (more t) (λ n → ∧-true-left (∧-true-right (h 1)) (h (suc n)))

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — ≈ IS the LIMIT of the bounded observations, reached by corecursion NOT
-- truncation; completeness is coinductive, NOT decidable — that is the point): 281 gave soundness (≈ ⟹
-- bisim-upto n ∀ n); this gives completeness (bisim-upto n ∀ n ⟹ ≈). Together ≈ ⟺ (∀ n, bisim-upto n) —
-- bisimilarity is EXACTLY the limit of the bounded per-step observations. head-eq-complete (①) extracts the
-- head equality, the ∧ lemmas (②) split the conjunction, and upto-limit (③) builds the ≈ by CORECURSION:
-- obs≈ from the depth-1 observation, more≈ from the tails of the (suc n) hypotheses. The key: this limit is
-- NOT reached by exhausting a finite check (running out of output = the verdict) — it is the coinductive
-- object, built step by step, never truncated. So completeness is NOT decidable, and that is the point: the
-- verdict (a total decision) is the truncation artifact; ≈ is what you get by NOT truncating. Positive,
-- coinductive, no Turing spook. Chain: 281 (soundness, bounded) → 283a (completeness, the coinductive limit).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = head-eq-complete, ∧-true-left/right, upto-limit (the coinductive
-- completeness). With 281's ≈→upto this is the full ≈ ⟺ (∀ n, bisim-upto n) equivalence. NOT a decision:
-- upto-limit takes the ∀-n hypothesis as GIVEN (a function) and corecurses — it does NOT decide whether the
-- hypothesis holds (that IS the undecidable part, deliberately not claimed). What's grounded: ≈ is the
-- coinductive limit of the bounded observations, reached by corecursion, not by running out of output.
------------------------------------------------------------------------
