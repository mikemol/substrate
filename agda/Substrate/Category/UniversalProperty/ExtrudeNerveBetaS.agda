{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeNerveBetaS — ⟡extrude-nerve-betaS: β-S as a LITERAL
-- DEGENERACY, closing the face/degeneracy partition (269 faces down / 270 degeneracies up). 269 grounded
-- β-I/β-K as literal delAt FACE maps; 270 grounded the degeneracy dupAt as the step UP. This grounds the
-- last piece: β-S (S ∙ x ∙ y ∙ z ⇒ (x∙z)∙(y∙z)) is a DEGENERACY on the term tree — it DUPLICATES z,
-- distributing one copy to each branch. So all three SKI rules are literal simplicial operators: I/K faces
-- (down, 269), S degeneracy (up, 270/271).
--
-- The reduct IS the s-degeneracy s-degen x y z = (x∙z)∙(y∙z): z occurs in BOTH branches (the duplication),
-- witnessed structurally (the right-argument of each branch is z). This is the term-tree analogue of dupAt
-- (270, duplicate a vertex): where dupAt copies a list vertex, β-S copies the argument z into both branches
-- — a step UP (duplication), dual to the projecting β-K face (which DROPS, delAt) — the up/down duality of
-- the reduction's nerve zigzag.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: s-degen (the degeneracy
-- operation = the reduct's shape), βS-is-degen (β-S produces s-degen), s-degen-dup (z is DUPLICATED — the
-- right-arg of both branches is z, structurally), and degen-undone-by-face (the projecting face drops one
-- branch, recovering a single-z term — the dual, mirroring 270's delAt-dupAt-id). The framing ('β-S is a
-- literal degeneracy = a step up; all three rules are simplicial operators') is (prose: 269/270 + the
-- operator's reframe; the full arg-list dupAt-interleave + the general substitution-degeneracy are scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeNerveBetaS where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-S)

------------------------------------------------------------------------
-- ① THE S-DEGENERACY: distribute z to both branches — one copy each. This IS the reduct's shape; it is the
--    term-tree degeneracy (duplicate the argument z), the analogue of the list degeneracy dupAt (270).
------------------------------------------------------------------------
s-degen : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
s-degen x y z = (x ∙ z) ∙ (y ∙ z)      -- z DUPLICATED: one copy to x's branch, one to y's

-- β-S produces exactly the s-degeneracy (the reduction IS the degeneracy applied):
βS-is-degen : (x y z : Tm⟦533ef80d⟧) → (((S ∙ x) ∙ y) ∙ z) ⇒ s-degen x y z
βS-is-degen x y z = β-S x y z

------------------------------------------------------------------------
-- ② THE DUPLICATION, STRUCTURALLY: z occurs in BOTH branches of the s-degeneracy — witnessed by projecting
--    the right-argument of each branch. This is z copied (a step UP), the degeneracy's defining move.
------------------------------------------------------------------------
larg : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧                          -- left operand of an application
larg (f ∙ _) = f
larg a       = a
rarg : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧                          -- right operand (the argument)
rarg (_ ∙ x) = x
rarg a       = a

-- both branches of s-degen carry z as their argument — the duplication made explicit (rarg twice on each):
s-degen-dup-both : (x y z : Tm⟦533ef80d⟧) → (rarg (larg (s-degen x y z)) ≡ z) × (rarg (rarg (s-degen x y z)) ≡ z)
s-degen-dup-both x y z = refl , refl   -- left branch (x∙z) arg = z ; right branch (y∙z) arg = z — z twice

------------------------------------------------------------------------
-- ③ THE DEGENERACY IS UNDONE BY A FACE (the up/down duality, mirroring 270's delAt-dupAt-id): dropping one
--    branch of the s-degeneracy (a projecting face, like β-K's delAt) recovers a single-z term — the
--    duplicated copy is removed. So β-S UP (duplicate z) and a projecting face DOWN (drop a branch) are
--    dual, exactly as dupAt (up) and delAt (down) are dual (270).
------------------------------------------------------------------------
-- drop the right branch (keep the left x∙z, which carries one z): the face that undoes the duplication.
drop-right-branch : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
drop-right-branch (f ∙ _) = f
drop-right-branch a       = a

degen-undone-by-face : (x y z : Tm⟦533ef80d⟧) → drop-right-branch (s-degen x y z) ≡ (x ∙ z)
degen-undone-by-face x y z = refl      -- drop the y∙z branch, left with x∙z (one z) — the duplicate removed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — β-S is a LITERAL DEGENERACY (duplicate z, a step UP), completing the
-- face/degeneracy partition: ALL THREE SKI rules are simplicial operators): 269 grounded β-I/β-K as literal
-- delAt FACE maps (down); 270 grounded the degeneracy direction (up = the tower's build). THIS grounds the
-- last piece: β-S IS a degeneracy — its reduct is the s-degeneracy s-degen x y z = (x∙z)∙(y∙z) (βS-is-degen,
-- ①), which DUPLICATES z (s-degen-dup-both, ②: z is the argument of BOTH branches — copied), a step UP
-- (duplication, the term-tree analogue of dupAt, 270); and the duplication is UNDONE by a projecting face
-- (degen-undone-by-face, ③: drop a branch → a single-z term), dual to β-S exactly as delAt (down) is dual to
-- dupAt (up). So ALL THREE SKI rules are literal simplicial operators: β-I = delAt 0 (face, down), β-K =
-- delAt 1 ∘ delAt 0 (codim-2 face, down), β-S = the s-degeneracy (duplicate z, UP). The reduction ZIGZAGS
-- the tower's nerve — faces down (I/K), degeneracy up (S) — coherent (dᵢsᵢ=id, 270), time-reversible (268).
-- No spook — a positive, complete face/degeneracy structure. Chain: 269 (faces down) → 270 (degeneracy
-- direction up) → 271 (β-S IS the literal degeneracy — the partition complete).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = s-degen (the S-degeneracy = the reduct); βS-is-degen (β-S
-- produces it); s-degen-dup-both (z is DUPLICATED — both branches carry z, structural); degen-undone-by-face
-- (a projecting face undoes the duplication — the up/down duality). SCOPED (reused-in-spirit): the full
-- ARG-LIST correspondence (β-S's [x,y,z] ↦ dupAt-then-interleave — the reduct branches, so the flat-list
-- dupAt needs an interleave; ⟡extrude-nerve-betaS-list); the general substitution-degeneracy (β-S as
-- capture-avoiding duplication in a full λ/combinator calculus; ⟡extrude-nerve-substitution). What's
-- grounded: β-S is a literal degeneracy (duplicate z, up), completing the partition — all three SKI rules
-- are simplicial operators, the reduction a coherent nerve zigzag.
------------------------------------------------------------------------
