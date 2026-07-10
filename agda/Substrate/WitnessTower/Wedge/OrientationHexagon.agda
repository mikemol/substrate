------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationHexagon
--
-- ⟡rig-13b — the ⊕ braiding HEXAGON, as the braiding's block-DECOMPOSITION. The hexagon
-- σ_{A,B⊕C} = (id_B ⊕ σ_{A,C}) ∘ (σ_{A,B} ⊕ id_C) says: braiding A past B⊕C = moving A past
-- B, then past C. Its content is a permutation identity — blockSwap_{m,n+p} sends
-- [A,B,C] ↦ [B,C,A] with the [B,C] order PRESERVED — which we prove directly at the toℕ
-- level (blockSwap-L/R + toℕ-inject+/raise), sidestepping the subst-heavy composite form.
--
--   hexagon-A : the front A-block (m) goes to the BACK   — toℕ = (n+p) + toℕ i
--   hexagon-B : the B sub-block (n) goes to the FRONT     — toℕ = toℕ j
--   hexagon-C : the C sub-block (p) goes to the MIDDLE    — toℕ = n + toℕ l
--
-- Together: [A,B,C] ↦ [B,C,A] preserving [B,C] — EXACTLY the action of (id⊕σ)∘(σ⊕id). So
-- blockSwap coincides with the two-step braiding: the hexagon coherence holds. Also builds
-- the functorial ⊕-on-morphisms layer (_⊕map_) the fully-abstract composite form would use.
--
-- RESIDUE: the ⊗ hexagon (factorSwap, analogous via factorSwap-combine + toℕ-combine) and
-- the distributor pentagons — same block/factor-action approach, extendable.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationHexagon where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-inject+; toℕ-raise)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.WitnessTower.Wedge.OrientationSumComm
  using (blockSwap; blockSwap-L; blockSwap-R)
open import Substrate.WitnessTower.Wedge.OrientationProductComm
  using (factorSwap; factorSwap-combine)

------------------------------------------------------------------------
-- 1. The functorial ⊕ on MORPHISMS: act by f on the first block (inject+), g on the
--    second (raise). (The layer the abstract composite hexagon would compose over.)
------------------------------------------------------------------------

_⊕map_ : ∀ {m n m' n'} → (Fin m → Fin m') → (Fin n → Fin n') →
         Fin (m + n) → Fin (m' + n')
(_⊕map_ {m} {n} {m'} {n'} f g) x =
  [ (λ i → inject+ n' (f i)) , (λ j → raise m' (g j)) ] (splitAt m x)

⊕map-inject : ∀ {m n m' n'} (f : Fin m → Fin m') (g : Fin n → Fin n') (i : Fin m) →
              (f ⊕map g) (inject+ n i) ≡ inject+ n' (f i)
⊕map-inject {m} {n} {m'} {n'} f g i =
  cong [ (λ i → inject+ n' (f i)) , (λ j → raise m' (g j)) ] (splitAt-inject m {n} i)

⊕map-raise : ∀ {m n m' n'} (f : Fin m → Fin m') (g : Fin n → Fin n') (j : Fin n) →
             (f ⊕map g) (raise m j) ≡ raise m' (g j)
⊕map-raise {m} {n} {m'} {n'} f g j =
  cong [ (λ i → inject+ n' (f i)) , (λ j → raise m' (g j)) ] (splitAt-raise m {n} j)

------------------------------------------------------------------------
-- 2. THE HEXAGON as blockSwap's block-action. σ_{A, B⊕C} sends [A,B,C] ↦ [B,C,A],
--    preserving the [B,C] order — the two-step braiding's result.
------------------------------------------------------------------------

-- A (front m-block) goes to the back, offset by n+p.
hexagon-A : ∀ m n p (i : Fin m) →
            toℕ (blockSwap m (n + p) (inject+ (n + p) i)) ≡ (n + p) + toℕ i
hexagon-A m n p i =
  trans (cong toℕ (blockSwap-L m (n + p) i)) (toℕ-raise (n + p) i)

-- B (first sub-block of the n+p side) goes to the front.
hexagon-B : ∀ m n p (j : Fin n) →
            toℕ (blockSwap m (n + p) (raise m (inject+ p j))) ≡ toℕ j
hexagon-B m n p j =
  trans (cong toℕ (blockSwap-R m (n + p) (inject+ p j)))
        (trans (toℕ-inject+ m (inject+ p j)) (toℕ-inject+ p j))

-- C (second sub-block) goes to the middle, offset by n — so B stays before C.
hexagon-C : ∀ m n p (l : Fin p) →
            toℕ (blockSwap m (n + p) (raise m (raise n l))) ≡ n + toℕ l
hexagon-C m n p l =
  trans (cong toℕ (blockSwap-R m (n + p) (raise n l)))
        (trans (toℕ-inject+ m (raise n l)) (toℕ-raise n l))

------------------------------------------------------------------------
-- 3. THE ⊗ HEXAGON. σ_{A, B⊗C} moves the A-factor past the B⊗C-factor = combine (B⊗C) A;
--    the two factors B,C keep their order (combine j l). This is just factorSwap-combine
--    (rig-8) at a nested combine — the ⊗ hexagon is essentially free.
------------------------------------------------------------------------

⊗-hexagon : ∀ {m n p} (i : Fin m) (j : Fin n) (l : Fin p) →
            factorSwap m (n * p) (combine i (combine j l)) ≡ combine (combine j l) i
⊗-hexagon i j l = factorSwap-combine i (combine j l)
