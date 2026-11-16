---
name: project_el_atlas_substrate_congruence
description: el-atlas (paraconsistent evidence-logic spec) MERGED INTO this repo (commit 78f2dd4, full history, el-atlas/) and CONTINUED HERE — no longer run independently; one project now. Was the PROSE chart to the substrate's AGDA chart.
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

**STATUS (2026-06-11): el-atlas is CONTINUED HERE — not a companion, THE SAME PROJECT.**
Merged full history (354 commits; cotype S0–S60, instrument v3.8.5) into this repo at commit **78f2dd4**
(`git merge --allow-unrelated-histories`, author rewritten to Mike Mol), living at
`el-atlas/`. Source tarballs dropped. User: "We are the
continuation of el-atlas; it will not be independently run any more — it exceeded the
capacity of an LLM outside this kind of environment." So: the snapshot/will-go-stale
framing is RETIRED — this repo IS where el-atlas advances now (Claude Code + the
substrate's git/memory/gate machinery is the native home for el-atlas's own
cotype/WAL/fiber-cert disciplines). LIVE HANDOFF for el-atlas's open work:
`el-atlas/NEXT.md` (+ `el-atlas-cotype.md`, the WAL `wal.md` /
`tools/wal-check.py`). Natural next: discharge NEXT.md #2 (the "Nedge G-Value Calculus
(Agda)" ↔ VerdictCrossbar ↔ line-1987 postulate-vs-derive note) using the substrate's
zero-postulate `ℚ-Canonical` as the derive-not-postulate witness.

**LANDED (2026-06-11, commit 19febe2 — FIRST proof-tier join, NEXT.md move #3):**
el-atlas's `proofs/VerdictCrossbar.agda` (W13, self-contained Bool/≡/⊥) re-homed onto
substrate Foundation as `Substrate.Logic.Evidence.Verdict` (defs: Evidence dual-rail
E⁺/E⁻, Verdict P/F/U/V, verdict map, swapE/swapV, apartness, probe pts) +
`.Verdict.Properties` (swapE/swapV involutive, intertwine = S4 crossbar) +
`.Verdict.NoCollapse`. NoCollapse GENERALIZES el-atlas §3 "no single-rail quotient"
from Bool to an arbitrary carrier, on the substrate's `Quotient` record:
`faithful-refines-verdict` (any quotient `verdict` factors through refines the
verdict-kernel — arbitrary Q, no finiteness/decidability, only `cong d`);
`verdict-kernel-achieved` (bound tight via (verdict,id) ⟹ verdict-kernel is the
COARSEST faithful quotient); el-atlas's Boolean `no-single-rail-quotient` is now a
COROLLARY via `two-of-three` pigeonhole (specific-from-general, no 2nd proof). All
green --safe --without-K, zero postulates. New `Substrate.Logic.*` namespace.
NOT YET reflected in el-atlas's OWN ledger (NEXT.md/cotype, under scratch/ — needs
user ok to write there); offer to update it.

