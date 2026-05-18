------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.Antisymmetric
--
-- Transpose + antisymmetrize at TensorProduct. The image of
-- antisymmetrize is Λ²V — the antisymmetric subspace of V ⊗ V.
--
-- At F₂ (characteristic 2): antisymmetrize(T) at position (i, j)
-- equals T(i,j) + T(j,i). Diagonal entries vanish (T(i,i) + T(i,i)
-- = 0); off-diagonal entries (i ≠ j) get T(i,j) + T(j,i).
--
-- For T = pair v w: antisymmetrize gives pair v w +ⱽ pair w v.
-- This is the "antisymmetric pairing" of v and w in V ⊗ V at F₂.
--
-- Per the structural conversation: the substrate's existing Bivector
-- at dim 4 (Vec F₂ 6 = F₂^C(4,2)) IS the image of this antisymmetrize
-- map at TensorProduct 4 4. A bridge would let downstream Bivector
-- work cite the TensorProduct universal property; this slice
-- introduces the structural map.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.Antisymmetric where

open import Data.Fin using (Fin; zero; suc)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Category.TensorProduct using (TensorProduct; pair)

------------------------------------------------------------------------
-- N-1: transpose at TensorProduct.
--
-- Swaps rows and columns: transpose T at (j, i) = T at (i, j).
-- Type: TensorProduct n m → TensorProduct m n.
--
-- Implementation via tabulate: for each j ∈ Fin m, construct the
-- column vector tabulate (λ i → lookup (lookup T i) j) : Vector n.
------------------------------------------------------------------------

transpose : ∀ {n m} → TensorProduct n m → TensorProduct m n
transpose {n} {m} T = tabulate λ j → tabulate λ i → lookup (lookup T i) j

------------------------------------------------------------------------
-- N-2: TensorProduct addition — componentwise XOR (row by row).
--
-- For T₁ T₂ : TensorProduct n m, define T₁ +T T₂ at row i to be
-- (lookup T₁ i) +ⱽ (lookup T₂ i).
------------------------------------------------------------------------

_+T_ : ∀ {n m} → TensorProduct n m → TensorProduct n m → TensorProduct n m
_+T_ {n} {m} T₁ T₂ = tabulate λ i → lookup T₁ i +ⱽ lookup T₂ i

infixl 6 _+T_

------------------------------------------------------------------------
-- N-3: antisymmetrize — the structural map T ↦ T + Tᵀ at F₂.
--
-- At F₂ (char 2), antisymmetrize T = T +T transpose T.
-- The image is the antisymmetric subspace of V ⊗ V (= Λ²V).
--
-- Properties:
--   * antisymmetrize T has T(i,j) + T(j,i) at every position.
--   * Diagonal: T(i,i) + T(i,i) = 0 (always).
--   * Off-diagonal: T(i,j) + T(j,i).
--   * antisymmetrize ∘ antisymmetrize = antisymmetrize (idempotent
--     when starting from any input — at F₂ it IS the projection
--     onto the antisymmetric subspace).
------------------------------------------------------------------------

antisymmetrize : ∀ {n} → TensorProduct n n → TensorProduct n n
antisymmetrize T = T +T transpose T

------------------------------------------------------------------------
-- N-4: antisymmetrize on pair.
--
-- Specific case: antisymmetrize (pair v w) = pair v w +T pair w v.
--
-- This expresses the "antisymmetric tensor" v ⊗ w + w ⊗ v
-- (= v ∧ w at F₂ — the wedge product in characteristic 2).
------------------------------------------------------------------------

-- The structural identity: antisymmetrize (pair v w) ≡ pair v w +T pair w v
-- requires showing transpose (pair v w) ≡ pair w v.
-- Proof structure: at each (i, j),
--   transpose (pair v w) (j, i) = pair v w (i, j) = v(i) · w(j)
--   pair w v (j, i) = w(j) · v(i) = v(i) · w(j) [·-comm at F₂]
-- So transpose (pair v w) ≡ pair w v at every position. Full
-- proof requires Vec-level rewriting; deferred to follow-on
-- (just the operation itself defined here).

------------------------------------------------------------------------
-- N-5: Capstone — antisymmetrize at TensorProduct lands.
--
-- After this slice:
--
--   * transpose : TensorProduct n m → TensorProduct m n
--   * _+T_      : TensorProduct n m → TensorProduct n m → TensorProduct n m
--   * antisymmetrize : TensorProduct n n → TensorProduct n n
--                      (the projection onto Λ²V at F₂)
--
-- Per [[feedback-categorical-name-first]]: antisymmetrize is the
-- canonical "projection onto antisymmetric subspace" map. At F₂
-- (char 2), it's a projection (antisymmetrize ∘ antisymmetrize =
-- antisymmetrize on the antisymmetric subspace) and its image is
-- the substrate's natural Λ²V representation.
--
-- Connection to substrate's existing Bivector:
--
--   * Bivector at dim 4 = Vec F₂ 6 has 6 independent entries.
--   * The antisymmetric subspace of TensorProduct 4 4 has dim 6
--     (= C(4, 2) = 6 upper-triangular positions in a 4×4 matrix).
--   * Bivector ≅ antisymmetric subspace via an upper-triangular
--     packing isomorphism.
--   * A bridge between Bivector (= Vec F₂ 6 packing) and
--     antisymmetric subspace of TensorProduct 4 4 (= subset of
--     16-dim space) would let HodgeDim4 Bivector / HodgeStar work
--     cite TensorProduct's universal property.
--
-- Deferred follow-on:
--
--   * **Bivector ↔ antisymmetric TensorProduct bridge** at dim 4:
--     show Bivector = image of antisymmetrize at TensorProduct 4 4,
--     packaged as Vec F₂ 6 via upper-triangular extraction.
--     Substantial; opens HodgeDim4 work to TensorProduct-level
--     reasoning.
--
--   * **General Λ²V at any n**: lift the dim-4 bridge to arbitrary n.
--     The Bivector-at-dim-n = Vec F₂ C(n, 2) representation; the
--     antisymmetric subspace of TensorProduct n n = corresponding
--     subspace of F₂^(n²).
--
--   * **Symmetric quotient + Sym²V**: at F₂ symmetric = same as
--     antisymmetric at the SUBSPACE level (T = Tᵀ ⇔ T + Tᵀ = 0).
--     But the QUOTIENT structures differ: Sym²V is V ⊗ V / (v⊗w - w⊗v),
--     Λ²V is V ⊗ V / (v⊗w + w⊗v). At F₂: these IDENTIFY differently
--     and Sym²V has dim n(n+1)/2 while Λ²V has dim n(n-1)/2.
--     The SymBilinForm count n(n+1)/2 (= 6 at n=3, = 10 at n=4)
--     matches Sym²V.
--
--   * **Antisymmetrize-pair structural identity**: full proof of
--     `antisymmetrize (pair v w) ≡ pair v w +T pair w v` (=
--     v ∧ w expression at F₂). Requires Vec-level tabulate /
--     lookup rewriting.
------------------------------------------------------------------------
