---
name: project_bridge_indexes_algebra_category
description: "the substrate's bridge-indexes (UP-Registry / Wedge-sphere / el-atlas WITNESS_RELATIONS), the Algebra∥Category non-convergence gap (parallel structure hierarchies, no bridge), and the circle-keying convergence target."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

**The repo HAS bridge-indexes (plural, scattered, NOT unified, NOT keyed by circles):**
- `Category.UniversalProperty.Registry` — THE index: typechecked `BackedUP` bridges
  (compile = certify; "the registry cannot be padded with vacuous claims") + an
  explicit COVERAGE = unification metric ("grow this list to unify the repo"). Only 4
  entries now (eq, Z3, Z5, crt=CRT). Indexes universal-PROPERTY bridges
  (Equalizer/CRT/Free/Limit/units), NOT structure-instances. The pre-commit gate
  `check_up_nonvacuity.sh` enforces non-vacuity.
- `Algebra.Wedge.Registry` — the wedge SPHERE: roots (objects ℕ/F₂/ℤ/List/sq-zero/⊤-div)
  + `WedgeIso` (invertible morphisms) + `Bridge` (non-invertible cross-root edges: ℕ↠F₂
  parity, ℕ↪ℤ inclusion); "roots as vertices, isos+bridges as edges, coherence closing
  it = the sphere".
- el-atlas `WITNESS_RELATIONS` (tools/el-atlas-depsort + cotype) — claim-pair → bridge
  (JOINED/iso / partition-complement / strict-containment / disjoint-by-type / EQUAL /
  ISO-WITH-REFRAMING). **CIRCLES = "stable homology classes of the claim complex"**; a
  2nd-order joiner = "the missing positive half of every circle" → bridges CLOSE circles.
- + dozens of `*Bridge.agda` modules; `Category.OrphanAudit` = the dual (what is NOT
  connected). v4cat MCP = a runtime breaks/witnesses graph (not a repo file).

**ALGEBRA ∥ CATEGORY non-convergence (confirmed 2026-06-12, mechanically):** `Algebra.
{Magma,Semigroup,Monoid,Group,…}` import 0 `Category`; `Category` imports an Algebra
structure-record in ~1 module; TWO parallel `record Monoid`/`Group` families (Algebra.*
vs Category.{CommutativeMonoid, FreeMonoid, …}); no delooping bridge; UP-Registry does
NOT cover Algebra structures. So **grounding in `Algebra.Group` is OFF the categorical
spine.** My categorical-grounding advisory's old "exclude Algebra as infra-BELOW-Category"
was a FALSE assumption — they are PARALLEL, not stacked. CONVERGENCE TARGET: bridge
Algebra→Category (deloop Monoid→one-object Category / Group→groupoid; register the
free-monoid/free-group backings as `BackedUP`; relate `Algebra.Monoid` ≅
`Category.CommutativeMonoid`). The advisory's GROUNDS-IN-ALGEBRA bucket flags leaf
symptoms (e.g. `Cocycles/V4Signature/S4GroupIso.agda`); the real fix is the hierarchy
bridge, registered once.

**LANDED (2026-06-12, ea81232) — the FIRST real Algebra→Category bridge:**
`Substrate.Category.Delooping.deloop : Algebra.Monoid A → Category.CategoryOf` — the
classical one-object category BM (Obj=⊤, hom=A, id=ε, compose g f = f·g, so
left-id=ε-right / right-id=ε-left / assoc direct, matching the term-category
CategoryOf instances). Leaf module (no Category→Algebra dep in the core).
`S4GroupIso.TotalSpace-Category = deloop TotalSpace-Monoid` puts the S₄ total space
ON the spine; categorical-grounding advisory **1→0, fully clean**. Still open (in
[[project_open_threads]]): Group→groupoid deloop (invertibility), register
free-monoid/free-group backings as `BackedUP`, `Algebra.Monoid` ≅
`Category.CommutativeMonoid`, and the circle-keying below.

**CIRCLE-KEYING convergence target:** the substrate bridge-indexes are NOT keyed by
el-atlas homology-circles. Target: tag each registered bridge with the circle (homology
class of the relevant complex) it closes, and unify UP-Registry + Wedge-sphere +
WITNESS_RELATIONS into one circle-keyed index. = the instrument's "homotopical
consolidation" applied to the substrate's own bridges.

**META (the audit trail):** twice in this thread I asserted glibly — S4GroupIso "false
positive"; "re-aim the advisory at UP-Registry coverage" (a CATEGORY ERROR: UP-bridge ≠
structure-instance) — and was corrected only by CHECKING the source. The retro's G8
handoff blind spot in the flesh: a verdict needs mechanical backing, not assertion.

Links: [[feedback_domain_skin_over_category]], [[feedback_categorical_name_first]], [[project_el_atlas_substrate_congruence]], [[project_commuting_sphere]], [[feedback_wedge_not_projection]].
