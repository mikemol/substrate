---
name: project_witness_tower_dossier
description: "The Witness-Tower dossier (witnessed-simplex primitive → S₄=V₄⋊S₃ → RM(1,4) codeword → Elduque/Hodge anchors); §8 UPTerm-identity discharged FIRSTHAND; B3 now COMPUTED in-tree via iterated enumeration + cycle-type census (not external/POSITED)."
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Portable formalization transported into the substrate repo. Full text in
the conversation that created this note; key claims + status below. Status
tags: VERIFIED / CONSTRUCTION / POSITED / EXTERNAL-ANCHOR (the dossier's own
vocabulary).

**The spine.** One primitive (witnessed simplex), one move (a point
witnesses the (k−1)-simplex below, lifting a dimension + reifying the lower
level as a new vertex). Rungs 0..3 = point/edge/triangle/tetrahedron, sym
S₁..S₄, glue index k+2 (catamorphism fold, combining op = ×, |Sₙ|=n!).
Roles (src/dst/witness/apex) are POSITIONS in the tower, not node-kinds.

**Group layer (all VERIFIED from axioms per dossier):** S₄ = V₄ ⋊ S₃ =
holomorph of V₄ (φ:S₃→Aut(V₄) faithful+full, B2). Witness-stabilizer tower
S₂⊂S₃⊂S₄ = Stab chain, orders [24,6,2,1], indices [4,3,2]. Seam = (DC)(SW)
double-transposition, reassignable transitively (B5). Sylow: 3×D₄ ↔ 3 seams,
4×Z₃ ↔ 4 points (B4). cycle-TYPE (not abstract class) distinguishes the two
V₄ roles (B3).
- C1 REFUTED (act_V4∘act_S3 is NOT an action — fails hom law 9216/18432;
  stale-negative if cited as prohibition — it MOTIVATED C2).
- C2 VERIFIED: correct action = CONJUGATION (gauge↦σ·gauge·σ⁻¹), 0
  violations, works because V₄ normal. "relabel vertices, don't translate."
- C3 VERIFIED: observable = NOT-IN-KERNEL. conjugation kernel = V₄ → cells
  observe S₄/V₄≅S₃. Ties to the §0 charter (constructible→reachable→
  observable→coverable) — same charter as [[project_realizability_charter_arc]].
- C4 VERIFIED: real 2-skeleton f-vector [30,42,17,0].

**Codeword:** incident vector = level-by-level which-is-witness = RM(1,4)
codeword. **Anchors (EXTERNAL):** Elduque/Hartwig–Terwilliger sl₂⊗A
(arXiv math/0604218) warrants "V₄ holds witness, S₃ orients"; dim-4 Hodge
star Λ¹↔Λ³ (both dim 4) = witness↔triangle duality, 32=24+8. Asymmetry
(D2): data-tower height 2 (f-vector 0 tetrahedra) vs symmetry-tower height
3 — the apex is a SYMMETRY, not a datum.

**B3 COMPUTED IN-TREE (commits ff71b53 + f6736f9) — carrying the
computation UP the tower, not a hardcoded Fin 24.** The S₄ record axis has
no DecEq, so instead of asserting B3 I built the symmetry tower as an
ITERATED ENUMERATION and ran the count over it:
- `WitnessTower.Enumerate`: `Perm n = Vec (Fin n) n`; `perms (suc n)` from
  `perms n` by the witnessing-insertion move (`insert-at p σ = p ∷ map
  (punchIn p) σ`, insert the new top at each of n+1 positions). The glue is
  literally ×(n+1); `length-all-positions` proves it; `perms 4` = 24 by
  construction. `punchIn` (Fin.Punctured) IS the insertion primitive — the
  same puncture that discharges §8(b).
- `WitnessTower.FirstAppearance`: cycle-type census, every count a refl over
  the enumeration. involutions 0,1,3,9; transpositions (moved-2) 1,3,6;
  double-transpositions (moved-4) ABSENT at rung 3, DEBUT 3 at rung 4.
  `census-rung4-split`: 6+3≡9 — the involution-count jump rung 3→4 IS the 3
  new (2,2)s = gauge V₄ minus id.
- `WitnessTower.KleinCensus`: 4 Klein-fours via commuting-distinct-involution
  ordered pairs / 6. `klein-pairs 3 ≡ 0`, `klein-pairs 4 ≡ 24` (= 4×6).
