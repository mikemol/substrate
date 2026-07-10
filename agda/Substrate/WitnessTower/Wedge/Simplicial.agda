------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.Simplicial
--
-- (CORRECTED.) An earlier version of this module called `insert-at` a "coface"
-- and gestured at a cosimplicial identity δⱼδᵢ = δᵢδⱼ₋₁ for it. That was wrong.
-- `insert-at` is ORDER-SENSITIVE: it decorates the witnessing step with an
-- insertion CHOICE — the Lehmer digit (WitnessTower.LehmerPath: decode (l ◂ p) =
-- insert-at p (decode l)). So that identity is an UNINHABITED proposition — an
-- honest proof attempt WALLS (the heads don't unify), and what holds is its
-- negation (the choice matters). `insert-at`'s non-commutation IS the permutohedron.
--
-- The honest picture is TWO SIDES bridged by the wedge:
--
--   FORGETFUL (order-INsensitive) — the nerve faces `delAt` (dᵢ, delete a vertex).
--     Order-preserving, so the simplicial identities DO hold:
--       SimplicialBoundary.simplicial : dᵢ d_{suc j} = dⱼ dᵢ  (i ≤ j), arbitrary n.
--     The ordering is already forgotten; everything commutes; this is the final
--     simplex (WitnessTower.WholeTower's underlying shape).
--
--   FREE (order-SENSITIVE) — the Lehmer step `insert-at` = the graded recon. Each
--     step records a CHOICE r : Fin (suc n) (the insertion slot). Distinct choices
--     give distinct results (`choice-injective`); nothing commutes. The n!
--     choice-sequences are the permutohedron P_{n-1} vertices = Sₙ, whose edges are
--     adjacent transpositions = the Coxeter generators (cf. FourPointReflection).
--
--   THE WEDGE is the adjunction between them: a ≡ recon q b r. The residue r is the
--     ORIENTATION — the counit-defect the forgetful side drops and the free side
--     keeps. Made explicit in WitnessTower.Wedge.Adjunction.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.Simplicial where

open import Substrate.Foundation.Nat using (ℕ; suc; _≤_)
open import Substrate.Foundation.Fin using (Fin; zero)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.SimplicialBoundary using (delAt; simplicial)
open import Substrate.Algebra.Wedge.Graded using (GradedWedge; recon; gcell)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded; tower-step)

------------------------------------------------------------------------
-- 1. THE FORGETFUL / ORDER-INSENSITIVE SIDE: the nerve faces and THE simplicial
--    identity. delAt is order-preserving, so it commutes with itself per the
--    keystone dᵢd_{suc j} = dⱼdᵢ — for arbitrary n. (Re-exported from
--    SimplicialBoundary; this is the map the identity genuinely lives on.)
------------------------------------------------------------------------

face : {A : Set} → ℕ → List A → List A
face = delAt

simplicial-identity : {A : Set} (i j : ℕ) → i ≤ j → (xs : List A) →
                      face i (face (suc j) xs) ≡ face j (face i xs)
simplicial-identity = simplicial

------------------------------------------------------------------------
-- 2. THE FREE / ORDER-SENSITIVE SIDE: the Lehmer step = the graded recon. It
--    records an insertion choice; there is NO cosimplicial identity — the choice
--    matters (choice-injective), and that non-commutation is the permutohedron.
------------------------------------------------------------------------

lehmer-step : (n : ℕ) → Fin (suc n) → Perm n → Perm (suc n)
lehmer-step n r σ = insert-at r σ

lehmer-step-is-recon : (n : ℕ) (r : Fin (suc n)) (σ : Perm n) →
                       lehmer-step n r σ ≡ recon tower-graded n σ r
lehmer-step-is-recon n r σ = refl

-- the CHOICE is faithfully recorded: distinct insertion slots give distinct
-- results. (The seed of order-sensitivity — no cosimplicial collapse.)
choice-injective : (n : ℕ) {r r′ : Fin (suc n)} (σ : Perm n) →
                   lehmer-step n r σ ≡ lehmer-step n r′ σ → r ≡ r′
choice-injective n {r} {r′} σ eq = cong (λ v → lookup v zero) eq

------------------------------------------------------------------------
-- 3. THE WEDGE = the adjunction unit. A grade-(n+1) perm decomposes against its
--    base at grade n, recording the ORIENTATION r as the wedge remainder. The
--    forgetful side (§1) drops r; the free side (§2) keeps it; the wedge is the
--    arrow between, its remainder the relative orientation. (Adjunction made
--    explicit in WitnessTower.Wedge.Adjunction.)
------------------------------------------------------------------------

wedge : (n : ℕ) (σ : Perm n) (r : Fin (suc n)) →
        GradedWedge tower-graded n (insert-at r σ) σ
wedge n σ r = tower-step n σ r

orientation-recorded : (n : ℕ) (σ : Perm n) (r : Fin (suc n)) →
                       gcell (wedge n σ r) ≡ r
orientation-recorded n σ r = refl