**LANDED (2026-06-12, commit fe16462 — JOINERS, NEXT.md #3 second rung):** the dual-
rail connectives, pinned from the in-repo spec (§1 carrier=two independent accumulators
Law 1.3; §5 Thm 5.2 "De Morgan IS the pin-swap"; §6 two log-linked operations FORCED,
Remark 6.2). Hosted WITH the carrier in `Verdict.agda` (carrier-locality gate forced
this — a file with ≥2 endo-ops over a foreign carrier is a "bucket"; ops belong with
the file declaring the carrier, à la Foundation.Bool). Added: `_∧E_`/`_∨E_` (truth
meet/join, bounds ⊤t=P/⊥t=F), `_⊕E_`/`_⊗E_` (info accumulate/consensus, bounds
⊤k=U/⊥k=V), `notE`(=swapE). Laws in `Verdict.Properties`: `deMorgan-∧∨`/`-∨∧` (Thm 5.2,
refl), `notE-⊕`/`-⊗` (twist: NOT preserves info order, refl), `*E-comm/assoc/idem/
identityʳ` (cong₂ on rails), `∧E≢∨E` (Remark 6.2 two-ops-forced, witnessed on the SAME
(P,F) probe as NoCollapse), `verdict-notE`=intertwine (joiner negation IS the crossbar's).
Foundation.Bool.Properties enriched with ∧/∨ semilattice laws (was xor-only). NOTE on
discipline: continuous AND~log-product/OR~log-sum-exp (§6) deliberately OUT of scope
(discrete-constructor-only).

**LANDED (2026-06-12, commit ca70a90 — GRADES/WARRANTS, NEXT.md #3 third rung):** the
provenance grades [W]/[S]/[C]/U (§0) as an epistemic-strength meet-semilattice. TYPE
NAMED `Warrant` (NOT `Grade` — substrate already has Clifford-degree `record Grade (n:ℕ)`
in Category/CliffordEmissionAlgebra.agda; genuine HOMONYMS, so distinct name not shape-
tag; constructors keep el-atlas W/S/C/U letters). `Substrate.Logic.Evidence.Warrant`:
Warrant=W⊒S⊒C⊒U, `_⊓w_`=WEAKEST-DOMINATES (the §0/line-1310 demotion: derived claim no
stronger than weakest premise), bounds ⊤w=W/⊥w=U. `.Warrant.Properties`: bounded meet-
semilattice (⊓w-comm/assoc/idem/identityʳ=W/zeroʳ=U, all refl over the 4-chain; W&U rows
uniform so assoc=22 clauses not 64). `.Graded`: GradedEvidence=Evidence×Warrant, graded
joiners `_∧G_`/`_∨G_` (content via ∧E/∨E, warrant via ⊓w) ⟹ warrant RIDES UNDER the
joiner; projection laws gr-∧G/ev-∧G refl. `.Graded.Properties`: ∧G/∨G-comm = cong₂ _at_
of the two factor laws (GradedEvidence = PRODUCT of evidence × warrant semilattices).
The grades are the epistemic shadow of the shared Realizability.Charter ladder. Gate
lesson: a 2nd `Grade` decl trips decl-shape-tag + import-shape ratchet; for homonyms,
RENAME (cleaner, no collateral edit to the other subsystem) beats shape-tagging both.

**LANDED (2026-06-12, commit 890b8bf — PHASE / H² SEPARATION, NEXT.md #3 FOURTH rung —
MOVE #3 NOW COMPLETE):** §5.10c exactly: the chart involutions exhibit the phase class
of 1→ℤ₂→D₄→V₄→1 in H²(V₄,ℤ₂). `Verdict.agda` gains negPos/negNeg/negBoth (N₊/N₋/−id;
carrier-local w/ swapE). `Verdict.Phase`: *-invol (involutions); negPos∘negNeg≡negBoth
+ comm (diagonal {id,N₊,N₋,−id} = abelian V₄); **`α·β≡γ` REFL in Substrate.Groups.V4** —
REAL link (id↦e,negPos↦α,negNeg↦β,negBoth↦γ), V₄'s _·_ computes on concrete elts;
`commutator-N₊-S≡negBoth` = the COCYCLE [N₊,S]=−id (S=swapE); `N₊-S-noncommute` = THE
SEPARATION (N₊,S don't commute ⟹ D₄≇V₄×ℤ₂, class non-trivial, witnessed on eP);
negBoth-central-* (kernel ℤ₂ central). Exhibits the extension DATA not a D₄ object
(faithful to §5.10c "cocycle exhibited by the commutator"). Follow-ons (NOT done):
Axis regular-rep iso (Substrate.Axes.act-axis), D₄ as group object, §8.6 V4Interface
holonomy (H1(complex;V4), biasShadow:V4→ℤ₂).

**MOVE #3 COMPLETE** (crossbar 19febe2 · NoCollapse/S3 19febe2 · joiners fe16462 ·
grades/warrants ca70a90 · phase/H² 890b8bf). `Logic/Evidence/`: Verdict(+Properties,
+NoCollapse,+Phase), Warrant(+Properties), Graded(+Properties). STILL open: el-atlas
move #2 (Nedge G-Value Calc Agda from Drive ↔ ℚ-Canonical line-1987 postulate-vs-derive);
**LANDED (2026-06-12, commit b8db271 — el-atlas LEDGER RECONCILED):** adopted el-atlas's
own WAL/cotype/NEXT discipline in-repo to record move #3 + the merge transition. wal.md:
MERGE marker + RECONCILED W23 (pre=78f2dd4 head=890b8bf). cotype: S66. NEXT.md: opening
move 3 marked COMPLETE + CONTINUATION banner. **KEY DISCOVERY — el-atlas's git-coupled
machinery is OBSOLETE post-merge (don't naively run it):** (1) `tools/wal-check.py` FAILS
on W1-W22 — the filter-branch rewrite during the merge changed every sha, so the WAL's
pre=/head= ancestry can't resolve; this is GRANDFATHERED at the MERGE marker (S0-S46
genesis class), warn-only, non-blocking, NOT a regression. (2) `tools/githooks/post-commit`
mis-targets: `git rev-parse --show-toplevel` now = substrate root, so it would tar the
whole substrate to ~/github/el-atlas-repo.tar.gz — DO NOT RUN IT. The CONTENT discipline
(WAL work-units, cotype monotonic log, NEXT handoff) is alive and now used; the git-COUPLING
(ancestry checks, tarball) is replaced by the substrate's native gates+memory. Also learned:
NEXT.md was stale at W15 but el-atlas's WAL actually ran to W22 (v3.13.0) in the web sessions
— trust wal.md+cotype over NEXT's State section. And: el-atlas W11 ALREADY computed H²(V₄,ℤ₂)
(8 vs 4 classes) in its depsort instrument + W19 admitted an extclass knob (z4 vs z2×z2) —
my Verdict.Phase is the Agda proof-tier TWIN of that instrument computation.

**CHECKED (2026-06-12 — el-atlas move #2, the Nedge Agda from Drive):** read the ancestor
Drive docs "Nedge G-Value Calculus: Formal Specification (Agda)..." (1-DIFqxPgrw...) +
"Agda SPPF G-Value Calculus Synthesis" (1lUYUHVXI27...). FINDINGS: module `NedgeGCalculus`
is SINGLE-RAIL real-valued CONDUCTANCE logic — carrier `postulate G : Set` + ALL arithmetic
(0g/1g/∞g, +,-,*,/, ≤, ≤?) POSTULATED; ops DERIVED (G-NOT=reciprocal 1/p, G-OR=parallel p+q,
G-AND=series/harmonic pq/(p+q), G-RES, G-COND) + a sequent calculus + SPPF graph layer. NO
dual-rail (E⁺,E⁻), NO 4-valued verdict, NO no-collapse, NO ℚ (gestured Float, unused), ZERO
machine-checked laws (De Morgan/involution are PROSE + a Python math.isclose check; no
--safe/--without-K, no typecheck evidence). VERDICT on line-1987/OB-6: the preamble's "replaced
postulates with concrete structures" is TRUE for graph plumbing, FALSE for the numeric core —
OB-6 NOT discharged by the ancestor (carrier postulated, no Agda laws). THE DISCHARGE IS THE
SUBSTRATE: Verdict.* DERIVES the carriers (Bool²/finite) + PROVES the laws (deMorgan-∧∨ etc.)
machine-checked zero-postulate; ℚ-Canonical is the derive-not-postulate number-system witness.
**USER FRAMING (2026-06-12, load-bearing — do NOT mis-frame this):** Nedge is ULTIMATELY
ABOUT HOLONOMY. The dual-carrier behavior is an UPGRADE to Nedge that does NOT force Nedge
to change — it just gives Nedge a way to express its conduits as STRUCTURED, MANIPULABLE
VECTORS instead of a single scalar. So the relationship is NOT "Nedge=collapse / substrate
=correction" (my first, too-adversarial framing — RETRACTED). It is: the scalar G is a valid
reading PRESERVED; the dual-rail (E⁺,E⁻) is the vector form; the scalar is a PROJECTION of it
(bias b=E⁺−E⁻; cf §8.6 biasShadow:V4→ℤ₂); a scalar has no direction so it can't carry holonomy
— THAT (the V₄-phase = the holonomy) is the expressive GAIN of the vector, not a defect of
Nedge. el-atlas §5.7e "the quotient shadow, LIFTED" matches: lift preserves the shadow.

**DEEPER REFINEMENT (2026-06-12, the load-bearing principle — supersedes "projection"):** it is
NOT a (lossy) projection but a NON-LOSSY WEDGE. The single channel is multi-channel UNDER THE
HOOD; the dual-rail → scalar map is a basis change (a ROTATION) that moves the residue into the
carrier's HIDDEN STRUCTURE — like two reals → one complex carrier (residue in the phase). **WE
NEVER DISCARD ANYTHING.** The only lossy act is TRUNCATION-ON-LOOKING: when we look at one
channel and the residue went into the other. So `bias-cannot-carry-verdict` is the LOOK failing,
not the encoding. Substrate constructs this maps to: the Wedge (keeps the remainder, a=qb+r);
Cayley-Dickson doubling ℝ²→ℂ; the exp⊣log atlas (two non-lossy charts); §11.5 Z=R+jX. Note the
F₂ degeneracy: over ℝ the (mass,bias) Hadamard is the rotation, but it's SINGULAR over F₂
(mass=bias=parity), so the discrete rotation is a different non-singular GL(2,F₂) element.

**LANDED (2026-06-12, commit 713ede5 — `Verdict/NedgeShadow.agda`):** the machine-checked
bridge. `bias : Evidence → Bias` (net+/net0/net-) = Nedge's scalar reading as a projection
(total — nothing lost); `bias-conflates-U-V` (refl: U,V both → net0, balanced); `bias-cannot-
carry-verdict` via `faithful-separates` (no decoder reconstructs the verdict from the scalar
alone). Green --safe --without-K. Also the OB-6/line-1987 answer in code: NedgeGCalculus
POSTULATES its scalar carrier + proves no Agda law; the Verdict.* vector form is concrete,
zero-postulate, laws machine-checked. **Extended (commit ab0d761) with the WEDGE:**
`recode`/`unrecode` (GL(2,F₂) basis change, visible bias-parity E⁺⊕E⁻ + hidden residue E⁺),
`recode-unrecode`/`unrecode-recode` (NON-LOSSY iso Evidence≅Bool×Bool, round-trip refl =
"never discard" as a theorem), `verdict-survives-recode` (verdict is a function of the full
re-encoding though not of the visible channel alone — the look truncates, the encoding keeps).

**LANDED (2026-06-12, commit 7ab1afc — the STRUCTURED-EDITION PROOF TIER as a Π):**
`el-atlas-structured.md` reserves "the Agda rung (proof tier EMPTY)". Filled NOT as
markdown (a sum-type freeze of the claim-function — user: "sum-type behavior when we
need pi-type dynamicism", see [[feedback_registry_as_pi_not_markdown]]) but as a
DEPENDENT FUNCTION. `Substrate.Logic.Evidence.ElAtlas`: `Claim` atoms + `Statement :
Claim → Set` + open `Frontier` (ADJ/SWP/GCX/NOE/IDC, names only). `.Proofs`:
`proof-tier : (c : Claim) → Statement c` — TOTAL, every case the real evidence-tier
theorem indexed by its el-atlas id (CRS=intertwine, PRO=no-single-rail-quotient,
JOI=deMorgan-∧∨, WAR=⊓w-assoc, TWN=N₊-S-noncommute, NGL=bias-cannot-carry-verdict).
No escape constructor ⟹ a claim can't sit undischarged; adding one forces a witness.
**ADJ then graduated (commit 660ba94):** `Substrate.Logic.Evidence.Atlas` names the
chart-adjunction structure (Chart₊/Chart×/exp/log + lossless round-trips = a set-level
adjoint equivalence); `nedge-atlas` instantiates it on the evidence carrier's recode
(the discrete shadow of exp⊣log; continuous maps + the gcd/Bézout additive↔mult.
instance stay out of scope / Frontier). The Π now discharges **7** claims
(CRS/PRO/JOI/WAR/TWN/NGL/ADJ). Still open: Frontier SWP/GCX/NOE/IDC; the computed
vantage map (`visibility : Claim → Vantage → Verdict`); and `el-atlas-structured.md`'s
own header still says EMPTY (not regenerated — but the substrate no longer leans on it).

Next natural: deepen H² toward the holonomy proper (Axis regular-rep iso via
Substrate.Axes.act-axis / D₄ as group object / §8.6 V4Interface holonomy = H1(complex;V4) with
biasShadow as the projection to Nedge's scalar), OR a Logic.Evidence barrel + worked end-to-end
example.

**Source (historical).** Was `scratch/el-atlas/el-atlas-repo (1).tar.gz` (a
git repo, S1..S28, draft 16, v3.7). Key files inside: `el-atlas-spec.md` (composed
from `spec-src/00x0-*.md`), `el-atlas-cotype.md` (the provenance/drift log),
`features/*.feature` (claims-as-obligations), `tools/*-pilot.py` (witness pilots),
`README.md` (disciplines). Same disciplines as the substrate: monotonic correction
(RETRACT-in-place, never delete), grades [W]/[S]/[C], P/F/V "vacuity is a value",
no unindexed verdicts (SPACE MANIFEST + sha fingerprint, "unseparated-in-S_<fp>"),
commit-on-each-move, composed-not-hand-edited + shrink-guard, cotype survives lost
reasoning traces (it was the workaround for a web LLM getting rerouted/downgraded
mid-session — externalized regenerating state, reasoner-independent).

**THESIS.** el-atlas = exp/log ATLAS over a Belnap-Dunn 4-valued paraconsistent
evidence logic: carrier (E⁺,E⁻) two independent additive accumulators; (mass,bias)
basis; chart 𝔸=signed line [−∞,∞] (sign-neg through 0) vs 𝕄=semiring [0,∞]
(reciprocal-neg through 1); exp⊣log ADJOINT EQUIVALENCE (not iso — Lemma 2.5b,
lossless on (mass,bias)); §3 NO-QUOTIENT PROHIBITION; De Morgan = the two conjugate
involutions exchanging under NOT; log-semiring (AND~sum-of-logs / OR~log-sum-exp);
instrument/pilot witness layer. Our 2026-06 ℚ/Hedberg conversation independently
re-derived its keystones (see [[feedback_convergence_over_isolation]]):
Remark 2.5c ratio-as-collapse vs ratio-as-chart-image = my collapse-vs-transport;
§3.6 "zero-divisors resolved by representation-as-rationals, the number becomes
structured" = ℚ reduce/Canonical; §10 Martin-Löf transport CANDIDATE = the
RouteAgreement/Hedberg work (its missing witness).

**ENRICHMENT CANDIDATES (graded V=value, R=risk; el-atlas → substrate Agda):**
CONFIRMED CONGRUENCE (already true; enrich = NAME/cross-reference, near-free):
- C1 [V-hi R-lo] ℚ=(num,den)+reduce/Canonical IS el-atlas §3 prohibition + §3.6 lift.
- C2 [V-hi R-lo] gcd(ℕ semiring)/Bézout(ℤ ring) = 𝕄/𝔸; trace↔shape↔Bézout = chart
  transitions; `Wedge/Shape/Twist` companion/conjoint = the chart-cross already named.
- C3 [V-hi R-lo] `Q.Properties.RouteAgreement` + Hedberg + phase-witness triangle =
  the §10 Martin-Löf transport WITNESS + truncation(set)-vs-equivalence refinement;
  --without-K = the §3 prohibition / phase-index; routes-agree = the "named external
  collapse" §3 permits; triangle = Def 3.3 "balance = decline the quotient" as code.
NEW AGDA CONSTRUCTIONS (real work):
- N1 [V-hi R-med] `Atlas` record: "one value space, two charts, exp⊣log adjoint
  equivalence"; instantiate on existing pairs (gcd/Bézout; F₂-div/ℤ-div join ℕ-div
  from [[project_wedge_pentagon_sphere]]). Adjunction machinery exists (Free⊣Forgetful,
  Realizability gates = left adjoints).
- N2 [V-hi R-hi] carrier (E⁺,E⁻) Belnap-Dunn 4-valued + (mass,bias) + no-collapse,
  as an Agda type; 4 regions (support/refute/disagree/ignorance) = F₂/3+1-parity themes.
- N3 [V-med R-med] two conjugate involutions + locked-locus (negate≡swap only on
  (u,−u)) as the frame organizing the involution zoo (V₄/Hodge★/Coxeter/3+1).
- N4 [V-med R-med] log-semiring duality (De Morgan = the exchange) + resistor-network
  witness → tropical/GradedMonoid (cf commuting_sphere "semiring-VM via tropical").
STRUCTURE/DISCIPLINE (tooling/process; the SURVIVABILITY win):
- S1 [V-hi R-lo] MEMORY.md is over budget + truncating (flagged). Adopt el-atlas's
  cotype/compose-spec/structured-edition discipline: composed-not-hand-edited,
  depsort-generated structured edition, size-threshold→decompose. Makes ALL future
  work more survivable. FIRST MOVE candidate.
- S2 [V-med R-lo] "no unindexed verdict / SPACE MANIFEST + fingerprint / P-I-C grade +
  FRONTIER" → sharpen comments-dont-overclaim into graded+fingerprinted claims.
- S3 [V-med R-med] depsort harness (claims-as-tests, intrinsic-vs-coincidence circles,
  basis refinement) → enrich scripts/agda_similarity.py.
CORRECTION TO CARRY:
- X1 [witnessed] el-atlas DRIFT-2: doubling-tree is PRIMARY, Cayley-Dickson is an
  optional completion, product ABSENT in the witness → correct
  [[project_commuting_sphere]] "Morton≅Cayley-Dickson via cocycle": don't assert the product.

**STRUCTURED EDITION = the instrument output (`el-atlas-structured.md`, gen by
`tools/el-atlas-structured-gen.py`).** Not a ToC — a 26-claim DEPENDENCY LATTICE,
layer-sorted (0/1/2), with: (a) PERSPECTIVE-VISIBILITY tables (each claim P/F/U/V
under 16 vantages: FULL,P1,CLASSICAL,PROB,NO-NEG,CHAR-2,SEDENION,SPHERE,COMPLEX…) =
"no unindexed verdict" fully mechanized; (b) CIRCLES = mutual-constitution classes,
typed expressibility-intrinsic / truth-intrinsic / characteristic-break-coincidence
(separated-in-space by a named knob) — this is the substrate's "intrinsic vs
coincidence" (cluster-action) question MECHANIZED + exhaustively model-checked;
(c) computed glossary + cross-ref + independence count (195/351 pairs independent).

**BIG FINDING — el-atlas's claim lattice IS the substrate's commuting-sphere program,
instrumented.** Near-complete claim↔substrate map (textual correspondence [S]; Agda
identity unverified [C]):
- ADJ (chart adjunction exp⊣log, Layer-0, near-standalone) ↔ the Atlas (N1) / gcd↔Bézout.
- SWP (semiring-weighted parsing: "carrier semiring carries the SPPF's packed
  multiplicity; probability=positive-rail section, Viterbi=idempotent pinning,
  inside×outside=zipper product") ↔ the SPPF/PackedTree-half I flagged OUTSTANDING in
  [[project_sppf_eea_unification]] + "semiring-VM via tropical". THIS is the deeper SPPF.
- NGL ≡ V4I (G-value lift = ⟨fraction-add, swap⟩ on formal-quotient pairs, carrier/diagonal
  ≡ exact V₄, diagonal sign-involutions=Klein-4) ↔ ℚ/reduce ≅ V₄ (a CLAIMED IDENTITY).
- D4C ≡ NVE ≡ TWN (braided V₄/D₄ = central ext of V₄ by the twist [N,S]=−id; the cocycle
  of the doubling interface; trivial in char 2) ↔ [[project_cycle_generator_as_2_cocycle]]
  (Z/4 vs V₄ = H² classes) / the Cayley-Dickson cocycle.
- GCX≡RAD≡RDW≡ZDG≡ZDW (codec/radial/zero-divisor schedule; CD norm mult through octonion
  (Hurwitz); ZDs from sedenion; char-2 every rung) ↔ the Cayley-Dickson sacrifice ladder /
  GF(2) model / Morton codec / sacrifice spaces.
- PHS (phase bit trivial on classical section, nontrivial off) ↔ 3+1 parity / chirality F₂.
- L26≡LOC (locked-locus (u,−u)=c≡0; negate≡swap iff f=−id) ↔ locked-locus / gauge /
  [[feedback_chain_walk_blocks_rotation_factor]] (negate-vs-swap).
- PRO≡PUR (prohibition; pinning conflates conflict/ignorance) ↔ ℚ-never-to-ℝ / no-collapse.
- IDC (bare nodes collapse; distinct participation separates) ↔ twin-detection /
  [[project_k_v4_twins_fail_cells_false_negative]] / the cluster work.
- CRS/NOE (crossbar (mass,bias); Noether mass/bias conservation) ↔ N2 carrier geometry (UNBUILT).

**INSTRUMENT MECHANISM (studied `tools/el-atlas-depsort-v3.py`, 859 lines).** A
model-theoretic constitution analyzer. Formal semantics: claim `C : S → {P,F,U,V}`
(P=true-here, F=false, U=observable-but-undecided, V=not-statable); each `t_XXX(m)`
is a REAL computation over model m (e.g. `t_RAD` does Cayley-Dickson mult + norm
check at cdlevel; `t_NGL` verifies the 6 G-value identities; `t_SWP` runs a semiring
inside-outside parse). `KNOBS`=13 axes (pins,adj,neg,ops,lock∈8,coeff∈{real,gf2,
complex},cdlevel∈{2,4,8,16},probe…), `SPACE`=product (165888 models), `BASE`=baseline.
Pipeline: (1) SELF-CERTIFICATION AUDIT — `{C(m) ∀m}=={P}` ⟹ FLAGGED vicious (P-
everywhere = no intervention reaches ground = vacuous) = MY HEDBERG POINT MECHANIZED;
PRO passes (never F but V somewhere = theorem, constrained by statability). (2) Break-2
knob-sensitivity (which knobs move a claim off P; localized = only its own). (3)
SEPARATOR search: st=truth-sep (one F one P), sk=any-kind, co-movement; verdict
`(un)separated-in-S_<fp>` ALWAYS indexed; emits MINIMAL WITNESS MUTATION (smallest
knob-δ from BASE). (4) THE RIDE: recompute on joint dep-projection × cylinder
multiplier, assert `ride==full` (two sensors). (5) WITNESS-STRATUM 2nd-order relations
(JOINED/containment/partition-complement/disjoint-by-type/UNREGISTERED). (6) FINGERPRINT
= sha256(manifest + FULL MODULE SOURCE) — "helpers are test semantics". (7) monotonic
PRIOR_LEDGER (every prior space's verdict retained). (8) per-claim earned `_COMPLEX_STANCE`
(no blanket guards — the v3.5→v3.5a correction). `structured-gen` imports CLAIMS/SPACE
and emits the layered/circled/perspective-visibility markdown.

**PORT TO SUBSTRATE (S3) — substrate ALREADY has the primitives:** shape-hash tags
`⟦shape:30f92ad5⟧` = el-atlas's source-fingerprint; coeff∈{F₂,ℤ,ℚ}/carrier/cdlevel
(CD ladder)/--without-K = the KNOBS (real axes already); intuitionistic typecheck/
refute/vacuous/open = P/F/U/V ([[feedback_reject_lem_in_substrate]]); cluster
intrinsic-vs-coincidence = the separator question. DESIGN FORK for claim-evaluators:
(A) Python-model the conjectures el-atlas-style (fast, exhaustive over knobs, but
SAMPLED — e.g. _rad_mult_ok samples 40 products, NOT ∀); (B) Agda-typecheck-per-config
(∀-rigorous, slow). SUBSTRATE'S VALUE-ADD: evaluators can be REAL PROOFS — el-atlas's
[W]-by-sampled-model becomes [W]-by-typecheck. RECOMMENDED: `substrate-depsort`
retargeted to [[project_commuting_sphere]]'s conjectures, Python instrument for the
lattice + Agda proofs as the grade-promoting witness tier (= el-atlas's pilots+spec
architecture, + the Agda proof layer it lacks). Turns the prose conjecture ledger into
a model-checked, fingerprinted, perspective-indexed instrument = survivability-of-structure.

**RECOMMENDED FIRST MOVE (revised after the structured edition):** the cross-reference IS
the enrichment — map el-atlas's claim lattice onto the substrate's commuting-sphere ledger
(it's the instrumented ledger those conjectures wanted). Cheap+highest-clarity: land the
claim↔module map + X1 correction. Headline construction: N1 = ADJ (Layer-0, fewest deps).
Survivability/structure: S3 (adopt the depsort/perspective-visibility instrument — it
mechanizes the substrate's intrinsic/coincidence verdicts) + S1 (memory). Each lands as a
committed increment cross-referenced here. User steers; scratch is theirs (ask before writing).

**RECALIBRATION — TARBALL (2) `el-atlas-repo (2).tar.gz` (2026-06-11; supersedes the
"el-atlas is sampled, substrate brings the ∀" framing above — outdated).** (2) = S28→S65,
v3.13.0, +37 sessions in BEGIN/END "W" work-units with a WAL (`tools/wal-check.py`, BEGIN
banks pre=<sha>), hierarchical `spec-src/NN/`, lineage/christening tracking, flush-recovery
doctrine ("resent prompt ⟹ check the WAL"). 136 commits, legit full history. Corrections to
MY framing:
- NOT sampled-as-method. v3.8 FIBER-CERTIFICATE taxonomy (`_FIBER_CERT`): model-space
  coverage is EXACT (exhaustive + the ride); each claim's fiber is classed guard /
  analytic-points / exact / witness / cited-theorem / sampled(n) / mixed / UNAUDITED —
  sampling is ONE flagged weakest class. W21 "compiled over sampled — search demoted to
  SENSOR; EEA doctrine restored; box-kite ZD decomposition" (exact).
- el-atlas HAS its own Agda proof tier (W13 `proofs/VerdictCrossbar.agda`, --safe
  --without-K, Agda 2.6.3, ZERO imports): Belnap `Verdict=P|F|U|V` over `Bool×Bool`;
  `swapE`/`swapV` involutions; `intertwine` = De Morgan CROSSBAR as a refl-square (substrate
  coherence-by-refl); `no-single-rail-quotient` = §3 prohibition PROVEN by pigeonhole (=
  substrate no-collapse / my phase-witness triangle, SAME theorem). My "[W]-by-sample →
  [W]-by-proof value-add" was already an adopted external-review point (v3.8) AND already
  acted on (W13). STOP under-crediting el-atlas.
- SHARP substrate hook: `NEXT.md` opening move #2 — check "Nedge G-Value Calculus: Formal
  Specification (Agda)" + "Agda SPPF G-Value Calculus Synthesis" (user's Drive) against
  VerdictCrossbar AND the spec line-1987 POSTULATE-vs-DERIVE note. G-Value Calculus = ℚ.
  Substrate's **zero-postulate `ℚ-Canonical`** is a derive-not-postulate witness — could
  DISCHARGE el-atlas's open obligation #2. Synthesis is BIDIRECTIONAL, already in motion on
  el-atlas's side; substrate isn't "the missing proof tier" — it's the larger one NEXT.md
  reaches toward.
