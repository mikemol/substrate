---
name: feedback_ground_in_tower_build
description: "To ground an object (a group, an attribute) in the witness tower: TAKE it from the tower's BUILD, don't compare against it — its parts ARE the build's parts, read off the build, bisimilar-with-build. The tower inductively constructs the whole chain of symmetry groups; use it."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**When you "ground X in the witness tower", the tower's GROWTH PROCESS already inductively constructs
X — take X FROM the build, do not merely compare X against the tower.** (User, 2026-07-05, on Ⓒ.v4.site:
"the tower's growth process inductively constructs the entire chain of symmetry groups possible as
structure gets more complex. The entire internal structure is provided. So if we have V4, we should take
V4 from the tower's *build* of it, not just compare against the tower." And: "grounding in the build IS
unification.")

**The method** (interned from the user's reference `~/Downloads/ExtrudeSKIKFaces.agda` =
`Category.UniversalProperty.ExtrudeSKIKFaces`, which grounds a simplicial FACE's dimension in
`WitnessTower.FaceSet`): the operator's coalgebra point — *"isn't this just bisimilarity with the tower's
build pattern? any attribute you derive from it can be bisimilar with it."* So:
- The object's PARTS are the build's parts: `weight` recurses through FaceSet's cone vocabulary
  (with-apex / without-apex / apex-bit / base-face); a face IS its build-trace (the cone-choice sequence).
- The object's LAWS are the ELEMENT-SHADOW of the tower's structural laws: `weight-with-apex ≡ suc`
  shadows FaceCount's Pascal cone-step. They are `refl` because the attribute co-varies with the build.
- The local object gets a COORDINATE/stratum in the tower (258's vertices `eᵢ` = the dimension-0 stratum).
- HONEST BOUNDARY (⟡H-overclaim): sharply separate GROUNDED (machine-checked: the fold, the bisimilarity
  laws, the placement) from SCOPED (reused-in-spirit: the full coinductive tower GROWTH; numeric agreements
  cited not re-proven). Never let prose claim what isn't inhabited.

**Worked (Ⓒ.v4.site → `WitnessTower.V4Grounding`):** V₄ is the Klein-four subgroup the tower BUILDS at rung
4 (`WitnessTower.Enumerate.perms 4` = S₄; `KleinCensus`: debut rung 4). So V₄'s carrier = the build's
permutations and its op = the build's `compose` (`FirstAppearance`): `⟦_⟧ : V₄ → Perm 4` (id + the 3
double-transpositions) and `·-is-compose : ⟦ x · y ⟧ ≡ compose ⟦x⟧ ⟦y⟧` — ALL 16 CASES `refl`, so Groups.V4's
`_·_` IS the tower's `compose` under the embedding (⟦_⟧ a homomorphism), never recomputed. The 3 non-id
elements are the double-transpositions (`is-involution`, refl). Because the carrier was the Ⓒ.v4-unified
`Groups.V4.V₄`, this regrounds all 82 dependents on the tower at once.

**Layering:** the grounding module sits ABOVE both the object and the tower (WitnessTower imports Groups/
Algebra, not vice-versa — so a module importing both is cycle-free); place it in WitnessTower.* (or a
grounding namespace, as the reference is in Category.UniversalProperty). A LOW module (e.g. Algebra.*Sites)
cannot import the tower — it stays honest (canonical carrier + real instance) and POINTS at the grounding.

**The GROWTH level (user's further deepening, Ⓖ.cyclic).** The method applies not just to a fixed object
but to a FAMILY that GROWS with the tower's rungs — via bisimilarity. The canonical cyclic group is
Word-based (xFreeCyclic: `Zn-Word` = a word gᵏ, `_Zn-++_` = concat-then-normalize, `Zn-normalize` = mod n).
A word gᵏ IS a build-trace ("apply the generator k times"), so the abstract Word-Zₙ and the tower's ⟨g⟩ ⊆
Sₙ are BISIMILAR coalgebras (iterate the generator, wrap at the rung) — and {Zₙ} GROWS as the tower grows,
collapsing the Word↔tower distinction. This is exactly the piece ExtrudeSKIKFaces SCOPED ("the full
coinductive tower-growth bisimulation") — for a family, REALIZE it. Grounded (WitnessTower.CyclicGrounding):
`pow g k` (word gᵏ = k-fold compose), `pow-hom : pow g (a+b) ≡ compose (pow g a)(pow g b)` (word-concat IS
compose, the (ℕ,+)→⟨g⟩ homomorphism, ANY generator; compose-assoc read off SnGroup's action-faithfulness).
Scoped: the ORDER/WRAP `pow g (suc n) ≡ id` (= Zn-normalize; witnessed generically by
`cyclic-suc-HasOrderPerm` — "expose-generator-not-orbit", one proof for all n).

**The bigger vision (Ⓖ.ground-in-tower / Ⓖ.tower-basis):** the abstract `data`-type group carriers are
build-traces of the tower's Sₙ construction — Cayley's theorem, made constructive. Already built: SymBridge
(tower-perms ≅ Groups.Symmetric, a homomorphism — the WHOLE symmetric group), SnGroup (Sₙ-as-group from
compose), M40Group (order-40 from compose), V4Grounding (the V₄ subgroup), CyclicGrounding (the cyclic
family's concatenation), CyclicCollapse (Ⓖ.cyclic-collapse — the WITNESS that F2.Linear.Permutation.Iterate
IS the tower's pow/order: pow-is-σ-iterate + order-collapse, via SnGroup.apply). KEY FINDING: that
`Iterate` (σ-iterate/HasOrderPerm/σ-iterate-add) is NOT F2-specific — it's over RAW `Fin n → Fin n`, a pure
combinatorial module MISFILED under F2.Linear (the user's "structural duplicate, reverse the dependency"
confirmed).

**⚠ THE TOWER IS NOT THE BASIS (Ⓖ.tower-basis, verified 2026-07-05 — corrects the earlier "reground on the
tower" framing).** "Ground X in the tower" means READ X's attributes/structure off the tower's BUILD (the
method above) — it does NOT mean make the tower the definitional BASIS for F₂-free combinators. The tower is
itself F₂-HEAVY (FaceSet/Codeword/Diagonal/HodgeGradeInvolution all `import Algebra.F2{,.Vector,.Linear}`),
and its Perm-power already BRIDGES to σ-iterate (CyclicCollapse). Grounding `cyclic-suc` "in the tower" would
drag the F₂ tower into everything cyclic — the OPPOSITE of the goal. The invariant under "tower-vs-F2.Linear
as basis" is NEITHER: it is the **F₂-free mod-suc arithmetic below both**. `cyclic-suc` is `(i+1) mod (suc n)`
on Fin — pure Fin/Nat, no Vector/Linear; it "dragged F2.Linear" ONLY by sharing a file with `cyclic-Linear`.
The "46 deps" was Iterate's (already shimmed by Ⓖ.iterate-to-foundation); `Permutation.Cyclic`'s real surface
was 11.

**What landed:** Ⓖ.tower-basis (split) — `cyclic-suc`+`cyclic-suc-toℕ`+`σ-iterate-toℕ`+`cyclic-suc-HasOrderPerm`
extracted to **`Substrate.Algebra.Nat.CyclicSuc`** (F₂-free, BELOW Algebra.F2.Linear by layer; iteration via
Foundation.Function.Iterate, not the F2.Linear-path shim). `Permutation.Cyclic` re-exports it + keeps only the
opaque Linear lift (`cyclic-Linear`/`cyclic-HasOrder`/`cyclic-Linear-basis`) that now FALLS OUT via
basis-permutation-Linear. Ⓖ.tower-basis (de-drag) — 7 generator-only consumers re-pointed to CyclicSuc; 3
fully F₂-freed (Concat, Bridge, Z-x-PhaseAdvance), 2 (Coxeter.Cyclic.Base, CoxeterFin) freed of the Cyclic
edge but still pull `HasOrderPerm` from the F2.Linear `Permutation` module, 2 inherently-F2 (ShiftRowsFace,
Cycle3-FreeLinearization). **Ⓖ.tower-basis Phase 3 (open):** the Fin-iterate shim (`σ-iterate`/`HasOrderPerm`/
`σ-iterate-add`/`HasOrderPerm-multiple`, at `...Permutation.Iterate`) is ALSO F₂-free-but-misfiled — relocate
it out of F2.Linear (the iterate-to-foundation residue) to fully free Base + CoxeterFin.

Remaining groundings: Ⓖ.s3 (S₃=perms 3), Ⓖ.a4 (A₄⊆S₄), Ⓖ.coxeter, Ⓖ.cyclic-order (the wrap, now =
order-collapse), Ⓖ.grounding-spine (register V4/Cyclic groundings as Category structure-instances — the
CyclicGrounding FLOATING advisory). "Grounding in the build IS unification." Related:
[[feedback_v4_carrier_action_gap]].
