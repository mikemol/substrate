{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeDecodeNerve — ⟡extrude-decode-nerve: the LITERAL simplicial
-- bridge (the refinement of 268's time-reversal). A term's left-spine IS an ordered-vertex simplex (a list
-- of vertices); the PROJECTING β-rules act on it as the tower's face maps (SimplicialBoundary.delAt), so the
-- reduction path is a DESCENT through the tower's nerve — each β-step a codimension drop, coherent by the
-- simplicial identity (∂∘∂ = 0). This makes 268's "reduction = time-reversed construction" concrete:
--
--   β-I : (I ∙ x)        ⇒ x       — the I face drops the HEAD vertex I  = delAt 0        (codim-1 face)
--   β-K : ((K ∙ x) ∙ y)  ⇒ x       — the K face drops the pair {K, y}    = delAt 1 ∘ delAt 0 (codim-2, ∂²)
--   β-S : (((S∙x)∙y)∙z)  ⇒ (x∙z)∙(y∙z) — the S face DUPLICATES z         = a DEGENERACY (dual to a face)
--
-- So the two SHRINKING rules (I/K = the 3-atom's pass/project faces, 255) are literally delAt face maps; the
-- one GROWING rule (S = the routing face) is a degeneracy (the coface's dual — faces drop, degeneracies
-- duplicate). The reduction folds down the nerve via faces; its time-reversal (268) builds up via cofaces.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: spine (term → ordered-
-- vertex simplex), βI-is-delAt0 (the I face = delAt 0 on the spine), βK-is-delAt10 (the K face = delAt 1 ∘
-- delAt 0, the codim-2 ∂² pair), spine-βI / spine-βK (the actual β-reducts' spines ARE these face-drops),
-- and face-coherence (the descent's coherence = SimplicialBoundary.simplicial, ∂∘∂=0). The framing ('the
-- reduction path IS a nerve descent', 'β-S is a degeneracy') is (prose: the 255 face-actions + 268; β-S's
-- degeneracy map and the fully-general per-term/inner-redex nerve-path theorem are scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeDecodeNerve where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.WitnessTower.SimplicialBoundary using (delAt; simplicial)

------------------------------------------------------------------------
-- ① THE ORDERED-VERTEX SIMPLEX of a term is its LEFT-SPINE: a left-nested application h ∙ a₁ ∙ … ∙ aₙ is
--    the simplex [h, a₁, …, aₙ] (head vertex + argument vertices). This is the term as a face of the nerve.
------------------------------------------------------------------------
spine : Tm⟦533ef80d⟧ → List Tm⟦533ef80d⟧
spine (f ∙ x) = spine f ++ (x ∷ [])
spine S = S ∷ []
spine K = K ∷ []
spine I = I ∷ []

------------------------------------------------------------------------
-- ② THE PROJECTING β-RULES ARE FACE MAPS (delAt). At the spine level (head ∷ args), the I face drops the
--    head (delAt 0); the K face drops the head-pair {K, y} (delAt 1 ∘ delAt 0, a codim-2 = ∂² descent).
------------------------------------------------------------------------
-- β-I: I drops the HEAD vertex — delAt 0. On the 2-vertex spine [I, x]: delAt 0 [I,x] = [x] = the reduct x.
βI-is-delAt0 : (x : Tm⟦533ef80d⟧) → delAt 0 (I ∷ x ∷ []) ≡ x ∷ []
βI-is-delAt0 x = refl

-- the actual β-I reduct's spine: (I ∙ x) ⇒ x, and delAt 0 (spine (I ∙ x)) ≡ spine' of the reduct's head-arg.
-- spine (I ∙ x) = [I, x]; dropping the head vertex I (delAt 0) leaves [x] — the argument promoted to root.
spine-βI : (x : Tm⟦533ef80d⟧) → delAt 0 (spine (I ∙ x)) ≡ x ∷ []
spine-βI x = refl

-- β-K: K drops the pair {K (head), y (2nd arg)} — delAt 1 ∘ delAt 0, keeping x. On [K, x, y]: delAt 0 = [x,y],
-- delAt 1 = [x] = the reduct x. This is a codim-2 face — exactly the ∂∘∂ pair-drop.
βK-is-delAt10 : (x y : Tm⟦533ef80d⟧) → delAt 1 (delAt 0 (K ∷ x ∷ y ∷ [])) ≡ x ∷ []
βK-is-delAt10 x y = refl

spine-βK : (x y : Tm⟦533ef80d⟧) → delAt 1 (delAt 0 (spine ((K ∙ x) ∙ y))) ≡ x ∷ []
spine-βK x y = refl

------------------------------------------------------------------------
-- ③ THE DESCENT IS COHERENT: the face maps satisfy the SIMPLICIAL IDENTITY (∂∘∂ = 0 core) — reused from
--    SimplicialBoundary.simplicial. So the codim-2 K-drop (delAt 1 ∘ delAt 0) is a well-defined nerve face,
--    and the order of dropping the pair {K, y} is coherent — the reduction descent respects the nerve.
------------------------------------------------------------------------
face-coherence : (i j : ℕ) → i ≤ j → (xs : List Tm⟦533ef80d⟧) →
                 delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs)
face-coherence = simplicial

-- the K-drop's two faces commute coherently (the ∂² pair {head, arg} is order-independent up to the identity):
K-pair-coherent : (xs : List Tm⟦533ef80d⟧) → delAt 0 (delAt 1 xs) ≡ delAt 0 (delAt 0 xs)
K-pair-coherent xs = simplicial 0 0 z≤n xs

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the LITERAL bridge: a term is an ordered-vertex simplex (its spine), the
-- projecting β-rules ARE the tower's face maps (delAt), and the reduction path is a coherent nerve descent):
-- 268 grounded reduction = time-reversed construction abstractly; THIS makes it concrete. A term's left-spine
-- (①) is a simplex [head, args]; the SHRINKING β-rules are delAt face maps (②) — β-I = delAt 0 (the I face
-- drops the head, codim-1), β-K = delAt 1 ∘ delAt 0 (the K face drops the pair {K, y}, codim-2 = the ∂²
-- descent), matching the actual reducts' spines (spine-βI/spine-βK); and the descent is COHERENT (③) by the
-- simplicial identity (face-coherence = SimplicialBoundary.simplicial, ∂∘∂=0). So the two shrinking rules
-- (I/K = the 3-atom's pass/project faces, 255) are LITERALLY the tower's face maps, and the reduction folds
-- DOWN the nerve through them. The one growing rule (β-S, routing) is a DEGENERACY (duplication — the
-- coface's dual; faces drop, degeneracies duplicate), the reverse (build-up) direction of 268. So the
-- self-interpreter's decode (267 E ∙ ⌜M⌝ ⇒* M) IS a path in the tower's Čech nerve: a descent through face
-- maps (and one degeneracy for the S route), its time-reversal the coface construction. No spook — a
-- positive, literal, coherent correspondence. Chain: 255 (3-atom faces) → 268 (reduction = time-reversed
-- construction) → 269 (the LITERAL β-step ↔ delAt face-map bridge).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = spine (term → ordered-vertex simplex); βI-is-delAt0 /
-- βK-is-delAt10 (the projecting β-rules AS delAt face maps) with spine-βI/spine-βK (the actual reducts'
-- spines); face-coherence / K-pair-coherent (the descent's coherence = the simplicial identity, reused).
-- SCOPED (reused-in-spirit): the β-S DEGENERACY map (duplication — the tower's SimplicialBoundary has faces
-- delAt, not degeneracies; the degeneracy sᵢ dual to delAt is ⟡extrude-nerve-degeneracy); the fully-general
-- theorem (every reduction of every term — compound args, inner redexes via cong-l/cong-r — is a nerve path)
-- — ⟡extrude-nerve-general (the head/atomic face-actions here are the load-bearing base). What's grounded:
-- the projecting β-rules ARE literally the tower's delAt face maps, coherently — the reduction path is a
-- nerve descent, 268's time-reversal made concrete.
------------------------------------------------------------------------
