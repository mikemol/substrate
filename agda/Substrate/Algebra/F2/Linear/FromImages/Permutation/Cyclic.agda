------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
--
-- The generic cyclic-suc on Fin (suc n) and its HasOrderPerm witness.
--
-- cyclic-suc {n} : Fin (suc n) → Fin (suc n) sends i ↦ (i + 1) mod
-- (suc n). σ₃, σ₄, σ₅ (from Cycle3 / Cycle4 / Cycle5) are precisely
-- cyclic-suc {2}, cyclic-suc {3}, cyclic-suc {4}. The HasOrderPerm
-- witness `cyclic-suc-HasOrderPerm` is derived once, via:
--
--   * mod-suc-id        (a < suc n → a mod-suc n ≡ a),
--   * mod-suc-periodic  ((a + suc n) mod-suc n ≡ a mod-suc n),
--   * mod-suc-suc       (suc a mod-suc n ≡ suc (a mod-suc n) mod-suc n),
--
-- + the toℕ ↔ fromℕ< roundtrips from Foundation.Fin.Properties.
--
-- After this slice, the Cycleₙ files (n ∈ {3, 4, 5}) and any new
-- Cycleₖ instance are thin renamings of cyclic-suc {k-1} with
-- HasOrderPerm coming free. The per-position n-case enumeration that
-- previously existed at each Cycleₙ is eliminated structurally.
--
-- Per [[expose-generator-not-orbit]]: the Cycleₙ chain was an orbit
-- "every k gets the same cyclic-suc + the same HasOrderPerm proof";
-- this module IS that chain, derived once from mod-suc arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc; +-identityʳ)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties
  using (toℕ-bound; toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; mod-suc-id; mod-suc-periodic; mod-suc-suc)

open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm; basis-permutation-Linear; HasOrder-from-perm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate
  using (σ-iterate)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

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
--
-- The defining relation: cyclic-suc's underlying ℕ is the mod-suc
-- of the input + 1.
------------------------------------------------------------------------

cyclic-suc-toℕ : ∀ {n} (i : Fin (suc n)) →
                 toℕ (cyclic-suc i) ≡ (suc (toℕ i)) mod-suc n
cyclic-suc-toℕ {n} i = toℕ-fromℕ< (mod-suc-bound (suc (toℕ i)) n)

------------------------------------------------------------------------
-- 3. Iteration corresponds to addition under mod-suc.
--
-- toℕ (σ-iterate k cyclic-suc i) ≡ (toℕ i + k) mod-suc n.
-- Proof by induction on k.
------------------------------------------------------------------------

σ-iterate-toℕ : ∀ {n} (k : ℕ) (i : Fin (suc n)) →
                toℕ (σ-iterate k cyclic-suc i) ≡ (toℕ i + k) mod-suc n
σ-iterate-toℕ {n} zero i =
  sym (trans (cong (_mod-suc n) (+-identityʳ (toℕ i)))
             (mod-suc-id (toℕ i) n (toℕ-bound i)))
σ-iterate-toℕ {n} (suc k) i =
  trans (cyclic-suc-toℕ (σ-iterate k cyclic-suc i))
        (trans (cong (λ z → suc z mod-suc n) (σ-iterate-toℕ k i))
               (trans (sym (mod-suc-suc (toℕ i + k) n))
                      (cong (_mod-suc n) (sym (+-suc (toℕ i) k)))))

------------------------------------------------------------------------
-- 4. cyclic-suc-HasOrderPerm — the structural HasOrderPerm witness.
--
-- σ-iterate (suc n) cyclic-suc i ≡ i. Via toℕ-injective + σ-iterate-toℕ
-- + mod-suc-periodic + mod-suc-id.
------------------------------------------------------------------------

cyclic-suc-HasOrderPerm : ∀ {n} → HasOrderPerm (cyclic-suc {n}) (suc n)
cyclic-suc-HasOrderPerm {n} i =
  toℕ-injective
    (trans (σ-iterate-toℕ (suc n) i)
           (trans (mod-suc-periodic (toℕ i) n)
                  (mod-suc-id (toℕ i) n (toℕ-bound i))))

------------------------------------------------------------------------
-- 5. cyclic-Linear / cyclic-HasOrder — the Linear lift, parametric.
--
-- Lifts the cyclic-suc permutation through basis-permutation-Linear to
-- a Linear (suc n) (suc n), and transports cyclic-suc-HasOrderPerm
-- through HasOrder-from-perm. Cycle{N}.agda for N ∈ {2, 3, 4, 5, 7}
-- become thin renamings of these.
------------------------------------------------------------------------

cyclic-Linear : ∀ {n} → Linear (suc n) (suc n)
cyclic-Linear {n} = basis-permutation-Linear (cyclic-suc {n})

cyclic-HasOrder : ∀ {n} → HasOrder (apply (cyclic-Linear {n})) (suc n)
cyclic-HasOrder {n} =
  HasOrder-from-perm (cyclic-suc {n}) (suc n) (cyclic-suc-HasOrderPerm {n})
