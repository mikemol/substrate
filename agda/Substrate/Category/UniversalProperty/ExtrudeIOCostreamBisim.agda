{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim — ⟡extrude-coio-bisim: bisimilarity on the
-- unbounded emit CoIO (289). Two costreams are bisimilar when they emit the same head and their rests are
-- bisimilar — the observational equality of the unbounded emit (the coinductive analogue of ≡, NOT a total
-- DecEq; D-no-classical-spook). Small, no funext/Set₁/levels/postulate.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: _≈ᶜ_ (coinductive
-- bisimilarity) + ≈ᶜ-refl/≈ᶜ-sym/≈ᶜ-trans (an equivalence) + take-cong (bisimilar costreams have equal finite
-- prefixes). The framing is (prose: 289 + Bisim 278).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream using (CoIO; emit-head; emit-rest; take-coio)

private variable O : Set

------------------------------------------------------------------------
-- ① BISIMILARITY on the unbounded emit: same head, bisimilar rest (coinductive — the observational equality).
------------------------------------------------------------------------
record _≈ᶜ_ {O : Set} (c d : CoIO O) : Set where
  coinductive
  field
    head≈ : emit-head c ≡ emit-head d
    rest≈ : emit-rest c ≈ᶜ emit-rest d
open _≈ᶜ_ public

infix 4 _≈ᶜ_

------------------------------------------------------------------------
-- ② AN EQUIVALENCE (refl/sym/trans, coinductive):
------------------------------------------------------------------------
≈ᶜ-refl : (c : CoIO O) → c ≈ᶜ c
head≈ (≈ᶜ-refl c) = refl
rest≈ (≈ᶜ-refl c) = ≈ᶜ-refl (emit-rest c)

≈ᶜ-sym : {c d : CoIO O} → c ≈ᶜ d → d ≈ᶜ c
head≈ (≈ᶜ-sym p) = sym (head≈ p)
rest≈ (≈ᶜ-sym p) = ≈ᶜ-sym (rest≈ p)

≈ᶜ-trans : {c d e : CoIO O} → c ≈ᶜ d → d ≈ᶜ e → c ≈ᶜ e
head≈ (≈ᶜ-trans p q) = trans (head≈ p) (head≈ q)
rest≈ (≈ᶜ-trans p q) = ≈ᶜ-trans (rest≈ p) (rest≈ q)

------------------------------------------------------------------------
-- ③ SOUNDNESS for finite observation: bisimilar costreams have EQUAL finite prefixes (every take agrees).
------------------------------------------------------------------------
take-cong : (n : ℕ) {c d : CoIO O} → c ≈ᶜ d → take-coio n c ≡ take-coio n d
take-cong zero    p = refl
take-cong (suc n) p = cong₂ _∷_ (head≈ p) (take-cong n (rest≈ p))

------------------------------------------------------------------------
-- ④ (⟡extrude-coio-bisim-complete) COMPLETENESS: equal on every finite prefix ⟹ bisimilar (the coinductive
--    limit — the converse of take-cong). Bisimilarity IS the "agrees on all observations" relation.
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream using (emit-head; emit-rest)

private
  hd : {O : Set} → O → List O → O
  hd d []      = d
  hd _ (x ∷ _) = x
  tl : {O : Set} → List O → List O
  tl []       = []
  tl (_ ∷ xs) = xs

bisim-complete : {c d : CoIO O} → ((n : ℕ) → take-coio n c ≡ take-coio n d) → c ≈ᶜ d
head≈ (bisim-complete {c = c} {d = d} f) =
  -- take-coio 1 c = emit-head c ∷ [] ; extract the head from f 1:
  cong (hd (emit-head c)) (f 1)
rest≈ (bisim-complete {c = c} {d = d} f) =
  bisim-complete (λ n → cong tl (f (suc n)))   -- prefixes of the rests agree, from f (suc n)

------------------------------------------------------------------------
------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — bisimilarity is the observational equality of the unbounded emit; sound for
-- every finite prefix; NOT a total DecEq): CoIO (289) is the unbounded emit; its equality is BISIMILARITY (①,
-- _≈ᶜ_ — same head, bisimilar rest, coinductive), an equivalence (②), sound for finite observation (③,
-- take-cong: bisimilar ⟹ equal prefixes). This is the coinductive equality (D-no-classical-spook: NOT total
-- DecEq — the costream is infinite; per-step observation + the coinductive limit). Small, no funext/Set₁/
-- levels/postulate. The emit-side's unbounded equality, matching the run-side's bisimilarity (278). Chain: 289
-- (CoIO) → 290c (its bisimilarity).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = _≈ᶜ_ + the equivalence + take-cong (finite-prefix soundness).
-- SCOPED: completeness (equal-on-all-prefixes ⟹ bisimilar — the coinductive limit, ⟡extrude-coio-bisim-
-- complete). What's grounded: the observational equality of the unbounded emit, sound for observation, small.
------------------------------------------------------------------------
