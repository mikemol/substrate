---
name: feedback_route_through_witness_tower
description: "The WitnessTower↔Algebra relationship is the CORNERSTONE for threading group-action/orbit context onto algebra — route lemmas THROUGH it, never around it into a bare leaf or a duplicate."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The **WitnessTower↔Algebra relationship is the cornerstone for how the substrate relates anything** —
it threads GROUP-ACTION / orbit context onto algebraic structure. It is NOT a "cycle to avoid" (I
mischaracterized it that way twice; the user corrected both).

**Why:** a lemma/definition with group-action meaning must keep that context. The FOUNDATIONAL fact
lives once in Algebra/Foundation (single source); the WitnessTower module IMPORTS it and ADDS the
group-action meaning. Canonical example: `bool→F₂-xor` lives in `Algebra/F2/FromBool`; the sign
character (`sign : Perm → F₂` = parity of the inversion count) threads through it in
`WitnessTower/Wedge/OrientationRigCatPermSignChirality`. Routing a lemma AROUND the tower into a bare
Algebra leaf (or duplicating it) strips the orbit context and violates single-source-of-truth
([[single-source-truth]]).

**How to apply:**
- Before defining a lemma/type, grep `catalog/reuse-index.md` for a canonical home; if one exists,
  IMPORT it (or `open ... public` re-export if downstream consumers pull it through this module), don't
  re-prove. A duplicate lemma across two homes is a dedup target; the deeper home is the single source.
- A DEFINITION needed by definition-provider modules (ones exporting `data`/`record`) must live in a
  DEF module, NOT a `*.Properties` (proof) module — the def/proof-separation gate enforces this. E.g.
  `Foundation.Bool.boolToℕ` belongs in `Bool.agda`, not `Bool/Properties.agda`.
- Watch for a hand-rolled local `data Bool`/`data ⊥`/etc. that duplicates a Foundation type — replace
  with `open import Foundation.X renaming (…)`; then route derived helpers through the canonical ops
  (e.g. `flip = not`, `bobs = boolToℕ ∘ not`).
- The mechanism to ground on the categorical spine: `open import` the canonical `UPArrow`/generator,
  instantiate `UPArrow` + `Contentful`, wrap as `BackedUP`, cons onto `Category.UniversalProperty.
  Registry.registry` (templates: `FreeMonoidBacked.agda`, `WedgeUP.agda`, `V4Grounding.agda`).
- PRESERVE (do NOT dedup): cross-domain bridges (`Wedge`/`DivStr`/`Trace`/`Mat` multi-homed
  Algebra↔S5 — [[dedup-preserve-crossdomain-bridges]]) and coalgebra orbits (`R/Trace/Orbit*`, `ana`
  into the terminal coalgebra — NOT group-action orbits).

Arc: the route-through-the-tower audit (2026-07-14) — `bool→F₂-xor` dedup (5dcbe31) generalized into
Class A single-source dedups (069d199 det-sign/parity/+-self; b6bcce7 boolToℕ + killed OrbitComplete's
duplicate `data Bool`). Remaining: ⟡A5 (OR-apex derive from `or-xor-and`), Class C (register the
orientation-rig UP / ground CyclicGrounding), ⟡B1 (OrbitKey-S3 through SymBridge).
Related: [[reuse-search-before-feasibility-conclusions]], [[expose-generator-orbit]].
