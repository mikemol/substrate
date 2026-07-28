------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Punctured.Pointed
--
-- The `extend` operator on the pointed decomposition
-- Fin (suc n) ≅ {k} ⊎ Fin n, with its β-laws — the structural lever
-- that frees finite proofs from concrete enumeration.
--
-- Where a definition like Stab-S3's `extend-fn` enumerates (4 anchors ×
-- 4 axes = 16 clauses) so round-trip proofs can close by `refl` on each
-- concrete value, `extend` here is ONE definition dispatching on i ≟ k,
-- and its β-laws
--
--   extend-point   : extend k f k             ≡ k
--   extend-punchIn : extend k f (punchIn k i) ≡ punchIn k (f i)
--
-- hold PARAMETRICALLY (one proof each), with NO case split on the
-- carrier.  A round trip like `restrict ∘ extend = id` then composes a
-- β-law with a punctured round-trip (`restrict-extend` below) — O(1) in
-- the carrier size, not O(N).  That is simultaneously (a) the fix for
-- value-by-value `refl` proofs that break under transport, and (b) the
-- way to keep normal forms small (the normaliser never builds the
-- per-value table).
--
-- --safe --without-K; zero postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Punctured.Pointed where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Fin.Punctured
open import Substrate.Foundation.Fin.Punctured
  using (punchIn; punchIn-≢; punchOut; punchOut-irrelevant; punchOut-cong;
         punchOut-punchIn; punchIn-punchOut)

private
  variable
    n : ℕ

------------------------------------------------------------------------
-- 1. extend : ONE definition (point ↦ point, punch j ↦ punchIn (f j)).
--
-- Dispatches on the decidable i ≟ k — the computational content of the
-- pointed decomposition Fin (suc n) ≅ {k} ⊎ Fin n.  (A `PunchView`
-- datatype could package the ⊎ explicitly, but the dependent index
-- makes its eliminator awkward and it is not needed for the β-laws, so
-- we work with the decidable dispatch directly.)
------------------------------------------------------------------------

extend : (k : Fin (suc n)) → (Fin n → Fin n) → Fin (suc n) → Fin (suc n)
extend k f i with i ≟ k
... | yes _ = k
... | no  p = punchIn k (f (punchOut {k = k} {i = i} p))

------------------------------------------------------------------------
-- 3. The β-laws — PARAMETRIC (no carrier case split).
------------------------------------------------------------------------

extend-point : (k : Fin (suc n)) (f : Fin n → Fin n) → extend k f k ≡ k
extend-point k f with k ≟ k
... | yes _ = refl
... | no ¬p = ⊥-elim (¬p refl)

extend-punchIn :
  (k : Fin (suc n)) (f : Fin n → Fin n) (i : Fin n) →
  extend k f (punchIn k i) ≡ punchIn k (f i)
extend-punchIn k f i with punchIn k i ≟ k
... | yes eq = ⊥-elim (punchIn-≢ k i eq)
... | no  p  =
      cong (λ z → punchIn k (f z))
           (trans (punchOut-irrelevant p (punchIn-≢ k i))
                  (punchOut-punchIn k i))

------------------------------------------------------------------------
-- 4. restrict ∘ extend = id, PARAMETRICALLY — the proof Stab-S3-Iso's
--    12-case `restrict-extend` should have been.
--
-- `restrict k g j` = punchOut of (g (punchIn k j)); for g = extend k f
-- the index is propositionally punchIn k (f j) (by extend-punchIn), so
-- punchOut-cong slides to that and punchOut-punchIn finishes.  Two
-- structural steps, no enumeration.
------------------------------------------------------------------------

-- the index extend produces at a punch is never the point (β + punchIn-≢).
extend-punch-≢ :
  (k : Fin (suc n)) (f : Fin n → Fin n) (j : Fin n) →
  ¬ (extend k f (punchIn k j) ≡ k)
extend-punch-≢ k f j eq =
  punchIn-≢ k (f j) (trans (sym (extend-punchIn k f j)) eq)

restrict-extend :
  (k : Fin (suc n)) (f : Fin n → Fin n) (j : Fin n) →
  punchOut {k = k} {i = extend k f (punchIn k j)} (extend-punch-≢ k f j) ≡ f j
restrict-extend k f j =
  trans (punchOut-cong (extend-punchIn k f j)
                       (extend-punch-≢ k f j)
                       (punchIn-≢ k (f j)))
        (punchOut-punchIn k (f j))