- KEY READING (user's framing): objects make a FIRST APPEARANCE at a rung;
  the rung where each cycle-type debuts reveals the inductive step n→n+1 =
  "which cycle-types newly fit." (2,2) needs 4 points ⟹ gauge V₄ impossible
  below rung 4. Maps to v4cat first_seen / tropical-MIN-origin methodology.
  DONE (commits 7a12c18 + b038532): the full cycle-type lego
  (`WitnessTower.CycleType` — partition λ by orbit-tracing, fuel n; full S₄
  conjugacy census 1+6+3+8+6=24, (4) vs (2,2) distinguished) and the full
  B3 split (`WitnessTower.B3Split`): 4 V₄s = 1 normal-gauge (6 pairs, triple
  all (2,2)) + 3 interface (18 pairs, sig 1×(2,2)+2×(2,1,1)); gauge-closure
  (3 double-transp closed → the gauge subgroup, all (2,2)s in it); SEAM =
  gauge ∩ interface = {id,d} ≅ V₂ (interface-full-sig ≡ 18: each interface's
  single (2,2) is the shared seam, its 2 transpositions outside the gauge).
  All refl over the enumeration. GOTCHA: distinctness of two (2,2)s must be
  on the element (_≡ᵇ_), NOT cycle type — all (2,2)s share a type (cost one
  iteration: 0≠6). This is the substrate-native B3-shared-v2-proof.py.
- SCALE PROFILE (commit 744b74a, measured n=4,5,6 = S₄..S₆): the enumeration
  approach is MEMORY-FLAT (~11–17 MiB at ALL n, both cost structures) —
  streaming filterL/concatMapL retain nothing, so NO OOM (the substrate's
  usual failure mode does NOT apply to runtime enumeration; contrast the
  load-bound All.agda OOM which is interface deserialization, a different
  axis). TIME is the sole wall: O(n!) censuses (length/involutions/cycle-
  type orbit-trace) ≤1.3s at n=6; O(n!²) pair census (klein-pairs/B3Split)
  0.02→2.3→59s for n=4,5,6, impractical by n=7 (~25M pairs). Lever:
  klein-pairs-fast iterates the INVOLUTION sublist (telephone numbers
  1,1,2,4,10,26,76,… ≪ n!) not all of Sₙ → 59s→9s at n=6. Gain < pair-ratio
  because Agda's normalizer doesn't share let-bindings during reduction and
  building perms n is itself O(n!). So: refl-forced enumeration normalizes
  fine to S₆; the design choice that matters is restricting the iteration
  domain, not memory.
- "TOWER IS Sₙ" PROOF ARC (user's key question: is the re-reading PROVED or
  just evidenced by matching counts?). HONEST STATUS: NOT fully proved yet —
  Perm n was just Vec (Fin n) n; the census ran over a length-n! list with
  NO proof its entries were permutations. Formal Sₙ in-tree =
  Groups/Symmetric.agda (Permutation record = apply+inv+proofs, genuine
  bijection; instantiate A=Fin n). BRICK 1 DONE (commit df11e61,
  `WitnessTower.IsPermutation`, zero postulates): IsPerm v = lookup v
  injective; insert-at-preserves (witnessing-insertion never leaves Sₙ, via
  punchIn-≢ + punchIn-injective); perms-all-perm : All IsPerm (perms n) by
  induction threading IH through concatMap (All-concatMapL with per-element
  witness — discarded a FALSE postulate "every Vec is a perm", caught by
  --safe). REMAINING: brick 2 (perms duplicate-free) + brick 3 (complete);
  OR the decisive route — Lehmer rank/unrank bijection Fin (n!) ≅ Symmetric
  (Fin n), self-contained, gives dup-free+complete+group-iso at once. That
  iso IS the machine-checked "tower = re-reading of Sₙ". Reusable lemmas
  landed: punchIn-injective, lookup-map.
  ARC COMPLETE (commits df11e61→f42dcad, ZERO postulates across 6 modules,
  each green standalone). Sₙ = bijective image vectors (Perm n + IsPerm =
  lookup injective). Bricks: 1 SOUND `IsPermutation.perms-all-perm`; the
  inverse-of-insert-at `Decompose.decompose` (σ = insert-at head tail, the
  crux); 3 COMPLETE `Complete.perms-complete` (∈ machinery); 2 DUP-FREE
  `DuplicateFree.perms-nodup` (insert-at-inj both args + NoDup-concatMapL).
  CAPSTONE `Sn.agda`: enumerate (=unrank=list index) is sound+injective+
  surjective over Fin (length=n!) — the Lehmer bijection Fin (n!) ≅ Sₙ, no
  div/mod (index IS the rank). GROUP `SnGroup.agda`: compose closed
  (compose-is-perm) + IS function composition (apply-compose) + unit
  (apply-id, compose-id-left/right) + faithful (apply-injective=lookup-ext)
  ⟹ Sₙ as a GROUP. So the censuses' counts are provably Sₙ's, generated by
  the tower's move. Re-reading PROVED. BRIDGE DONE TOO (commit 7ee6122):
  `Surjective.perm-surjective` (injective⟹surjective, reuses decomp-tail +
  Fin DecEq) supplies the inverse; `SymBridge` (parametric n) builds
  to-Sym/from-Sym : Σ(Perm n)IsPerm ↔ Groups.Symmetric.Permutation (Fin n)
  with both round trips (≈ record / ≡ vector), to-Sym-hom (compose↦·),
  to-Sym-id. Tower is group-isomorphic to the substrate's OWN symmetric-
  group record. ARC FULLY COMPLETE, 8 modules, zero postulates. Reusable:
  lookup-ext, punchOut-injective, NoDup-*, ∈-*, lookupL-*, map-injective,
  insert-at-inj, perm-surjective.
- GRADING GENERALIZATION (commit ce8df3a, `WitnessTower.SupportGrading`,
  prompted by an external LLM reading — CONFIRMED in-tree, not just prose):
  first-appearance IS minimal SUPPORT. grade(structure)=min{n|realizable at
  rung n}=support. support = moved-count for ANY permutation. "new at rung
  n" = cycle types with support exactly n; the fully-supported (no-fixed-
  point) debutants at rung n number the DERANGEMENT Dₙ (by-support n n ≡ Dₙ:
  D₂=1,D₃=2,D₄=9, all refl). support-1 impossible ⟹ grading skips rung 1.
  HONESTY BOUNDARY (also built): support is COARSER than cycle type —
  moved-count can't tell (1234) from (12)(34) (both support 4), so the
  rung-4 support-4 debut (9) splits 3 double-transp + 6 four-cycles, a split
  needing σ²=id not moved-count. The involution census worked ONLY because
  involutions linearize moved-count=2·#2-cycles (injective on type there).
  Open finer axis: grade by partition λ (cycle type), not just support sum —
  the tower as a graded object indexed by partitions, support = degree.
