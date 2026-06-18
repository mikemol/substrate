------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.MultilinearUniversal  (ⁿ̌ — uniqueness half)
--
-- The GENERIC arity-n rung of the multilinear extensionality ladder: an
-- n-linear map is determined by its values on basis n-TUPLES. The fold of
-- `linear-extensionality` over a `Vec ℕ n` of arities — the "generator of
-- generators" at the uniqueness side. It IS the proof the lower arities are
-- instances of: `bilinear-extensionality` (n=2, β̌) is now literally this
-- theorem read through a `Bilinear → IsMultilinear (k∷l∷[])` adapter (see
-- `BilinearUniversal`), and `linear-extensionality` (n=1) is the base it
-- folds. (The Bilinear record bundles curried arguments + named leg-laws for
-- ergonomic consumption; this generic form takes uncurried `Args` and the
-- unbundled `IsMultilinear` predicate so the arity can fold — the adapter
-- bridges the two representations. The earlier standalone n=3 rung was
-- redundant once this existed and has been removed.)
--
-- The arguments are kept UNCURRIED: `ap : Args ks → Vector m`, a
-- heterogeneous product `Args ks = Vector k₀ × ⋯ × Vector kₙ₋₁ × ⊤`. The
-- codomain stays `Vector m` at every depth, so the induction NEVER needs a
-- module structure on the codomain (the currying that would force that is
-- exactly what the uncurried representation avoids). The proof peels slot 0
-- with `linear-extensionality` and recurses on the tail — the per-basis
-- residual is itself an n-1-linear map, the induction hypothesis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.MultilinearUniversal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Linear using (Linear; apply; preserves-+; preserves-*ₛ)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)

------------------------------------------------------------------------
-- The uncurried argument tuple, its basis-index tuple, and the
-- index→basis-vector map. All three fold over the Vec of arities.
------------------------------------------------------------------------

-- Args ks = Vector k₀ × ⋯ × Vector kₙ₋₁ × ⊤  (heterogeneous product).
Args : ∀ {n} → Vec ℕ n → Set
Args []       = ⊤
Args (k ∷ ks) = Vector k × Args ks

-- A choice of basis index for each slot.
BasisIndices : ∀ {n} → Vec ℕ n → Set
BasisIndices []       = ⊤
BasisIndices (k ∷ ks) = Fin k × BasisIndices ks

-- Realise a basis-index tuple as the corresponding tuple of basis vectors.
basis-tuple : ∀ {n} {ks : Vec ℕ n} → BasisIndices ks → Args ks
basis-tuple {ks = []}     tt      = tt
basis-tuple {ks = k ∷ ks} (i , j) = basis i , basis-tuple j

------------------------------------------------------------------------
-- Multilinearity, stated recursively over the argument structure: linear
-- in slot 0 (for every fixing of the rest), and multilinear in the rest
-- (for every fixing of slot 0). No record needed; the predicate folds.
------------------------------------------------------------------------

-- "h : Vector k → Vector m is F₂-linear" as a bare pair of laws (so a
-- Linear can be assembled from it without bundling up front).
IsLinear : ∀ {k m} → (Vector k → Vector m) → Set
IsLinear {k} h = ((u v : Vector k) → h (u +ⱽ v) ≡ (h u +ⱽ h v))
               × ((c : F₂) (v : Vector k) → h (c *ₛ v) ≡ (c *ₛ h v))

IsMultilinear : ∀ {n} → (ks : Vec ℕ n) → (m : ℕ) → (Args ks → Vector m) → Set
IsMultilinear []       m f = ⊤
IsMultilinear (k ∷ ks) m f =
    ((rest : Args ks) → IsLinear (λ u → f (u , rest)))
  × ((u : Vector k) → IsMultilinear ks m (λ rest → f (u , rest)))

------------------------------------------------------------------------
-- Multilinear extensionality: two multilinear maps agreeing on every basis
-- TUPLE agree everywhere. The generic fold of linear-extensionality.
------------------------------------------------------------------------

multilinear-extensionality :
  ∀ {n} {ks : Vec ℕ n} {m}
  (f g : Args ks → Vector m) →
  IsMultilinear ks m f → IsMultilinear ks m g →
  ((idx : BasisIndices ks) → f (basis-tuple idx) ≡ g (basis-tuple idx)) →
  (xs : Args ks) → f xs ≡ g xs
multilinear-extensionality {ks = []}     f g _            _              agree tt        = agree tt
multilinear-extensionality {ks = k ∷ ks} f g (lin , deep) (lin' , deep') agree (u , rest) =
  linear-extensionality
    (record { apply = λ u → f (u , rest)
            ; preserves-+  = proj₁ (lin rest)
            ; preserves-*ₛ = proj₂ (lin rest) })
    (record { apply = λ u → g (u , rest)
            ; preserves-+  = proj₁ (lin' rest)
            ; preserves-*ₛ = proj₂ (lin' rest) })
    (λ i → multilinear-extensionality
             (λ r → f (basis i , r)) (λ r → g (basis i , r))
             (deep (basis i)) (deep' (basis i))
             (λ j → agree (i , j))
             rest)
    u
