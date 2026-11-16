# ⟡UPDATE (2026-07-23c) — f₁ ARC COMPLETE (identify₁ proven, 128 MB); committing; NEW arc = ⟡heavy-decompose. COMPACTION-SAFE. Read THIS first.

## STATE (one line, current)
**identify₁ DONE + PROVEN.** `Substrate/Algebra/Q/JacCubeNorm.agda`: `identify₁ : evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z`,
GENERAL in (x y z), typechecks at **128 MB** (was 781 MB monolithic). Full cube arc done: `cube : sumNum Cᶠ ≡ N_C`
(125 MB) via `same : norm e-N ≡ norm e-R = refl` (95 MB, the Ux³ binomial by the reflective normalizer) + the two
FAITHFUL reflection bridges (`bridgeN`/`bridgeR`). **⟡cube-commit IN FLIGHT** — background commit `bqfwh4oip` running
the pre-commit full-build gate; HEAD still `3c9343b` until it lands (wait for the `post-commit advisory (auto-captured)`
amend marker; then USER pushes). Staged EXACTLY: ZRingNorm.agda, ZRingNorm/{Sound.agda,Makefile}, JacCube.agda,
JacCubeNorm.agda, Q/Makefile, Z/Makefile (nothing from scratch/). Probes retired (RingTraceProbe, ZRNDemo, ⟡ring-trace-probe-retire done). Name checks passed (ZE/Mon fresh; no .Properties import from the def module).

## ⚑ CYCLE7 FINDING — ALREADY DECOMPOSED (do NOT re-do it)
`Substrate/Algebra/F2/Linear/FromImages/Permutation/Cyclic.agda` ALREADY carries the FreeUP β-interface route-around:
an `opaque` block sealing the dense `cyclic-Linear`/`cyclic-HasOrder` (typechecked ONCE at abstract n — "this module is
light", :50-70) + the exposed `cyclic-Linear-basis : apply (cyclic-Linear {n})(basis k) ≡ basis (cyclic-suc k)`
(the "hand consumers the LEMMA, not the unfolded construction" pattern). The old `Cycle{2,3,4,5,7}.agda` were
"dissolved into the Sylow registry". No current consumer instantiates `{6}` densely (GaugeGenerators uses `{2}`,
SpectralCycle the generic `{n}`). So Cycle7's OOM is already fixed — the user's mental note was stale.

## THE NEW ARC — ⟡heavy-decompose (user, 2026-07-23c): "find the current single-heaviest-RAM module and decompose it"
NOT the reflective normalizer by default. The route DEPENDS ON THE KIND of heaviness (CLAUDE.md's opacity/OOM +
decomposition guidance): (a) DENSE OPERATOR/MATRIX materialization → the FreeUP β-interface (opaque seal +
basis-action lemma + prove-on-generators-then-lift; the Cycle7 pattern) · (b) STUCK ℤ/ring polynomial identity →
the reflective ℤ-ring normalizer JUST BUILT (ZRingNorm + norm-sound; reflect → refl-match canonical → sandwich) ·
(c) exhaustive KAT / S-box / 256-byte reflection → membudget decomposition (lemma-per-file, +RTS heap cap) ·
(d) monolithic `refl` → def/proof split + lemma extraction. The FIRST STEP is to MEASURE (buildtime.py --mem) which
module is heaviest + WHY, then pick the matching route. Two read-only agents dispatched (2026-07-23c) — MIRROR each
result here when it lands; if a compaction hits first, RE-DISPATCH from §PROMPTS below (they are self-contained;
do NOT read the agent .output files raw — full JSONL, overflow).

### ⟡heavy-decompose PROMPTS (self-contained; re-dispatch after a compaction)
Standing discipline: report PRESENCE with file:line witnesses; RUN the instrument, do not predict it; an empty/absent
ledger entry is a fact about the METHOD (buildtime only records SUCCESSFUL shim-routed compiles; an OOM-killed or
pre-commit-only module may be ABSENT), stated as such.
- **AGENT A → §MEM-CENSUS.** From the repo root `/home/mikemol/github/substrate`, RUN `python3 scripts/buildtime.py
  --mem` and `python3 scripts/buildtime.py --top 15`. Report the top ~10 modules by peak_mb (maxRSS) and by median
  time, file:line for each. For the top 5 by RAM, OPEN the module and characterize the KIND of heaviness by EVIDENCE:
  dense F₂/matrix/linear materialization (Vector/Linear/linear-from-images, a matrix power in normal form) · a stuck
  ℤ/ℚ/ring polynomial identity (a big `refl`/normalize over `_*ℤ_`/`_+ℤ_`/mkℚ) · exhaustive KAT/S-box/256-byte
  reflection (AES/round/exhaustive tables) · a monolithic categorical/Set₁ construction. Flag which are ALREADY
  decomposed (an `opaque` seal / a basis-action lemma / a lemma-per-file split / a membudget note) vs GENUINELY
  un-decomposed. CROSS-CHECK: the pre-commit `full_build_check.py` caps each module at `+RTS -M1024m` (1 GB heap) —
  anything whose maxRSS is near 1 GB is the real culprit; also note any module KNOWN to OOM from comments
  (grep `OOM|heaviest|dense|blowup|super-exponential`). Deliverable: the ranked heavy list + per-module (peak_mb,
  time, KIND, decomposed?), the single heaviest UN-decomposed module NAMED with its file:line why-heavy.
- **AGENT B → §DECOMP-PLAYBOOK.** Ground the repo's EXISTING heavy-module decompositions as a decision tree (route by
  KIND). READ + quote file:line: (1) the FreeUP β-interface / opaque route-around — `Algebra/F2/Linear/FromImages/
  Permutation/Cyclic.agda` (the `opaque` block + `cyclic-Linear-basis`), `Algebra/F2/Linear/FromImages.agda:145-150`
  (why linear-from-images OOMs), and the CLAUDE.md "Opacity / OOM → the FreeUP β-interface" paragraph +
  `extend-on-basis`/`HasOrder-from-perm`/`extend-unique`/`package-comm`. (2) the reflective ℤ-ring normalizer JUST
  COMMITTED — `Algebra/Z/ZRingNorm.agda` + `ZRingNorm/Sound.agda` (`norm`/`norm-sound`) + `Algebra/Q/JacCubeNorm.agda`
  (reflect → `refl`-match → norm-sound sandwich); when it applies (a stuck ℤ ring identity, NOT a dense operator, NOT
  a point-eval KAT). (3) the membudget/lemma-per-file decomposition — the AES KAT modules + `scripts/membudget`
  (heap-cap + lease) + the "lemma-per-file, AES-Full pattern" (grep `AES-Full pattern|lemma-per-file|membudget`). (4)
  the def/proof split + Set₁ paydown. Deliverable: a DECISION TREE {heavy-module-kind → route → the exact in-repo
  template to copy + its file:line}, so whatever Agent A names, the matching route + template is turn-key. Name the
  ONE route that does NOT fit each kind (e.g. reflective normalizer does NOT help a dense operator; the β-interface
  does NOT help a point-eval KAT — reflection + membudget do).

