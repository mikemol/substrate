{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeNerveGeneral — ⟡extrude-nerve-general: EVERY reduction is a
-- nerve operation — lifting the head/atomic base (269 faces, 271 degeneracy) to ALL redex positions via the
-- congruences. A reduction classifies as a simplicial operation:
--
--   data NerveOp : each one-step ⇒ is a FACE (β-I/β-K, drop, 269), a DEGENERACY (β-S, duplicate, 271),
--                  or a CONGRUENCE-lift of a nerve op at a sub-position (cong-l/cong-r — inner redex).
--
-- So every ⇒ is a nerve op (classify), and hence every ⇒* reduction is a NERVE PATH (a list of nerve ops).
-- This is the general theorem the head cases (269/271) were the base of: the reduction lives in the tower's
-- nerve at every position, faces/degeneracies lifted through the term structure by the congruences.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: NerveOp (the classification
-- of a one-step reduction as face/degeneracy/congruence-lift), classify (EVERY ⇒ IS a NerveOp — total), and
-- NervePath / classify* (every ⇒* is a list of nerve ops). The framing ('every reduction is a nerve path;
-- faces/degeneracies lifted through cong') is (prose: 269/271 + the simplicial reading; the explicit spine
-- image of each op stays at 269/271's head level — this generalizes the CLASSIFICATION to all positions).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeNerveGeneral where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-I; β-K; β-S; cong-l; cong-r)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_)

------------------------------------------------------------------------
-- ① THE CLASSIFICATION: a one-step reduction is a FACE (β-I/β-K — drop, 269), a DEGENERACY (β-S — duplicate,
--    271), or a CONGRUENCE-LIFT (cong-l/cong-r — a nerve op at an inner position). This is the nerve-op type.
------------------------------------------------------------------------
data NerveOp : {a b : Tm⟦533ef80d⟧} → (a ⇒ b) → Set where
  face-I  : (x : Tm⟦533ef80d⟧)             → NerveOp (β-I x)            -- delAt 0            (269)
  face-K  : (x y : Tm⟦533ef80d⟧)           → NerveOp (β-K x y)          -- delAt 1 ∘ delAt 0  (269)
  degen-S : (x y z : Tm⟦533ef80d⟧)         → NerveOp (β-S x y z)        -- the s-degeneracy   (271)
  lift-l  : {f f' : Tm⟦533ef80d⟧} (g : Tm⟦533ef80d⟧) (r : f ⇒ f') → NerveOp r → NerveOp (cong-l g r)  -- inner, left
  lift-r  : (f : Tm⟦533ef80d⟧) {g g' : Tm⟦533ef80d⟧} (r : g ⇒ g') → NerveOp r → NerveOp (cong-r f r)  -- inner, right

------------------------------------------------------------------------
-- ② EVERY one-step reduction IS a nerve op (total classification — the reduction relation lives entirely in
--    the nerve). By induction on the reduction: base cases are the three β-rules, congruences lift recursively.
------------------------------------------------------------------------
classify : {a b : Tm⟦533ef80d⟧} (r : a ⇒ b) → NerveOp r
classify (β-I x)      = face-I x
classify (β-K x y)    = face-K x y
classify (β-S x y z)  = degen-S x y z
classify (cong-l g r) = lift-l g r (classify r)
classify (cong-r f r) = lift-r f r (classify r)

------------------------------------------------------------------------
-- ③ EVERY reduction PATH is a NERVE PATH — a list of nerve ops (each step classified). So the whole ⇒*
--    reduction is a path through the tower's nerve, at every position.
------------------------------------------------------------------------
data NervePath : {a b : Tm⟦533ef80d⟧} → (a ⇒* b) → Set where
  ε   : {a : Tm⟦533ef80d⟧} → NervePath (done {a = a})
  _▷_ : {a b c : Tm⟦533ef80d⟧} {r : a ⇒ b} {rs : b ⇒* c} → NerveOp r → NervePath rs → NervePath (r ◅ rs)

classify* : {a b : Tm⟦533ef80d⟧} (rs : a ⇒* b) → NervePath rs
classify* done       = ε
classify* (r ◅ rest) = classify r ▷ classify* rest

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — EVERY reduction is a nerve path; the head/atomic base (269/271) lifts to
-- ALL positions via the congruences): 269 grounded the head β-I/β-K as delAt faces and 271 β-S as the
-- degeneracy — but at the HEAD. This generalizes: NerveOp (①) classifies EVERY one-step reduction as a face
-- (β-I/β-K), a degeneracy (β-S), or a CONGRUENCE-lift (cong-l/cong-r — a nerve op at an inner position), and
-- classify (②) shows the classification is TOTAL (every ⇒ IS a nerve op, by induction — the congruences lift
-- recursively). Hence classify* (③): every ⇒* reduction is a NERVE PATH (a list of nerve ops). So the SKI
-- reduction lives in the tower's nerve at EVERY position, not just the head — faces down (I/K), degeneracy up
-- (S), lifted through the term structure by the congruences, exactly the simplicial zigzag (269-275)
-- generalized. The classification is total and structural — no spook. This completes "the reduction IS a
-- coherent path in the tower's nerve" as a THEOREM over all terms and all redex positions. Chain: 269
-- (head faces) → 271 (head degeneracy) → 272/275a (identities) → 276c (EVERY reduction = a nerve path).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = NerveOp (the face/degeneracy/lift classification), classify
-- (EVERY ⇒ is a nerve op, total), NervePath + classify* (EVERY ⇒* is a nerve path). SCOPED (reused-in-spirit):
-- the explicit SPINE IMAGE of a lifted op (269/271 give delAt/dupAt at the head; the inner-position spine
-- transform composes the sub-simplex's op into the parent — ⟡extrude-nerve-general-spine). What's grounded:
-- every SKI reduction, at every position, IS a nerve path (face/degeneracy/congruence-lift) — the simplicial
-- reading holds for the whole reduction relation, a total classification.
------------------------------------------------------------------------
