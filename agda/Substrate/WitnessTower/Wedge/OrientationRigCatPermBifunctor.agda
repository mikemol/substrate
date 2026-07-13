------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermBifunctor
--
-- ⟡rig-UP-cat-perm-bifunctor — THE ⊕-BIFUNCTOR ON MORPHISMS of the symmetric
-- rig category orientationRigCatPerm, and the CONCRETE grade-3 closure of the
-- primality gap it enables.
--
-- THE GAP (OrientationRigCatPermGap, numpy-verified). orientationRigCatPerm's
-- braidings (block-swap rotations, factor-swaps) generate Sₙ only for COMPOSITE
-- n; at PRIME n ≥ 3 they reach only Cₙ (proven at grade 3: ⟨braidings⟩ = C₃ ⊊
-- S₃). THE FIX is a monoidal product on MORPHISMS — a bifunctor gmap⊕ — because
-- with it the adjacent transpositions sᵢ = id ⊕ s₁ ⊕ id become reachable
-- morphisms, and ⟨s₁ … s_{n-1}⟩ = Sₙ (numpy-confirmed n = 3,5,7).
--
-- WHAT THIS MODULE SETTLES (three parts):
--
--   PART 1 — the ⊕-bifunctor functoriality laws (the missing structure).
--     gmap⊕ = blockSum on morphisms (reused from OrientationDistributor). The
--     TWO bifunctor laws not previously in the tree:
--       blockSum-id      : blockSum (id σ) (id τ) = id (m+n)       ( = gmap-id )
--       blockSum-compose : (σ⊕τ) ∘ (σ'⊕τ') = (σ∘σ') ⊕ (τ∘τ')       ( = gmap-∘ )
--     Both via apply-injective (SnGroup faithfulness — pointwise on lookups),
--     splitting each index by splitAt-view and discharging with
--     blockSum-inject/blockSum-raise + apply-id/apply-compose. Together
--     (blockSum , blockSum-id , blockSum-compose) IS the ⊕-bifunctor:
--     Perm _ × Perm _ → Perm _ functorial in both slots.
--
--   PART 2 — adjacent transpositions as bifunctor composites.
--     s₁ : Perm 2 = [1,0] (the grade-2 transposition = the block-swap braiding
--     at grades (1,1)); adjT i j = blockSum (blockSum (id-perm i) s₁)
--     (id-perm j) : Perm ((i+2)+j) = "id ⊕ s₁ ⊕ id". At grade 3 these ARE the
--     two adjacent transpositions on the nose (refl):
--       adjT 0 1 = [1,0,2] (= a0)      adjT 1 0 = [0,2,1] (= a1)
--     — reachable ONLY via the bifunctor (they are not braidings).
--
--   PART 3 — the concrete grade-3 gap-closure ⟨a0,a1⟩ = S₃, in the sibling
--     def-provider OrientationRigCatPermAdjClosure (data AdjGen + 6 witnesses).
--     Referenced here via the refl bridges adjT-is-a0 / adjT-is-a1, closing the
--     argument: the bifunctor composites sᵢ ARE the adjacent transpositions that
--     generate all of S₃. Gap closed: C₃ (braidings) ⊊ S₃ (adjacent transp.).
--
-- HONEST SCOPE — do NOT overclaim full freeness. This delivers (i) the
-- bifunctor STRUCTURE (blockSum-id/compose = gmap-id/∘), (ii) the REACHABILITY
-- sᵢ = id ⊕ s₁ ⊕ id, and (iii) the CONCRETE grade-3 closure ⟨adjacent transp.⟩
-- = S₃. The GENERAL positive UP (orientationRigCatPerm-with-bifunctor is
-- free/initial ∀ grade) needs COXETER COMPLETENESS — "every Perm n is a word in
-- adjacent transpositions". THAT IS NOW PROVEN (commit 9dcdbb7), ∀n, --safe
-- --without-K, zero holes:
--   Ⓐ ⟡coxeter-completeness (CLOSED) :
--       OrientationRigCatPermCoxeterGeneral.Properties.coxeter-complete :
--         {n} (σ : Perm n) → IsPerm σ → CoxGen σ           (Properties.agda:220)
--     via decode-CoxGen — insert-at p IS a bubble-run of adjacent transpositions
--     (idInsert-step), so decode of the Lehmer path is a CoxGen derivation.
-- ⇒ every perm is an adj-word ⇒ an F-hom is determined by F(s₁) ⇒ free.
-- Consumed downstream by OrientationRigCatSymUP / …PermSign / PyAstRewrite.
-- (This header's earlier "NOT yet in the tree" was committed one commit before
-- the close; it was stale — corrected here.)
--
-- This module declares NO data/record — it is a PURE-LEMMA (proof-side) module,
-- so it may import proof-carrying modules (Vec.Properties via SnGroup /
-- OrientationDistributor) without tripping def/proof separation. The datatype
-- AdjGen lives in the self-contained sibling AdjClosure.
--
-- zero postulates, zero holes, --safe --without-K, GREEN.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermBifunctor where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.SnGroup using (apply-injective; apply-compose; apply-id)
open import Substrate.WitnessTower.Wedge.OrientationDistributor
  using (blockSum; blockSum-inject; blockSum-raise)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermAdjClosure using (a0; a1)

