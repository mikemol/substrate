---
name: feedback_domain_skin_over_category
description: "domain/literature terminology is a THIN RENAMING SKIN over the substrate's categorical primitives (the AsNamed pattern) — preserve the domain terms as named legs, never discard them for generic CT names; CT is load-bearing, domain is the skin, the renaming IS the bridge."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

User directive (2026-06-12, building the evidence-logic tier): the domain
terminology — verdict / evidence / bias / holonomy / Nedge / warrant, i.e. the
terms the user uses in their documents AND the terms the literature uses for the
same ideas — is **CRITICAL and must NOT be discarded.** These terminology
bridges are the point. But: make the domain terminology a **thin skin over the
underlying category theory.** The categorical primitive is load-bearing; the
domain term is a *renaming projection* of it. "A really good use of the
`using … renaming` pattern."

**Why:** I built `Logic/Evidence/` bottom-up as bare `data` + functions +
`refl`, floating free of `Category/*` — every theorem a hand-rolled instance of
a structure the substrate already names. That loses cross-navigability (the
whole convergence goal) and under-applies categorical-name-first. The fix is NOT
to rename the domain away into CT jargon (that loses the literature/document
bridge) — it is to make the domain term the *named leg* of the categorical
skeleton, so both coexist and each is provably the other.

**How to apply:** build the categorical INSTANCE, then the domain module is a
2-line `open Category.X.AsNamed inst renaming (named-thing to domainName)` — the
`Functor.AsNamed` pattern (legs: `AutomorphismGroup.AsFunctor`, etc.). Where no
AsNamed skeleton exists yet for the primitive, either add a thin one or rename
the record's field projections directly. The concrete op is defined once (the
real computational content), wrapped as the categorical instance (the
load-bearing witness), and re-exported under the domain name.

Map for the evidence tier (the planned refactor onto its categorical spine):
- joiners `∧E/∨E/⊕E/⊗E` → `Category.CommutativeMonoid` (×4; record = R,_+R_,0R,
  assoc,identityˡ,identityʳ,comm — all my laws fit, identityˡ = comm∘identityʳ).
- `swapE`/`notE`,`intertwine`,De Morgan → `DaggerCategory.AsNamed` (involution).
- `verdict-kernel` / no-collapse → `Coequalizer` of the kernel pair of `verdict`
  (verdict = the regular epi; faithful-refines-verdict = its universal property),
  registered in `UniversalProperty/Registry`.
- phase / H² (`[N,S]=−id`) → `Cocycle` / `Algebra.IsomorphicCocycle` / `Cocycles/`.
- `recode` wedge; exp⊣log atlas → `Adjunction` / `FreeUniversalProperty` (an
  equivalence; the look = a non-faithful functor, residue = its kernel).

**Two more facets (same directive):**
- CONCRETIZATION. The domain skin is not just naming — it is the GROUNDING a
  reviewer demands: pure categorical language invites "you named a Coequalizer —
  where IS it?", and the domain witness (the actual verdict map, the dual rail)
  is the answer. The realizability charter applied to the proof tier: the
  categorical claim is witness-bearing; the domain instance is the witness.
- INSTRUMENT SYNERGY, "better than refl." el-atlas's depsort instrument is
  DESIGNED to discover structural equivalences (for homotopical consolidation +
  structural normalization — the W2 "joiner pairs" EQUAL/ISO verdicts, the W11
  2-cell separation, the W19 extclass). So the loop: the instrument DISCOVERS a
  structural equivalence (domain-X ≃ categorical-Y); the categorical layer PROVES
  it; the domain skin CONCRETIZES it. The bridge then need not be a bare `refl`
  (defeq, opaque, the OOM-heavy enumeration kind) — it can be a PROVED
  equivalence with content (iso / equivalence-of-categories / natural-iso / path),
  which is "better than refl": stronger, structural, and the thing the instrument
  was built to find. Renaming (defeq) is the floor; the discovered-and-proved
  equivalence is the rich bridge.

Links: [[project_named_categorical_structure_skeletons]], [[feedback_categorical_name_first]], [[feedback_skeleton_as_pullback]], [[feedback_wedge_not_projection]], [[project_realizability_charter_arc]], [[project_el_atlas_substrate_congruence]].
