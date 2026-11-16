# pyast rigcat — the dissolution + reuse-maximal composition

<!-- ═══════════════════════════════════════════════════════════════════════════════════════ -->
<!-- ⟡ REGROUNDING + RETROSPECTIVE (compaction-safe; the cotype root for this arc) -->
<!-- ═══════════════════════════════════════════════════════════════════════════════════════ -->

## ⟡ REGROUNDING #6 (retrospective-ritual + shadow-engineer) — 2026-07-13 (nat-enum J₂+J₃ + reuse-first cascade)

### Frozen state (G1) — committed this arc, all GREEN, --safe --without-K, zero postulates
- `42a4867` ⟡nat-enum — enumerate hom-squares (J₂), reuse-aware, --safe PARAMETERIZED emission.
- `452d9f3` ⟡nat-enum-residue — synthesize the RESIDUE of failed squares (wedge a=recon q b r):
  `len(⊗ˢ) = n²·len l₁ + m·len l₂` (exact ℕ fit); `sign(⊗ˢ)` (F₂/GF(2) fit).
- `a21b4fb`/`abc0670` reuse-first cascade — resolve_dep reuses the EXISTING parity : ℕ→F₂ (dropped my
  DUPLICATE); sign is F₂-valued reusing parity/bool→F₂/F₂ end-to-end; write_prim synthesizes only if absent.
- `0e35877` ⟡nat-enum-higher — the DISTRIBUTOR (J₃): `sign` RESPECTS δ (δ is EVEN, sign(δ)=0); `len`
  RESIDUE `+ 2·p·q·pyLength l₁` (cross-term); `decode` residue = δ (reuse OrientationDistributor). --safe emit.
- Prototypes (scratch, uncommitted): nat_enum_prototype, nat_residue_prototype, nat_higher_prototype.
- 6 commits unpushed (⟡push). `scripts/sppf_db.py` uncommitted (⟡es-orbit-resume).

### Delta + cause (G2/G3, blameless/systemic) — a RECURRING class, now CONFIRMED (2nd instance)
- **Delta 1 (the big one):** I synthesized AND committed a DUPLICATE `parity : ℕ → Bool` — the substrate
  already had `parity : ℕ → F₂` (Algebra.N-to-F2-Parity), framed for EXACTLY this. Caught by the cascade's
  own reuse-resolve + the user, NOT by me before committing.
- **Root cause (systemic, RECURRING):** I do not comprehensively reuse-search my OWN output before building
  — I searched `Foundation`, not `Algebra`. This is the SAME root cause as #5 (decode-⊕ reproven in a leaf;
  on-iso written twice). **Two confirmed instances ⇒ the class is real, not a one-off.**
- **Delta 2 (process):** `a21b4fb` committed an INTERMEDIATE nat_enum.py (its message described the final
  F₂/reuse code, the content was the older bool/write_parity version) — a background-commit timing gap; I
  didn't verify HEAD-content == working-tree. Fixed by `abc0670` (land the real version).

### Sustain (G6) — protect these
- The reuse-first cascade SELF-CORRECTED: resolve_dep's grep-before-synth CAUGHT my duplicate (returned the
  existing home). The architecture the user asked for (reuse-first, synth-only-absent) works AS a guard.
- The residue + higher synthesis landed REAL math: len's ⊗ˢ / distributor residues (exact), and sign(δ)=0
  (the distributor is an EVEN permutation) — a genuine discovery, mechanically found.
- Mechanical-synthesis discipline held: parity's DEF is base+step-detected (no hand-derivation); the missing
  primitive is BUILT, not flagged.

