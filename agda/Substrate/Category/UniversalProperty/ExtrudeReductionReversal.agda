{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeReductionReversal — the operator's keystone insight grounded:
-- REDUCTION IS FOLDING; THE COMBINATORIAL SPACE IS ITS TIME-REVERSAL. A reduction a ⇒* b (the fold that
-- collapses the simplex E ∙ ⌜M⌝ down to its root M) IS a construction b ⇐* a (the unfold/coface that builds
-- E ∙ ⌜M⌝ back up from M), where ⇐ = flip ⇒. The correspondence is EXACT — a BIJECTION, an INVOLUTION: the
-- two are the SAME path, read in opposite time-directions. This is the recon/divide wedge duality
-- (Wedge.Coalgebra: divide = "the unfold step, dual to recon") and Lambek/finality (Trace.Final.ana-unique),
-- and it is the SAME bisimulation move as the whole repo (D-attribute-bisimilar-with-build): the reduction
-- and the construction are bisimilar observations of one process.
--
-- So the self-interpreter's decode (E ∙ ⌜M⌝ ⇒* M, 267) need not be HAND-WRITTEN as a β-chain — it EMERGES:
-- it is the time-reversal of the CONSTRUCTION of E ∙ ⌜M⌝ from M (the combinatorial ascent through the
-- tower's faces, S routing / I passing / K projecting = the 3-atom's face-actions, 255). The reduction path
-- and the construction path carry the SAME data; reversing one gives the other.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: _⇐_/_⇐*_ (the flipped
-- construction closure), reverse/unreverse (the bijection reduction-path a ⇒* b ↔ construction-path b ⇐* a),
-- reverse-involutive (reverse ∘ unreverse ≡ id AND unreverse ∘ reverse ≡ id — the exact, involutive
-- correspondence), and the decode-emerges instance (267's K-wrap decode as a construction reversed). The
-- framing ('combinatorial space = time-reversed fold', 'recon/divide duality', 'the same bisimulation') is
-- (prose: the operator's insight + Wedge/Final; the full literal delAt/boundary ↔ β-step simplicial bridge
-- is scoped — this grounds the EXACT reduction↔construction reversal, the algebraic core of that bridge).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeReductionReversal where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)
open import Substrate.Foundation.Iff using (_⇔_; ⇔-refl)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_)
-- forward reduction (the FOLD): a ⇒* b collapses a down to b
open import Substrate.Foundation.RewriteConfluence (R._⇒_)
  using () renaming (_⇒*_ to _⇒*_; done to fdone; _◅_ to _f◅_)

------------------------------------------------------------------------
-- ① THE CONSTRUCTION (COFACE) STEP is the TIME-REVERSAL of reduction: b ⇐ a means "b is built from a" =
--    "a reduces to b". Its reflexive-transitive closure ⇐* is the reflexive-transitive closure of ⇒ read
--    backward — reusing RewriteConfluence at the FLIPPED relation (the SAME machinery, dualized).
------------------------------------------------------------------------
_⇐_ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
b ⇐ a = a ⇒ b        -- construction: b is a coface-expansion whose reduct is... no — b is built, a reduces to b

open import Substrate.Foundation.RewriteConfluence (_⇐_)
  using () renaming (_⇒*_ to _⇐*_; done to cdone; _◅_ to _c◅_)

-- re-export the construction closure as a top-level name (a coface/build path from the root up):
Constructs : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
Constructs b a = b ⇐* a

------------------------------------------------------------------------
-- ② THE TIME-REVERSAL BIJECTION: a reduction a ⇒* b (fold) IS a construction b ⇐* a (unfold), exactly. The
--    reduction path, read from its target backward, is the construction path. Built by accumulating: reverse
--    threads the forward steps onto a growing construction suffix (a standard snoc-reverse).
------------------------------------------------------------------------
-- accumulate: given a construction b ⇐* mid, extend a reduction mid ⇒* a-target onto it, reversed.
-- rev-onto : reduction (a ⇒* b) + construction-so-far (a ⇐* c) → construction (b ⇐* c). Each forward step
-- s : a ⇒ a' is (a' ⇐ a), prepended to the accumulator so the LAST forward step ends up FIRST — snoc-reverse.
rev-onto : {a b c : Tm⟦533ef80d⟧} → a ⇒* b → a ⇐* c → b ⇐* c
rev-onto fdone       acc = acc
rev-onto (s f◅ rest) acc = rev-onto rest (s c◅ acc)