### ⟡cap-384 — USER DIRECTIVE (2026-07-23c): "set the global memory cap to 384MiB; we can decompose further."
THE FORCING FUNCTION lowered to 384 MiB → whatever exceeds it must decompose. THE TWO KNOBS:
- **membudget per-module ceiling** `AGDA_MB_MAX` (default 1536, `scripts/membudget:159` `cap="${AGDA_MB_MAX:-1536}"`;
  retry ladder `192→384→768→1536`). Set `AGDA_MB_MAX=384` → each shim/make lease caps at 384; a >384 MB module
  OOM-kills (137) at the cap and can't self-heal → forced to decompose. Global budget stays 8192 (concurrency fine).
- **pre-commit heap cap** `MEM = "1024m"` (`scripts/full_build_check.py:24`, used at `:47` `+RTS -M{MEM}`). Set
  `MEM = "384m"` → the COMMITTED build gate enforces 384. ⚑ NOTE heap≠maxRSS: `-M384m` heap ≈ ~484 MB maxRSS
  (CLAUDE.md: heap+~0.1 GB RTS). For a strict 384 maxRSS use `-M256m`-ish. Pick the interpretation with the user.
- (the global budget `membudget init 384` throttles CONCURRENCY to 384 total — NOT what forces a single module; use
  the per-module knobs above.)
⚑⚑ CRITICAL SEQUENCING — lowering the cap BREAKS THE PRE-COMMIT GATE until the >384 modules decompose. So this is an
ARC, not a config flip: (1) lower the cap locally; (2) build the >384 modules → confirm they 137; (3) DECOMPOSE them
under 384; (4) commit the cap change + the decompositions TOGETHER (gate green). Do NOT commit a cap that reds the gate.
⚑ WHAT EXCEEDS 384 (from the census): ONLY 3 — `Q/JacobianEncodingLiteral.agda` (857), `Q/JacobianCounterexample.agda`
(821), `Permutation/Cyclic.agda` (546). Everything else ≤256 (pow2 of ≤153) already fits. ⚑ BUT all 3 are "already
decomposed" — their PEAK is IMPORT-CLOSURE DESERIALIZATION (loading the .agdai dependency graph of JacobianCollision +
JacobianEncodingLiteral), NOT elaboration. So getting them under 384 is a DIFFERENT problem than the cube: minimal-import
pruning / splitting the aggregator / breaking the import closure — there may be a deserialization floor. Harder, not
guaranteed. FIRST STEP after the commit lands: `AGDA_MB=384 agda …` (or lower) on each of the 3, read the actual peak
+ whether it's deserialize-bound; then decide split-vs-floor. Also re-run `buildtime.py --mem` to catch any module the
stale ledger missed. STATE: commit `bqfwh4oip` still gating (do NOT touch the RAM knobs mid-gate); ⟡cap-384 execution
starts once it lands.

