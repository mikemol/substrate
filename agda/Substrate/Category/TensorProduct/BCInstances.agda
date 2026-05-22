------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.BCInstances
--
-- The substrate's BCSquare instances arising from the TensorProduct
-- primitive, packaged via the `factor-via-pair-BCSquare` and
-- `section-BCSquare` combinators from `Substrate.Category.BeckChevalley`.
--
-- After this module:
--
--   * poly-mult-BCSquare       — polynomial multiplication
--                                  (anti-diag-sum ∘ pair ≡ *P)
--   * bilinform-eval-BCSquare  — bilinear-form evaluation
--                                  (bilin-via-tensor ∘ pair ≡ bilin)
--   * bivector-roundtrip-BCSquare — Bivector ↔ TensorProduct 4 4
--                                  section (extract ∘ embed ≡ id)
--
-- Each instance is now a one-line application of the appropriate
-- BC combinator: factor-via-pair for the bilinear → linear via tensor
-- pattern, section for the round-trip-closure pattern.
--
-- This consolidates the prior per-domain BCInstance modules into a
-- single parameterized module living next to the TensorProduct
-- primitive that motivates them.
--
-- Per [[feedback-categorical-name-first]]: each instance names the
-- categorical pattern (factorization-via-pair = ⊗-Hom adjunction unit;
-- section = bridge with one-sided round-trip closure) and the
-- combinator carries the universal-property content.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: three
-- instances expressed via two combinators rather than as three
-- bespoke BCSquare records.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.BCInstances where

open import Substrate.Foundation.Nat using (ℕ) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Product using (_×_; _,_)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
  using (Polynomial; _*P_; anti-diag-sum)
open import Substrate.Algebra.F2.Polynomial.TensorProductView
  using (*P-via-tensor-eq)
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm; bilinear-form-of)
open import Substrate.Algebra.F2.SymBilinForm.TensorProductView
  using (bilinear-form-of-via-tensor; bilinear-form-of-via-tensor-agrees)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
  using (bivector-to-tensor; tensor-to-bivector; bivector-tensor-roundtrip)
open import Substrate.Category.TensorProduct using (TensorProduct; pair)
open import Substrate.Category.BeckChevalley
  using (BCSquare; factor-via-pair-BCSquare; section-BCSquare)

------------------------------------------------------------------------
-- N-1: poly-mult-BCSquare — BCSquare for polynomial multiplication via
-- the anti-diag-sum ∘ pair factorization.
--
-- The factor-via-pair combinator absorbs the structural symmetry; the
-- agreement comes from *P-via-tensor-eq.
------------------------------------------------------------------------

private
  PolyPair : ℕ → ℕ → Set
  PolyPair n m = Vector n × Vector m

  pair-poly : ∀ {n m} → PolyPair n m → TensorProduct n m
  pair-poly (v , w) = pair v w

  anti-diag-poly : ∀ {n m} → TensorProduct n m → Polynomial (n ℕ+ m)
  anti-diag-poly = anti-diag-sum

  mult-poly : ∀ {n m} → PolyPair n m → Polynomial (n ℕ+ m)
  mult-poly (v , w) = v *P w

poly-mult-BCSquare :
  ∀ {n m} →
  BCSquare {A = PolyPair n m}
           {B = TensorProduct n m}
           {C = PolyPair n m}
           {D = Polynomial (n ℕ+ m)}
           pair-poly
           (λ x → x)
           anti-diag-poly
           mult-poly
poly-mult-BCSquare =
  factor-via-pair-BCSquare pair-poly anti-diag-poly mult-poly
    (λ { (v , w) → *P-via-tensor-eq v w })

------------------------------------------------------------------------
-- N-2: bilinform-eval-BCSquare — BCSquare for bilinear-form evaluation
-- factoring through TensorProduct.
------------------------------------------------------------------------

private
  VecPair : ℕ → Set
  VecPair n = Vector n × Vector n

  pair-vec : ∀ {n} → VecPair n → TensorProduct n n
  pair-vec (v , w) = pair v w

  eval-tensor : ∀ {n} → BilinForm n → TensorProduct n n → F₂
  eval-tensor M T = bilinear-form-of-via-tensor M T

  eval-direct : ∀ {n} → BilinForm n → VecPair n → F₂
  eval-direct M (v , w) = bilinear-form-of M v w

bilinform-eval-BCSquare :
  ∀ {n} (M : BilinForm n) →
  BCSquare {A = VecPair n}
           {B = TensorProduct n n}
           {C = VecPair n}
           {D = F₂}
           pair-vec
           (λ x → x)
           (eval-tensor M)
           (eval-direct M)
bilinform-eval-BCSquare M =
  factor-via-pair-BCSquare pair-vec (eval-tensor M) (eval-direct M)
    (λ { (v , w) → bilinear-form-of-via-tensor-agrees M v w })

------------------------------------------------------------------------
-- N-3: bivector-roundtrip-BCSquare — section BCSquare for Bivector ↔
-- TensorProduct 4 4. The section combinator says: extract ∘ embed ≡ id.
------------------------------------------------------------------------

bivector-roundtrip-BCSquare :
  BCSquare {A = Bivector}
           {B = TensorProduct 4 4}
           {C = Bivector}
           {D = Bivector}
           bivector-to-tensor
           (λ x → x)
           tensor-to-bivector
           (λ x → x)
bivector-roundtrip-BCSquare =
  section-BCSquare bivector-to-tensor tensor-to-bivector
    bivector-tensor-roundtrip

------------------------------------------------------------------------
-- N-4: Capstone — three BC instances, two combinators, one module.
--
-- The substrate's BC primitive #5 is load-bearing across:
--
--   #1 poly-mult-BCSquare        (factor-via-pair, *P-via-tensor-eq)
--   #2 bilinform-eval-BCSquare   (factor-via-pair, bilin-via-tensor-agrees)
--   #3 bivector-roundtrip-BCSquare (section, bivector-tensor-roundtrip)
--
-- Each is a one-line application of a named BC combinator. The cells
-- carry the universal-property content; the combinators carry the
-- categorical shape.
--
-- Per [[project-3plus1-parity-universal]]: each BCSquare's cell is the
-- structural content of the corresponding factorization or section.
--
-- Substrate-wide implication: any bilinear b : V → W → U factors
-- through TensorProduct via pair + a unique linear b̃ (factor-via-pair);
-- any bridge with a one-sided round-trip closes as a section BCSquare
-- (section-BCSquare). The combinators name these universal-property
-- shapes; the instances apply them.
--
-- Deferred follow-ons:
--
--   * **Retraction BCSquare (other direction)**: bivector-to-tensor ∘
--     tensor-to-bivector ≡ id on the antisymmetric subspace of
--     TensorProduct 4 4. Requires the AntisymmetricTensor n subtype.
--
--   * **BC composition**: combinators for vertical / horizontal pasting
--     of BCSquares (the 2-cell calculus).
--
--   * **Adjunction-cell BCSquare**: an explicit combinator for "BC
--     square arising from an adjunction unit/counit" pattern, naming
--     factor-via-pair as one of its instances.
--
--   * **More instances**: dim-3 ↔ dim-4 SymBilinForm bridge,
--     ReservedBridge gauge family, V₄-orbit / chirality split, etc.
------------------------------------------------------------------------