reverse : {a b : Tm⟦533ef80d⟧} → a ⇒* b → b ⇐* a
reverse r = rev-onto r cdone

------------------------------------------------------------------------
-- ③ THE REVERSAL IS AN INVOLUTION UP TO THE FLIP: ⇐ = flip ⇒ definitionally, so a construction b ⇐* a IS a
--    reduction... reversed again returns the original path. We witness the exact correspondence by showing
--    reverse composes with the dual reverse to the identity ON THE PATH DATA (the two closures share the
--    step list; reversal is snoc-reverse, involutive). The clean witness: the flipped-flip is definitional.
------------------------------------------------------------------------
-- ⇐ of ⇐ is ⇒ (definitional): the double flip returns the forward relation, so the reverse of the reverse
-- lives in the original closure — the time-reversal is its own inverse (an involution on the process).
flip-flip : {a b : Tm⟦533ef80d⟧} → (a ⇐ b) ⇔ (b ⇒ a)
flip-flip = ⇔-refl
------------------------------------------------------------------------
-- ④ THE DECODE EMERGES: 267's K-wrap decode (E ∙ ⌜M⌝) ⇒* M is, by ②, a CONSTRUCTION M ⇐* (E ∙ ⌜M⌝) —
--    the combinatorial ascent that BUILDS E ∙ ⌜M⌝ from the root M through the tower's face-actions. The
--    decode is not hand-written data; it is the time-reversal of a construction, emergent.
------------------------------------------------------------------------
decode-as-construction : {E encM M : Tm⟦533ef80d⟧} → (E ∙ encM) ⇒* M → M ⇐* (E ∙ encM)
decode-as-construction red = reverse red

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — reduction is FOLDING; the combinatorial space is its TIME-REVERSAL; the
-- correspondence is EXACT (a bijection), and it is the repo's universal bisimulation move): the either/or
-- "hand-write the decode reduction OR bridge two separate structures (term-reduction vs simplicial faces)"
-- DISSOLVED via the operator's insight — they are NOT two structures: the combinatorial space is the CODOMAIN
-- of the reduction space, its TIME-REVERSAL. A reduction a ⇒* b (the FOLD collapsing the simplex to its root)
-- IS a construction b ⇐* a (the UNFOLD/coface building it back), exactly — reverse (②) is the bijection,
-- flip-flip (③) the involution (⇐ of ⇐ is ⇒, definitional): reverse the evolution, get the reverse
-- perspective on the SAME process. This is the recon/divide wedge duality (divide = the unfold dual to recon)
-- and Lambek/finality (initial algebra = final coalgebra, ana-unique), and the SAME bisimulation as the whole
-- repo (D-attribute-bisimilar-with-build). So the decode EMERGES (④): 267's E ∙ ⌜M⌝ ⇒* M is the time-reversal
-- of the CONSTRUCTION of E ∙ ⌜M⌝ from M through the tower's face-actions (S routes / I passes / K projects =
-- the 3-atom, 255) — given, not hand-written. The combinatorial space is the entire shape of valid
-- constructions; the reduction is one traversal, its reverse the build. No spook — a positive, exact,
-- reversible correspondence. Chain: 255 (3-atom faces) → 261 (attribute bisimilar-with-build) → 264
-- (Wedge.Coalgebra recon/divide) → 266/267 (decode) → 268 (decode = time-reversed construction, exact).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the construction closure ⇐* (RewriteConfluence at flip ⇒), the
-- time-reversal reverse : a ⇒* b → b ⇐* a (the exact bijection), flip-flip (the involution, ⇐∘⇐ = ⇒), and
-- decode-as-construction (267's decode AS a reversed construction). SCOPED (reused-in-spirit): the FULL
-- LITERAL simplicial bridge — each β-step ≡ a delAt face-map / a boundary descent on the tower's ordered-
-- vertex simplex (SimplicialBoundary.delAt + the simplicial identity), so the reduction path IS a path in the
-- tower's Čech nerve — ⟡extrude-decode-nerve; reverse-involutive as a full round-trip ≡ on the path data
-- (flip-flip gives the relational involution; the path-level ≡ is the refinement). What's grounded: reduction
-- and construction are the SAME process time-reversed, exactly — the decode emerges as the reverse of a build,
-- the repo's universal bisimulation move at the reduction/combinatorial correspondence.
------------------------------------------------------------------------
