------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties
--
-- ⟡rig-11 (instances) — ⊕ and ⊗ as instances of the ONE GradedProductOver, and both
-- associators as instances of the ONE GradedAssocOver. The proof-dependent face of
-- OrientationBimonoidal (imports the ordering ops + their proof modules).
--
--   ⊕-over : GradedProductOver _+_ 0 LehmerPath ;  ⊕-assoc-over : GradedAssocOver +-assoc ⊕-over
--   ⊗-over : GradedProductOver _*_ 1 Perm       ;  ⊗-assoc-over : GradedAssocOver *-assoc ⊗-over
--
-- ⊕-assoc-over = ⊕-assoc and ⊗-assoc-over = ⊗-assoc typecheck — rig-5 and rig-8 are the
-- SAME law over different grading monoids.
--
-- The full four-law table, all proven this arc (--safe --without-K, zero postulates):
--   assoc         : ⊕ rig-5 (OrientationSumLaws)   | ⊗ rig-8 (OrientationProductLaws)
--   unit          : ⊕ rig-5                          | ⊗ rig-9 (OrientationProductUnit)
--   comm-iso (r)  : ⊕ rig-6 blockSwap                | ⊗ rig-8-comm factorSwap
--   comm-natural  : ⊕ rig-7 (OrientationSumNat)      | ⊗ rig-10 (OrientationProductNat)
-- So decode is a COMPLETE symmetric bimonoidal functor.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Wedge.Product using (GradedProduct)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_; 0#)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_; 1#)
open import Substrate.WitnessTower.Wedge.OrientationSumLaws using (⊕-assoc)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (⊗-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; GradedAssocOver)

⊕-over : GradedProductOver _+_ 0 LehmerPath
⊕-over = record { u = 0# ; _∧_ = _⊕_ }

⊗-over : GradedProductOver _*_ 1 Perm
⊗-over = record { u = 1# ; _∧_ = _⊗_ }

⊕-assoc-over : GradedAssocOver +-assoc ⊕-over
⊕-assoc-over = ⊕-assoc

⊗-assoc-over : GradedAssocOver *-assoc ⊗-over
⊗-assoc-over = ⊗-assoc

------------------------------------------------------------------------
-- REUSE UNIFICATION (dedup: GradedProductOver and Algebra.Wedge.Product.GradedProduct
-- share the record fingerprint {u, _∧_}). GradedProductOver _+_ 0 IS GradedProduct — the
-- existing fixed-`+` product is the (ℕ,+,0) instance of the general grading-op product.
-- A field-copy bijection (round-trips refl by record η), formalizing the rig-11 equation.
------------------------------------------------------------------------

GP→over : {C : ℕ → Set} → GradedProduct C → GradedProductOver _+_ 0 C
GP→over P = record { u = GradedProduct.u P ; _∧_ = GradedProduct._∧_ P }

over→GP : {C : ℕ → Set} → GradedProductOver _+_ 0 C → GradedProduct C
over→GP P = record { u = GradedProductOver.u P ; _∧_ = GradedProductOver._∧_ P }

GP→over→GP : {C : ℕ → Set} (P : GradedProduct C) → over→GP (GP→over P) ≡ P
GP→over→GP P = refl

over→GP→over : {C : ℕ → Set} (P : GradedProductOver _+_ 0 C) → GP→over (over→GP P) ≡ P
over→GP→over P = refl
