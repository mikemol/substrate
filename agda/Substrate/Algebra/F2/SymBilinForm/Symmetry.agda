------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.Symmetry
--
-- Symmetry properties of generic bilinear-form-of + congruence-act:
--
--   * sum-swap — Fubini for sum-F₂: the order of nested finite sums
--     is interchangeable.
--   * bilinear-form-of-sym-arg — for a symmetric M, bilinear-form-of M
--     is symmetric in its v / w arguments.
--   * is-symmetric-congruence-act — congruence-act preserves
--     symmetry: T^T M T is symmetric when M is.
--
-- Closes the deferred gap from CongruenceCompose's capstone:
-- congruence-act fully respects the SymBilinForm structure (data +
-- symmetry property).
--
-- After this slice: congruence-act lifts to the SymBilinForm
-- Σ-subtype (BilinForm + IsSymmetric) without breaking symmetry.
-- The infrastructure (especially bilinear-form-of-sym-arg) also
-- unblocks the dim-3 / dim-4 congruence-act-bridge slices, which
-- in turn unlock StabiliserClosure-style demotions.
--
-- Per `feedback_categorical_name_first`: symmetry is the universal
-- property of SymBilinForm (vs general BilinForm); proving
-- congruence-act preserves it confirms the congruence-act
-- restriction to SymBilinForm is well-defined.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.Symmetry where

open import Data.Fin using (Fin; zero; suc)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Vec using (lookup)
open import Function using (_∘_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm; IsSymmetric; bilinear-form-of; congruence-act)
open import Substrate.Algebra.F2.SymBilinForm.Bilinearity
  using (sum-F₂-+-distribute; sum-F₂-scalar)
open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast
  using (sum-of-zeros)

------------------------------------------------------------------------
-- N-1: sum-swap — Fubini for sum-F₂.
--
--   sum-F₂ {n} (λ i → sum-F₂ {m} (λ j → f i j))
--     ≡ sum-F₂ {m} (λ j → sum-F₂ {n} (λ i → f i j))
--
-- The order of nested finite sums over Fin n × Fin m is interchangeable.
-- Proof by induction on n (the outer dimension).
--
--   n=0: LHS = 𝟘 (empty sum); RHS = sum-F₂ {m} (λ _ → 𝟘) ≡ 𝟘 by
--     sum-of-zeros. Bridge via sym.
--
--   n=suc: LHS unfolds to (sum_m of f zero) + (sum-swap rec at n).
--     RHS at suc unfolds to sum_m of (f zero + sum_n of f-suc-i).
--     Bridge via sum-F₂-+-distribute on the inner +.
------------------------------------------------------------------------

sum-swap :
  ∀ {n m} (f : Fin n → Fin m → F₂) →
  sum-F₂ {n} (λ i → sum-F₂ {m} (λ j → f i j))
    ≡ sum-F₂ {m} (λ j → sum-F₂ {n} (λ i → f i j))
sum-swap {zero}  {m} f = sym (sum-of-zeros {m})
sum-swap {suc n} {m} f =
  trans (cong (sum-F₂ {m} (λ j → f zero j) +_)
              (sum-swap {n} {m} (λ i j → f (suc i) j)))
        (sym (sum-F₂-+-distribute
                (λ j → f zero j)
                (λ j → sum-F₂ {n} (λ i → f (suc i) j))))

------------------------------------------------------------------------
-- N-2: Three-factor shuffle helper.
--
--   a · (b · c) ≡ c · (b · a)
--
-- Used in bilinear-form-of-sym-arg to rearrange vᵢ · (M(j,i) · wⱼ)
-- into wⱼ · (M(j,i) · vᵢ). Direct chain using ·-assoc + ·-comm.
------------------------------------------------------------------------

·-shuffle-acb : (a b c : F₂) → a · (b · c) ≡ c · (b · a)
·-shuffle-acb a b c =
  -- a · (b · c) ≡ (a · b) · c  [sym ·-assoc]
  --             ≡ c · (a · b)  [·-comm]
  --             ≡ c · (b · a)  [cong (c ·_) (·-comm a b)]
  trans (sym (·-assoc a b c))
  (trans (·-comm (a · b) c)
         (cong (c ·_) (·-comm a b)))

