------------------------------------------------------------------------
-- Substrate.Category.TensorProduct
--
-- Primitive #7 in the Substrate.Category.Primitives roadmap.
-- Names the tensor product ⊗ (the carrier `Vec (Vec F₂ m) n`) and the
-- universal bilinear map `pair`. The bilinear universal property itself —
-- bilinear maps ≅ basis-pair tables, with the four bilinearity laws and the
-- basis lookup — IS formalised, at the F₂-linear level, in
-- `Algebra.F2.Linear.BilinearFromImages` (FreeLinearization at arity 2:
-- `apply₂`, `bilinear-from-images-basis`, `Bilinear`) for EXISTENCE, and
-- `Algebra.F2.Linear.BilinearUniversal` for UNIQUENESS
-- (`bilinear-extensionality`: agreement on basis pairs ⟹ agreement
-- everywhere; `bilinear-from-images-unique`: any bilinear map IS the free
-- bilinear map of its basis-pair table). So "factoring uniquely through ⊗"
-- is now backed at the F₂-linear level. (What remains purely local to THIS
-- module is only the cosmetic identification of `pair` with that apparatus's
-- `apply₂` — the substantive UP is the two cited modules.)
--
-- For F₂-vector spaces: V ⊗ W ≅ F₂^(n × m) when V = F₂^n, W = F₂^m.
-- The substrate's natural representation is `Vec (Vec F₂ m) n`
-- (nested Vec).
--
-- Per the structural conversation: polynomial multiplication factors
-- through the ⊗-Hom adjunction. outer = unit of the adjunction at
-- (p, q); anti-diag-sum = a specific Hom-element. This primitive
-- names what the polynomial multiplication slice (slice 1 of the
-- last trio) constructed concretely.
--
-- Per [[feedback-categorical-name-first]]: tensor product is the
-- standard categorical name; the universal property IS the inference
-- rule for bilinear maps.
--
-- This is the BILINEAR extension primitive, complementing the LINEAR
-- extension provided by Adjunction (#4):
--
--   Adjunction (#4):     Hom(Free A, B) ≅ A → B   (linear extension)
--   TensorProduct (#7):  Bilinear(V × W, U) ≅ Linear(V ⊗ W, U)   (bilinear extension)
--
-- Both are universal-property-of-free constructions; ⊗ is the
-- "free bilinear" lift.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

------------------------------------------------------------------------
-- N-1: TensorProduct — the substrate's representation of V ⊗ W.
--
-- For F₂-vector spaces V = F₂^n, W = F₂^m:
--   V ⊗ W ≅ F₂^(n × m)
-- represented as `Vec (Vec F₂ m) n` (n rows of m-vectors).
--
-- Type alias for clarity.
------------------------------------------------------------------------

TensorProduct : ℕ → ℕ → Set
TensorProduct n m = Vec (Vector m) n

------------------------------------------------------------------------
-- N-2: pair — the universal bilinear map (unit of ⊗-Hom adjunction).
--
-- pair p q : TensorProduct n m has at row i the vector p_i · q
-- (where p_i is p's i-th coefficient and · is scalar-by-vector).
--
-- This IS the outer product (= `outer` from Substrate.Algebra.F2.
-- Polynomial); named here at the categorical level as the universal
-- bilinear map.
--
-- Categorical reading: pair is the unit of the ⊗-Hom adjunction at
-- (V, W) — the unique "most general" way to combine an element of
-- V and an element of W into something living in V ⊗ W.
------------------------------------------------------------------------

pair : ∀ {n m} → Vector n → Vector m → TensorProduct n m
pair []      _ = []
pair (a ∷ p) q = (a *ₛ q) ∷ pair p q

------------------------------------------------------------------------
-- N-3: Universal-property statement (structural).
--
-- The universal property of the tensor product: bilinear maps
-- V × W → U correspond bijectively to linear maps V ⊗ W → U.
--
-- At the substrate level, "linear maps V ⊗ W → U" are functions
-- `TensorProduct n m → U` that preserve the +ⱽ structure (and
-- scalar multiplication). The bijection:
--
--   Bilinear(V × W, U) ≅ Linear(V ⊗ W, U)
--
-- is given by:
--   forward:  f : V × W → U      ↦  f' : V ⊗ W → U via f'(pair v w) = f(v, w)
--             then extend linearly
--   backward: f' : V ⊗ W → U     ↦  λ v w → f' (pair v w)
--
-- The forward direction's "linear extension" uses the ⊗-Hom
-- adjunction's homset isomorphism — analogous to how Adjunction (#4)
-- extends a function f : Fin n → Vector m to a Linear n m via
-- linear-from-images.
--
-- This slice packages the BASIC structural object (TensorProduct +
-- pair); the full bilinear↔linear bijection requires more
-- infrastructure (notably "bilinear function" as a record vs general
-- function). Deferred to a follow-on slice.
------------------------------------------------------------------------

-- Documentation-level: the universal property's STATEMENT (not
-- formalised here; requires bilinear-function records to be defined).
--
-- factor-bilinear : ∀ {n m} {U : Set} →
--                   (f : Vector n → Vector m → U) →
--                   IsBilinear f →
--                   TensorProduct n m → U
--
-- factor-bilinear-extends : ∀ {n m} {U} (f) (bilin) (v w) →
--   factor-bilinear f bilin (pair v w) ≡ f v w

------------------------------------------------------------------------
-- N-4: Concrete substrate-relevant maps OUT of TensorProduct.
--
-- These are SPECIFIC linear maps from the tensor product, each
-- corresponding (via the universal property) to a specific bilinear
-- operation.
--
-- For the polynomial multiplication case, the relevant map is
-- `anti-diag-sum` (defined in Substrate.Algebra.F2.Polynomial),
-- which collapses the tensor product to a polynomial of degree n+m.
-- The substrate's `_*P_ = anti-diag-sum ∘ outer` factors polynomial
-- multiplication through the tensor product via this slice's
-- categorical structure.
--
-- Other potential maps out of TensorProduct (for other bilinear
-- operations, deferred):
--   * trace : TensorProduct n n → F₂           — sum of diagonal
--   * inner-product (when n = m): trace ∘ ... or via metric
--   * antisymmetrize : TensorProduct n n → AntisymTensor n
--                                              — produces Λ²(F₂ⁿ)
--   * symmetrize : TensorProduct n n → SymTensor n
--                                              — produces Sym²(F₂ⁿ)
------------------------------------------------------------------------

------------------------------------------------------------------------
-- N-5: Capstone — TensorProduct primitive #7 introduced.
--
-- After this slice, the Category roadmap covers seven primitives:
--
--   #1 Coalgebra (+ FiniteOrder + LagrangeOrder + StructuralGCD) ✓
--   #2 Equalizer ✓
--   #3 Pullback ✓
--   #4 Adjunction (linear-extension) ✓
--   #5 BeckChevalley ✓
--   #6 FreeLinearization — deferred (Prong B / continuous-side)
--   #7 TensorProduct (bilinear-extension) — THIS ✓
--
-- The TensorProduct primitive is THE structural extension of
-- Adjunction (#4) from linear (single-argument) to bilinear
-- (two-argument) universal properties. The ⊗-Hom adjoint pair is
-- the canonical example.
--
-- Substrate instances ready to retrofit via this primitive:
--
--   * Polynomial multiplication: _*P_ = anti-diag-sum ∘ outer is
--     literally the ⊗-Hom adjunction's composition. outer = pair
--     (this slice's universal map); anti-diag-sum = a specific
--     linear map out of TensorProduct. Slice 2 of this trio
--     retrofits.
--
--   * Bivector at dim 4 (Substrate.Algebra.F2.HodgeDim4.Bivector):
--     Λ²(F₂⁴) is the antisymmetric QUOTIENT of F₂⁴ ⊗ F₂⁴. Currently
--     constructed directly; could be re-expressed via TensorProduct
--     + antisymmetrization map. Substantial refactor; deferred.
--
--   * SymBilinForm (generic n-parametric): the symmetric tensor
--     square Sym²(F₂ⁿ). Currently expressed via Σ-typed BilinForm +
--     IsSymmetric predicate. Could re-express via TensorProduct +
--     symmetrization. Refactor deferred.
--
--   * Substrate's various bilinear-form operations (bilinear-form-of,
--     metric pairings, etc.): each is a Linear map out of
--     V ⊗ V → F₂, corresponding (via the universal property) to a
--     bilinear form V × V → F₂. The Bilinearity slice
--     (SymBilinForm.Bilinearity) proves the bilinearity needed for
--     this correspondence.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * **IsBilinear record + factor-bilinear**: full universal
--     mapping property. Requires bilinear-function records.
--
--   * **Linear-out-of-tensor**: characterize linear maps
--     TensorProduct n m → U as a Linear record (with closure
--     under +ⱽ and *ₛ structure on TensorProduct).
--
--   * **Antisymmetrization / symmetrization quotients**: specific
--     linear maps producing Λ²V and Sym²V.
--
--   * **Multi-tensor products** (V ⊗ W ⊗ X): n-ary universal
--     property for n-linear maps. Builds on the binary case.
------------------------------------------------------------------------