- DAG ANSWER (commit 2f2777d, `WitnessTower.FamilyWitness`, prompted by the
  same external reading: "if witnessing took a FAMILY not one object, stay
  linear or become a DAG/groupoid?"). Becomes a DAG (the simplex face
  lattice). Three CHECKED facts: (a) Core IS a chain — WSimplex-unique:
  WSimplex k is a singleton, one inhabitant per rung; (b) family move
  BRANCHES — FSimplex.cell carries (suc (suc k)) facets per rung, branching
  ≥2 always (edge has 2); the constructor type is the witness; (c) bridge —
  a linear spine = an ordering of the (k+1) vertices, so #spines = (k+1)! =
  |perms (suc k)| = the census (spine-count-is-census via the now-GENERAL
  perms-length : |perms n| ≡ n!, proved this session, was spot-checked n≤4).
  Reading: linearity is a GAUGE CHOICE (a chart); spines + permutations form
  a groupoid (torsor under S_{k+1}); Core.walk is one object, the census
  enumerates the morphism set. Same atlas-vs-chart / choice-rigidification
  pattern as the rest of the substrate ([[feedback_choice_rigidification_in_substrate]],
  [[discipline/project_multi_route_equivariance_recovery]]).

**§8 OPEN SEAM — DISCHARGED FIRSTHAND THIS SESSION (the repo is here; read
Term.agda/Morphism.agda/UniversalProperty.agda directly):**
- (a) "one ∷ = one new witnessing designation" → **VERIFIED.** UPTerm._∷_
  prepends exactly one UPGen; the only UPGen ctor is `lift mor` carrying one
  UPMorphism. One cons = one morphism = one designation; the chain
  U₁→U₂→U₃ IS the path of witnesses.
- (b) "∷ lifts the simplicial dimension by one" → **DISCHARGED** (later,
  via the WitnessTower build). The lift is the PUNCTURE: the witnessing
  step rung k→k+1 takes a cell w of the higher rung (Fin (suc (suc k)),
  k+2 cells); the witness occupies w, the witnessed rung-k simplex
  occupies the remaining k+1 cells via punchIn w. Built in
  Substrate.WitnessTower.Puncture using Foundation.Fin.Punctured
  (Fin (suc n) ∖ {w} ≅ Fin n) — machinery already in the tree. The
  partition {witness} ⊎ embed-witnessed(rung k) is proved by the punctured
  round-trips (recover-embed/embed-recover). My earlier "not in the tree,
  needs new infra" was WRONG: the indexed layer is Fin.Punctured (built
  this session for Stab-S3); the lift is punchIn/punchOut. Correction: a
  cluster/seam "needs new infrastructure" is itself a claim to CHECK
  (grep the tree) before asserting — same lesson as
  [[discipline/feedback_cluster_means_find_apex]].
  NOTE: this discharges the GEOMETRIC dimension-lift on WSimplex cells; it
  does NOT yet identify that lift with UPTerm's ∷ (the Agda cons-list) —
  that identification is still (a)+(c) below, the UP-side.
- (c) "UPMorphism witness field = choice-of-witnessing-vertex" → **PARTIAL /
  REINTERPRETED.** UPMorphism has NO single witness field — it's
  source-map + target-map + coherent (a commuting span-square). Defensible
  reading: the WHOLE morphism is the designation, `coherent` preserves
  witnessing. "the witness field" is an overstatement.

Per the dossier's own rule, (b)/(c) narrowing does NOT disturb the
geometric/group/codeword/anchor layers — only the Agda-identity claim is
corrected. To fully discharge (b): the substrate would need a
dimension-indexed UPTerm or a proved simplex↔UPArrow functor; that's a real
construction arc, not a reading. (Connects to the term-algebra
[[project_term_algebra_extension]] — UPTerm is the existing cons-list; the
simplex reading is the proposed semantic layer over it.)