### §MEM-CENSUS RESULT (Agent A, 2026-07-23c) — ran buildtime.py --mem. ⚑ THE HEAVY MODULES ARE ALL ALREADY DECOMPOSED.
The genuinely-heavy (>500 MB) modules are re-engineered already; the heaviest UN-decomposed is only ~153 MB (well
under the 1 GB per-module cap) — so ⟡heavy-decompose is POLISH, not a pressing OOM. Ledger top-by-peak_mb:
`D8Test`/`rr`/`G8Test` (883/128/128 MB, 42/23/6 s) are STALE — deleted scratch files, historical rows, not current.
Real top (all ALREADY DECOMPOSED): `Q/JacobianEncodingLiteral.agda` (857 MB, thin re-export; heavy elab in
`JacobianLiteral1[A/B]`, lemma-per-file + `Assemble` seal) · `Q/JacobianCounterexample.agda` (821 MB, def/proof
split, defers `detJac-literal`) · `Permutation/Cyclic.agda` (546 MB, opaque-sealed — the Cycle7 fix). Documented-OOM
walls all fixed: `AES/KAT/Full` (was >5.6 GB → `Assemble` param-module), `Q/JacobianDetLiteral` (was >3 GB → ~85 MB),
`F2/Polynomial/Wedge/GF16DLog` (x¹⁵ OOM → division/log regime). **Absence from the ledger = a METHOD fact** (buildtime
records only successful shim compiles; OOM/pre-commit-only modules absent).

**THE HEADLINE — heaviest GENUINELY-UN-DECOMPOSED (3 near-ties, ~151-153 MB, each a DIFFERENT kind):**
- **`WitnessTower/EvenInComm/Properties.agda`** — 153 MB, ~450 lines. KIND ~4 monolithic combinatorial group proof
  (the whole `Aₙ ⊆ [Sₙ,Sₙ]` = `even→InComm`, `:443-445`). Heavy: nested `Fin ≟` dispatch in `swapFin`/its 5
  value-lemmas (`:81-119`) rewritten through everywhere; `conj-gtransp` 3-deep case-split (`:191-234`);
  `disjoint-InComm` inline 4-point action (`:308-355`); `foldInComm`+`flatten` bridge (`:415-436`). NO opaque/
  membudget/split. ROUTE: lemma-per-file split at its own §-headers (§1 swapFin/§2 gtransp kernel · §4 conj-gtransp ·
  §6-8 trichotomy `pairInComm-eq`/`adj-InComm`/`disjoint-InComm` · §11-13 word→perm fold), mirroring
  `JacobianLiteral1A/1B` (KIND-3 template). It is ALREADY a `.Properties` sibling, so the split is intra-file, not
  def/proof.
- **`Algebra/Z/JacobianDetNative.agda`** — 152 MB, 67 lines. KIND ~1 dense-operator: forces the native 3×3 Leibniz
  `det` over `NormPoly` (`:29`). Little to split; a determinant-as-basis-action seal is the only real lever (harder).
- **`Algebra/Z/MPolySemiring.agda`** — 151 MB, 511 lines. KIND 2 stuck-ring-identity: the `NormPoly` `Semiring`
  instance, stuck ℤ-convolution ring laws over `_*ℤ_`/`_+ℤ_` (`:11-18`,`:254-284`) — THE reflective-normalizer's
  exact domain (same kind as the cube). Single coherent ring-instance; a weaker split candidate but the route I
  just built (ZRingNorm) is the natural fit if it's the target.
DECISION FOR THE USER: pick one (or defer — none OOMs). `EvenInComm/Properties` = most-splittable + clearest seams;
`MPolySemiring` = reuses the just-built normalizer; `JacobianDetNative` = hardest (dense det).

### §DECOMP-PLAYBOOK RESULT (Agent B, 2026-07-23c) — the DECISION TREE (route by KIND; file:line-grounded, turn-key)
Classify the census-named heavy module into ONE kind → apply its route → copy its template. All heavy compiles route
through `scripts/membudget` regardless (the universal heap-cap/lease harness, CLAUDE.md:3-49) — orthogonal to which
structural route dissolves the term.

| census signal | KIND | route | COPY this (file:line) | route that does NOT fit |
|---|---|---|---|---|
| concrete linear-map / perm-matrix / bilinear OOMs on normalize (Cycle7-like) | 1 dense-operator | `opaque` seal + basis-action β-interface | `Algebra/F2/Linear/FromImages/Permutation/Cyclic.agda:60-74` (seal + `cyclic-Linear-basis`); family `FromImages.agda:163-178` (`opaque linear-from-images`) | reflective normalizer (no identity to canonicalize) |
| `a ≡ b` ℤ ring / multivariate-poly identity; hand-trace balloons | 2 stuck-ring-identity | reflect→`norm`→`norm-sound` sandwich | `Algebra/Z/ZRingNorm.agda` + `ZRingNorm/Sound.agda:127` + driver `Algebra/Q/JacCubeNorm.agda:102-113` (JUST BUILT) | FreeUP β-interface (no operator to seal) |
| monolithic KAT `refl` / 10-round chain / 256-byte S-box table | 3 exhaustive-KAT/reflection | membudget + lemma-per-file + abstract `open` reassembly | leaf `Algebra/F2/AES/KAT/Round1.agda:9`; hub `AES/KAT/Full.agda:1-45`; parent `AES/KAT.agda:86-98` | FreeUP β-interface (point-evals have no basis-action; CLAUDE.md:173-174) |
| def module drags `Properties`/`Set₁` closure into all consumers | 4 monolithic-categorical/Set₁ | def/proof split → `.Properties` sibling | `Category/Coalgebra/StructuralGCD.agda:1-30` + `StructuralGCD/Properties.agda`; also `TmDBGodel.agda`+`.Properties` | reflection+membudget (no chain/table to force) |

