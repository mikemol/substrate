------------------------------------------------------------------------
-- Substrate.Algebra.Nat.CyclicSuc
--
-- The generic cyclic-successor permutation on Fin (suc n) and its order
-- witness — the F₂-FREE cyclic generator, derived purely from mod-suc
-- arithmetic (Algebra.Nat.Mod) + the generic iterate (Foundation).
--
-- cyclic-suc {n} : Fin (suc n) → Fin (suc n) sends i ↦ (i + 1) mod (suc n).
-- Nothing here touches Vector or Linear — it is pure Fin/Nat arithmetic.
--
-- Ⓖ.tower-basis (2026-07-05): this WAS §1–4 of
-- Algebra.F2.Linear.FromImages.Permutation.Cyclic, colocated with the Linear
-- lift (cyclic-Linear). Because they shared a file, importing the *generator*
-- transitively dragged the whole F2.Vector/Linear stack — for the ~8
-- permutation-only consumers (Coxeter, the witness-tower grounding, AES
-- ShiftRows, CoxeterFin) that never touch a Linear map. Split out here, BELOW
-- Algebra.F2.Linear by layer, so:
--   * the generator reads F₂-free, and
--   * the Linear lift now FALLS OUT of it (Permutation.Cyclic imports this +
--     applies basis-permutation-Linear) — reversing the old dependency
--     direction ([[tower-as-combinatorial-basis]] / [[expose-generator-not-orbit]]).
-- Neither the tower (which is itself F₂-heavy) nor F2.Linear is the basis for
-- the cyclic chain — this F₂-free mod-suc arithmetic is. The tower's Perm-power
-- bridges to it via WitnessTower.CyclicCollapse.
--
-- The HasOrderPerm witness is derived once, via:
--   * mod-suc-id        (a < suc n → a mod-suc n ≡ a),
--   * mod-suc-periodic  ((a + suc n) mod-suc n ≡ a mod-suc n),
--   * mod-suc-suc       (suc a mod-suc n ≡ suc (a mod-suc n) mod-suc n),
-- + the toℕ ↔ fromℕ< roundtrips from Foundation.Fin.Properties.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.CyclicSuc where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc; +-identityʳ)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties
  using (toℕ-bound; toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Function.Iterate using (iterate; HasFixedOrder)

open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; mod-suc-id; mod-suc-periodic; mod-suc-suc)

------------------------------------------------------------------------
-- 1. cyclic-suc — the cyclic successor on Fin (suc n).
--
-- (i + 1) mod (suc n), converted from ℕ back to Fin (suc n) via
-- mod-suc-bound + fromℕ<.
------------------------------------------------------------------------

cyclic-suc : ∀ {n} → Fin (suc n) → Fin (suc n)
cyclic-suc {n} i = fromℕ< (mod-suc-bound (suc (toℕ i)) n)

------------------------------------------------------------------------
-- 2. toℕ ∘ cyclic-suc = (suc ∘ toℕ) mod-suc n.
------------------------------------------------------------------------

cyclic-suc-toℕ : ∀ {n} (i : Fin (suc n)) →
                 toℕ (cyclic-suc i) ≡ (suc (toℕ i)) mod-suc n
cyclic-suc-toℕ {n} i = toℕ-fromℕ< (mod-suc-bound (suc (toℕ i)) n)

------------------------------------------------------------------------
-- 3. Iteration corresponds to addition under mod-suc.
--
-- toℕ (iterate k cyclic-suc i) ≡ (toℕ i + k) mod-suc n.  (Historically
-- named σ-iterate-toℕ; `iterate` here is the generic Foundation combinator
-- that the F2.Linear `σ-iterate` is the Fin-specialization of, so the name
-- is preserved for the SpectralCycleDim consumer.)  Proof by induction on k.
------------------------------------------------------------------------

σ-iterate-toℕ : ∀ {n} (k : ℕ) (i : Fin (suc n)) →
                toℕ (iterate k cyclic-suc i) ≡ (toℕ i + k) mod-suc n
σ-iterate-toℕ {n} zero i =
  sym (trans (cong (_mod-suc n) (+-identityʳ (toℕ i)))
             (mod-suc-id (toℕ i) n (toℕ-bound i)))
σ-iterate-toℕ {n} (suc k) i =
  trans (cyclic-suc-toℕ (iterate k cyclic-suc i))
        (trans (cong (λ z → suc z mod-suc n) (σ-iterate-toℕ k i))
               (trans (sym (mod-suc-suc (toℕ i + k) n))
                      (cong (_mod-suc n) (sym (+-suc (toℕ i) k)))))

------------------------------------------------------------------------
-- 4. cyclic-suc-HasOrderPerm — the structural order witness.
--
-- iterate (suc n) cyclic-suc i ≡ i. Via toℕ-injective + σ-iterate-toℕ
-- + mod-suc-periodic + mod-suc-id.  Typed as HasFixedOrder (the generic
-- Foundation predicate); definitionally equal to the historical
-- HasOrderPerm (cyclic-suc) (suc n).
------------------------------------------------------------------------

cyclic-suc-HasOrderPerm : ∀ {n} → HasFixedOrder (cyclic-suc {n}) (suc n)
cyclic-suc-HasOrderPerm {n} i =
  toℕ-injective
    (trans (σ-iterate-toℕ (suc n) i)
           (trans (mod-suc-periodic (toℕ i) n)
                  (mod-suc-id (toℕ i) n (toℕ-bound i))))
