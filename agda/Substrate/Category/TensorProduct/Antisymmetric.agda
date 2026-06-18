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

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate; vec-ext)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; trans; sym)

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
-- Properties (proved in N-3½ below):
--   * antisymmetrize T has T(i,j) + T(j,i) at every position (entry-antisym).
--   * Diagonal: T(i,i) + T(i,i) = 0 (always).
--   * antisymmetrize T is a SYMMETRIC matrix (antisym-symmetric): it equals
--     its own transpose, since T(i,j)+T(j,i) = T(j,i)+T(i,j) by +-comm.
--   * THE SQUARE LAW (antisymmetrize-square): P² = P +T P  (= 2·P), with NO
--     characteristic hypothesis. This is the common structure of which the
--     two readings are degenerate corners:
--       - char ≠ 2: P²=2P, so ½P is idempotent — a PROJECTION onto the
--         antisymmetric subspace (the classical reading).
--       - char  = 2 (THIS F₂ carrier): 2=0, so P²=0 — antisymmetrize is
--         SQUARE-ZERO / NILPOTENT (a differential d²=0), NOT idempotent
--         (antisymmetrize-square-zero). An earlier comment here asserted
--         "idempotent projection"; that is the char≠2 corner, false at F₂.
------------------------------------------------------------------------

antisymmetrize : ∀ {n} → TensorProduct n n → TensorProduct n n
antisymmetrize T = T +T transpose T

------------------------------------------------------------------------
-- N-3½: the algebra of transpose/+T and THE SQUARE LAW.
--
-- The Vec-level rewriting the original slice deferred, done via matrix
-- extensionality (TP-ext, from Foundation.Vec.Properties.vec-ext) reducing
-- everything to pointwise F₂ facts. `entry T i j = T(i,j)`.
------------------------------------------------------------------------

-- matrix entry access.
entry : ∀ {n m} → TensorProduct n m → Fin n → Fin m → F₂
entry T i j = lookup (lookup T i) j

-- matrix extensionality: equal at every entry ⟹ equal (vec-ext twice).
TP-ext : ∀ {n m} (S T : TensorProduct n m) →
         ((i : Fin n) (j : Fin m) → entry S i j ≡ entry T i j) → S ≡ T
TP-ext S T p = vec-ext S T (λ i → vec-ext (lookup S i) (lookup T i) (p i))

-- entry computations for transpose and +T.
entry-transpose : ∀ {n m} (T : TensorProduct n m) (i : Fin m) (j : Fin n) →
                  entry (transpose T) i j ≡ entry T j i
entry-transpose T i j =
  trans (cong (λ r → lookup r j)
              (lookup∘tabulate (λ j′ → tabulate (λ i′ → lookup (lookup T i′) j′)) i))
        (lookup∘tabulate (λ i′ → lookup (lookup T i′) i) j)

entry-+T : ∀ {n m} (A B : TensorProduct n m) (i : Fin n) (j : Fin m) →
           entry (A +T B) i j ≡ (entry A i j + entry B i j)
entry-+T A B i j =
  trans (cong (λ r → lookup r j) (lookup∘tabulate (λ i′ → lookup A i′ +ⱽ lookup B i′) i))
        (lookup-+ⱽ (lookup A i) (lookup B i) j)

-- antisymmetrize's entry: T(i,j) + T(j,i).
entry-antisym : ∀ {n} (T : TensorProduct n n) (i j : Fin n) →
                entry (antisymmetrize T) i j ≡ (entry T i j + entry T j i)
entry-antisym T i j =
  trans (entry-+T T (transpose T) i j) (cong (entry T i j +_) (entry-transpose T i j))

-- ★ antisymmetrize T is SYMMETRIC (transpose-fixed): T(i,j)+T(j,i) = T(j,i)+T(i,j).
antisym-symmetric : ∀ {n} (T : TensorProduct n n) →
                    transpose (antisymmetrize T) ≡ antisymmetrize T
antisym-symmetric T =
  TP-ext (transpose (antisymmetrize T)) (antisymmetrize T)
    (λ i j → trans (entry-transpose (antisymmetrize T) i j)
              (trans (entry-antisym T j i)
               (trans (+-comm (entry T j i) (entry T i j))
                (sym (entry-antisym T i j)))))

-- ★ THE SQUARE LAW (characteristic-agnostic): antisymmetrize² = antisymmetrize +T antisymmetrize.
antisymmetrize-square : ∀ {n} (T : TensorProduct n n) →
  antisymmetrize (antisymmetrize T) ≡ (antisymmetrize T +T antisymmetrize T)
antisymmetrize-square T = cong (antisymmetrize T +T_) (antisym-symmetric T)

-- the zero matrix, and the self-cancellation P +T P ≡ 0 at F₂.
𝟎T : ∀ {n m} → TensorProduct n m
𝟎T = tabulate (λ _ → 𝟎ⱽ)

entry-𝟎T : ∀ {n m} (i : Fin n) (j : Fin m) → entry (𝟎T {n} {m}) i j ≡ 𝟘
entry-𝟎T i j = trans (cong (λ r → lookup r j) (lookup∘tabulate (λ _ → 𝟎ⱽ) i)) (lookup-𝟎 j)

+T-self-zero : ∀ {n m} (A : TensorProduct n m) → (A +T A) ≡ 𝟎T
+T-self-zero A =
  TP-ext (A +T A) 𝟎T
    (λ i j → trans (entry-+T A A i j) (trans (+-self-inverse (entry A i j)) (sym (entry-𝟎T i j))))

-- ★ THE CHAR-2 READING: at F₂ (this carrier) 2 = 0, so the square law collapses to
-- SQUARE-ZERO — antisymmetrize is nilpotent (d²=0), the honest fact for this carrier.
antisymmetrize-square-zero : ∀ {n} (T : TensorProduct n n) →
  antisymmetrize (antisymmetrize T) ≡ 𝟎T
antisymmetrize-square-zero T =
  trans (antisymmetrize-square T) (+T-self-zero (antisymmetrize T))

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
--                      (the map onto the antisymmetric subspace at F₂)
--
-- Per [[feedback-categorical-name-first]]: antisymmetrize is the
-- canonical "antisymmetric subspace" map T ↦ T + Tᵀ. Its square obeys
-- antisymmetrize² = antisymmetrize +T antisymmetrize (= 2·antisymmetrize,
-- antisymmetrize-square, char-agnostic). At F₂ (char 2) that is SQUARE-ZERO
-- (antisymmetrize-square-zero) — antisymmetrize is nilpotent here, not
-- idempotent; the "projection" reading is the char≠2 corner (where ½·it is
-- idempotent). Its image is the substrate's natural Λ²V representation.
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