KIND-1 key interfaces (reuse verbatim): `basis-permutation-Linear` (`FromImages/Permutation/Linear.agda:24`),
`apply-basis-permutation-Linear` = the β-rule / `extend-on-basis` (`:27-29`), `HasOrder-from-perm`
(`FromImages/Permutation/Order.agda:47-50`), `extend-unique` (`Category/FreeUniversalProperty.agda:71`;
`FreeMonoid.agda:99`; `FreeF2Module.agda:156`), `package-comm` (`FreeUniversalProperty/PackageComm.agda:4`). The
`opaque` seal is BOTH the obstruction and the enforcement — it channels consumers into the basis-action interface.
KIND-3 named idiom "AES-Full pattern"/"lemma-per-file" also at `Q/JacobianLiteral1.agda:4`, `JacobianEncodingLiteral.agda:10`.
The def/proof split is FRACTAL: KIND-1's opaque seal ("hand consumers the lemma, not the unfolded construction",
`Cyclic.agda:58`) and KIND-2's `ZRingNorm/Sound.agda:9` (Sound imports ring Properties; ZRingNorm holds defs) are the
same lesson one level deeper.

---

# ⟡UPDATE (2026-07-23b) — ⟡cube-sentinel RESOLVED + ⟡cube-reflect-nc DONE (faithful). Read THIS first; the base regrounding below still stands.

## STATE (one line, current)
Engine DONE (72 MB). **⟡cube-sentinel RESOLVED** (no engine change — the zero-literal clause would break the clean
general `norm-sound (lit c)`; the trailing `+ℤ 0ℤ` is a BRIDGE concern, one `+ℤ-identityʳ`; probed EXIT=0). **⟡cube-
reflect-nc DONE** — `Substrate/Algebra/Q/JacCubeNorm.agda`: `e-N` reflected + `bridgeN : ⟦ e-N ⟧ ≡ Cur.N_C x y z`
typechecks (84 MB) — the `N_C` reflection is proven FAITHFUL (closes the N_C-side instrument-fidelity from the prior
G8 handoff), and this IS the `N_C` half of ⟡cube-bridge. Nothing committed. Next = ⟡cube-reflect-sum → ⟡cube-reflmatch.

## THE RECURSIVE EITHER/OR COLLAPSE (this micro-arc)
Both forks collapsed to ONE move: **REIFY the `⟦e⟧ ≡ side` bridge as a checkable term; read the actual structure to
find where the glue lives — don't add a normalizer feature for a boundary artifact.**
- "add `norm (lit (+0)) = []` engine clause vs handle in the bridge" → NEITHER-as-posed: the sentinel is a boundary
  artifact of `sumNum [] = 0ℤ`, absorbed by the RING'S OWN `+ℤ-identityʳ`; the engine clause would make `norm (lit c)`
  stuck on a variable and break the clean general `norm-sound`. The engine stays MINIMAL; the glue lives in the bridge.
- "reflect-nc = just define `e-N` vs also prove the bridge" → NEITHER separately: a reflection without its faithfulness
  bridge is unverified SURFACE (the tightening-loop's reify-audit — a prose "the reflection is right" vs the checkable
  `bridgeN`). So reflect-nc = reflect + prove-faithful, one atomic unit.
- **Deepest bottom:** the cube arc is the engine's move (spread the proof over the reflection AST) applied to the
  ACTUAL terms; `bridgeN`/`bridgeR`/`same` are three positions of ONE operation (build `⟦e⟧≡side`, refl-match `norm`),
  the `N_C` side carrying the `Qn`-glue (cong-chain), the `sumNum` side the sentinel (refl + one `+ℤ-identityʳ`), the
  refl-match the binomial core — all memory-bounded (84 MB). `⟦e⟧ = evalC (norm e)` is the wedge once more.

## RETROSPECTIVE (gated, LIGHT — two clean steps)
- **G0.** Resolve ⟡cube-sentinel; reflect `N_C`.
- **G2 delta.** POSITIVE + a de-risk. ⟡cube-sentinel corrected DOWNWARD (no engine change; the clause was the wrong
  tool). ⟡cube-reflect-nc landed faithful FIRST TRY (`bridgeN` typechecked, 84 MB) — the hand-quoting was correct,
  settling the `N_C`-side instrument-fidelity flagged at the last G8.
