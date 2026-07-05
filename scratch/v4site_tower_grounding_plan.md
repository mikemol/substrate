# Ⓒ.v4.site — ground V₄ IN the tower's build (not compare against it)

**User's decisive reframe (2026-07-05):** the tower's growth process INDUCTIVELY CONSTRUCTS the whole
chain of symmetry groups (Sₙ up the rungs); the entire internal structure is provided. So V₄ must be
TAKEN FROM the tower's *build* of it — its carrier = the tower's permutations, its op = the tower's
composition — NOT Groups.V4.V₄ compared to the tower.

**Reference interned:** `~/Downloads/ExtrudeSKIKFaces.agda` (= `Category.UniversalProperty.ExtrudeSKIKFaces`).
Method: an attribute IS its build-trace — `weight` reads off `WitnessTower.FaceSet`'s cone (with-apex/
without-apex), the laws (`weight-with-apex ≡ suc`) are the ELEMENT-SHADOW of FaceCount's Pascal cone-step,
the local vertices (258 `eᵢ`) are placed as the dimension-0 stratum, and an HONEST BOUNDARY separates
GROUNDED (machine-checked) from SCOPED (reused-in-spirit: the full coinductive growth).

**The build primitives (reuse-search — take, don't reinvent):**
- `WitnessTower.Enumerate`: `Perm n = Vec (Fin n) n`; `perms : (n) → List (Perm n)` (perms 4 = 24, up the rungs).
- `WitnessTower.FirstAppearance`: `compose σ τ = tabulate (λ i → lookup σ (lookup τ i))`; `is-involution`;
  and its own note "the 3 double-transpositions are exactly the non-identity elements of the normal V₄",
  debuting at rung 4.
- `WitnessTower.KleinCensus`: the Klein-four DEBUTS at rung 4 (klein-pairs 4 = 24; /6 = 4 subgroups); rung 3 = 0.
- `Groups.V4.Bundle.V₄-Group : Group V₄` (proven) — the bridge target if the build-V₄ ≅ it.
- `Algebra.TopologicalGroup`: `record TopologicalGroup (A) { group : Group A ; <topology marker> }`.

**The current Sites.V4 (the thing to fix):** a self-contained `data V4` + `V4-op` (bare 16-entry table, NO
laws) that OVERCLAIMS in prose ("populated by the runtime concrete instance", "demonstrates the BRIDGE")
without inhabiting anything. The last local group-V₄ carrier (Ⓒ.v4.site).

**PLAN (following the reference):**
- The 4 Klein elements AS `Perm 4` values (from the build): id=[0,1,2,3], (12)(34)=[1,0,3,2],
  (13)(24)=[2,3,0,1], (14)(23)=[3,2,1,0].
- `data V₄` (4 ctors) + `⟦_⟧ : V₄ → Perm 4` embedding INTO the build (perms 4).
- op `_·_` grounded so `·-is-compose : ⟦ x · y ⟧ ≡ compose ⟦x⟧ ⟦y⟧` (refl IF compose computes — the crux
  under test) — the bisimilarity-with-build law (element-shadow, like weight-with-apex).
- Klein facts read off the build (refl): exponent-2 `x·x ≡ e`, abelian `x·y ≡ y·x`, closure.
- PLACEMENT: the 3 non-id elements ARE FirstAppearance's double-transpositions, debut rung 4 (KleinCensus).
- Inhabit `TopologicalGroup V₄` from the build-derived Group (or bridge to V₄-Group).
- HONEST BOUNDARY: GROUNDED = carrier/op FROM the build + the bisimilarity law + Klein facts + placement;
  SCOPED = full assoc if 64-case-heavy, the topology (discrete marker), the KleinCensus count agreement.

**Layering:** WitnessTower does NOT import Algebra.TopologicalGroup (checked) → a grounding module importing
BOTH is cycle-free. Reference lives HIGH (Category.UniversalProperty). So the grounding module goes high
(WitnessTower.* or a grounding namespace), NOT in low Algebra.Sites (which would invert Algebra→WitnessTower).

**Status:** feasibility test = does `compose` compute on the concrete Klein perms (→ refl laws)?