### Shadow-engineer reading (axis-signatures)
- The nat-enum builds were **010/110** (artefact↔shadows; build the tool through the tower centers).
- The reuse-first correction is **L₆ guard-reconstitution**: I attempted a direct goal→artefact synthesis
  (001, synthesize parity), the guard fired (don't synthesize what exists), and it RECONSTITUTED as the
  reuse-first cascade (110) — the guard's prohibition became the positive `resolve_dep` affordance. L₆ COMPLETE.

### THE DISSOLUTION (recursive common structure) — synthesize-vs-reuse, and the resolver tower
The arc's either/or was **synthesize vs reuse**. It dissolves: every "need X" is one operation —
**resolve X: REUSE if present in the tree, SYNTHESIZE if absent** (the Minesweeper flood: existing→reuse,
empty→cascade, obstruction→synth). `resolve_dep` IS that atom. And recursively:

  `resolve_dep` (one dep) ⊂ **⟡reuse-sweep** (all new defs, pre-commit) ⊂ **⟡core-extrude** (read the whole
  .agdai forest → resolve/extract/act).

All three are "read the tree/forest → resolve-or-act." Apex: **⟡tree-resolve** — reuse-first resolution
against the tree; `resolve_dep` is the query, ⟡reuse-sweep the sweep, ⟡core-extrude the forest-reader. The
catalog/reuse-index is its persisted index.

### ⟡ NEXT STEPS — labelled (invoke by symbol)

**⟡tree-resolve** — the apex: reuse-first resolution against the tree (resolve_dep DONE as the atom).
  Instantiated by:
  - **⟡reuse-sweep** — NOW URGENT (2nd confirmed reuse-miss). Generalize `resolve_dep` to a PRE-COMMIT sweep:
    resolve EVERY new def/lemma/module against the tree + the interner; flag duplicates + facts-reproven-
    in-leaves BEFORE commit. This is the G9 gate the class demands — the measure that would have caught BOTH
    the parity duplicate AND the decode-⊕ leaf-reproof.
  - **⟡core-extrude** — the .agdai-forest driver (read forest → extract → act); its actions are
    ⟡pyrig-rebuild-synth (extrude the rig) + ⟡reuse-sweep (dedup) + ⟡nat-enum-vocab (extract the vocab).
  - **⟡pyrig-rebuild-synth** — re-extrude synth_pyrig from the corrected SnRig/LehmerPath cores.

**⟡nat-enum** (the synthesizer — J₂+J₃ DONE). Remaining facets:
  - **⟡nat-enum-prove** — discharge the parameterized laws (J₂: len-⊕/sign-⊕/len-⊗ˢ/sign-⊗ˢ; J₃: len-δ/sign-δ)
    into --safe TREE theorems. Recursively (per the "no hand-derivation" principle): resolve each PROOF —
    MECHANICAL if finite-reducible (sign via parity's period-2 → a 2×2 refl-table, synth_agda_prototype's
    class), else the parameterized interface STANDS until a mechanical prover exists. This is the frontier
    of mechanical synthesis: statements+defs+residues are mechanized; PROOFS are the open edge.
  - **⟡nat-enum-vocab** — auto-extract the map/op vocab from the interner (drop the curated MAPS/SOURCE_OPS)
    — closes the loop (the vocab is the last curated input). An action of ⟡core-extrude.

**⟡pyrig-object-carrier** — OPEN frontier: the object carrier (pyast TERM) + orbit COLLAPSE (the rewrite rig
  is a bijection; collapse is the object story). Feeds ⟡pyrig-rebuild-synth + ⟡es-orbit-resume.

**⟡push** — 6 unpushed (per @{u}); wait for post-commit amend marker, fetch + ff.
**⟡es-orbit-resume** — the paused python orbit-interning (sppf_db.py uncommitted); grounded by SnRig.

### Probe state (standing-line rule)
- L₆ (guard-reconstitution) COMPLETE (synth-guard → reuse-first cascade).
- L₁ (positive-closure) STANDS on ⟡tree-resolve: resolve_dep (atom) is built; ⟡reuse-sweep + ⟡core-extrude
  are the reachable-but-unbuilt points — build ⟡reuse-sweep next (the class demands the gate).
- ⟡pyrig-object-carrier remains the one GENUINELY-OPEN construction (not yet an instance of a named center).

### G9 escalate (correct-by-construction) — the class is now CONFIRMED; the gate is overdue
- The reuse-miss (fact/def reproven or duplicated because I didn't comprehensively search) has **2 confirmed
  instances** (#5 decode-⊕/on-iso; #6 parity). Coverability: `resolve_dep` is a PARTIAL gate (reuse-first for
  nat-enum's deps only). The measure the class demands is **⟡reuse-sweep** — generalize resolve_dep to a
  pre-commit sweep over ALL new defs, at the HOOK/GATE layer (automatable ⇒ must be a hook, not memory).
  Until built, this is a live coverability RESIDUE, now overdue. Do not relabel done.

---

## ⟡ REGROUNDING #5 (retrospective-ritual + shadow-engineer) — 2026-07-13 (rebuild-trunk complete + reuse-dedup + nat-enum)

### Frozen state (G1) — committed this arc, all GREEN, --safe --without-K, zero postulates
- `11b4741` ⟡pyrig-rebuild-rig — PyRewrite = LehmerPath, interp = foldR (Coxeter words = generators).
- `9022d0e` ⟡pyrig-rebuild-semantics — pyLength (Coxeter length) + pySign (parity), LehmerAlgebra readings.
- `e46e5be` ⟡pyrig-rebuild-semantics-rig (HEART) — `perm-⊗ᶜ-step-decode`: the ⊗ᶜ-step coherence PROVEN
  by reduction to the tower's `lehmer-⊗ᶜ-step`. Retired my earlier "barrier" defer.
- `4d11e07` ⟡pyrig-rebuild-semantics-rig (RECORD) — `SnRig : RigAlgebra (λ n → Σ (Perm n) Iso)`. The
  genuine non-trivial rig algebra. Carrier = funext-free Sₙ (`Σ Perm Iso`, NOT `Σ Perm IsPerm` — the
  latter needs funext). `interp = foldR SnRig` = a rewrite ↦ its permutation. Every law reduces through
  decode to a definitional LehmerPath identity.
- `f67ce90` ⟡pyrig-rebuild-normalize — `normalize = encode` (Lehmer normal form), round-trips = tower iso.
- `894ce85` ⟡pyrig-rebuild-act — `actR = act ∘ decode` (= pyRecon transposed), functoriality reused.
- `b5m0d8fak` (IN GATE) reuse refactor — extracted `IsoDecodeLift.on-iso/on-iso₂` (decode-density lift)
  + relocated `decode-⊕` → `OrientationSumDecode`. Interner-confirmed dedup (nodes 561/772 gone,
  sharing 23.5%→13.5%).
- `scratch/nat_enum_prototype.py` — WORKING numpy hom-square enumerator; rediscovers decode-⊕, finds
  sign/len as ⊕-homs, prunes false. (uncommitted, scratch)
- 26 commits unpushed (⟡push pending post-commit amends).

### Delta + cause (G2/G3, blameless/systemic) — the reuse-miss is a NEW gap
- **Delta:** I reproved `decode-⊕` locally and wrote the `rewrite decode-encode` lift skeleton TWICE.
  Caught by the interner (`jea_pysim --recursive`) + the user's prompt, NOT by me before "done".
- **Root cause (systemic):** the reuse-search discipline (CLAUDE.md) fires on PLANS ("before building
  X, search"). There is NO counterpart that fires on my OWN COMPLETED output ("after building, dedup
  against the tree + against my own new modules"). So a general fact reproven in a leaf, and a
  skeleton written twice, survive to commit. The interner already CAN find this mechanically.
- **Prior delta (already retrospected #4-carryover):** the "RigAlgebra barrier" was an absence-claim
  before search; user rejected it → proven. Covered by CLAUDE.md's "absence-words ARE the trigger".

### Sustain (G6) — protect these
- The tower's density made EVERY rebuild face an instance (rig=LehmerPath, normalize=encode, act=act∘decode,
  the record's laws = decode-reductions). "Reuse-maximal" held.
- The interner is a real dedup oracle on MY OWN code — it found the skeleton with no hints.
- The numpy enumerator validated the auto-pushout: naturality facts are a finite, enumerable family.

### Shadow-engineer reading (axis-signatures)
- The rebuild faces were **110 mediated-composite** (goal→tower-shadows→Agda artefact), each landing an
  instance. The reuse refactor was **010 pure-SA** (artefact→shadows: extract the shared skeleton), then
  **111 triadic** (the extracted `on-iso` serves the original reuse-maximal goal). L₅ (SA-triadic) COMPLETED:
  the regroup (dedup) matched the original request (maximal reuse) — deliverable extracted (`on-iso`).
- Guard (e₃): no unmediated goal→artefact smuggling; every fact went through a tower center.

### THE DISSOLUTION (recursive common structure) — the either/or the open AIs pose
Three open build-AIs LOOK distinct: ⟡pyrig-rebuild-synth (extrude the rig), ⟡nat-enum (enumerate hom
facts), ⟡reuse-sweep (dedup my output). **Common structure, recursively:** all three are ONE driver —
*read the interned SPPF forest of the typechecked `.agdai` cores → extract structure → act*. They differ
ONLY in the ACTION: instantiate-rig / verify-&-emit-lemma / flag-duplicate. This is the auto-pushout
mechanism (`scratch/auto_pushout_typeholer_path_design.md`) with a pluggable action. So they collapse to:

  **⟡core-extrude** — the `.agdai`-forest-reading driver, action-pluggable. Its three actions ARE the three AIs.

That is the apex; the three are its instantiations, not separate tools.

### ⟡ NEXT STEPS — labelled (invoke by symbol)

**⟡core-extrude** — the unifying driver (read `.agdai` forest → extract → act). Instantiated by:
  - **⟡pyrig-rebuild-synth** — re-extrude `synth_pyrig` from the CORRECTED cores (SnRig/LehmerPath,
    not the old SPPF-over-positions). The synthesizer should read `interp=foldR SnRig`.
  - **⟡nat-enum** — productionize `nat_enum_prototype.py`: (a) model `⊗ˢ` via replay-aux/offsetDigit;
    (b) auto-extract the map/op vocab from the interner (drop the curated list); (c) emit Agda lemma
    stubs via `synth_agda_prototype.py`'s emitter, generalized past compose/id to the hom-square shape;
    (d) dedup proof-skeletons (via the interner) before emit.
  - **⟡reuse-sweep** — the G9-escalation driver: run the interner on changed/new `.agdai` and flag
    shared skeletons + facts-reproven-in-leaves BEFORE commit (the missing "dedup-my-own-output" gate).

**⟡pyrig-object-carrier** — OPEN conceptual gap. What carries the pyast TERM (objects), where orbit
  COLLAPSE lives (the rewrite rig is a BIJECTION — each perm its own normal word; collapse is the OBJECT
  story). `Objpy = SPPF (Fin n)` survives as the object carrier; the collapse = quotient by the Sₙ action.
  Feeds ⟡pyrig-rebuild-synth (what to extrude) + ⟡es-orbit-resume.

**⟡nat-enum-higher** — the multiplihedra dimension: climb J₂ (binary squares, done) → J₃ (a map coheres
  with associativity + the DISTRIBUTOR δ). In this strict substrate the associativity cells collapse
  (associators = id, `rig_coherence.py`); the ONLY non-collapsing higher rung is the rig distributor.
  So ⟡nat-enum-higher = "does F respect δ" — the morphism-analog of the Laplaza object-coherences
  (`wedge-pentagon-sphere`). Extends ⟡nat-enum.

**⟡push** — 26 unpushed; wait for `post-commit advisory (auto-captured)` in HEAD, fetch + ff, push.

**⟡es-orbit-resume** — the PAUSED python arc (`.claude/plans/radiant-weaving-dawn.md`): jea_rigcat.py +
  sppf_db.py orbit-interning (nodes = orbits). Now grounded by SnRig (the proven group) — the
  refactor's `on-iso`/normalize=encode ARE the orbit-rep machinery. Depends on ⟡pyrig-object-carrier.

**⟡pyrig-cospan** (stands) — the cospan face (PyAstRigCospan); may reframe post-rebuild as the object-orbit
  overlap. Lower priority.

### Probe state (standing-line rule)
- L₅ (SA-triadic) COMPLETED this arc (dedup ⇒ maximal-reuse goal ⇒ `on-iso` deliverable). 
- L₁ (positive-closure) STANDS on ⟡core-extrude: the three actions are named; the unified driver is
  reachable but not built — do NOT force it; build the first action (⟡pyrig-rebuild-synth or ⟡nat-enum)
  and let the common driver crystallize from two instances.
- ⟡pyrig-object-carrier is the one GENUINELY-OPEN construction (not yet an instance of a named center) —
  the honest frontier.

### G9 escalate (correct-by-construction)
- The reuse-miss (fact-reproven-in-leaf; skeleton-twice) is a RECURRING class. Coverability: the
  before-build reuse-search is at the CLAUDE.md-instructions layer; the AFTER-build dedup has NO layer.
  It is AUTOMATABLE (interner on changed cores) ⇒ per the charter it must be a HOOK/GATE, not memory.
  **That gate IS ⟡reuse-sweep** — siting the measure. Until built, it is a coverability residue (named,
  owned, not yet enforced). Do not relabel done.

---

## ⟡ REGROUNDING #4 (retrospective-ritual + shadow-engineer) — 2026-07-12 (SPPF-built-wrong)

### Frozen state (G1)
COMMITTED: PyAstRig (331753c), synth+dump (f1c72c9), Normalize (ee0d8dd), Cospan (c939bc6), synth-
orbit/normalize (757a65a), ground-residue (1c447be), ground-action+permMonoid (93f7a61). COMMITTING:
SPPFUP (bg b0q4yltn7). Research map + regroundings #1–3 in this file. ~19 commits unpushed.

### THE CORRECTION (G2/G3) — the record-orphan finding was an ARTIFACT of a wrong carrier
User: "our SPPF is built wrong. If you look at the LehmerRig and how it's meant to be used, each
Coxeter word IS a generator." VERIFIED against the tower:
- `coxeter-complete : IsPerm σ → CoxGen σ` — every perm IS a word in adjacent transpositions (`sadj`).
- `LehmerPath ≅ Perm` (`decode`/`encode`) — a LehmerPath IS a Coxeter word in normal form.
- `LehmerRig : RigAlgebra LehmerPath`, `foldR : RigAlgebra C → LehmerPath n → C n` — LehmerPath is the
  INITIAL rig algebra; `foldR` is THE universal interpretation of a word into any semantic rig.
So the rig of pyast REWRITES is NOT a new SPPF over positions — it IS `LehmerPath` (generators =
Coxeter words). I built `Objpy = SPPF (Fin n)` = the free semiring on OPERAND POSITIONS: I made the
OBJECT-carrier the rig, when the rig is the MORPHISMS (transformations). **ROOT CAUSE (systemic):**
before choosing the free-structure's GENERATOR SET I did not identify what the tower ALREADY models
as THE generators of that structure (Coxeter words = LehmerPath). This is why regrounding #3's
"record-orphan" was real-but-DERIVATIVE: the splits (pyEval≠foldR, act no record home) are ARTIFACTS
of the wrong carrier. Fix the generators ⇒ they DISSOLVE into instances.

### Shadow-engineer reading
Regroundings #2→#3→#4 are the iterated-subtraction converging: #2 "re-derived all four" → #3 verified
"lemma-grounded/record-orphaned" → #4 (USER as the decorrelated reviewer) "the orphan is because the
CARRIER is wrong." Each corrected the prior; the deepest is the carrier. The verification discipline
(⟡reuse-structural-first) SURFACED the anomaly (the splits) that the user then diagnosed — the guard
fired, the reviewer named the root. Signature: the whole ⟡pyrig-ground was a mediated goal→artefact
move whose guard (verification) exposed a smuggled carrier-choice.

### THE DISSOLUTION (recursive) — and it answers my own (a)/(b) fork
I asked: (a) reuse LehmerPath/foldR, vs (b) build the multi-generator Coxeter free rig. COMMON
STRUCTURE: both are "the free rig whose WORDS are permutations." `LehmerPath` = the free rig on the
SINGLE walking generator X (◂-tower builds all words); the `sadj` presentation = free rig on the n−1
Coxeter generators. `coxeter-complete` + `LehmerPath≅Perm` prove they are the SAME rig (Sₙ), two
PRESENTATIONS (normal-form vs word). So (a)=(b); use `LehmerPath` (the normal form), recognise the
Coxeter-word presentation via `coxeter-complete`. Recurse once more: the RIG CATEGORY of pyast
transformations IS the tower's `orientationRigCatSym` (the Sₙ-morphism rig category, Coxeter-free);
pyast enters as a `RigFunctor`/`RigAlgebra` VALUATION. **Invariant:** PyAstRig should be a THIN pyast
valuation on the tower's LehmerPath/orientationRigCatSym rig — NOT a parallel SPPF.

### ⟡ NEXT STEPS — labelled (invoke by symbol)
TRUNK `⟡pyrig-rebuild` — the rewrite rig = `LehmerPath`/`orientationRigCatSym`; pyast = a valuation:
- **⟡pyrig-rebuild-rig** — DONE, GREEN (committing bc3eeflyu). `PyAstRewrite.agda`: `PyRewrite =
  LehmerPath` (rewrite rig, reused); `interp = foldR` (pyEval, THE unique interpretation — the
  initiality split DISSOLVED into an instance); `interp-id = fold-idAlg`; `rewrite-is-coxeter-word =
  coxeter-complete∘decode-is-perm` (every rewrite IS an adjacent-transposition word — the correction
  WITNESSED). RETROACTIVE: this resolves the ⟡pyrig-ground splits — residue (already an instance via
  towerDiv), initiality (NOW an instance via interp=foldR), action (lemma-grounded via SnGroup; act =
  the LehmerPath/Perm action = the tower's). The splits were SPPF-carrier artifacts; LehmerPath
  grounds them. Non-destructive (old SPPF modules remain the object-carrier pending
  ⟡pyrig-object-carrier).
- **⟡pyrig-rebuild-semantics-rig** — DONE, GREEN (the "barrier" RETIRED). `PyAstRewritePermRig.agda`
  (heart, HEAD e46e5be): `perm-⊗ᶜ-step-decode` — the ⊗ᶜ-step coherence PROVEN by reduction to the
  tower's `lehmer-⊗ᶜ-step`. `PyAstRewriteSnRig.agda` (record, b4093od59): `SnRig : RigAlgebra (λ n → Σ
  (Perm n) Iso)` — the genuine non-trivial rig algebra; `interp = foldR SnRig` = a rewrite ↦ its
  permutation; `interp-is-decode`. CARRIER = the tower's funext-free Sₙ (`Σ Perm Iso`, NOT `Σ Perm
  IsPerm` — the latter needs funext for `IsPerm-prop`, unavailable). Every law reduces through `decode`
  to a DEFINITIONAL LehmerPath identity; built `decode-⊕` (mirrors `decode-⊗ˢ`). REUSE: `Iso`/
  `IsPerm→Iso`/`iso-blockSum` from OrientationRigCatSym/UP. TOOL: `synth_agda_prototype.py --class orbit`
  generates the CONCRETE-grade Sₙ GROUP instances (S₃ Coxeter-completeness, 62 lines, green, in seconds —
  the per-arity form the python consumes); its vocabulary is group-only (compose/id), so the GENERIC rig
  record's ⊕/⊗ coherence is the hand-proof above (outside the tool).
- **⟡pyrig-rebuild-semantics** — DONE (achievable readings + verified barrier), GREEN.
  `PyAstRewriteSemantics.agda`: `pyLength` (the rewrite's Coxeter LENGTH = Σ Lehmer digits = # atomic
  adjacent-transposition rewrites = cost, via a LehmerAlgebra fold) + `pySign` (parity/chirality via
  the tower's sign∘decode). VERIFIED BARRIER: a full non-trivial pyast `RigAlgebra` (rich valued
  `interp`/`foldR`) is gated by the `⊗ᶜ-step` coherence (replayᶜ) — the tower packages only
  `LehmerRig` (identity) + `TrivRig`; a new one is `OrientationProductStructural` territory →
  **⟡pyrig-rebuild-semantics-rig** (deferred). So `interp = foldR` is grounded (PyAstRewrite,
  LehmerRig = normal form); the achievable pyast readings are the two invariants above. Uncommitted
  (awaiting bc3eeflyu).
- **⟡pyrig-rebuild-normalize** — `normalize` = the Lehmer normal form = `encode` — an instance
  (the normalize↔encode question resolves: encode IS the canonical form). [110]
- **⟡pyrig-rebuild-act** — `act` = `decode`-then-apply; already grounded in `SnGroup` (survives). [010]
- **⟡pyrig-rebuild-synth** — re-extrude synth_pyrig from the rebuilt Agda (foldR/LehmerPath, not SPPF).
- **⟡pyrig-object-carrier** — OPEN HONEST QUESTION: what carries the pyast TERM (the objects being
  rewritten), distinct from the rewrite rig (LehmerPath)? Is `SPPF`-over-primitives still the object
  carrier, or subsumed? Verify — don't assume the term-carrier vanishes.

SALVAGED (survive the rebuild — SPPF the CONSTRUCT is fine; it was the wrong CARRIER for the rig):
- **SPPFUP** (`inside-unique`) — general SPPF free-semiring UP; stands (benefits ElAtlas/SWP).
- **⟡pyrig-ground-residue** (`pyRecon-is-towerDiv-residue`) — was ALREADY the right grounding
  (pyRecon used a LehmerPath residue) — it PRESAGED this correction. Survives.
- **permMonoid** (raw Perm = tower compose-monoid) · the research map · the synth pipeline (retargeted).

DEFERRED (the pre-correction open items, re-eval after rebuild):
- **⟡pyrig-ground-cospan** — verify structural-vs-CrossMul (still open; may also reframe post-rebuild).
- **⟡pyrig-synth-cospan** · **⟡pyrig-pipeline** (stands) · **⟡pyrig-difftest** · **⟡push** (~19).

DISCIPLINE (G9 — SHARPENED measure):
- **⟡reuse-structural-first** (v3): before choosing a free structure's GENERATOR SET, identify what
  the tower already models as THE generators of that structure. Here: transformations = Coxeter words
  = LehmerPath, NOT positions. Generator-set choice is the highest-leverage reuse decision.

### Probe state
`⟡pyrig-rebuild` (110) is FORCED (the correction compels it). `⟡pyrig-object-carrier` STANDS (verify,
don't assume). `⟡reuse-structural-first` (v3) is the standing guard for the rebuild's generator choice.

<!-- ─────────────────────────────────────────────────────────────────────── -->

## ⟡ REGROUNDING #3 (retrospective-ritual + shadow-engineer) — 2026-07-12 (post-⟡pyrig-ground)

### Frozen state (G1)
COMMITTED: PyAstRig (331753c), synth_pyrig+dump (f1c72c9), Normalize (ee0d8dd), Cospan (c939bc6),
synth-orbit/normalize (757a65a). IN FLIGHT: ⟡pyrig-ground-residue (bg bw1xanmhz, finalizing — HEAD
not yet moved). GREEN UNCOMMITTED: `permMonoid` + the action verified-split (working-tree change on
`PyAstRigGround.agda`, `AM`). Research map: `scratch/tree_research.md`. 17 commits unpushed.

### Delta + cause (G2/G3) — the "re-derivation" claim was itself imprecise; verifying sharpened it
Regrounding #2 asserted the arc "re-derived all FOUR" tower constructs. Tackling ⟡pyrig-ground
VERIFIED each face, and the result is sharper AND corrects that claim:
- **residue** — a DEFINITIONAL instance (`pyRecon-is-towerDiv-residue = refl`): pyRecon IS
  `act∘decode` over `towerDiv`'s Lehmer-digit residue. The tower's-own, exactly.
- **action** — a VERIFIED SPLIT: act's LAWS are already grounded (`act-id`/`act-∘` built from
  `SnGroup.apply-id`/`apply-compose`); `permMonoid` shows raw `Perm n` IS the tower's compose-monoid.
  BUT no RECORD home: `Actionᴳ` needs a strict `Group`, raw `Perm` is the transformation MONOID Tₙ
  (no bare-Vec inverse), Sₙ is a `SetoidGroup` (`Groups.Symmetric`, ≈), and there is NO `MonoidAction`
  record. Grounded at the LEMMA level, orphaned at the RECORD level.
**THE CORRECTED INVARIANT:** the arc did NOT re-derive the tower's THEOREMS — it REUSES them
(apply-*, decode, positions, compose-laws). It built NEW RECORDS (`Objpy`, `act`, `normalize`,
`shared`) because the existing RECORDS (`GradedRigCat`/`Objₛ`, `Actionᴳ`/`Group`, `CrossMul`/algebraic)
do NOT accept the pyast carrier (SPPF, not LehmerPath/Perm) / the monoid-not-group / structural-not-
algebraic readings. So PyAstRig = **LEMMA-GROUNDED + RECORD-ORPHANED**, not "re-derivation". Root
cause: regrounding #2 claimed "instance" from the research's NAME-MATCHES without verifying RECORD
FIT — the exact miss ⟡reuse-structural-first must extend to cover.

### Shadow-engineer reading
Verifying each face = the iterated-subtraction/decorrelation (G4): each verification (residue refl
fits; action reuse-search shows no Group) is decorrelated from the prior assumption. ⟡pyrig-ground-
{residue,action} = L6 reconstitution (the shadow reconstituted: residue→definitional instance,
action→verified split). The remaining faces (initiality, cospan) are pure-GS SHADOWS (goal→shadow,
not artefact) — STANDING lines: don't assume instance, VERIFY each.

### THE DISSOLUTION (recursive)
The four faces share one structure: each grounds at the LEMMA level (tower proofs reused) but the
RECORD-level instance is GATED by a carrier/packaging mismatch. Recurse on the either/or "bridge the
records vs accept the orphan": the common structure is **extract the GENERIC record BOTH the tower's
construct and PyAstRig's construct instantiate** (e.g. a `MonoidAction` record the tree LACKS — it has
`Actionᴳ` over `Group` but nothing over `Monoid`; a generic catamorphism both `foldR` and `cata`
instantiate). That converts "bridge each" into "extract the common structure once, both instantiate"
— the reuse-maximal move AND a genuine gap-fill. Bottoms out: the grounding is DONE where definitional
(residue); elsewhere it is a CHOICE — build the generic record (both instantiate) or accept the honest
lemma-grounded/record-orphaned status (the reuse is at the lemma level, which is correct and sufficient).

### ⟡ NEXT STEPS — labelled (invoke by symbol)
TRUNK `⟡pyrig-ground` — residue+action DONE; invariant = lemma-grounded / record-orphaned:
- **⟡pyrig-ground-residue** — DONE (definitional, `refl`; committing bw1xanmhz).
- **⟡pyrig-ground-action** — DONE (verified split; `permMonoid` green, uncommitted).
- **⟡pyrig-ground-initiality** — DONE. VERIFIED SPLIT + gap-fill (same shape as action).
  VERIFIED: `pyEval`/`inside` (SPPF fold) is NOT an instance of `LehmerRig.foldR` — DIFFERENT initial
  objects (SPPF = ungraded free SEMIRING on generators G; LehmerPath = graded initial RIG algebra).
  Same pattern (initial ⇒ unique fold), different instance. GAP FOUND + FILLED: `SPPF.inside`'s
  uniqueness (the free-semiring UP the header CLAIMS) was UNPROVEN — `Substrate/Algebra/Semiring/
  SPPFUP.agda` now proves `inside-unique` (inside = the unique semiring hom extending v), grounding
  every "universal fold" over SPPF (pyEval, ElAtlas, SWP) in a theorem, not the header's assertion.
  So pyEval's universality (my synth prose "the universal fold") is now BACKED. Green, uncommitted
  (awaiting biembe4g2). `normalize`↔`encode`: NOT verified — predict analogy not instance (normalize
  FORGETS the perm to canonicalise a term; encode RECORDS a perm's factoradic — dual, not the same
  map); a standing sub-question.
- **⟡pyrig-ground-cospan** — OPEN, VERIFY: is `PyAstRigCospan.shared` an instance of `CrossMul`, or a
  DIFFERENT (structural vs algebraic) reading? Predict: a split (CrossMul's graded case is deferred).

THE DISSOLVED MOVE (optional, reuse-maximal) — extract the common record instead of bridging each:
- **⟡pyrig-generic-monoidaction** — the tree has `Actionᴳ` (over `Group`) but NO `MonoidAction`
  (over `Monoid`). Extract it; BOTH the tower's `permMonoid`-actions and PyAstRig's `act` instantiate
  it. Grounds `act` by INSTANTIATION (not bridging) AND fills a genuine tree gap. [110]
- **⟡pyrig-ground-action-bridge** — (alt) the strict record instance via `SymBridge` + a strict-Group
  repackage of `Groups.Symmetric` + transport `act` — only if the strict-`Actionᴳ`/`Torsor` home is
  wanted (heavier than the generic-record extraction).

PIPELINE CLOSURE (unchanged):
- **⟡pyrig-synth-cospan** — extrude the cross-term into synth_pyrig (last Gap-B extrusion). [110]
- **⟡pyrig-pipeline** — SNAP-CHECK (111); STANDS until synth-cospan lands. Do not force.
- **⟡pyrig-difftest** — jea_pyalg vs pyrig_synth readout diff (handoff instrument, G8).

HOUSEKEEPING / PARALLEL:
- **⟡pyrig-commit-ground** — reconcile: bw1xanmhz commits residue-only (in flight); then commit
  `permMonoid`/action grounding separately (`AM` working-tree change).
- **⟡push** (17 unpushed) · **⟡es-orbit-resume** (paused Python arc, uncommitted).

DISCIPLINE (G9 — refined measure):
- **⟡reuse-structural-first** (EXTENDED): before claiming "X is an INSTANCE of Y", verify the RECORD
  FIT, not just the name-match. The research surfaced name-matches (residue=TowerDiv, cata=foldR,
  act=Actionᴳ); only VERIFICATION separated the definitional instance (residue) from the record-orphan
  (action). Name-match ≠ instance.

### Probe state (standing-line rule)
`⟡pyrig-ground-{initiality,cospan}` STAND (one point each — verify, do not assume instance).
`⟡pyrig-pipeline` (111) STANDS until ⟡pyrig-synth-cospan. `⟡reuse-structural-first` is the standing
mediation guard for any further "instance/reuse" claim in this subtree.

<!-- ─────────────────────────────────────────────────────────────────────── -->

## ⟡ REGROUNDING #2 (retrospective-ritual + shadow-engineer) — 2026-07-12 (post-research)

### Frozen state (G1)
COMMITTED: PyAstRig (331753c), synth_pyrig+dump (f1c72c9), PyAstRigNormalize (ee0d8dd). IN FLIGHT:
PyAstRigCospan+Makefile (bg bkqjlb3tq, full-build gate) then synth_pyrig.py orbit+normalize
extrusion. Research map: `scratch/tree_research.md` (4-agent sweep of witness-tower + rig trees).
Gap A (orbit) CLOSED end-to-end; Gap B (cospan) MODELLED (shared-equivariant proven), extrusion
pending. ~15 commits unpushed.

### Delta + cause (G2/G3) — the research is the load-bearing finding
The arc DELIVERED the pipeline-core closure, BUT the 4-agent structural sweep (= manufactured
independence, G4) revealed the arc **re-derived machinery the substrate already proves**:
- `normalize`/`pyRecon` residue **= `OrientationTowerDiv` (residue = Lehmer digit, `recon n l d =
  l ◂ d`)** — already modelled.
- `cata`/`pyEval` **= `LehmerRig` foldR** (LehmerPath = the INITIAL rig algebra, unique fold).
- `act`/torsor **= `orientationRigCatPerm`/`Sym`** morphisms (Sₙ-morphism rig cat, laws proven).
- `PyAstRigCospan` **= `Algebra.Wedge.CrossMul`** (the two cospan faces).
ROOT CAUSE (systemic): reuse-search fired on GREP/NAMES (searched "normalize"/"cross-term"), which
MISSED the generators because they live under DIFFERENT names (TowerDiv, LehmerRig,
orientationRigCatPerm) — the classic **similarity-not-grep** miss. The STRUCTURAL sweep (the tree
map / jea_pysim) is exactly the tool CLAUDE.md says to run BEFORE building, and it's what caught
this — AFTER the fact. Measure EXISTS; the gap is APPLICATION (didn't run the structural sweep on
entering the dense WitnessTower/Wedge subtree).

### Shadow-engineer reading
The research pass = the **mediation-guard firing**: it caught the direct goal→artefact building
(re-deriving without grounding = bypassing the reuse shadow) and redirects. `⟡pyrig-ground` is the
**L6 guard-reconstitution**: the un-grounded builds, caught, are reconstituted as the grounding
move (recognise each PyAstRig def AS its proven generator). Signature 110→111.

### THE DISSOLUTION (recursive common structure)
The four bridges (residue / initiality / action / cospan) are ONE move: recognise each PyAstRig
construct as an INSTANCE of its already-proven witness-tower/rig generator. Recurse: they bottom
out in a single fact — **`Objpy` (SPPF over pyast positions) is a specialisation of the
witness-tower rig machinery; the arc built its SHADOW.** The invariant: grounding = registering the
instances (act = a RigFunctor/Perm-morphism; normalize/pyRecon = TowerDiv's Lehmer-digit residue;
cata = foldR; cospan = CrossMul). Not four tasks — one trunk `⟡pyrig-ground` with four faces.

### ⟡ NEXT STEPS — labelled (invoke by symbol)
TRUNK — `⟡pyrig-ground` (dissolve the shadow into grounded instances; L6 reconstitution):
- **⟡pyrig-ground-residue** — DONE, GREEN. `PyAstRigGround.agda`:
  `pyRecon-is-towerDiv-residue : pyRecon rep (recon towerDiv n l d) ≡ act (insert-at d (decode l)) rep`
  — proof is `refl` (DEFINITIONAL): pyRecon = act∘decode over `towerDiv`'s residue-recon; a top Lehmer
  digit d acts by the tower's OWN step `insert-at`. The residue IS the tower's Lehmer digit, verified.
  ⚠ OVERCLAIM CORRECTED: the retrospective's "re-derived all FOUR" is only VERIFIED for the residue
  (the refl). The other three faces route through a DIFFERENT carrier (SPPF-over-positions, not
  LehmerPath/Perm) — clean-instance-vs-genuinely-new is a PER-FACE open question, not settled. So the
  verified claim is NARROWER: only the residue is confirmed the tower's-own.
- **⟡pyrig-ground-initiality** — relate `cata`/`pyEval` to `LehmerRig` (`foldR`, initial rig
  algebra) and `normalize` (first-appearance rank) to `encode` (the factoradic canonical). [110]
- **⟡pyrig-ground-action** — register `act`/torsor as a `RigFunctor`/`orientationRigCatSym`
  morphism (or `Actionᴳ`/`GTorsor` via `SymBridge`). Ties PyAstRig INTO the rig cat (was
  ⟡pyrig-action-bridge). [010]
- **⟡pyrig-ground-cospan** — relate `PyAstRigCospan` (structural) to `Algebra.Wedge.CrossMul`
  (algebraic, graded-deferred) — the two cospan faces. [010]

PIPELINE CLOSURE:
- **⟡pyrig-synth-cospan** — extrude the cross-term into synth_pyrig (pyrig_synth gains the binary
  coherence op; last Gap-B extrusion). [110]
- **⟡pyrig-pipeline** — SNAP-CHECK (111): demonstrate pyrig_synth as the pipeline core, I/O
  adapters only. STANDS until ⟡pyrig-synth-cospan + (ideally) ⟡pyrig-ground populate — do not force.

VERIFICATION (handoff, G8):
- **⟡pyrig-difftest** — run jea_pyalg AND pyrig_synth on one corpus, compare readouts (the
  operator=self instrument; residue to operator=other = is the normalize≈encode correspondence the
  RIGHT one).

HOUSEKEEPING / PARALLEL:
- **⟡pyrig-commit-cospan** (bg bkqjlb3tq) + **⟡pyrig-commit-synth** (after) — land the pending.
- **⟡push** — ~15 commits unpushed (fast-forward when ready).
- **⟡es-orbit-resume** — the PAUSED Python orbit-interning (`jea_rigcat.py`+`sppf_db.py`, uncommitted).

DISCIPLINE (G9 measure):
- **⟡reuse-structural-first** — on entering a DENSE subtree, run the STRUCTURAL sweep (the 4-agent
  tree-map / `jea_pysim --clusters` / reuse-index) BEFORE building — not grep. This arc's
  re-derivations were caught only by the structural map, after the fact. (Re-instance of
  similarity-not-grep + reuse-search-before-building; measure exists, gap was application.)

### Probe state (standing-line rule respected)
`⟡pyrig-ground` (110→111 trunk) is FORCED now (the research populated the generator-shadows — the
grounding is the compelled third point). `⟡pyrig-pipeline` (111) STANDS until synth-cospan +
grounding land — do NOT force the pipeline-core claim early. The guard (⟡reuse-structural-first)
is the standing mediation guard for any further building in this subtree.

<!-- ─────────────────────────────────────────────────────────────────────── -->

## ⟡ REGROUNDING #1 (retrospective-ritual + shadow-engineer) — 2026-07-12

### Where we are (frozen state, G1)
- **Agda, COMMITTED (HEAD 331753c, full build 1894/1894):** `agda/Substrate/WitnessTower/Wedge/
  PyAstRig.agda` — the free rig on pyast positions (`SPPF (Fin n)`), the group action
  `act = mapSPPF ∘ apply` (`act-id`/`act-∘` proven), the orbit coordinate `pyRecon rep r`
  (residue `r : LehmerPath n`), and the torsor `pyRecon-spine-injective`. Grounded constructions
  only (no sum/subtype/Σ). 13 commits ahead of origin, UNPUSHED.
- **Python, UNCOMMITTED:** `jea/metalanguage/synth_pyrig.py` (Agda-core→python reconstructive
  synthesizer: definition graph → initial F-algebra `F(X)=1+A+X²+X²` + fmap + catamorphism;
  ×/+ roles RECOVERED by following `pyEval→inside` into `SPPF.agdai`) and
  `jea/metalanguage/dump_agdai_pyast.py` (.agdai → jea_pyalg IR dump). `scratch/generated/
  pyrig_synth.py` is the emitted rig category; `--demo` is 4/4 + `2×(3+5)=16`.

### Delta + cause (G2/G3, blameless/systemic)
The arc ran far past the opening "an instance": reuse-maximal composition → loop closed
(Agda-core→python) → ×/+ recovered → the "is pyrig_synth the pipeline core?" test. Every step
forward was a USER CORRECTION of a premature declaration: log/antilog-zero, "unfused-axes"-wrong,
no-subtypes, no-sum-types, "×/+ is-a-gap-not-information". **Root cause (systemic):** the loop
had no gate forcing *"verify the structure DETERMINES this before calling it a gap/boundary/
information"* — the absence-word/overclaim trigger (CLAUDE.md) fires on PROSE declarations, and I
under-fired it. The measure EXISTS (CLAUDE.md "absence-words ARE the trigger" + memory
[[feedback_no_bespoke_sum_or_subtypes]] + [[feedback_reuse_search_before_feasibility_conclusions]]);
the residue is a coverage-of-APPLICATION gap, not a missing measure. (G9: no new gate warranted;
re-read the absence-words rule before any "gap/boundary/left-to-caller/information" claim.)

### Sustain (G6) — protect these
Reuse-search-before-building + **recursive either/or dissolution** produced every win (the whole
arc bottomed out at ONE invariant — the wedge residue `a = recon q b r`). Keep dissolving; keep
searching the tree before declaring.

### THE DISSOLUTION of the current either/or (pipeline-core test)
"pyrig not fully MODELED" vs "not properly EXTRUDED" is not a choice. Recurse:
- Gap A (orbit machinery: `pyRecon`+normalizer, in Agda but not extruded) = the **diagonal**
  residue (one carrier up to Sₙ; residue = Lehmer digit).
- Gap B (the CrossMul **cospan**: ast×cst cross-term, not modeled in Agda) = the **off-diagonal**
  residue (two carriers up to shared structure; residue = nilpotency degree).
- Common structure: BOTH are the **wedge residue = counit-defect**
  ([[adjunction-is-the-wedge-residue-counit]]). ⇒ they are ONE move, `⟡pyrig-residue`, with a
  diagonal face (A) and an off-diagonal face (B). Model+extrude the residue once.

### ⟡ NEXT STEPS — labelled action items (invoke by symbol)
Housekeeping:
- **⟡pyrig-commit** — commit `synth_pyrig.py` + `dump_agdai_pyast.py` (python-only; the pre-commit
  gate won't force an Agda rebuild). [shadow-sig 110 mediated: goal→shadows→artefact]
- **⟡push** — `git fetch` + fast-forward the 13 unpushed commits (wait for post-commit amend marker
  first). [I/O]

The pipeline-core closure — `⟡pyrig-residue` (the dissolved trunk; A + B are its faces):
- **⟡pyrig-synth-orbit** (Gap A / EXTRUSION) — DONE (the extrudable half). `reconstruct` now
  recognises orbit-coordinate defs STRUCTURALLY via the call hierarchy fold←comp←orbit-coord (a def
  that CALLS a comp = a further application of the action); orbits=['act-grown','pyRecon'].
  Emitted `pyRecon(rep, residue) = act(residue, rep)` (the recon direction of the wedge). Demo:
  pyRecon(rep,id)==rep, distinct residues→distinct points (torsor). HONEST BOUND (no overclaim): the
  FORGET/normalize direction (point → canonical rep = the interning KEY) is NOT modelled → the
  "orbit-interning RUNS" claim is BLOCKED on ⟡pyrig-normalizer; did NOT hand-write a normalizer.
- **⟡pyrig-normalizer** — DONE (Agda model + the hard proof), COMMITTING (background).
  `agda/Substrate/WitnessTower/Wedge/PyAstRigNormalize.agda`: `normalize t = mapSPPF (rank
  (positions t)) t : SPPF ℕ` (positions → first-appearance rank). THEOREM PROVEN:
  `normalize-orbit-inv : IsPerm σ → normalize (act σ t) ≡ normalize t` — orbit-equivalent terms get
  the SAME key. Crux = `rank-inj` (first-appearance rank invariant under injective relabel; IsPerm =
  apply injective) + the already-proven `mapSPPF-∘`. GENERAL (rank:ℕ handles repeated/absent
  positions — the spine-only worry was unfounded). Reuse-note: FirstAppearance is a DIFFERENT
  first-appearance (cycle-types), so the rank-canonicaliser is new. Idempotence (fixed-point over ℕ)
  is a follow-on, NOT needed for key correctness. --safe, no postulates.
- **⟡pyrig-synth-normalize** — DONE. GAP A FULLY CLOSED. synth_pyrig auto-detects the sibling
  PyAstRigNormalize.agdai, recognises the leaf-fold (positions = a cata into List) + normalize
  (calls mapSPPF), and emits `positions`/`rank`/`normalize`. Demo RUNS orbit-interning:
  normalize(spine)==normalize(act s spine) [same orbit ⇒ same key, the proven normalize-orbit-inv],
  normalize(spine)≠normalize(other) [distinct orbit ⇒ distinct key] ⇒ intern(normalize(t)) interns
  ORBITS not points. positions reuses the emitted `cata`. UNCOMMITTED: synth_pyrig.py (this
  extrusion); PyAstRigNormalize.agda committing in background (bb5ql5awx).
  ⇒ GAP A (orbit) is closed end-to-end Agda-core→python; only GAP B (⟡pyrig-cospan) remains before
  ⟡pyrig-pipeline.
- **⟡pyrig-cospan** (Gap B / MODELLING; was ⟡pyrig-semantics) — model the CrossMul cospan (ast×cst /
  two-carrier cross-term = the off-diagonal residue) in Agda, then extrude it into the synthesizer.
  Reuse `Substrate.Algebra.Wedge.CrossMul` + `jea_pyalg.CrossMix` as the two carriers. [100]
- **⟡pyrig-pipeline** — SNAP-CHECK: after A+B, DEMONSTRATE `pyrig_synth` as the pipeline core with
  I/O adapters only (lower → pyrig_synth → readout); show no non-I/O exterior adapter remains.
  This is the original goal's completion. [111 triadic-full]

Grounding (Agda):
- **⟡pyrig-action-bridge** — register `act`/torsor as an `Actionᴳ`/`GTorsor` instance via `SymBridge`
  (`S-Group : SetoidGroup (Permutation n)`); makes PyAstRig non-orphan, grounds the action in the
  generic. [010 pure-SA]

Verification / handoff (G8):
- **⟡pyrig-difftest** — the HANDOFF INSTRUMENT for the blind spot "is `pyrig_synth` extensionally =
  the jea_pyalg pipeline, not just structurally plausible?": run BOTH on the same corpus, compare
  readouts (operator=self). Residue left to operator=other: whether my SPPF-encoding of the
  pipeline is faithful. [pure-G guard → run before claiming ⟡pyrig-pipeline done]

Parallel (separate arc, do not conflate):
- **⟡es-orbit-resume** — the PAUSED Python orbit-interning (`jea_rigcat.py` + `sppf_db.py`,
  UNCOMMITTED from before this arc) — decide commit-or-drop; distinct from pyrig. [external]

### Probe state (shadow-engineer, standing-line rule respected)
- L1 positive-closure: `⟡pyrig-commit`(110) reachable now (artefact exists). COMPLETE-able.
- `⟡pyrig-residue` trunk: two faces `⟡pyrig-synth-orbit`(A) + `⟡pyrig-cospan`(B) are the forced
  decomposition; `⟡pyrig-pipeline`(111) is FORCED only once BOTH faces populate — until then it
  STANDS (do not force it; do not claim pipeline-core until A+B done + ⟡pyrig-difftest run).
- Guard (L2/L3): every "gap/boundary" claim must fire the absence-word check first (the systemic
  root cause above). This is the mediation guard for this arc.

<!-- ═══════════════════════════════════════════════════════════════════════════════════════ -->


## Goal (user, verbatim-ish)
Instantiate rigcat in the Agda repo using **pyast primitives and transformations** as the
category rigcat grades over — model the **set of valid semantics-preserving transformations**
over pyast's IR. Deeper: a **formal category for rewrites under group action, grounded in the
witness tower, so that growing the size of the group automatically constructs all the
consequences** of the larger group. Maximal reuse / maximal prebuilt-free-structure. Perm
morphism is the starting point. "A basic impl should be < 10 lines." There is a Properties
file that constructs a concrete rigcat as a **free graded UP taking a homomorphism and a span**.

## The either/or, dissolved recursively (per user's standing principle)
- L0: pyast = free-rig **generators** vs pyast = fold **valuation/target**.
- L1 common structure: the **Free ⊣ Forgetful adjunction** — generators = unit η:G→UFG,
  valuations = hom-set transpose FG→A. Same structure.
- L2 (under unit vs counit): the **universal arrow / fold** (`foldF-free-unique`).
- L3 (under the fold): `a = recon q b r` — the **witness-tower `Trace`/wedge step**,
  counit-defect residue ([[adjunction-is-the-wedge-residue-counit]]).
- Bottom / invariant: the tower's single decomposition step, iterated = **already the tower**.
  `Action.agda`: the rung step `τ = insert-at p σ = recon (suc n) σ p` IS Sₙ→Sₙ₊₁
  (insert a generator at Lehmer slot p) — "grow the group" = the wedge recon = the Trace step.

⇒ Build **`Free PyPrim`** (the graded free-rig functor), whose unit is the generator
embedding and whose UP is every valuation, and whose action-on-grade is the Sₙ tower step.

## Confirmed reuse surface (mechanical)
- `Algebra/Semiring/SPPF.agda`: `data SPPF (G)` = **free semiring on generators** (gen/one/⊗/⊕,
  no zero — correct: it's a **rig**, ring comes via log/antilog, not a zero ctor [user]).
  `inside : Semiring A → (G→A) → SPPF G → A` = the universal fold (hom + (valuation) span-leg).
- `OrientationRigCat.agda`: `record GradedRigCat (Obj:ℕ→Set) (Hom)`.
- `OrientationRigCatPerm.agda`: `orientationRigCatPerm : GradedRigCat Objₚ Homᵣ`,
  `Homᵣ i j = Σ(i≡j)(Perm j)`. **CRUCIAL: idᵣ/∘ᵣ/left-idᵣ/right-idᵣ/assocᵣ/braids are all
  OBJECT-CONTENT-INDEPENDENT** (ignore the object args) → the whole proven Sₙ morphism suite
  transplants onto ANY `Obj:ℕ→Set` supplying ⊕obj/⊗obj.
- `OrientationRigInitial`: `LehmerPath` is the **initial** rig algebra (foldR unique out).
- `OrientationRigFreeUP`: `FreeRigAlgebra` + `foldF`/`foldF-free-unique` (free UP, takes a hom g).
- `OrientationRigCatUP/Properties`: `freeObj T` + `freeFunctorₛ` (free graded functor UP;
  matches "free graded UP taking a homomorphism").
- `WitnessTower/Wedge/Action.agda`: insert-at = the group-growth wedge (the tower step).

## The two real boundaries the last mile hits (INFORMATION, not blockers)
1. `orientationRigCatPerm`'s braid module is **`private`** → can't import `B⊕.swPerm` to
   re-bundle a GradedRigCat over pyast objects without exposing it (a small edit to a heavy
   proven module) or re-deriving braids.
2. The **GENERAL free functor into an arbitrary target T is explicitly NOT built**
   (OrientationRigCatUP/Properties header): F-⊕obj-∧ needs a ⊕-unit/assoc law the target's
   bare `GradedProductOver` product deliberately lacks. So "free RigFunctor into
   orientationRigCatPerm" is blocked for a documented reason — only the skeletal self-functor
   (`freeFunctorₛ = id`) and the *uniqueness* (any-target) are built.
3. Putting pyast content in objects reopens the multiplicative grade `(ℕ,*,1)` labeling
   (Vec ⊗ needs Fin(i*j)→Fin i×Fin j + a PyAtom pairing) — the distributor/SOP frontier the
   existing design parks in the Perm morphisms over singleton objects (why Objₚ = grade-⊤).

## Reuse-maximal composition (the convergent read)
`Free PyPrim` = `SPPF PyAtom` (free rig on pyast primitives = what it grades over); the
rewrites-under-group-action = the witness-tower `Perm`/`LehmerPath` Sₙ (`orientationRigCatPerm`,
inherited, grows via `Action.insert-at`); joined by the universal fold `inside`/`foldR`. The
rewrite-orbit of a pyast term = its LehmerPath canonical form (= the earlier Python
orbit-interning, now formal + self-extending).

## OPEN (the one thing not derivable — needs the user's pointer)
Which specific "free graded UP taking a homomorphism **and a span**" Properties file? Candidates:
`freeObj`/`freeFunctorₛ` (OrientationRigCatUP/Properties), `foldF-free-unique`
(OrientationRigFreeUP), or the SPPF/CrossMix cospan fold. "span" undecoded. This picks the
last-mile packaging (RigFunctor vs fold) and whether to expose the private braids.

## SHARPENING (external review — load-bearing correction)
The group does **NOT** act on `SPPF`. It acts on the **generator positions** (`Fin n`). Since
`SPPF` is the **free rig FUNCTOR**, its action on a generator map lifts a position-permutation
`Fin n → Fin n` to a rig-endomorphism **by functoriality** (`mapSPPF`) — the free extension
writes itself. ⇒ pyast content lives in the **generator set**; symmetry in `Perm n ↷ Fin n`;
`SPPF`'s map does the lift. This **dissolves boundary #3** (multiplicative object labeling): we
never put a `GradedProductOver` on pyast-Vec objects. `Action.insert-at` (Sₙ→Sₙ₊₁) = the
naturality square for extending generators ⇒ every new generator induces every new rewrite for
free (Free preserves colimits). "span" = the reviewer reads it as the *semantic* cospan
(interpretation witness), addable later — NOT a prerequisite. So ⟡pyrig-pointer no longer blocks.

## Next steps (labelled)
- ⟡pyrig-free — DONE, GREEN (exit 0, .agdai built). `Substrate/WitnessTower/Wedge/PyAstRig.agda`:
  `PyPrim`, `mapSPPF` (free extension), `Objpy n = SPPF (Fin n)`, `act σ = mapSPPF σ` (rewrite
  under group action), `pyEval = inside` (universal interpretation fold). ~14 lines, reuse-only.
- ⟡pyrig-action — DONE, GREEN (exit 0, --safe, no postulates). Extended PyAstRig.agda:
  `act σ = mapSPPF (apply σ)` (witness-tower Perm n on positions), `act-id` + `act-∘` PROVEN
  (functoriality of mapSPPF over apply-id/apply-compose), `act-grown = act ∘ insert-at`
  (Sₙ→Sₙ₊₁ acts by the SAME act, zero new code). HONEST BOUNDARY (kept as residue, not forced):
  did NOT package a `GradedRigCat Objpy` record — that needs an honest `⊗obj : SPPF(Fin i)→
  SPPF(Fin j)→SPPF(Fin (i*j))`, which is the tensor/distributive (boundary #3) frontier; the
  rigcat of the SYMMETRY is `orientationRigCatPerm` (reused), and `act` is its representation on
  pyast terms. The three axes stay unfused (syntax SPPF / symmetry Perm / interpretation inside).
- ⟡pyrig-orbit — DONE, GREEN. `pyRecon rep r = act (decode r) rep`: a point = an orbit rep +
  a RESIDUE `r : LehmerPath n` (the factoradic orbit coordinate, per-level `◂` digit = the
  orientation). The orbit is NOT a collapse; the residue is KEPT (never discarded). Couples
  symmetry (which point) to interpretation (meaning, orbit-invariant) at the point-within-orbit.
- SUBSTRATE-DISCIPLINE corrections applied (memory [[feedback_no_bespoke_sum_or_subtypes]]):
  (a) removed `Σ same-orbit` (subtype/proposition-packaging — the orbit coordinate is a TOTAL
  construction `LehmerPath n`, the point IS its residue); (b) removed `data PyPrim` (sum type —
  the meaning is the CONSUMER's valuation `Fin n → A`; `pyEval = inside`); (c) SPPF zero-free is
  correct (rig, ring via log/antilog). Whole module: Fin/SPPF/Perm/LehmerPath only, no bespoke
  data/Σ. GREEN.
- ⟡pyrig-torsor — DONE, GREEN (--safe, no postulates). `pyRecon-spine-injective`: on the
  position-spine (each Fin n once), distinct residues ⇒ distinct points — LehmerPath n ≅ the
  spine's orbit (a torsor). Proved from the tower's OWN faithfulness: `spine-sep` (mapSPPF-∘ +
  constructor injectivity gen-inj/⊕-injˡ/ʳ, fine without-K as SPPF is non-indexed) → `act-
  faithful-spine` (apply-injective) → `pyRecon-spine-injective` (decode-injective). "Different
  points in one orbit" is now a THEOREM, grounded, no sum/subtype.
- ⟡pyrig-commit — DONE. Committed PyAstRig.agda (HEAD 331753c, full build 1894/1894 PASS,
  post-commit amend settled). 13 ahead of origin, unpushed.
- ⟡pyrig-collapse — DONE (verdict). act/act-id/act-∘ = the generic `Actionᴳ`/`GTorsor` SHAPE, but
  the tower packages Sₙ as `S-Group : SetoidGroup (Permutation n)` (≈), bridged to raw Perm (≡)
  only via `SymBridge` — so the proper grounding is a bridge INSTANCE, not an in-place collapse;
  `act`/`spine` names are idiomatic (every action module uses `act`), no rename. Filed
  ⟡pyrig-action-bridge (register Actionᴳ/GTorsor via SymBridge) as the grounding follow-up.
- ⟡pyrig-synth — DONE. Validated + CLOSED THE LOOP. `jea/metalanguage/synth_pyrig.py` (the
  Agda-core→python mirror of synth_agda_prototype): reads PyAstRig.agdai through the SHARED SPPF
  interner (jea_agdai → same Intern jea_pyalg uses), DISCOVERS the structure mechanically per-def
  alphabet — SPPF ctors {gen,one,⊗,⊕}, mapSPPF=fold, act=mapSPPF∘apply, pyEval=semiring fold — and
  EMITS runnable python (scratch/generated/pyrig_synth.py). --demo RUNS it and checks EXACTLY the
  Agda-proved laws: act-id, act-∘, torsor (pyRecon-spine-injective), plus EQUIVARIANCE
  `pyEval(v, act s x) == pyEval(v∘s, x)` (mapSPPF functoriality). Charter: all four gates ✓.
  OVERCLAIM CORRECTED (external review): earlier demo/prose said pyEval is "invariant under act
  (Agda orbit-invariance)" — FALSE. act with a FIXED valuation is NOT invariant (relabelling
  changes leaf values; only the full-spine + commutative-fold special case looked invariant); and
  orbit-invariance was NEVER proved in Agda (proved: act-id/act-∘/torsor). The honest statement is
  EQUIVARIANCE (meaning transports with σ). A passing special-case demo made a false general claim
  print True — verify the claim matches what's proved, not what a witness happens to show.
  UNCOMMITTED: synth_pyrig.py.
- ⟡pyrig-synth-graph — DONE. Rebuilt synth_pyrig recognisers to be STRUCTURAL (over the interned
  clause graph), not lexical. Probe confirmed the recursion graph: mapSPPF = Defn[Pi, Clause×4],
  each Clause = [.., PATTERN, BODY]; a fold reconstructs the pattern ctor with a self-call per
  recursive field. Recognisers: ctor = qname in pattern position (arity = pattern child-count);
  fold = ≥2 ctor-cases + self-recursive + reconstructs; comp = non-rec/non-proof applying a fold;
  eval = non-rec folding into Semiring; proof = references `_≡_`. Discovered {gen:1,one:0,⊗:2,⊕:2},
  folds[mapSPPF], comps[act], evals[pyEval]; proofs/spine/pyRecon excluded structurally; demo still
  4/4. Reuse note: implemented the clause-walk INLINE (jea_sppf_torsor not import-safe;
  fiber_skeleton too coarse — doesn't split pattern/body). cohomology() available as an idiom
  cross-check (--cohomology) if wanted. UNCOMMITTED: synth_pyrig.py.
- ⟡pyrig-action-bridge — (open) register act/torsor as Actionᴳ/GTorsor instance via SymBridge.
- ⟡pyrig-semantics — (open) the "span"/cospan interpretation leg (CrossMix cospan).
- ⟡pyrig-synth-UP — DONE. synth_pyrig rebuilt as a semantic reconstruction (not local heuristics):
  CALL GRAPH (calls, not mentions) + POLYNOMIAL FUNCTOR from arity+recursive-positions → SPPF = μF,
  mapSPPF = fmap, act = fmap∘apply, pyEval = catamorphism. Emitted `cata(alg,·)` is generic over an
  F-algebra. F(X) = 1(one)+A(gen)+X²(⊕)+X²(⊗).
- ⟡pyrig-synth-roles — DONE. FILLED THE ×/+ GAP (user: "that IS a gap, and filling it was the point
  of instantiating PyAstRig"). Earlier I wrongly flagged ⊗-vs-⊕ as "left to the caller / information
  not a gap" — WRONG (absence-word trap). The reconstruction now FOLLOWS the pyEval→inside call edge
  into SPPF.agdai and reads which monoid each ctor's clause uses: ⊗→Semiring.*-monoid ⇒ ×,
  ⊕→Semiring.+-monoid ⇒ +, one→*-monoid+ε ⇒ ×-unit (rig, no zero). roles {'_⊗_':'mul','_⊕_':'add',
  'one':'mul'} RECOVERED, not guessed; emitted pyEval bakes them. Demo proof: 2×(3+5)=16 (swapped
  would be 17). The rig structure is recovered end-to-end Agda-core→python. UNCOMMITTED:
  synth_pyrig.py, dump_agdai_pyast.py.
- LESSON (overclaim/absence-word): don't label an unfilled hole "information, not a gap" — verify
  whether the structure determines it FIRST. Here PyAstRig was instantiated precisely to make ×/+
  determinate (via pyEval=inside); the fact was one call-edge away. [[feedback_reuse_search_before_feasibility_conclusions]]

---

## REGROUNDING #7 (2026-07-13) — "isn't all this in the sqlite DB?" (user, load-bearing)

**Finding (verified, not asserted).** `catalog/catalog.db` (event-sourced projection, gitignored/regenerable)
ALREADY materializes everything `reuse_tui.py` re-derived by re-interning raw `.agdai`:
- `_node` 77394, `node_child` 362307, `shared_subtree` (fanin≥2) **20460**, `_unit` **18269** (== jea_pysim's
  unit count), `unit_node` 417123, `orbit_node` 10091.
- `reuse_tui --build` re-interned 1906 cores → bespoke `scratch/generated/sppf_index.json`: a PARALLEL,
  drift-prone store (this IS why the stale-core problem kept biting — re-decoding raw interfaces vs reading
  the projection). Shadow-engineer e₂ (shadows↔artefact): the TUI artefact duplicates the DB shadow.

**The one gap = provenance.** The projection lacked `copy` (Agda `Definition.defCopy`). Fixed in
`⟡es-p3-copy` (commit 1e4c8b6): `unit_obs.copy` ← defmarks' per-record `copy` (same shim), carried into
`_unit.copy`, exposed on the `unit` view. Full rebuild (temp DB, 204s): 18269 units, **4114 copies**.

**The verdict is now a JOIN, not a re-derivation** (proven over the fresh DB):
`shared_subtree ⋈ unit_node ⋈ unit.copy` → 13324 DUP (all originals) / 2151 MIXED / 1004 CONSOLIDATED.
Top DUP orbit: a shared subtree with 495 independent (copy=0) instances = a real consolidation target.

**Labeled next steps (⟡):**
- ⟡db-install — install the fresh copy-carrying DB over `catalog/catalog.db` (regenerable; a destructive
  replace → confirm first). Or regenerate in place via `python scripts/sppf_db.py ""` (all cores).
- ⟡reuse-query-db — rewire `reuse_tui`/`reuse_sweep` to QUERY catalog.db (retire the re-intern + JSON cache
  + jea_pysim `copy` plumbing + the fail-loud stale-core scaffolding, which all treated a symptom whose root
  cause was "reads raw cores, not the DB"). head/size/instances/contains/rung all derive from
  node/node_child/unit_node.
- ⟡es-copy-gate — the copy column needs a fresh ingest (unit_obs gained a column); ensure the standard
  catalog rebuild path (gen_catalog / pre-commit) reingests so copy stays populated.

## REGROUNDING #7 — resolution (committed)

- ⟡es-p3-copy (1e4c8b6): copy in the projection (unit_obs/_unit/unit view).
- ⟡db-install: regenerated catalog.db in place (18269 units, 4114 copies). Backup: scratchpad/catalog.db.bak.
- ⟡reuse-query-db (d216741): reuse_tui.db_rows() + reuse_sweep + sppf_query `reuse` all QUERY catalog.db.
  Retired the jea_pysim re-intern + bespoke JSON cache + fail-loud stale-core scaffolding. Verdict via
  defCopy for all 7098 orbits (0 heuristic). TUI headless-smoke green.
- ⟡es-copy-gate: SATISFIED by construction — write_events DROPs+recreates unit_obs each build (sole writer);
  reuse_catalog never touches unit_obs; consumers fail-loud if copy absent.
- ⟡node-view-kindid (in flight): FIXED the PRE-EXISTING empty-`node`-view bug — project_sppf's tid was
  non-inserting, so node kinds ("AgdaCore") were never in `terms` and the view's kind_id inner join
  dropped every row (broke sppf_query fanin/extract/clusters too). Made tid intern-if-missing; rebuilding.
- Design notes: subtree size = CAPPED unfolded count (exact distinct = 4.5GB/32s, too heavy); head via
  _node LEFT JOINs (op ▸ role).

Remaining ⟡: node-view-kindid verify+commit; ⟡consolidate-coxeter (now: pick a ✗DUP orbit from
`sppf_query.py reuse` / the TUI and parameterize); ⟡push (unpushed commits); the pyrig frontier
(⟡nat-enum-prove, ⟡pyrig-object-carrier, ⟡core-extrude).

---

## REGROUNDING #8 (2026-07-13) — retrospective-ritual + shadow-engineer at the session boundary

### Retrospective (gates that constrained, not narrated)

- **G0 precommit.** Session opened on ⟡reuse-provenance-wire (thread defCopy to the verdict). Standing
  mission: a meaningful pyast RigAlgebra, grounded in the witness tower, maximal reuse.
- **G2 delta.** Expected: wire defCopy through the jea_pysim cache. ACTUAL: that cache was a PARALLEL
  STORE duplicating catalog.db; consolidated onto the projection instead (better AND smaller — retired
  code). Surfaced by the user's "isn't this all in the sqlite DB?"
- **G3 cause.** trigger = committed provenance on the re-intern path. ROOT = did not check whether the
  data already lived in a projection before building a derivation. contributing = the recurring
  "stale-core" fights were a symptom of the same root (raw cores vs the DB).
- **G6 sustain (protect these).** verify-structurally-before-asserting (node-view bug found by grounding;
  S₄ confirmed against reuse-index, not asserted); fail-loud on the user's prompt; the recursive
  common-structure lens paid off 3× (min_fanin+SCATTER = κ; 5 knobs → 3 intensive → S₄; s vs s/n).
- **G8 handoff.** The S₄ identification + s/n fix are UNVERIFIED — but the instrument is self-runnable
  (⟡verify-s4-basis), so per probe-before-handoff it is a RUN, not a handoff. Genuine operator=other
  residue: whether the (κ,φ,σ) box faithfully matches what the USER means by "a parameterization target"
  (only the user judges a real target).
- **G9 escalate (recurring class → coverability).** ROOT is a class: "derive before checking the
  projection." Measure = extend the reuse-search trigger to DATA HOMES. Sited as ⟡reuse-search-data-homes
  (propose the CLAUDE.md line; memory feedback_reuse_analysis_queries_catalog_db already deposited).

### The recursive either/or collapse (common structure under the open threads)

Every open thread bottoms out in ONE invariant: **the SPPF projection (catalog.db) is the single
substrate; the rest are its symmetry-readings.**
- reuse verdict   = the SPPF's shared-subtree (sharing) reading.
- S₄ tunable space = the symmetry of the orbit-invariants {n,m,c,s} (V₄⋊S₃ on 4 counts).
- rig-orbit interning (plan radiant-weaving-dawn) = SPPF nodes as ORBITS under the proven rig group.
- pyrig mission    = a RigAlgebra whose carrier IS pyast structure = the same SPPF.
So "tooling vs mission" DISSOLVES: the tooling is the mission's substrate-reading apparatus. The either/or
was never two things.

### Shadow-engineer (Fano)

- The user's "isn't it in the DB?" = a **guard event (001)**: rejected the direct goal→artefact (wire the
  cache) and redirected through shadows (the projection) → **L₆ guard-reconstitution** fired; the mediated
  composite (DB-backed tooling) realises what the direct move would have, correctly.
- **L₁ positive-closure COMPLETE**: decomp (provenance) + regroup (retire parallel store) → the delivered
  DB-backed reuse apparatus.
- **Standing line** (do NOT force): the pyrig mission is a goal↔shadows line with no artefact populated
  THIS session. Left standing — it is the next arc's start, not a gap to close now.

### Labeled next steps (⟡) — unambiguous symbols

DO-NOW / mechanical:
- **⟡push** — 2 unpushed commits (95f7596 verdict-sort, 8e803cf ref-axis+slider) → origin/main.

TOOLING — the S₄-adapted tunable system (verify → loosen → build), one arc:
- **⟡verify-s4-basis** — construct the standard-rep basis for (κ,φ,σ); SHOW ∇N collapses to the trivial
  (1,1,1) direction and the pinned-frontier is the standard 2-d irrep. Probe-before-build. [RUN first]
- **⟡loose-cache** — rebuild the TUI cache at min_size=2/min_fanin=2/cap=None so min_size & min_fanin
  become LIVE filters (not baked-in exclusions).
- **⟡truncation-notices** — "showing N of M" for cap/1500/--top/[:40]; the no-silent-caps fix.
- **⟡size-per-instance** — S₄-predicted: min_size cuts s/n (size per instance), not raw s, to close the
  third pair-partition {n,s}|{m,c}. Falsifiable consequence of the symmetry.
- **⟡s4-sliders** — the normalized slider system in the S₄-adapted basis: trivial-rep "strictness" master
  (pin axis) + standard-rep 2-DOF steering (sum-fixed barycentric) + pin-N compensation + V₄ Chirality
  cut-orientation. INSTANTIATE Substrate.Groups.V4-Coxeter / S4-Composed — do not rebuild.

TOOLING — discharge the point of the tool:
- **⟡consolidate-coxeter** — take the concrete ◆tgt (the anonymous `Algebra.Polynomial.Graded.Over` shape,
  ×98 across 5 modules) and ACTUALLY parameterize it: extract+name one abstraction, instantiate each. The
  tool's whole purpose, still undischarged.

REUSE-DISCIPLINE escalation:
- **⟡reuse-search-data-homes** — propose the CLAUDE.md line: the reuse-search trigger fires on DATA HOMES
  too — before a new cache/derivation/store, name the projection/DB it duplicates. (G9 coverability.)

UNCOMMITTED artefact to reconcile:
- **⟡rigcat-reconcile** — jea/metalanguage/jea_rigcat.py (plan radiant-weaving-dawn Phase 1, DONE but
  uncommitted) + the sppf_db orbit projection: commit, or fold into the SPPF-substrate reading? Decide.

DEFERRED MISSION (the standing center — the rig-cat proper):
- **⟡pyrig-object-carrier** — the OPEN frontier: what IS the pyast rig-category's object carrier
  (meaningful-in-python object). The mission's live edge.
- **⟡nat-enum-prove** — mechanically discharge the enumerated naturality facts (nat_enum → Agda).
- **⟡core-extrude** — (carried from prior regroundings).

---

## ⟡verify-s4-basis — DONE (verified, with an honest correction)

**Instrument run** (scripts inline; over the 1993 non-ref orbits). Verdict in three parts:

1. **Group + rep structure: EXACT (definitional).** {n,m,c,s} are the 4 S₄-objects; the 3 knobs are the 3
   pair-partitions = V₄∖{e}; S₃=S₄/V₄ permutes them. The perm rep = **trivial ⊕ standard**, explicit basis
   triv=(1,1,1)/√3, std=⟨(1,−1,0)/√2,(1,1,−2)/√6⟩. This part needs no data — it holds by construction.

2. **∇N ∥ trivial: APPROXIMATE, ~0.80–0.99, and the residual is DIAGNOSTIC.** Raw knob units are 40:1
   anisotropic (incommensurable). Percentile-normalized: cos(∇N,(1,1,1)) = **0.99 on the clean 2-axis
   (κ, originality)**, **0.80 on 3 axes**. Dominantly trivial → the pin/steer construction is WELL-POSED.
   But NOT exact (1,1,1).

3. **The obstruction (measured): POINT MASSES break exchangeability.** φ=c/n has a **73% pile at 0** (pure
   originals), size has a **38% pile at SIZE_CAP**. Percentile-rank can't smooth ties → the count-gradient
   spikes at the mass → a standard-rep residual. κ=n/m is continuous (no mass) → its pairs are the
   exchangeable ones (2-axis 98%). The symmetry-breaking pattern FINGERPRINTS exactly the defective
   coordinates — residue-as-signal.

**CORRECTION (anti-affect, honest reporting).** My earlier claim "∇N is forced by representation theory to
collapse to (1,1,1)" was TOO STRONG. Rep theory forces the DECOMPOSITION (triv⊕std always exists); it does
NOT force ∇N into the trivial part — that requires the DATA to be S₃-exchangeable, which it is only
approximately (point masses break it). Correct statement: the pin/steer DECOMPOSITION is exact and free;
the ALIGNMENT of ∇N with the pin is empirical (~0.8–0.99) and its residual is a diagnostic, not noise.

**Consequences (updated ⟡):**
- ⟡s4-sliders — still VALID (pin trivial / steer standard is well-posed at cos ≥ 0.8). Proceed.
- ⟡size-per-instance — STRENGTHENED: not just "closes the partition" but "de-saturate the size coord"
  (38% pile at the cap makes s a broken coordinate).
- ⟡tie-aware-normalize (NEW) — the point masses (φ 73%, size 38%) need tie-aware normalization (mid-rank /
  copula / smoothed CDF) for the pin to be clean; else part of the standard residual is a ranking artifact.
- The standard residual is genuinely informative: **originality (copy-fraction) dominates ∇N** — the data
  says the consolidated-vs-not axis carries the most count-sensitivity (expected: it's the ✗/✓ axis).

## ⟡s4-sliders — DONE (committed)

The S₄-adapted control surface in reuse_tui, built to the tie-aware verdict (the elaborate steering
collapsed): 2 isotropic percentile sliders (κ concentration, σ size/instance; [k] pick, [ ] adjust) + 2 V₂
toggles ([c] copy-family = the ✗/✓ verdict, [z] saturated = the SIZE_CAP artifact) + [r] ref + [d] target
preset. Retired the monolithic scatter slider + tgt-only. Headless-verified isotropy: a κ-step removed 22,
a σ-step removed 46 (~2:1, same order) vs the raw 40:1 — equal steps trade equal counts, so no pin/steer
basis is needed. SIZE_CAP promoted to module scope.

Open follow-ons: ⟡size-per-instance (dissolve the sat V₂ artifact → finer σ); ⟡pin-drag-integrable (d²N=0
→ drag one slider, others hold N); ⟡dual-knob-triple (the Λ₋ within-pair coords); ⟡clean-knob-plucker.
Still-standing center: ⟡consolidate-coxeter (cash a concrete ◆target), and the pyrig mission.

## ⟡size-per-instance — DONE (committed)

Dissolved the σ saturation V₂ atom: replaced capped-unfolded size with LOG-unfolded (log-sum-exp DP,
lsize = log(1+Σ exp(lsize(child))), O(V+E), never saturates). σ = lsize − log n (the {n,s} log-contrast).
σ's dominant atom 38%→1%; 3-axis cos(∇N,pin) 0.80→0.869; sliders still trade comparably. The sat V₂ toggle
is now purely diagnostic. lsize cached in rows.

NORTH STAR (user): once the knobs are clean, AUTOCORRELATION over the frame should let us MECHANICALLY /
AUTOMATICALLY synthesize the consolidation (not hand-do ⟡consolidate-coxeter). ⟡size-per-instance was a
prerequisite — a 38%-atom axis would poison the autocorrelation. Next knob-cleanup / then the autocorr synth.

Open ⟡: ⟡autocorr-synth (NEW, the north star — mechanical consolidation via autocorrelation over the clean
κ/σ/V₄ frame); ⟡pin-drag-integrable; ⟡dual-knob-triple; ⟡clean-knob-plucker; ⟡consolidate-coxeter (now
possibly subsumed by ⟡autocorr-synth); the pyrig mission.

## ⟡autocorr-synth — DONE (committed) — the north star, first rung

Mechanical consolidation synthesis, NO LLM: reused jea_extrude_ir.templatize (the existing anti-unifier —
reuse-search found it before any rebuild). same-skeleton cluster = template; varying residue = holes;
fillings = substitutions (Free⊣Forgetful residue). autocorrelation score = instances×(1−hole_density) →
many-copies/few-holes lead. NEW jea/metalanguage/autocorr_synth.py.

Grounded on the substrate's own .py tooling: 533 units → 13 consolidatable clusters. `strip(s)` copied 15×
(1 hole = replacement string); exact triplicates reach/rank/refs (0 holes = CSE). `--emit <#>` prints
template + all substitutions = the consolidation, derived not guessed.

Honest scope: Python closes fully (templatize is ast-based). AGDA path = same algorithm over the SPPF
(skeleton + ordered lit/op residue per unit from catalog.db); residue-alignment over the shared DAG is the
next rung = ⟡autocorr-synth-agda (design in the header).

Open ⟡: ⟡autocorr-synth-agda (extend to the Agda targets — the ◆tgt orbits); ⟡consolidate-strip (cash the
15× strip dedup the tool found); ⟡pin-drag-integrable; ⟡dual-knob-triple; pyrig mission.

## ⟡autocorr-synth-agda — DONE (committed) — but the real lesson was SQL-native/declarative

First cut walked the SPPF in Python (skeleton-hash + N-tuple co-traversal) → TIMED OUT (2m42s). User forced
the honest path: PROFILE (load=2.7s → SQLite is NOT the bottleneck; the pickle-cache-on-mtime I reached for
was the wrong-fix TELL), then "think like JOIN queries + declarative constraints over the materialized
enumeration, not recursive-imperative behaviors." Rewrote via SQLAlchemy Core:
- body size = GROUP BY unit_node (count the DONE enumeration, don't re-walk).
- exact body = GROUP BY the unit_node SET-signature (group_concat) — root_id is a depth-1 packing that
  FALSE-clusters (verified +-assoc vs Z30-multiplicities: 20 vs 48 nodes, ∩5).
- copy=0 keeps independent units. → 2m42s → 4s, correct: 190 clusters, top = 20 sporadic-group
  ConjugationCoalgebra bodies (extract one, ref 19).
Memory saved: [[feedback_sql_declarative_over_materialized_enumeration]]. Shifted the DB access layer to
SQLAlchemy Core (added to requirements).

Open ⟡: ⟡autocorr-synth-agda-holes (near-dups = unit_node self-join + set-difference — the WITH-holes
targets, the richer synthesis); ⟡consolidate-conjugation-coalgebra (cash the ×20 CSE the tool found);
⟡node-view-kindid already fixed; pyrig mission still the standing center.

## ⟡autocorr-synth-agda-holes — DONE (committed) — the arc closes

The WITH-holes synthesis, declaratively (unit_node self-join + set-difference, no walk):
- candidates bounded to same (root_id,size) buckets; giant buckets SKIPPED LOUD (42/7786 units to stderr).
- within-bucket self-join → pairwise overlap ≥ sim·size → connected components = near-dup families.
- holes = set-difference: shared CORE (nodes in ALL units) = the abstraction; per-unit complement + heads
  = the substitution. Fast (7.7s).
CONVERGENCE: independently surfaced the Algebra.Polynomial.Graded.Over family the κ/σ/V₄ frame flagged.
Emit: *P-distribʳ/ˡ/mono-assoc → 76-node shared abstraction + 37 hole-nodes each (distribʳ vs ˡ differ in
_*P_/_+P_/convCoeff/nth-*P/trans = the distributivity direction). `--agda --holes [--emit #]`.

The whole autocorr arc: the knobs (κ/σ/V₄, S₄-adapted) RANKED targets → the anti-unification SYNTHESIZED
them mechanically (exact CSE via set-signature; near-dups+holes via self-join+set-difference). No LLM.

Open ⟡: ⟡holes-render-agda (render the shared core as compiling Agda + the fillings — the last mile, like
typeholer's honest boundary); ⟡consolidate-graded-over (cash the distribʳ/ˡ parameterization); ⟡push
(many unpushed); pyrig mission still the standing center.

## ⟡holes-render-agda — REFRAMED by the user (permutation-over-canonical = the wedge residue)

First cut anti-unified the SOURCE TEXT (templatize idea for Agda). It rendered CLEANLY for
substitution-variation (freeFunctorₚ/ₛᵧ, 5% holes) but FRAGMENTED on distribʳ/distribˡ (31 text-holes) —
because they differ by ARGUMENT-ORDER PERMUTATION (p,q,r ↔ r,p,q), not leaf-substitution. I called that a
"boundary." Two user corrections:

1. "We have an entire system designed around identifying THAT as an orbit." — permutation-variation isn't
   a text boundary; it's an ORBIT. The rig-cat coherence-iso quotient (orbit_node, plan
   radiant-weaving-dawn; RIG_OPS = the proven ⊕/⊗ set) exists to collapse exactly the braiding/reassoc.
   So the anti-unification must run over the ORBIT quotient (unit ⋈ orbit_member), where the permutation
   is already collapsed and only the GENUINE holes remain.
2. "Where we find permutation-only distinctions, the dedupe resolves to permutation-over-CANONICAL." —
   the deeper point: dedup doesn't DROP the permutation-distinction, it FACTORS it losslessly as
   (canonical orbit-representative) + (the permutation residue). This IS the wedge: a = recon q b r, with
   r = the permutation = orientation = Lehmer digit ([[adjunction-is-the-wedge-residue-counit]]). So
   distribʳ/distribˡ consolidate to ONE canonical distributivity proof + each instance = canonical ∘ its
   ⊗-braiding. The "hole" is not an opaque token — it's a PERMUTATION (an Sₙ element / Coxeter word,
   [[coxeter-word-is-combine-generators]]), and canonical+permutation is the FULL mechanical consolidation,
   renderable as `canonical ∘ braiding`.

ARCHITECTURE this implies for the render: near-dup over orbit-membership → a hole is either a genuine
substitution (render as a parameter) OR a permutation residue (render as canonical ∘ braiding, the wedge
form) — LehmerPath/decode gives the canonical factoradic; the residue is the coherence iso.

HONEST STATUS: the orbit projection (RIG_OPS ⊕/⊗, jea_rigcat) is the right machinery and COVERS ⊗-braiding
(distribʳ/ˡ = right/left ⊗-distributivity → in scope), but (a) it is NOT materialized in the current
catalog.db (built via `sppf_db --orbit`; and unit→orbit membership isn't a table yet — derive via
unit_node ⋈ orbit_member) and (b) extracting the residue permutation + rendering canonical∘braiding is
unbuilt. The text-anti-unification render was DISCARDED (restored to committed 71688c3).

Labeled ⟡:
- ⟡holes-over-orbit — build/materialize the orbit projection (sppf_db --orbit) + unit→orbit membership;
  re-key the near-dup/holes over orbit-sets so permutation-only distinctions collapse.
- ⟡holes-permutation-over-canonical — for a permutation-only hole, extract the RESIDUE permutation (the
  wedge r) via the orbit representative + LehmerPath, render each instance as canonical ∘ braiding.
- ⟡holes-render-substitution — the clean substitution-variation render (freeFunctorₚ/ₛᵧ) DOES work at the
  text level (5% holes); ship that path for the genuine-substitution clusters.

## REFINEMENT (user): permutation-over-STAB, not over-canonical — the orbit-stabilizer coset G/Stab

Correcting my "permutation-over-canonical": a permutation-only distinction factors as an element of the
COSET SPACE **G/Stab**, NOT a raw permutation over a canonical. Permutations in Stab(x) (the term's own
argument-symmetries) don't yield a distinct instance, so the residue is only defined modulo Stab —
orbit-stabilizer: |orbit| = |G|/|Stab|, each instance ↔ a coset gStab.

The substrate PROVES exactly this (reuse targets, don't rebuild):
- Substrate.Groups.V4-Cosets — `S₄/V₄ ↔ Stab` (the coset space).
- Substrate.Cocycles.V4Signature.S4Iso — `TotalSpace ≃ S₄`, TotalSpace = Σ OrbitKey (λ _ → V₄) =
  (orbit-key, fiber-position) = the orbit-stabilizer product. Each instance = (orbit-key, coset).
- Substrate.Groups.Stab-S3-Iso — `Stab ≃ S₃`. Substrate.Category.GTorsor — coset-space data.
- LehmerPath.encode = the canonical coset representative (factoradic).

So the consolidation of a permutation-only cluster = ONE orbit-representative term + each instance tagged
by its **G/Stab coset** (a permutation MODULO the term's symmetry group), rendered as the (orbit-key,
coset) pair — the S4Iso TotalSpace shape, GTorsor data. The wedge residue r IS the coset.

CONFIRMED scope: project_orbit_sppf's canon_syms sorts children ONLY for RIG_OPS (⊕/⊗) nodes; all else is
positional → lemma-argument permutation is NOT covered. User: "it should." The extension:
- ⟡orbit-arg-permutation — extend the orbit quotient to the Sₙ action on a Defn's argument telescope,
  canonical via LehmerPath, residue = the G/Stab coset (instantiate V4-Cosets / S4Iso / Stab-S3, don't
  rebuild). This subsumes ⟡holes-over-orbit + ⟡holes-permutation-over-canonical (now over-Stab).
- ⟡holes-render-substitution — the clean text-level render (freeFunctorₚ/ₛᵧ, 5% holes) still ships for
  genuine-substitution clusters; permutation clusters route to the G/Stab factoring above.

## ⟡orbit-arg-permutation — GROUNDED + prototyped, but hit an honest WALL (not done)

VERIFIED enabler: variables are de Bruijn indices carried as node ROLE `dbN` (db0..db25+; 803 db0-nodes,
etc.). So an argument-permutation IS a permutation of the dbN labels, and the orbit key is the body with
dbN canonically relabeled (first-occurrence), residue = that perm mod Stab (the G/Stab coset; reuse
V4-Cosets/S4Iso/LehmerPath).

BUILT a prototype canonicalizer (unfold body pre-order, relabel dbN by first occurrence). EMPIRICAL RESULT
over 46 polynomial ring-law lemmas: **0 orbits merged distinct exact-bodies** — pure arg-permutation pairs
are ~absent. Investigated distribʳ/distribˡ directly: a naive "1.00 canon overlap" was a TRUNCATION
ARTIFACT — both bodies hit the 3000-node cap still inside the giant recursive Polynomial TYPE; the
discriminating PROOF term is a small tail beyond the cap. distribʳ/ˡ are NOT pure arg-permutation — they
compose arg-perm with *P-commutativity (a non-RIG_OP ⊗) AND companion-lemma swap (convCoeff-distrib ↔
convCoeff-distribˡ). db-relabeling alone doesn't merge them.

HONEST WALL (wall-before-declaring): the naive unfold-canonical is CONFOUNDED — def bodies here are
TYPE-DOMINATED (the polynomial type unfolds to 1000s of nodes), swamping the discriminating proof term; and
dbN is depth-relative (shifts under inner binders), so a flat first-occurrence relabel is wrong in general.
A correct arg-perm orbit must (a) act on the SMALL top-level telescope only (S₂/S₃/S₄ — enumerable), (b)
work over the DISTINCT-node structure / the proof term (not the type-swamped unfold), (c) be depth-aware.
That is the real remaining build — now precisely scoped, not yet done.

Labeled ⟡:
- ⟡orbit-arg-permutation (REOPENED, scoped): telescope-only Sₙ (n≤~4, enumerate perms), over the proof
  term (strip the type prefix), depth-aware dbN; residue = G/Stab coset (V4-Cosets/S4Iso).
- ⟡combined-orbit: the REAL targets (distribʳ/ˡ) need arg-perm ∘ operator-commutativity ∘ companion-lemma
  quotient TOGETHER — a combined orbit, not arg-perm alone. This is why the rig-⊕/⊗ orbit + arg-perm must
  compose (and *P etc. would need adding to RIG_OPS, or a general commutativity-discovery).

## CORRECTION of posture + the real structure: orbits are points in larger orbits (a GRADED tower)

(Retract the "honest wall / 0-merges is the truthful signal" framing above — that was self-defeating. The
0-merges was a broken measurement, not a finding. Reframed:)

The user's probes cut through: (1) the unbounded prefix probe showed the def UNFOLD is DEGENERATE — the
recursive polynomial type re-expands under DFS, 200000 identical tokens capped, so unfold-comparison is the
wrong object; the DISTINCT-node DAG (113 nodes) is. (2) The DAG set-difference is precise and beautiful:

  distribʳ-only = convCoeff-distrib  + {4×_*P_, 2×convCoeff, 2×nth-*P, _+ⱽ, trans}
  distribˡ-only = convCoeff-distribˡ + {4×_*P_, 2×convCoeff, 2×nth-*P, _+ⱽ, trans}

SAME operator multiset (differ only in db-arguments = the permutation) PLUS one substitution
convCoeff-distrib → convCoeff-distribˡ. And that companion is a point in ITS OWN arg-swap orbit. So:

**Orbits are themselves points in larger orbits — a GRADED TOWER.** distribʳ/ˡ sit in a level-k orbit whose
points reference level-(k-1) orbit-points (convCoeff-distrib/ˡ). The consolidation isn't a single Sₙ
quotient; it's the ITERATED/graded quotient — quotient the permutation at each level, the residue at level
k is a G_k/Stab_k coset AND a choice of lower-orbit-point. This IS the witness tower / LehmerPath (the
factoradic: each digit = a level's residue) / the graded wedge — the substrate's core architecture.

CONSTRUCTIVE PATH (not a wall — a build):
- ⟡graded-orbit-interner: a FIXPOINT orbit-quotient over the SPPF DAG (not the unfold): bottom-up, identify
  level-0 orbits (companions like {convCoeff-distrib, convCoeff-distribˡ} — same-shape-up-to-db-perm), then
  level-1 orbits over those, to fixpoint. The interner hash-conses positional structure; this quotients the
  permutation group graded. Reuse LehmerPath (the graded canonical), V4-Cosets/S4Iso (the G/Stab coset per
  level), the witness-tower machinery.
- Work over DISTINCT nodes (the DAG), never the unfold (degenerate).
- distribʳ/ˡ then collapse: level-0 merges the convCoeff companions, level-1 merges distribʳ/ˡ over db-perm.

---

## REGROUNDING #9 (2026-07-13) — retrospective-ritual + shadow-engineer at the session boundary

### Retrospective (gates that constrained)

- **G0 precommit.** Session opened on ⟡autocorr-synth-agda ("tackle it"). Standing mission: a rig cat over
  pyast, grounded in the witness tower, maximal reuse.
- **G2 delta.** Expected: build the Agda anti-unifier. ACTUAL, two big deltas: (a) my Python graph-walk
  REINVENTED A QUERY ENGINE (timed out) → rewrote SQL-native/declarative over the materialized enumeration
  (SQLAlchemy Core); (b) the permutation-variation I called a "render boundary" turned out to be the GRADED
  ORBIT TOWER = the rig-cat self-collapse = the mission's own spine. The detour WAS the destination.
- **G3 cause.** trigger = graph walk timed out. ROOT = reached for a bespoke Python algorithm + a
  pickle-cache-on-mtime instead of PROFILING (load was 2.7s) + querying declaratively — same root as the
  earlier ⟡reuse-query-db lesson ("reads raw, not the projection"); the declarative discipline wasn't the
  default. Contributing = POSTURE: I dressed broken/preliminary measurements ("0 merges", the truncated
  "1.00") as "honest walls / truthful signals" — self-defeating; the user corrected it twice.
- **G6 sustain (protect).** Reuse-search-before-building paid off HUGELY: templatize found before
  rebuilding the anti-unifier; V4-Cosets/S4Iso/LehmerPath for the coset; the OrientationRigCatPerm*
  machinery grounded the self-collapse. Grounding claims in the actual DB/machinery, not asserting. The
  recursive common-structure lens: consolidation→orbit→tower→rig-cat; DAG-vs-unfold→self-collapse.
- **G8 handoff.** ⟡graded-orbit-interner is designed, unbuilt; the "does the prime-generated fixpoint
  collapse distribʳ/ˡ" test is SELF-runnable → a RUN, not a handoff. operator=other residue: whether my
  reading of the grade-3-trivial-braiding self-collapse maps to arg-permutation of ARBITRARY lemmas (not
  just rig ⊕/⊗) — that mapping is the part I can't self-verify.
- **G9 escalate (recurring classes → coverability).** (1) "bespoke/pickle instead of profile+declarative
  query" → memory feedback_sql_declarative_over_materialized_enumeration (saved) + ⟡reuse-search-data-homes
  (extend CLAUDE.md). (2) "framed a broken measurement as a verdict / self-defeating posture" → NEW memory
  ⟡posture-surprises-are-questions.

### The recursive either/or collapse (this session's invariant)

Every open thread is one object: **consolidation = orbit-decomposition in the rig-cat witness tower, and it
is FINITE because the tower self-collapses at the primes (PrimeFactoredGauge — prime grades have no
⊗-factorization ⇒ trivial braiding ⇒ the grading is finitely generated by grades 2,3).** REGROUNDING #8's
"tooling vs mission dissolves" is now IDENTIFIED, not just dissolved: the consolidation tooling IS the
witness-tower orbit-decomposition; the pyrig mission IS instantiating it over pyast. The DAG (finite) is the
self-collapsed form; the unfold (200k tokens) is its infinite re-expansion.

### Shadow-engineer (Fano)

- The user's chain — "it's an orbit" → "permutation-over-Stab (G/Stab coset)" → "orbits are points in
  larger orbits" → "rig cat self-collapses at depth 3" — is a run of GUARD events (001→redirect): each
  rejected my direct move (text-render; wall-declaration) and routed through the shadow structure. **L₆
  guard-reconstitution fired repeatedly** — the redirect produced the mediated composite (the graded-orbit
  understanding) the direct move would have botched.
- **L₁ positive-closure COMPLETE**: the DB-native reuse + autocorr-synth apparatus, delivered + committed.
- **Standing line (do NOT force)**: ⟡graded-orbit-interner + the pyrig mission — goal↔shadows lines with no
  artefact at session end. The next arc's start, not a gap.

### Labeled next steps (⟡) — unambiguous symbols

DO-NOW / mechanical:
- **⟡push** — the unpushed commit stack (autocorr-synth ×3 + s4/size + …) → origin/main.
- **⟡rigcat-reconcile** — commit jea/metalanguage/jea_rigcat.py (uncommitted; now clearly load-bearing —
  it IS the self-collapse machinery, RIG_OPS + canonical).

THE GRADED-ORBIT TOWER (this session's frontier = the convergence with the mission):
- **⟡graded-orbit-plan** — write the plan FIRST (real depth): each grade's canonical grounded in
  LehmerPath, each residue in the V4-Cosets/S4Iso G/Stab coset, termination in the prime-factored
  self-collapse (grade-3 trivial braiding).
- **⟡graded-orbit-interner** — the TERMINATING fixpoint orbit-quotient over the DAG (never the unfold):
  quotient at prime grades (2,3), composites fall out by ⊗/⊕; residue = G/Stab coset per grade. Reuse
  PrimeFactoredGauge / OrientationRigCatPerm* / LehmerPath. Bounded by the self-collapse.
- **⟡combined-orbit** — the real targets (distribʳ/ˡ) need arg-perm ∘ operator-commutativity ∘
  companion-orbit-swap TOGETHER = the graded tower (subsumed by ⟡graded-orbit-interner; note *P etc. need
  adding to the op-set or a general commutativity-discovery).

TOOLING POLISH (deferred, low-risk):
- **⟡holes-render-substitution** — the clean text-render for genuine-SUBSTITUTION clusters (freeFunctorₚ/ₛᵧ,
  5% holes) ships now; permutation clusters route to the orbit tower.
- **⟡truncation-notices** — "showing N of M" no-silent-caps fix (reuse_tui cap/1500/--top).
- **⟡consolidate-conjugation-coalgebra** / **⟡consolidate-graded-over** — cash a concrete CSE / near-dup
  the tool already found.

DISCIPLINE (G9 escalations):
- **⟡reuse-search-data-homes** — extend the CLAUDE.md reuse trigger to DATA HOMES (before a new
  cache/derivation, name the projection it duplicates). [carried from REGROUNDING #8]
- **⟡posture-surprises-are-questions** — memory: a broken/preliminary measurement is a CURIOUS QUESTION to
  pursue, not an "honest wall / truthful signal" verdict. (This session's ×2 correction.)

THE STANDING CENTER (the mission — dormant but now IDENTIFIED with the tooling):
- **⟡pyrig-object-carrier** — the pyast rig-cat's object carrier (the live edge).
- **⟡nat-enum-prove**, **⟡core-extrude** — carried; the pyrig-* cluster is the original mission.

---

## REGROUNDING #10 (2026-07-13) — graded-orbit A–D COMPLETE (full detail in plan radiant-weaving-dawn.md)

⟡graded-orbit-interner A–D committed (60e938f A, 20dc4d0 B, c161af7/80d6810 C, 7b01af2 D; 4c3731c
rigcat-reconcile). The whole session's invariant is now BUILT not just seen: consolidation =
orbit-decomposition = the WEDGE (instance = orbit-rep ∘ residue r) = the LehmerPath tower (each factoradic
digit = one grade's coset) = the rig SELF-COLLAPSE at the primes (PrimeFactoredGauge) = the witness tower.
graded_orbit.py + _orbit_def ARE the mission's orbit-interning apparatus; ⟡pyrig-object-carrier is the live edge.

KEY delta (positive): distribʳ/ˡ merge at the TYPE orbit, SPLIT at the GRADED (proof) orbit — the split
localizes to the δ-distributor DIAGONALIZATION (a single companion ref). "type-twin, proof-distinct" is
CORRECT, not a defect. Perf class recurred (deep per-qname recursion → timeout); fixed by the user's
DEPTH-3 = rig-precomputed-coherence self-collapse insight (beyond it → collapse back into the SPPF).

Open ⟡ (full menu in the plan): DO-NOW ⟡push, ⟡argperm-full-corpus (only 6 Distrib rows in _orbit_def now).
Payoff: ⟡cosets-into-autocorr, ⟡combined-orbit (*P into the op-set), ⟡argperm-canonical-proof,
⟡coxeter-completeness. Center: ⟡pyrig-object-carrier. Discipline: ⟡reuse-search-data-homes,
⟡memory-depth3-selfcollapse (done below).
