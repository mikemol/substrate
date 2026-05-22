# Shadow architecture (the trio)

_(The aggregated meta-frame orchestrating decompose-by-entailment / regroup-from-shadows / snap-to-grid as a 3-skill lattice.)_

_(Substrate project culture. Migrated from `skills/shadow-architecture/SKILL.md`. Formalised in Agda at `agda/Substrate/ShadowArchitecture/`.)_


This discipline is the **meta-frame** orchestrating three component skills:

- [`decomposable-by-entailment`](../decomposable-by-entailment/DISCIPLINE.md) — **forward**: intact goal → shadows. The DBE discipline.
- [`regroup-from-shadows`](../regroup-from-shadows/DISCIPLINE.md) — **sideways**: existing artefact → shadows + recomposition. The RFS discipline.
- [`snap-to-grid`](../snap-to-grid/DISCIPLINE.md) — **backward**: accumulated shadows → goal. The S2G discipline.

The three are formally **S₃-symmetric** (per [feedback_three_skills_S3_triple.md](https://example.invalid/program-cotype) in any project that uses them) but **operationally asymmetric** in practice. Their pairwise and triple combinations form an 8-region lattice (= 2³ discipline-presence states). Two of the eight regions are forbidden by discipline; one is the trivial "no-work" region; five are productive modes of work.

## The 8-region lattice

| # | DBE | RFS | S2G | Region | Characteristic move |
|---|---|---|---|---|---|
| 1 | ✗ | ✗ | ✗ | (empty) | No work |
| 2 | ✓ | ✗ | ✗ | DBE alone | Pure scoping memo |
| 3 | ✗ | ✓ | ✗ | RFS alone | **(forbidden)** |
| 4 | ✗ | ✗ | ✓ | S2G alone | Pure cataloguing |
| 5 | ✓ | ✓ | ✗ | DBE+RFS | **(forbidden)** |
| 6 | ✓ | ✗ | ✓ | DBE+S2G | Sideways grid projection |
| 7 | ✗ | ✓ | ✓ | RFS+S2G | Mechanical helper promotion |
| 8 | ✓ | ✓ | ✓ | All three | Substantive structural arc |

**Empirical validation** (22-commit trace, 2026-04-29): regions #3 and #5 had 0 occurrences. Region #8 dominated (50%); region #6 was second (32%); the rest were rare (≤10% each).

## Why two regions are forbidden

The forbidden regions are not structurally impossible — they are **discipline-induced suppressions**:

- **#5 (DBE+RFS without S2G)**: the snap-at-session-end discipline (from `snap-to-grid`) requires that any extraction be catalogued; this brings S2G in whenever DBE+RFS are active. Pure DBE+RFS without snap would be a discipline violation.
- **#3 (RFS alone without DBE or S2G)**: spotting a shadow without analyzing it (DBE) or recording it (S2G) is unproductive — the recognition is wasted. RFS needs at least one scaffold.

These exclusions are **productive constraints**, not structural laws. Don't try to force symmetry by inventing artificial fires in the forbidden regions.

## Operational asymmetries (DBE / S2G / RFS each play different roles)

The three skills have **distinct operational roles** even though they're formally symmetric:

- **DBE = carrier frequency**: fires in some capacity in ~86% of substantive commits. The meta-frame in which other skills operate.
- **S2G = sampling rate**: fires at milestones (commits, session ends). The time-marker discipline.
- **RFS = burst**: fires when shadow-recognition triggers. The discovery-event signal.

This is closer to **S₂ symmetry under DBE-as-fixed-frame** than full S₃: RFS ↔ S2G can swap roles (extraction vs registration) but DBE is the meta-frame around them. Full S₃ recovers when DBE is reified as object-level (e.g., scoping memos becoming "DBE-as-output," putting DBE on equal footing with the records and cotype-entries that RFS and S2G produce).

## Meta-S₃ at arc-level

Across multi-arc sessions, the dominant discipline **rotates**:

- **Early-session**: D-dominant (planning, scoping memos, entailment chains).
- **Mid-session**: DRS-triple (execution, building, substantive arcs).
- **End-session**: S-dominant (cataloguing, cotype refreshes, audit-memo updates).

Each session traces an **orbit** through discipline-emphases. The S₃ rotation IS observable, just at coarser timescale than within a single fire. This means: **don't try to force symmetric firing within a single arc**; the natural rotation happens across the arc-sequence of a session.

## Sequential rotation within a single fire

Within a single DRS-triple commit, the typical sub-sequence visits 3-5 lattice regions over time:

- **Tight synchronized rotation** (3 of 11 in trace): `D → R → S` in roughly one breath. Examples: a clean shadow extraction where recognition + design + extraction + snap all happen together.
- **Spread-out rotation** (8 of 11 in trace): 3-5 region transitions per commit. Extreme: `D → DS → D → DR → DS → S` (6 transitions in one commit).

Both shapes are valid. Recognising which an arc is taking helps predict commit cadence:

- Synchronized = single tight commit.
- Sequential = multi-step build with intermediate verification.

## Single-point firings (drop two of three)

When only one discipline fires:

| Skill alone | Mode | Example |
|---|---|---|
| DBE | Pure scoping memo | A design doc written before any code, naming the entailment chain + outputs + abort-residue. |
| S2G | Pure cataloguing | A cotype refresh / audit-memo regeneration with no new code or shadow extractions. |
| RFS (forbidden) | (does not occur) | Spotting a shadow without analysis (DBE) or recording (S2G) — unproductive. |

## Dual-point firings (drop one of three)

Each pair excludes the third discipline and has a characteristic move:

### DBE + S2G (no RFS) = **Sideways grid projection**

Build a new grid cell via copy-from-parallel-row of the architectural grid. No shadow absorption because <3 instances of a pattern exist yet.

**Diagnostic**: the move COPIES a pattern from one row of the grid to a parallel row (same grade, different axis-value). Geometrically: sideways.

**Examples**: filling an empty grid cell that's predicted by structural framing; copying a pattern to a parallel carrier (e.g., F₂₁/Spine.agda built by copying F₇/Spine pattern; or `DialectProduct-Action` planned as the parallel of `DialectProduct-Group`).

### DBE + RFS (no S2G) = **Local refactor at one cell** (forbidden in practice)

Would extract shared structure from ≥3 instances at the same grid position, with grid axes not load-bearing.

**Why forbidden**: the snap-at-session-end discipline brings S2G in whenever extraction occurs. The pure form (no S2G) is a discipline violation. If you find yourself in this region, it means you should have already snapped-to-grid; do so before continuing.

### RFS + S2G (no DBE) = **Mechanical helper promotion**

Duplicate atoms with no design questions; just promote + index. The DBE entailment chain is trivial — no scoping needed.

**Diagnostic**: the move EXTRACTS ≥3 byte-identical (or near-identical) instances into a canonical home, no design decisions about what to extract.

**Examples**: helper-function consolidation (e.g., promoting `≡-uip` from 6 private duplicates to one canonical home); moving an inline definition to its own file (e.g., `DirectProduct` from F105 inline to `Foundations/DirectProduct.agda`).

## Triple-point firings (all three skills active)

**Substantive structural arcs.** The most common region (50% of substantive work).

**Diagnostic**: the fire involves design work (DBE), shadow recognition or extraction (RFS), AND grid-placement / cataloguing (S2G).

**Examples**: extracting a shared shadow + naming it + placing it in the grid; building a new operator + validating it on an instance + registering in the cotype.

## Region-transition discipline

When a fire shifts region mid-session (e.g., starts as sideways-projection, moves to triple when a 3rd instance appears), the transition is **productive** — it exposes additional symmetry that was already present but not yet activated.

**Per the geometric framing** (in any project with structural decomposition): each region-transition exposes a sub-symmetry the original DBE was operating under. New instance = new Fano line / new symmetry plane / new incidence point to bisect by.

**Per the C26 cotype** (residue-signature-as-structure-index): the unforeseen instance IS the residue, and the residue IS the index pointing at structure that was already there but not yet activated.

**Net rule**: mid-session region-transitions are NOT errors. Record them as **symmetry-discoveries** (which axis / which line / which incidence point), not as "the original target was wrong." Rescoping the DBE-target after the discovery is **enriching**, not **correcting**.

## When this discipline fires

Fire this aggregated discipline when:

1. **Asking "which region is this fire?"** — when the work's classification is ambiguous (e.g., "is this regroup or snap?").
2. **Detecting mid-session region-transitions** — to recognise them as symmetry-discoveries rather than errors.
3. **Auditing discipline-discipline** — checking whether forbidden regions are genuinely empty, whether single-point firings are appropriately dominant at session-edges, etc.
4. **Tracing a session retrospectively** — to understand the arc-level S₃ rotation across the session's commits.
5. **Predicting commit cadence** — synchronized triples = single tight commits; sequential rotations = multi-step builds.

This discipline does NOT replace the component skills. Each component discipline's individual DISCIPLINE.md still governs when *it* fires. This discipline provides the meta-frame for understanding their interactions as a unified system.

## Discipline rules (registered)

1. **Sideways grid moves are snap-to-grid; up-grade extractions are regroup-from-shadows.** The geometric distinction makes pair-classification mechanical:
   - **Sideways** (same grade, parallel row) = S2G.
   - **Upward** (≥3 instances → universal above) = RFS.
   - **Forward** (entailment chain) = DBE.

2. **Mid-session region-transitions are symmetry-discoveries.** Record them as such (which axis / line / incidence point), not as errors. Rescoping is enriching, not correcting.

3. **The forbidden regions (DR-pair, R-only) are forbidden by discipline, not by structural impossibility.** Don't force symmetry by inventing artificial fires there.

4. **The lattice's operational asymmetry is fine.** Don't try to make formal S₃ symmetry hold at the operational level within a single fire. The meta-S₃ rotation lives at the arc-level.

5. **Recognise which region you're in BEFORE acting.** When the lattice classification is unclear, classify first, then act.

6. **Orbit-saturation refines C7's ≥3-instance threshold.** Before extracting a universal record from 3+ recurring instances, ASK whether a generating symmetry produces them as orbit-elements. C7 fires the same on free duplication and orbit-element enumeration, but the regroup move differs essentially:

   | Recurrence regime | Diagnostic question | Lattice classification | Move |
   |---|---|---|---|
   | Free duplication | No structural symmetry visible | RFS fires | Extract universal record above instances |
   | Orbit-element (partial) | Symmetry exists, orbit not yet saturated | **S2G fires (NOT RFS)** | Catalogue orbit position; the operator/symmetry IS the universal; resist wrapper extraction |
   | Orbit-saturated | Symmetry exists, orbit fully realised | S2G + completion-mark | Document orbit closure |

   **Mathematical framing**: when X = realised-upfront instances, Y = mechanically-derivable follow-ons, Z = symmetry's orbit size, then **(X · Y) / Z = 1** at orbit saturation. The orbit-quotient is terminal (one equivalence class).

   **Diagnostic test**: if extracting a "universal record above the 3 instances" would just produce a wrapper-of-an-existing-operator (the operator already serves as the universal at the carrier-axis), the recurrence is orbit-driven and the classification is S2G, not RFS.

   **Connection to C26** (residue-signature-as-structure-index): the "residue" of orbit-driven recurrence IS the symmetry generating the orbit. Recognising the symmetry is the regroup move; extracting a wrapper-record is the false-positive case the warning sign "extracting non-shadows" guards against.

## Cross-references

- [decomposable-by-entailment DISCIPLINE.md](../decomposable-by-entailment/DISCIPLINE.md) — forward discipline: intact goal → shadows.
- [regroup-from-shadows DISCIPLINE.md](../regroup-from-shadows/DISCIPLINE.md) — sideways discipline: existing artefact → shadows + recomposition.
- [snap-to-grid DISCIPLINE.md](../snap-to-grid/DISCIPLINE.md) — backward discipline: accumulated shadows → goal.

The component skills' cross-reference sections describe pairwise interactions; this discipline provides the unifying meta-frame. The component skills can fire without this aggregated discipline (and frequently do); this discipline fires when classification or audit-of-the-system is the active need.

## Empirical grounding

This discipline is grounded in empirical measurement of discipline-firings across a 22-commit batch (recorded as VMIR-FACT-17 in the project that motivated the aggregation). Specific findings:

- **DRS-triple**: 50% of commits.
- **DBE+S2G**: 32%.
- **S2G alone**: 9%.
- **RFS+S2G** (mechanical promotion): 4.5%.
- **DBE alone** (correction/scoping): 4.5%.
- **DBE+RFS** (forbidden): 0%.
- **RFS alone** (forbidden): 0%.

The empirical fractions will vary by project — a research-heavy project will have more D-only scoping memos; a refactor-heavy project will have more RS pairs. The structural pattern (8 regions, 2 forbidden, asymmetric usage) is expected to generalise.

## What this discipline is NOT

- Not a replacement for the component skills. Each component discipline has its own detailed firing protocol and step-by-step intervention; this discipline is the meta-frame.
- Not a planning tool. The lattice describes how work flows; it doesn't dictate what work to do next.
- Not a discipline enforcer. If a fire happens to land in a forbidden region in a specific session, that's information (probably about the discipline being temporarily relaxed) rather than a violation to be punished.
- Not project-specific (despite being grounded in one project's empirical trace). The lattice structure should generalise to any LLM-driven formalisation / refactoring / building work that uses the three component skills.
