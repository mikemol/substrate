{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIFVector — ⟡extrude-ski-fvector: the numeric bisimilarity.
-- The f-vector COUNT (how many weight-(suc k) faces a rung-n simplex has) is a BISIMILAR OBSERVATION of the
-- tower's build (D-attribute-bisimilar-with-build, 261) — it follows the SAME Pascal cone recursion as
-- FaceCount.faces. So the concrete weight-grading (261) and the abstract f-vector count (FaceCount) are the
-- same coinductive process, read two ways.
--
-- cw m w = the number of length-m F₂-vectors of weight w. Defined via the CONE-SPLIT (the build move): a
-- length-(suc m) vector is apex-bit ∷ base (FaceSet.cone-split); by 261's weight-with/without-apex, a
-- weight-(suc w) one is EITHER 𝟙∷(weight-w base) OR 𝟘∷(weight-(suc w) base) — the two Pascal summands. So
-- cw satisfies Pascal BY THE BUILD, and cw (suc n)(suc k) ≡ FaceCount.faces n k (both Pascal, same base).
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: cw (the count via the cone
-- recursion), cw-cone (its Pascal step, the build bijection), and fvector-bisim (cw (suc n)(suc k) ≡
-- faces n k) + cw-vertices (cw m 1 counts the vertices). The framing ('bisimilar observation of the build')
-- is (prose: 261's coalgebra point; the full list-enumeration grounding of cw-as-a-literal-count is scoped —
-- cw is the build's own count recursion, justified by the cone-split bijection).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIFVector where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.WitnessTower.FaceCount using (faces)

------------------------------------------------------------------------
-- ① THE f-VECTOR COUNT via the CONE (bisimilar with the build). cw m w counts length-m weight-w vectors.
--    The cone-split (a length-(suc m) vector = apex-bit ∷ base) splits a weight-(suc w) vector into
--    𝟙∷(weight-w base) [apex present] + 𝟘∷(weight-(suc w) base) [apex absent] — Pascal, by the build.
--    Base: length 0 has ONE vector (the empty, weight 0) and none of positive weight.
------------------------------------------------------------------------
cw : ℕ → ℕ → ℕ
cw zero    zero    = suc zero               -- the empty vector: one, of weight 0
cw zero    (suc w) = zero                    -- no positive-weight vector of length 0
cw (suc m) zero    = cw m zero               -- weight 0 ⟹ apex bit 𝟘 forced; base weight 0
cw (suc m) (suc w) = cw m (suc w) + cw m w    -- 𝟘∷(weight suc w) [away] + 𝟙∷(weight w) [over apex] = PASCAL

-- the cone/Pascal step, as a named law (the build bijection at the count level):
cw-cone : (m w : ℕ) → cw (suc m) (suc w) ≡ cw m (suc w) + cw m w
cw-cone m w = refl

cong₂ : {A B C : Set} (f : A → B → C) {a a′ : A} {b b′ : B} → a ≡ a′ → b ≡ b′ → f a b ≡ f a′ b′
cong₂ f refl refl = refl


------------------------------------------------------------------------
-- ② THE NUMERIC BISIMILARITY: the weight-based count cw and FaceCount.faces are the SAME Pascal process.
--    A k-face of Δⁿ is a weight-(suc k) vector over the n+1 = suc n vertices, so cw (suc n) (suc k) counts
--    them — and it equals faces n k. Proof: both satisfy Pascal with matching base, by induction on n.
------------------------------------------------------------------------
cw-zero : (m : ℕ) → cw m zero ≡ suc zero
cw-zero zero    = refl
cw-zero (suc m) = cw-zero m

-- base: cw (suc n) 1 counts the vertices (weight-1 vectors over suc n positions) = suc n = faces n 0.
cw-vertices : (n : ℕ) → cw (suc n) (suc zero) ≡ suc n
cw-vertices zero    = refl
cw-vertices (suc n) =                            -- cw (suc(suc n)) 1 = cw (suc n) 1 + cw (suc n) 0 = suc n + 1
  trans (cong₂ _+_ (cw-vertices n) (cw-zero (suc n))) (+-comm (suc n) (suc zero))

fvector-bisim : (n k : ℕ) → cw (suc n) (suc k) ≡ faces n k
fvector-bisim n       zero    = trans (cw-vertices n) refl        -- faces n 0 = suc n = cw (suc n) 1
fvector-bisim zero    (suc k) = refl                              -- cw 1 (suc (suc k)) = 0 = faces 0 (suc k)
fvector-bisim (suc n) (suc k) =                                    -- both Pascal: cw-cone / FaceCount.cone-step
  trans (cw-cone (suc n) (suc k))
        (cong₂ _+_ (fvector-bisim n (suc k)) (fvector-bisim n k))

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the f-vector COUNT is a bisimilar observation of the tower's build,
-- matching FaceCount.faces via the SAME Pascal recursion): the concrete weight-grading (261) and the
-- abstract f-vector count (FaceCount) are NOT two computations to reconcile — they are the SAME coinductive
-- build read two ways. cw (①) counts weight-w faces via the cone-split (the build move: a face splits into
-- apex-present/absent, 261's weight-with/without-apex), so it satisfies Pascal BY THE BUILD (cw-cone); and
-- fvector-bisim (②) proves cw (suc n)(suc k) ≡ faces n k — both Pascal, matching base (cw-vertices: cw counts
-- the suc n vertices = faces n 0). So the f-vector is bisimilar with the build (D-attribute-bisimilar-with-
-- build), and the vertex/face grading (255-261) numerically agrees with the tower's own f-vector. No spook —
-- a positive numeric identity of two build-observations. Chain: 261 (weight bisimilar-with-build) → 262 (the
-- COUNT bisimilar-with-build = FaceCount.faces).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = cw (the count via the cone recursion), cw-cone (its Pascal step
-- = the build bijection), fvector-bisim (cw (suc n)(suc k) ≡ faces n k), cw-vertices/cw-zero (the base).
-- SCOPED (reused-in-spirit): the FULL list-enumeration grounding that cw m w is LITERALLY the length of the
-- list of weight-w length-m vectors (needs List map/length-++/len-map, absent — would be reinvention); cw is
-- the build's OWN count recursion, justified structurally by the cone-split bijection (261), and its
-- agreement with faces is the numeric bisimilarity. What's grounded: the f-vector count follows the tower's
-- Pascal build and equals FaceCount.faces — the vertex/face geometry numerically IS the tower's f-vector.
------------------------------------------------------------------------