------------------------------------------------------------------------
-- N-3: bilinear-form-of-sym-arg — argument symmetry under matrix symmetry.
--
--   IsSymmetric M → bilinear-form-of M v w ≡ bilinear-form-of M w v
--
-- Chain:
--   bf M v w
-- = sum-F₂ i → vᵢ · sum-F₂ j → M(i,j) · wⱼ                  [definition]
-- = sum-F₂ i → vᵢ · sum-F₂ j → M(j,i) · wⱼ                  [sym-M inside cong]
-- = sum-F₂ i → sum-F₂ j → vᵢ · (M(j,i) · wⱼ)                 [sym sum-F₂-scalar]
-- = sum-F₂ j → sum-F₂ i → vᵢ · (M(j,i) · wⱼ)                 [sum-swap]
-- = sum-F₂ j → sum-F₂ i → wⱼ · (M(j,i) · vᵢ)                 [·-shuffle-acb]
-- = sum-F₂ j → wⱼ · sum-F₂ i → M(j,i) · vᵢ                   [sum-F₂-scalar]
-- = bf M w v                                                  [definition]
------------------------------------------------------------------------

bilinear-form-of-sym-arg :
  ∀ {n} (M : BilinForm n) → IsSymmetric M → (v w : Vector n) →
  bilinear-form-of M v w ≡ bilinear-form-of M w v
bilinear-form-of-sym-arg {n} M sym-M v w =
  trans
    -- Step 1: replace M(i,j) with M(j,i) via symmetry (inside cong).
    (sum-F₂-cong {n} (λ i →
      cong (lookup v i ·_)
           (sum-F₂-cong {n} (λ j →
             cong (_· lookup w j) (sym-M i j)))))
  (trans
    -- Step 2: pull vᵢ inside inner sum.
    (sum-F₂-cong {n} (λ i →
      sym (sum-F₂-scalar (lookup v i)
                         (λ j → M j i · lookup w j))))
  (trans
    -- Step 3: swap order of summation.
    (sum-swap {n} {n} (λ i j → lookup v i · (M j i · lookup w j)))
  (trans
    -- Step 4: shuffle factors v, M, w → w, M, v.
    (sum-F₂-cong {n} (λ j →
      sum-F₂-cong {n} (λ i →
        ·-shuffle-acb (lookup v i) (M j i) (lookup w j))))
    -- Step 5: pull wⱼ out of inner sum.
    (sum-F₂-cong {n} (λ j →
      sum-F₂-scalar (lookup w j)
                    (λ i → M j i · lookup v i))))))

------------------------------------------------------------------------
-- N-4: is-symmetric-congruence-act — congruence-act preserves symmetry.
--
--   IsSymmetric M → IsSymmetric (congruence-act T M)
--
-- (congruence-act T M)(i, j) = bilinear-form-of M (T eᵢ) (T eⱼ).
-- (congruence-act T M)(j, i) = bilinear-form-of M (T eⱼ) (T eᵢ).
-- By bilinear-form-of-sym-arg using IsSymmetric M, these are equal.
------------------------------------------------------------------------

is-symmetric-congruence-act :
  ∀ {n} (T : Linear n n) (M : BilinForm n) →
  IsSymmetric M → IsSymmetric (congruence-act T M)
is-symmetric-congruence-act T M sym-M i j =
  bilinear-form-of-sym-arg M sym-M (apply T (basis i)) (apply T (basis j))

------------------------------------------------------------------------
-- N-5: Capstone — symmetry chain closed.
--
-- After this slice:
--
--   * `sum-swap` — Fubini for finite F₂ sums. Useful well beyond
--     bilinear forms; lands in the substrate's sum-F₂ infrastructure.
--
--   * `bilinear-form-of-sym-arg` — argument symmetry of bilinear-form-of
--     when the matrix is symmetric. Universal property of SymBilinForm
--     at the evaluation level.
--
--   * `is-symmetric-congruence-act` — congruence-act respects the
--     symmetric subtype. Together with the existing CongruenceCompose
--     and Bilinearity infrastructure, the generic SymBilinForm theory
--     is now self-contained: every operation (bilinear-form-of,
--     congruence-act, metric-id, NonDegenerate) preserves / respects
--     the SymBilinForm structure.
--
-- Enables (deferred follow-on):
--
--   * **congruence-act-bridge-3** at dim 3: extends bilinear-form-of-
--     bridge-3 to congruence-act. The lower-triangular bridge cases
--     (where the dim-3 packing folds entries by symmetry) rely on
--     `bilinear-form-of-sym-arg` + `is-symmetric-bridged-3` to swap
--     argument order in the generic evaluation. Unlocks
--     StabiliserClosure (166 LoC) demotion via FixedPoint-of-compose
--     + congruence-compose-pointwise.
--
--   * **congruence-act-bridge-4** at dim 4: analogous slice for dim 4.
--
--   * **Σ-level congruence-act**: with is-symmetric-congruence-act,
--     congruence-act lifts to the SymBilinForm Σ-subtype
--     `(BilinForm n × IsSymmetric)`. Adapter slice if/when needed.
------------------------------------------------------------------------