------------------------------------------------------------------------
-- PART 1 — THE ⊕-BIFUNCTOR FUNCTORIALITY LAWS.
--
-- gmap⊕ = blockSum : Perm m → Perm n → Perm (m+n) is the action on morphisms.
-- The two functor laws below make it a genuine bifunctor. Both are proven
-- pointwise (apply-injective) by splitting the query index via splitAt-view:
-- the inject+ half is governed by the m-block (σ/σ'), the raise half by the
-- n-block (τ/τ'), exactly as blockSum-inject/blockSum-raise characterize.
------------------------------------------------------------------------

-- gmap-id : blockSum preserves identities.
blockSum-id : ∀ {m n} → blockSum (id-perm m) (id-perm n) ≡ id-perm (m + n)
blockSum-id {m} {n} = apply-injective aux
  where
  aux : (k : Fin (m + n)) →
        lookup (blockSum (id-perm m) (id-perm n)) k ≡ lookup (id-perm (m + n)) k
  aux k with splitAt-view m {n} k
  ... | fromₗ j = trans (trans (blockSum-inject (id-perm m) (id-perm n) j)
                               (cong (inject+ n) (apply-id j)))
                        (sym (apply-id (inject+ n j)))
  ... | fromᵣ i = trans (trans (blockSum-raise (id-perm m) (id-perm n) i)
                               (cong (raise m) (apply-id i)))
                        (sym (apply-id (raise m i)))

-- gmap-∘ : blockSum is functorial in BOTH slots — (σ⊕τ)∘(σ'⊕τ') = (σ∘σ')⊕(τ∘τ').
blockSum-compose :
  ∀ {m n} (σ σ' : Perm m) (τ τ' : Perm n) →
  compose (blockSum σ τ) (blockSum σ' τ')
    ≡ blockSum (compose σ σ') (compose τ τ')
blockSum-compose {m} {n} σ σ' τ τ' = apply-injective aux
  where
  aux : (k : Fin (m + n)) →
        lookup (compose (blockSum σ τ) (blockSum σ' τ')) k
          ≡ lookup (blockSum (compose σ σ') (compose τ τ')) k
  aux k with splitAt-view m {n} k
  ... | fromₗ j =
    trans (apply-compose (blockSum σ τ) (blockSum σ' τ') (inject+ n j))
    (trans (cong (lookup (blockSum σ τ)) (blockSum-inject σ' τ' j))
    (trans (blockSum-inject σ τ (lookup σ' j))
    (sym (trans (blockSum-inject (compose σ σ') (compose τ τ') j)
                (cong (inject+ n) (apply-compose σ σ' j))))))
  ... | fromᵣ i =
    trans (apply-compose (blockSum σ τ) (blockSum σ' τ') (raise m i))
    (trans (cong (lookup (blockSum σ τ)) (blockSum-raise σ' τ' i))
    (trans (blockSum-raise σ τ (lookup τ' i))
    (sym (trans (blockSum-raise (compose σ σ') (compose τ τ') i)
                (cong (raise m) (apply-compose τ τ' i))))))

------------------------------------------------------------------------
-- PART 2 — ADJACENT TRANSPOSITIONS AS ⊕-BIFUNCTOR COMPOSITES.
--
-- s₁ : Perm 2 = [1,0], the grade-2 transposition. (It is also the block-swap
-- braiding braid⊕ at grades (1,1) — OrientationRigCatPerm.B⊕.swPerm 1 1 — but
-- that swPerm is `private` there and carries a subst, so we state s₁ as the
-- concrete image-vector; the identity s₁ = swap of the two grade-1 blocks is
-- OrientationSumComm.blockSwap 1 1 read as a Perm.)
------------------------------------------------------------------------

s₁ : Perm 2
s₁ = suc zero ∷ zero ∷ []                       -- [1,0]

-- sᵢ = id ⊕ s₁ ⊕ id : the adjacent transposition swapping positions i, i+1 of
-- Fin ((i+2)+j). This is precisely "id-perm i ⊕ s₁ ⊕ id-perm j" with the
-- Perm-side ⊕ = blockSum (Part 1). Reachable ONLY via the ⊕-bifunctor.
adjT : (i j : ℕ) → Perm ((i + 2) + j)
adjT i j = blockSum (blockSum (id-perm i) s₁) (id-perm j)

-- At grade 3 the two adjacent transpositions ARE a0 = [1,0,2] and a1 = [0,2,1]
-- on the nose (blockSum reduces definitionally on the concrete small args).
-- These a0,a1 are the generators shown to reach ALL of S₃ in the sibling
-- OrientationRigCatPermAdjClosure — so the bifunctor composites close the gap.
adjT-is-a0 : adjT 0 1 ≡ a0
adjT-is-a0 = refl

adjT-is-a1 : adjT 1 0 ≡ a1
adjT-is-a1 = refl
