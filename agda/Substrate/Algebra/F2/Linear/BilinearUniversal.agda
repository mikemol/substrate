------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.BilinearUniversal
--
-- The UNIQUENESS half of the bilinear universal property — the arity-2
-- sibling of `Linear.Universal.linear-extensionality`. A bilinear map's
-- behaviour is DETERMINED by its behaviour on basis PAIRS (eᵢ, eⱼ): two
-- bilinear maps agreeing on every basis pair agree everywhere.
--
-- Together with `BilinearFromImages` (the EXISTENCE half: a bilinear map
-- built from any basis-pair table, with apply₂ f (eᵢ,eⱼ) ≡ f i j), this is
-- the full universal property of the tensor — what `Category.TensorProduct`
-- N-3 / `Category.TensorProduct.Bilinearity` named as the deferred piece.
--
-- The proof does NOT rebuild the sum machinery: each leg of a `Bilinear` IS
-- an arity-1 `Linear` map (its leg-laws are exactly preserves-+/-*ₛ), so the
-- arity-1 `linear-extensionality` applies TWICE — fix the left basis vector
-- and run it on the right leg, then run it on the left leg. (Attempting this
-- is what revealed it is a clean reuse, not the "nested basis-expansion
-- plumbing" an unattempted estimate had walled it as.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.BilinearUniversal where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; sym; trans)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.BilinearFromImages
  using ( Bilinear; apply₂′
        ; preserves-+ₗ; preserves-*ₛₗ; preserves-+ᵣ; preserves-*ₛᵣ
        ; bilinear-from-images; bilinear-from-images-basis )

------------------------------------------------------------------------
-- Each leg of a bilinear map is an arity-1 linear map.
------------------------------------------------------------------------

-- left leg: fix the right argument v; u ↦ B(u, v) is Linear.
left-leg : ∀ {k l n} → Bilinear k l n → Vector l → Linear k n
left-leg B v = record
  { apply        = λ u → apply₂′ B u v
  ; preserves-+  = λ u u' → preserves-+ₗ B u u' v
  ; preserves-*ₛ = λ c u → preserves-*ₛₗ B c u v
  }

-- right leg: fix the left argument u; v ↦ B(u, v) is Linear.
right-leg : ∀ {k l n} → Bilinear k l n → Vector k → Linear l n
right-leg B u = record
  { apply        = λ v → apply₂′ B u v
  ; preserves-+  = λ v v' → preserves-+ᵣ B u v v'
  ; preserves-*ₛ = λ c v → preserves-*ₛᵣ B c u v
  }

------------------------------------------------------------------------
-- Bilinear extensionality: agreement on all basis PAIRS ⟹ agreement
-- everywhere. (linear-extensionality applied twice: right leg per basis
-- row, then left leg.)
------------------------------------------------------------------------

bilinear-extensionality :
  ∀ {k l n} (B B' : Bilinear k l n) →
  ((i : Fin k) (j : Fin l) → apply₂′ B (basis i) (basis j) ≡ apply₂′ B' (basis i) (basis j)) →
  (u : Vector k) (v : Vector l) → apply₂′ B u v ≡ apply₂′ B' u v
bilinear-extensionality B B' agree u v =
  linear-extensionality (left-leg B v) (left-leg B' v)
    (λ i → linear-extensionality (right-leg B (basis i)) (right-leg B' (basis i)) (agree i) v)
    u

------------------------------------------------------------------------
-- Capstone — the UNIVERSAL PROPERTY of the tensor, in full: any bilinear
-- map that matches a basis-pair table IS the free bilinear map of that
-- table (existence = BilinearFromImages, uniqueness = here).
------------------------------------------------------------------------

bilinear-from-images-unique :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (B : Bilinear k l n) →
  ((i : Fin k) (j : Fin l) → apply₂′ B (basis i) (basis j) ≡ f i j) →
  (u : Vector k) (v : Vector l) → apply₂′ B u v ≡ apply₂′ (bilinear-from-images f) u v
bilinear-from-images-unique f B matches u v =
  bilinear-extensionality B (bilinear-from-images f)
    (λ i j → trans (matches i j) (sym (bilinear-from-images-basis f i j)))
    u v
