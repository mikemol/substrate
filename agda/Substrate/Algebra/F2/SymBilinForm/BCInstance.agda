------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.BCInstance
--
-- A concrete `BCSquare` instance demonstrating substrate's
-- BeckChevalley primitive #5 in action — applied to the
-- bilinear-form-of bridge.
--
-- The square: evaluating a bilinear form `bilinear-form-of M` on
-- (v, w) factors through TensorProduct via the ⊗-Hom adjunction
-- (pair + bilinear-form-of-via-tensor). The two paths commute via
-- the universal-property witness `bilinear-form-of-via-tensor-agrees`.
--
-- Slice 2 of 3 in the BC-load-bearing trio. Companion to
-- Substrate.Algebra.F2.Polynomial.BCInstance — same categorical
-- pattern at a different substrate operation (bilinear evaluation
-- vs polynomial multiplication).
--
-- Per [[feedback-categorical-name-first]]: bilinear-form-of IS the
-- natural "linear function out of the tensor product" evaluated at
-- the universal pair; this slice names the agreement as a BCSquare.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.BCInstance where

open import Data.Nat using (ℕ)
open import Data.Product using (_×_; _,_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.SymBilinForm using (BilinForm; bilinear-form-of)
open import Substrate.Algebra.F2.SymBilinForm.TensorProductView
  using (bilinear-form-of-via-tensor; bilinear-form-of-via-tensor-agrees)
open import Substrate.Category.TensorProduct using (TensorProduct; pair)
open import Substrate.Category.BeckChevalley using (BCSquare; bc-trivial)

------------------------------------------------------------------------
-- N-1: bilinform-eval-BC — BCSquare for bilinear-form-of factoring
-- through TensorProduct via pair.
--
-- At fixed dimension n and fixed bilinear form M, the BCSquare has:
--   A = Vector n × Vector n        (input pair)
--   B = TensorProduct n n          (lifted via pair)
--   C = Vector n × Vector n        (identity)
--   D = F₂                         (scalar output)
--
-- Paths:
--   A → B → D : (v, w) → pair v w → bilinear-form-of-via-tensor M (pair v w)
--   A → C → D : (v, w) → (v, w)  → bilinear-form-of M v w
--
-- Cell: bilinear-form-of-via-tensor M (pair v w) ≡ bilinear-form-of M v w
-- (via sym (bilinear-form-of-via-tensor-agrees M v w)).
------------------------------------------------------------------------

private
  VecPair : ℕ → Set
  VecPair n = Vector n × Vector n

  pair-uncurried : ∀ {n} → VecPair n → TensorProduct n n
  pair-uncurried (v , w) = pair v w

  id-uncurried : ∀ {n} → VecPair n → VecPair n
  id-uncurried = λ x → x

  eval-tensor-uncurried : ∀ {n} → BilinForm n → TensorProduct n n → F₂
  eval-tensor-uncurried M T = bilinear-form-of-via-tensor M T

  eval-direct-uncurried : ∀ {n} → BilinForm n → VecPair n → F₂
  eval-direct-uncurried M (v , w) = bilinear-form-of M v w

bilinform-eval-BCSquare :
  ∀ {n} (M : BilinForm n) →
  BCSquare {A = VecPair n}
           {B = TensorProduct n n}
           {C = VecPair n}
           {D = F₂}
           pair-uncurried
           id-uncurried
           (eval-tensor-uncurried M)
           (eval-direct-uncurried M)
bilinform-eval-BCSquare {n} M =
  bc-trivial pair-uncurried id-uncurried
             (eval-tensor-uncurried M) (eval-direct-uncurried M)
    (λ { (v , w) → sym (bilinear-form-of-via-tensor-agrees M v w) })

------------------------------------------------------------------------
-- N-2: Capstone — BC primitive #5's second concrete substrate instance.
--
-- After this slice:
--
--   * bilinform-eval-BCSquare — a BCSquare instance witnessing the
--     bilinear-form-of factorization through TensorProduct. The cell
--     is bilinear-form-of-via-tensor-agrees (= the unit of the ⊗-Hom
--     adjunction at this specific bilinear map).
--
-- Together with poly-mult-BCSquare (Slice 1), this establishes that
-- the substrate's two main "bilinear → linear via tensor product"
-- patterns (polynomial multiplication; bilinear-form evaluation)
-- both package as BCSquares with substantive (non-refl) cells.
--
-- Per [[project-3plus1-parity-universal]]: both BCSquares witness a
-- factorization through TensorProduct — the CELL in each carries
-- structural content (the specific bilinear/linear correspondence).
--
-- Substrate-wide implication: any bilinear map `b : V × W → U`
-- factors uniquely through TensorProduct via a linear map
-- `b̃ : V ⊗ W → U` with `b(v, w) = b̃(pair v w)`. The BCSquare
-- packages this universal property at the level of concrete
-- substrate instances.
--
-- Slice 3 of this trio: BCSquare for Bivector ↔ TensorProduct bridge
-- (the Hodge dim-4 instance).
------------------------------------------------------------------------