- **G3 cause (of success — PROTECT).** READ-ACTUAL-DEFS-BEFORE-BUILDING (`qq≡Q110` the only glue; `1ℤ=+1` and
  `(+m)*ℤ(+n)=+(m*n)` defeq; `N_C`'s exact tree) → correct first try. PROBE-BEFORE-BIG-QUOTING (the tiny sentinel
  probe confirmed the plan). REIFY-NOT-ASSERT (`bridgeN` is a checkable faithfulness term, not prose). MEASURE (84 MB).
- **G6 sustain (PROTECT).** All of G3 + the reflect+prove-faithful ATOMIC UNIT (never bank a reflection without its
  bridge) + honest scope narrowing (⟡cube-sentinel down to a no-op; ⟡cube-bridge's `N_C` half done as `bridgeN`).
- **G8 handoff.** `operator=other` residue: whether `norm e-N ≡ norm e-R = refl` holds (the binomial identity AND
  whether `e-R` reflects faithfully) — settled ONLY by ⟡cube-reflmatch running. The `N_C`-side fidelity is CLOSED
  (`bridgeN`); the `sumNum`-side reflection + the refl-match remain.
- **G9.** No new failure class. The tightening-loop reify-audit fired correctly (`bridgeN`, not a pointer). Clean.

## SHADOW-ENGINEER (Fano, light)
- **L₁ positive-closure ×2** (⟡cube-sentinel resolved; ⟡cube-reflect-nc + `bridgeN` delivered).
- **L₆ guard-reconstitution.** The ⟡cube-sentinel engine-clause direct move was REJECTED by the guard (it breaks the
  clean general `norm-sound`) and RECONSTITUTED through the shadow structure (the ring's own `+ℤ-identityʳ` in the
  bridge) — the guard's prohibition kept the engine minimal.
- **S₃-fixed core:** SPREAD-THE-PROOF-OVER-THE-AST + REIFY-THE-`⟦e⟧≡side`-BRIDGE (checkable, not prose). Retained
  regardless of which side (N_C / sumNum) is fed. **Standing line (do NOT force):** ⟡cube-reflmatch (make-or-break).

## LABELED ⟡ ROSTER (current — specify by symbol)
### DONE
- **⟡engine** — ZRingNorm + ZRingNorm/Sound (`norm-sound`) + ZRNDemo `(a+b)²` (72 MB).
- **⟡cube-sentinel** — RESOLVED, no engine change (bridge `+ℤ-identityʳ`; `sumNum` side refl-clean; probed).
- **⟡cube-reflect-nc** — `JacCubeNorm.agda`: `e-N` + `bridgeN : ⟦e-N⟧ ≡ Cur.N_C x y z` FAITHFUL (84 MB). = the
  `N_C` half of ⟡cube-bridge.
### REMAINING — the cube consumer (dependency-ordered; one focused block)
- **⟡cube-reflect-sum** — reflect `sumNum Cᶠ` as `e-R` (7-term `padNum` tree, refl-clean per probe) +
  `bridgeR : ⟦ e-R ⟧ ≡ sumNum Cᶠ` (one `+ℤ-identityʳ` up the `+ℤ` spine). Subsumes ⟡cube-bridge's `sumNum` half.
- **⟡cube-reflmatch** — `same : norm e-N ≡ norm e-R = refl`. THE make-or-break binomial check + RAM measurement.
  Should hold (`normalize R.f₁ = normalize Cᶠ` = `bridgeᶠ` refl, JacCube). Not-refl ⇒ the differing monomials ARE
  the residue localizing a defect (both outcomes are the deliverable).
- **⟡cube-identity** — `cube : sumNum Cᶠ ≡ N_C`
  `= trans (sym bridgeR) (trans (norm-sound e-R) (trans (cong evalC (sym same)) (trans (sym (norm-sound e-N)) bridgeN)))`.
- **⟡identify1** — compose `identify₁ : evalℚ f₁ ≈ℚ C.f₁`
  (`normalize-eval f₁ ∘ ≡→≈ℚ bridgeᶠ ∘ evalCD-sound Cᶠ ∘ ≡→≈ℚ (cong (λ n→mkℚ n Dden) cube) ∘ ≈ℚ-sym evalCD_C`);
  measure 781 → ~200 MB.
- **⟡cube-commit** — register `JacCubeNorm` + `ZRingNorm` + `ZRingNorm/Sound` in the Makefiles
  (`gen_build_makefiles.py`), full-build-gated commit (engine + consumer together), wait for the amend marker.
  ⚑ pre-commit name check: `ZE`/`Mon` fresh (sumtype ratchet); MPolyNormalize import not `.Properties` (def/proof).
### STANDING / RESIDUE
- **⟡push** — unpushed stack (`3c9343b` evalCD_C + earlier); USER pushes.
- **⟡jaccube-scaffold** — `JacCube.agda` (scratch): `bridgeᶠ : normalize R.f₁ ≡ normalize Cᶠ = refl`, `sumNum-++`,
  `Cᶠ`. `bridgeᶠ` IS ⟡identify1's `normalize-eval → Cᶠ` bridge. REUSE.
- **⟡ring-trace-probe-retire** — `RingTraceProbe.agda` (scratch, superseded by the normalizer). Retire or keep as
  the `_⇒*_` trace-idiom reference. Residue, not deleted.
- **⟡identify-rest** — `f₂`/`f₃` components reuse the SAME engine once ⟡identify1 lands. Not this arc.

---

# ⟡REGROUNDING (2026-07-23) — the reflective ℤ-ring normalizer ("extruder-search layer") arc. COMPACTION-SAFE, stands alone.

## STATE (one line)
The **extruder-search layer is BUILT + VALIDATED END-TO-END** (`ZRingNorm.agda` engine + `ZRingNorm/Sound.agda`
`norm-sound` + `ZRNDemo.agda` `(a+b)²` demo, compiles **72 MB / 2.56 s**, `refl`-match works). The directive
"build the extruder-search layer so it generates the trace automatically" is FULFILLED. NONE of the three modules
committed/registered (validated scratch-adjacent; dead surface until the cube consumes them). The cube consumer
(`sumNum Cᶠ ≡ N_C` → compose `identify₁`) is the next arc — well-scoped, de-risked, NOT trivial.

## THE ENGINE (the deliverable — the terms, so it stands alone)
- `agda/Substrate/Algebra/Z/ZRingNorm.agda` `(k : ℕ)(ρ : Vec ℤ k)`: `data ZE (var/lit/⊕/⊗)`, `Exps=Vec ℕ k`,
  `record Mon (co,ex)`, `Canon=List Mon`, `powℤ`, `evalE′/evalE/evalM/evalC`, `⟦_⟧`, canonical arith
  (`zeros/oneE/unitE/addE/eqE/ltE`, `insertM` [combine like exps, NO zero-pruning], `addC/scaleC/mulC`),
  `norm (var i)=mkMon(+1)(unitE i)∷[] ; norm(lit c)=mkMon c oneE∷[] ; norm(a⊕b)=addC ; norm(a⊗b)=mulC`.
- `agda/Substrate/Algebra/Z/ZRingNorm/Sound.agda` `(k)(ρ)`: `norm-sound : (e : ZE) → ⟦ e ⟧ ≡ evalC (norm e)`
  (structural recursion, each case ONE local ring lemma — the proof SPREAD over the AST, bounded memory) + the
  ~10 supporting lemmas (powℤ-add, evalE′-zeros/unit/add, eqE-≡, evalM-mul, insertM-sound, addC/scaleC/mulC-sound).
- `agda/Substrate/Algebra/Z/ZRNDemo.agda` (scratch): `sq : (a+b)*(a+b) ≡ (a·a)+2(a·b)+(b·b)`
  `= trans (norm-sound eL) (trans (cong evalC same-nf) (sym (norm-sound eR)))`, `same-nf = refl`. 72 MB.
- WORKFLOW for a ℤ ring identity `L ≡ R`: reflect both as `ZE`, `same : norm eL ≡ norm eR = refl` (same canonical),
  then `L ≡[⟦eL⟧-bridge] ⟦eL⟧ ≡[norm-sound] evalC(norm eL) ≡[cong evalC same] evalC(norm eR) ≡[sym norm-sound]
  ⟦eR⟧ ≡[bridge] R`. `norm` auto-generates the canonical trace; `norm-sound` auto-generates the proof.

## THE RECURSIVE EITHER/OR COLLAPSE (the arc's invariant)
Every fork collapses to ONE move: **SPREAD THE PROOF OVER THE REFLECTION AST — never materialize a monolithic term.**
- "let Agda normalize the cube" vs "hand-trace it" → NEITHER: reflect it and let `norm`+`norm-sound` do it, so the
  proof lives in the STRUCTURAL RECURSION, not a single stuck term (the 781 MB → the ~72 MB shape).
- "engine done vs cube done" → NOT competing: the directive (engine) is fulfilled; the cube is the next directive
  (sequential, not a fork).
- "checkpoint vs push into the cube" → same operation (apply-engine-to-cube), differ only in WHEN → a reachability
  gate call, not a kind-fork.
- "sentinel: engine clause vs post-hoc drop" → the engine clause (`norm (lit (+0)) = []`) IS the proper form — a
  normalizer SHOULD prune zeros; it handles the sentinel AND any future cancellation. Not hack-vs-proper.
- "refl-match vs it won't match" → the refl-match IS the load-bearing MEASUREMENT: `refl` = the ℤ cube identity is
  proven; not-`refl` = the residue localizes the defect. Both outcomes are the deliverable (never-discard-residue).
- **Deepest bottom:** `⟦e⟧ = evalC (norm e)` IS the wedge `a = recon q b r` — value = canonical (quotient)
  reconstructed, `norm-sound` the structural proof. The RAM cap is the guard that keeps aiming this move. The
  normalizer is the split-idempotent / free-UP move once more. [[set1-is-grade-collapse]] cousin at the value layer.

## RETROSPECTIVE (gated, LIGHT — clean arc)
- **G0.** Build the extruder-search layer (reflective ℤ-ring normalizer) that auto-generates the reduction.
- **G2 delta.** STRONGLY POSITIVE + two load-bearing reads: engine built + validated on a demo (72 MB, first-try
  after ONE insertM-sound fix); + a DE-RISK (`(+m)*ℤ(+n)=+(m*n)` is DEFINITIONAL → the sign coercion is `refl`-clean);
  + a CORRECTION to the "just quote it" expectation — the two sides SPELL ℕ-powers differently (`N_C`: `Qn a b c`
  nested `^`/`·1`; `sumNum`: `powℤ` towers; reflection: flat `+(a·b)`), so the `⟦e⟧ ≡ side` bridges are cong-chains
  over the existing leaf lemmas (`qq≡Q110`/`qyy≡Q020`/`qzn≡Q001`), NOT `refl`. Reading the defs BEFORE quoting caught it.
- **G3 cause (of success — PROTECT).** VALIDATE-THE-MECHANISM-ON-A-DEMO-BEFORE-THE-REAL-INSTANCE (the 72 MB
  `(a+b)²` demo proved the entire workflow before any cube quoting — the single highest-value move); READ-ACTUAL-
  DEFINITIONS-BEFORE-ASSERTING (both the coercion de-risk AND the ℕ-power mismatch would have bitten a blind quote);
  MEASURE (72 MB, not theorized); SCOPE-THE-REMAINDER-PRECISELY-THEN-CHECKPOINT (the reachability gate, applied — I
  surfaced the exact remaining glue + the fork once, rather than grinding a long fiddly tail in an already-huge turn).
  ONE watch: internal grind-vs-checkpoint deliberation ran long (the `scope-reachability-early` tell) — but the OUTPUT
  was disciplined (de-risk → scope → checkpoint with a clear fork), a partial improvement over explore-then-waffle.
- **G6 sustain (PROTECT).** All of G3 + probe-before-real (demo first) + isolate-typecheck-with-real-exit-codes +
  the def/proof split (engine defs in ZRingNorm, proofs in Sound) + honest dead-surface stance (don't commit the
  engine until the cube consumes it — land them together).
- **G8 handoff.** `operator=self` fully spendable (the cube is buildable, no blocker). The genuine `operator=other`
  residue: (i) whether `norm e_N ≡ norm e_R = refl` actually holds — argued yes (`normalize R.f₁ = normalize Cᶠ`
  established) but settled ONLY by running it; (ii) INSTRUMENT-FIDELITY — whether my hand-reflection of `N_C`/`sumNum`
  is faithful is the `operator=other`-only check (only running agda on the reflected terms verifies the transcription).
- **G9 escalate.** No NEW failure class. The scope-reachability discipline HELD (partial improvement). The
  validate-on-a-demo-first move is a form of probe-before-real (already a memory). Nothing to escalate; clean arc.

## SHADOW-ENGINEER (Fano)
- **L₁ positive-closure COMPLETE** for the engine: goal[auto-generate the reduction under the RAM cap] →
  shadows[the reflection AST · `norm` canonicalizer · `norm-sound` structural proof · the `(a+b)²` demo validation ·
  the reduction-trace `_⇒*_` idiom it supersedes] → artefact[ZRingNorm + Sound, validated 72 MB].
- **L₆ guard-reconstitution — the arc's defining shape.** The RAM cap (the guard) REJECTED the direct move
  (Agda-normalizes-the-cube / monolithic `refl` → 781 MB / OOM) and RECONSTITUTED it through the shadow structure
  (the reflective normalizer that spreads the proof over the AST). The cap's prohibition PRODUCED the correct
  architecture — the negative axis as positive affordance. Same guard-reconstitution as the whole memory-cap mission.
- **S₃-fixed core:** SPREAD-THE-PROOF-OVER-A-STRUCTURE (reflect → canonicalize → structural soundness) = the wedge
  `⟦e⟧ = evalC(norm e)`. Retained regardless of which identity is fed to the engine.
- **Standing line (do NOT force):** the mission center — this is one component (`identify₁`) of the ℚ Jacobian-
  counterexample; other `identifyᵢ` for `f₂`/`f₃` reuse the SAME engine once this lands.

## LABELED ⟡ NEXT STEPS (specify by symbol)
### THE CUBE CONSUMER — the next arc (dependency-ordered; one focused session; commit engine+consumer together)
- **⟡cube-sentinel** — engine edit: add `norm (lit (+ 0)) = []` clause to ZRingNorm + `norm-sound (lit (+ 0)) = refl`
  case to Sound (`0ℤ = + 0`, `evalC [] = 0ℤ` → `refl`). Prunes `sumNum`'s trailing stuck `+ℤ 0ℤ` sentinel that would
  inject a spurious `mkMon 0ℤ oneE` and break the `refl`-match. Re-typecheck both engine modules. SMALL, do FIRST.
- **⟡cube-reflect-nc** — reflect `N_C = N1 +ℤ N2` as `e_N : ZE 6` over ρ=[px,py,pz,+qxn,+qyn,+qzn]. `Ux`/`Vx`
  reflected ONCE each and reused. `N1 = (pz⊗(Ux⊗(Ux⊗Ux)))⊗var4`; `N2 = ((((py⊗py)⊗Ux)⊗Vx)⊗var3)⊗var5`;
  `Ux = (lit(+1)⊗ eQn110)⊕((var0⊗var1)⊗lit(+1))`; `Vx=(lit(+4)⊗eQn110)⊕((lit(+3)⊗(var0⊗var1))⊗lit(+1))`.
- **⟡cube-reflect-sum** — reflect `sumNum Cᶠ` as `e_R : ZE 6`, mirroring `padNum`'s single-product tree per term
  (7 terms, ending in `⊕ lit 0ℤ`). `padNum (term (mono a b c) k) = k *ℤ (powℤ px a *ℤ(powℤ py b *ℤ powℤ pz c))
  *ℤ (powℤ(+qxn)(3∸a) *ℤ(powℤ(+qyn)(4∸b) *ℤ powℤ(+qzn)(1∸c)))`. Reflect `powℤ atom n` as an n-tower `atom⊗(...⊗lit(+1))`.
  `Cᶠz={(0,0,1):1,(1,1,1):3,(2,2,1):3,(3,3,1):1}`, `Cᶠy={(0,2,0):4,(1,3,0):7,(2,4,0):3}` (JacCube.agda scratch).
- **⟡cube-bridge** — the two `⟦e_N⟧ ≡ N_C` and `⟦e_R⟧ ≡ sumNum Cᶠ` bridges. THE NON-TRIVIAL GLUE: the ℕ-power
  spelling mismatch means these are cong-chains, NOT `refl` — `⟦var3⊗var4⟧ = +(qxn·qyn)` must be rewritten to
  `+ Qn110` via `cong +_ qq≡Q110` (+ `qyy≡Q020`, `qzn≡Q001`), threaded through the tree. Bounded (Ux/Vx bridged once).
- **⟡cube-reflmatch** — `same : norm e_N ≡ norm e_R = refl`. THE MAKE-OR-BREAK binomial check + the load-bearing
  MEASUREMENT. Should hold (`normalize R.f₁ = normalize Cᶠ` established, JacCube `bridgeᶠ = refl`). If not `refl`,
  the differing monomials ARE the residue localizing the defect. Measure the RAM here.
- **⟡cube-identity** — `cube : sumNum Cᶠ ≡ N_C` via the norm-sound sandwich (`trans (sym ⟦e_R⟧-bridge) (trans
  (norm-sound e_R) (trans (cong evalC (sym same)) (trans (sym (norm-sound e_N)) ⟦e_N⟧-bridge)))`).
- **⟡identify1** — compose `identify₁ : evalℚ f₁ ≈ℚ C.f₁`:
  `evalℚ f₁ ≈[normalize-eval f₁] evalℚ (normalize f₁) ≡[bridgeᶠ] evalℚ Cᶠ ≈[evalCD-sound Cᶠ] mkℚ (sumNum Cᶠ) Dden
  ≈[≡→≈ℚ (cong (λ n → mkℚ n Dden) cube)] mkℚ N_C Dden ≈[≈ℚ-sym evalCD_C] C.f₁`. Measure (target 781 → ~200 MB).
- **⟡cube-commit** — register ZRingNorm + Sound + the cube module in the Makefiles (`gen_build_makefiles.py`),
  full-build-gated commit (engine+consumer together), wait for the `post-commit advisory (auto-captured)` amend marker.
  ⚑ NAME CHECK before commit: `data ZE` and `record Mon` are fresh (sumtype ratchet); MPolyNormalize import is not
  `.Properties` (def/proof gate). Both likely clean; verify.

### STANDING / RESIDUE
- **⟡push** — the unpushed stack (`3c9343b` evalCD_C + earlier: c1e02d5, bd683a6, a4f033d, …). USER pushes
  (`git fetch` + fast-forward after the amend marker). Do NOT push from the assistant.
- **⟡ring-trace-probe-retire** — `RingTraceProbe.agda` (scratch, validated 77 MB, the explicit `_⇒*_` reduction-trace
  idiom) is SUPERSEDED by the normalizer for the cube. Decide: retire, or keep as the trace-idiom reference. Residue,
  not deleted (never-discard-residue).
- **⟡jaccube-scaffold** — `JacCube.agda` (scratch): `sumNum-++` (fold hom), `Cᶠz`/`Cᶠy`/`Cᶠ`, `bridgeᶠ : normalize
  R.f₁ ≡ normalize Cᶠ = refl`. REUSABLE — ⟡identify1's `normalize-eval → Cᶠ` bridge is exactly `bridgeᶠ`.
- **⟡identify-rest** — once ⟡identify1 lands, the same engine composes the analogous `identifyᵢ` for `f₂`/`f₃` (the
  other ℚ Jacobian-counterexample components). NOT this arc; the engine makes them cheap.
