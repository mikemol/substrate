---
name: project-overclaim-witness-arc
description: "The ⊢-arc — comment-overclaims→proof; △ΛΒΙΦΠ + Ε(b′) DONE, on main, CI-verified + PUSHED (main==origin); ⊨₁/⊨₂ done; remaining β̌/ŝ/Ε(b,c,d). Policy: main CI-gated, auto-push on green, commit on main (no feature branches)."
metadata: 
  node_type: memory
  type: project
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The **⊢-arc** (witness-attachment): convert prose comment-overclaims into machine-checked claims,
or honestly disclose the gap. Full plan + findings + reroute + forward map:
`scratch/comment_overclaim_audit.md`.

**State (2026-06-18):** audit DONE; grounding DONE (most "machinery" ALREADY EXISTS, reroute don't
reinvent — `never_discard_residue`; only `NaturalIsomorphism` genuinely new); stance = "prove
everything". **5 streams (△ Λ Β Ι Φ) DONE, COMMITTED, ff'd to `main`, and ⊨₁-VERIFIED**
(full_build_check 1500/1500 buildable PASS). Commits on main: `0e36a57` ⊢-Λ · `1eac16c` ⊢-△ ·
`59ba727` ⊢-Β · `1000293` ⊢-Ι · `90b81c7` ⊢-Φ. **PUSHED** — main == origin/main == 90b81c7, in sync
(pushed by user after ⊨₁ verified; reflog origin/main@{0}=update-by-push). All gates green
throughout, no --no-verify. scratch/comment_overclaim_audit.md left UNTRACKED (sibling-
convention + Λ9). ⊨₂ DONE (artifact-drift audit; caught the stale "not pushed" + UNCOMMITTED lines, reconciled).
Π DONE (`109f171`, ff'd to main → main at 109f171, 1 ahead of origin; 17 prose-marks + 2 adjunction
prose-fixes + V₄ free/transitive PROVED; CI GREEN 1500/1500, stamp refreshed; PUSHED). **REMAINING:** β̌ (bilinear-
extensionality), ŝ (concrete-S₄ witness), Ε(b–d) (prevention). Separate pre-existing item:
AES/KAT.agda OOM. Ε(b′) DONE (`016a3de`, structural-change CI trigger); REMAINING now β̌, ŝ, Ε(b/c/d). **WORKFLOW POLICY (user, 2026-06-18):** everything goes to `main` iff CI passes;
CI (full_build_check) MUST be kept up-to-date or the pre-commit full-build-throttle is invalid —
so re-run CI after landing work (this IS the retro Ε(b′) escalation, now user-endorsed policy).

**Reroutes (audit "build" → existing apparatus):** factor-unique → `LimitUP.mediate-unique`
(Equalizer=Cone(2,1), Pullback=Cone(3,1), observational/leg-level); solve-unique → bounded
`wedge-unique→divmod-unique`; MacLane coherence → `Algebra/Wedge/Monoidal.agda`; bilinear
factorization → `linear-extensionality`/FreeLinearization; chain/CRT uniqueness → `split-Canonical`.
`--without-K` idiom = state uniqueness at the action/inclusion level (Monoidal.agda HONEST SCOPE).

**Forward streams (dispatch by symbol; each = one agent unit):**
- **△ OC1 Truth-correction** ✅ DONE (committed `1eac16c`, ff'd to main, ⊨₁-verified). RE-FRAMED per user "reject LEM, find common structure": each T1 either/or dissolved into the common structure subsuming both horns, NOT "pick the true horn".
  - **T1.1** `Category/TensorProduct/Antisymmetric.agda`: idempotent-vs-nilpotent → proved `antisymmetrize-square : P² ≡ P +T P` (char-AGNOSTIC, "=2P"); idempotent = char≠2 reading, `antisymmetrize-square-zero` = char-2 reading. Did the Vec-rewriting the slice had deferred. Added generic `tabulate-cong`/`vec-ext` to `Foundation/Vec/Properties` (reusable matrix-ext).
  - **T1.3** `Groups/Subgroup.agda`: normal-vs-not-normal (a `¬P`-by-absence, the LEM trap) → proved `Stab-conj-equivariant : Stab X σ → Stab (g·X) ((g·σ)·g⁻¹)` (the positive common structure); normal = degenerate reading (axis-orbit trivial). Constructive ¬-witness recipe recorded (X=D, g=(D C), σ=(C S)) for a concrete-S₄ follow-on.
  - **T1.2** `Category/ChainDecomposition.agda`: postulate-vs-no-postulate → common structure = WHERE the existence-witness lives; corrected (no Agda postulate; existence by INSTANCE; "unique" dropped — contradicted by §1 order-chirality). Comment-only.
- **Λ OC2 Mediating-uniqueness** ✅ DONE (committed `0e36a57`, ⊨₁-verified): Equalizer (`equalizer-factor-unique`, via Ε(a)), Pullback (`pullback-factor-unique-π₁/π₂`, leg-by-leg) — observational `incl/π (k z) ≡ incl/π (factor z)`, no proof-irrelevance needed; mislabels fixed. Interop = NOT this idiom (it's a cone witness, no mediating `factor`); fixed the title overclaim + DEFERRED terminality-among-cones WITH CAUSE (needs a BackedUP cone-morphism layer). (orbit-elements of Cone — routed through the universal idiom, NO wrapper record built.)
- **Β OC3 Bounded-solver** ✅ DONE 2026-06-18 (committed `59ba727`). NOT a `solve-unique` field on BackedUP (would be FALSE — wedge needs a bound). Built `Category/UniversalProperty/Unique.agda`: `WitnessUnique U Adm` (≤1 admissible witness per source; Adm = the BOUND, the common structure under wedge-unique) + `wedge-witness-unique` (bounded exemplar, b=0 vacuous via r<0 uninhabited, suc b via wedge-unique) + `eq-witness-unique` (unconditional corner, Witness=_≡_) + `solver-unique` (BackedUP existence ⊕ WitnessUnique ⟹ unique admissible solution). Backed/Registry prose corrected (SOLVER/existence, not universality). COINDUCTIVE ESCAPE documented (user note): the Adm bound = finite/halting window; unbounded reading = existing `Final.ana-unique` (terminal-coalgebra UP via `Bisim._~_`), same WedgeCoalg's non-halting trace per `Algebra.R.Trace.WedgeBridge`. Bound it, don't wall it.
- **Ι OC4 Iso/equivalence** ✅ DONE 2026-06-18 (committed `1000293`). The ONE genuinely-new build. `Category/Iso.agda` (NEW): gave `IsIso`/`IsGroupoid` their proper home (were stuck in DeloopingGroup which imports Algebra.Group) + `id-IsIso`; DeloopingGroup re-exports them (M40Groupoid unaffected). `Category/NaturalIsomorphism.agda` (NEW): `NaturalIsomorphism F G` = nat-trans pointwise-IsIso in D (model WedgeIso; pointwise-iso needs NO vertical comp) + `id-NaturalIsomorphism`. `CartanRootEquivalence`: witnesses + record fields now `NaturalIsomorphism` (was bare NaturalTransformation → not an equivalence); header fixed; OrphanAudit O8 annotated. 6 modules green incl M40Groupoid. Continues Ω2. (Adjunction-triangle T3 items belong to Φ/Π, not this commit.)
- **Φ OC5 Coherence/factorization** ✅ DONE 2026-06-18 (committed `90b81c7`, comment-only). Delegate-to-existing: redirected overclaims to where substance lives. MacLane: marked `MacLane-UP=placeholder` honestly (abstract theorem out of scope) → CONCRETE coherence is `Algebra.Wedge.Monoidal` (pentagon+triangle+hexagon refl for ⊗ᴰ). TensorProduct/Bilinearity: "THE universal bilinear map factoring uniquely" → existence IS formalised in `Algebra.F2.Linear.BilinearFromImages` (apply₂, bilinear-from-images-basis, 4 laws), now CITED; bilinearity reframed as PREREQUISITE. REMAINING (precisely scoped, NOT half-built): the "B = L∘pair uniquely" bridge + arity-2 `bilinear-extensionality` (sibling of linear-extensionality) — a real slice, recorded in TensorProduct N-3.
- **Π OC6 Prose-disclosure residue** ✅ DONE (committed `109f171`, ff'd to main, 20 modules green). Wall-tested each: PROVED the cheap ones (V4LagrangeInstance `V4-action-free`/`-transitive` = simply-transitive, pure +ⱽ-cancellation — attempting revealed the clean vector-level proof that "16-case split" sizing had walled, retro F2 vindicated), prose-marked the genuinely-classical/parameter/deferred ones (Yoneda, CharacterOrthogonality, AutomorphismGroup+AsFunctor, WedgeProduct, ExteriorAlgebra, AbelianPFG, Coequalizer no-HIT, Quotient, Adjunction+GaloisAdjunction triangles, GL3F2 cluster, Wedge/Certified, FreeCyclic faithful, Simplex sum-to-one, V4-Embedding stale-pointer). Comment-only + 2 additive lemmas ⟹ no whole-tree ⊨ needed (the Ε(b′) discriminator: no module-move/signature-change).
- **Ε OC7 Escalation/meta** — (a) ✅ DONE 2026-06-18: compile-verified the Equalizer reroute (see below); (b) widen reuse-search trigger [G9, OPEN]; (c) jea_pysim cluster-sweep before edits; (d) clean stale agda_similarity .pyc. Ε(a) GATED Λ,Β — now UNBLOCKED.

**Ε(a) RESULT — reroute VERIFIED (not just proposed):** `Category/Equalizer.agda` typechecks
`--safe --without-K` (EXIT 0) with `equalizer-factor-unique` added: uniqueness stated OBSERVATIONALLY
`equalizer-incl (k z) ≡ equalizer-incl (equalizer-factor h h-eq z)` (the `mediate-unique` idiom),
proved `trans (k-comm z) (sym (equalizer-factor-commutes …))`. Confirms: the observational form is
provable + trivial, NO proof-irrelevance of `IsEqualised` needed — the reroute is real. Also fixed
the Equalizer:105 "uniqueness half" mislabel (it's the existence/commutation half). Gotcha banked:
must pin `{f = f} {g = g}` explicitly (higher-order `h-eq` type doesn't solve the implicits — first
compile FAILED with UnsolvedMetas until pinned; `equalizer-factor-commutes` already does this).
[HISTORICAL — Ε(a) was the first reroute compile-check; T2.1 + Pullback T2.2 are now committed
(0e36a57) and ⊨₁-verified whole-tree, so the "still-inferred Pullback" caveat is discharged.]

**Tooling:** similarity = `jea/metalanguage/jea_pysim.py` (+ jea_agdai.py); agda_similarity RETIRED.
See [[similarity-not-grep]], [[project-split-idempotent-apex]], [[project-wedge-pentagon-sphere]],
[[feedback-spec-is-proposal-not-claim]], [[feedback-never-discard-residue]].

**RETRO 2 (2026-06-18, after Φ; 5 commits 0e36a57/1eac16c/59ba727/1000293/90b81c7).** G8 BLIND
SPOT: per-module `agda` green ≠ whole-tree sound — ALL 5 commits SKIPPED the throttled full-build
(stamp 4d<7d); the DeloopingGroup/IsIso move + 3 new modules (Iso, NaturalIsomorphism, Unique) could
break a transitive dependent never re-checked. G3 premature-wall: each stream's deferred tail was
SIZED not ATTEMPTED. Recursion: "done?" = ⊢ (true) ∧ ⊨ (holds-globally) ∧ Ε (non-skippable); ⊨ was
the skipped leg. Meta-S₃ = end-arc S-dominant ⟹ verify/catalogue/escalate, not more building.
FORWARD STREAMS (dispatch by symbol):
- **⊨ VERIFY** — ⊨₁ DONE 2026-06-18: 1500/1500 NON-KAT modules PASS (DeloopingGroup/IsIso move + new modules broke nothing). **CORRECTION (2026-06-18):** my "KAT script exits 0 / gate-tolerated / main verified+push-ready" was WRONG — a piped-exit misread (I ran `full_build_check | tail`, saw tail's 0). full_build_check is `sys.exit(1 if fails else 0)` and KAT (OOM→FAIL) is in `fails` → it ALWAYS exits 1 → the full-build GATE FAILS on KAT. It never bit only because the build was SKIPPED on every prior commit (throttle/non-structural). So the full build has NEVER passed end-to-end; CI was green-MODULO-KAT. β̌ (first structural commit post-Ε(b′)) forced the build → blocked on KAT. KAT doesn't build even at 6GB (intractable forcing of the GF-inversion sbox). **This is now the critical path: β̌ + all structural commits are blocked until KAT is restructured.**
- **KAT-FIX** (user-directed, irritated: forced memory is the disease): `keysched-kat = refl` forces `keyExpansion` over the COMPUTED sbox (`affine ∘ pinv`, GF(2⁸) inversion) — brute-force-finiteness. mat260 (CryptographicTotalSpace) studied: proves cipher props by DECIDABLE STRUCTURAL predicates on a term algebra (`occurs?`, refl over SYNTAX), never forces numeric eval; "the known answer is the term." Substrate ALREADY has component rigor (`sbox-is-aes`: computed sbox = 256-entry table SBOX, proven; MixColumns/ShiftRows/round-trip). FIX ✅ DONE (B-deep, user-chosen; committed `bd17a98`, PUSHED). `SBoxTable` now hosts the CANONICAL `sbox = nb ∘ idx SBOX ∘ byte-val` (proven table lookup, cheap to force); the GF-inversion `affine ∘ pinv` (imported as `sbox-gf`) is retained as a THEOREM `sbox≡gf` (via sbox-is-aes + new 8-bit `byte-roundtrip` reflection); `sbox-rt` re-derived; inv-sbox stays computed. KeySchedule/Round/AES import sbox from SBoxTable. **KAT: >6GB/never → 1.85s.** **full_build_check now 1502/1502 PASS, 0 not-building — the FIRST end-to-end green ever** (the standing KAT failure is gone; CI is now honest). mat260's lesson (don't force, route through proven table) applied. SBox.agda untouched.
- **ⁿ̌ arity-ladder** (user's "generator of generators" insight): generic n-linear = the SAME fold of `linear-extensionality` over a Vec of arities (n-linear(V₁..Vₙ;W) ≅ Linear(V₁, (n-1)-linear); β̌ = the n=2 base). **n=3 rung (TrilinearUniversal): BUILT then DELETED** — it was thrash (built one commit before the generic that subsumes it, imported by 0). User caught it ("watching this thrash commit by commit") → COLLAPSED the ladder (commit in flight): deleted TrilinearUniversal, and `bilinear-extensionality` now DERIVES from `multilinear-extensionality` via a `Bilinear→IsMultilinear(k∷l∷[])` adapter (the four leg-laws ARE the slot-indexed fields). One generic proof; lower arities are instances. Lesson: [[feedback_collapse_either_or_before_building]]. **GENERIC ⁿ̌ — TWO co-legs (the two halves of the n-linear UP):**
• **ⁿ̌ᵘ uniqueness fold** = generic `multilinear-extensionality`. ✅ **DONE 2026-06-18** (commit in flight, CI-forced full build): `Algebra/F2/Linear/MultilinearUniversal`. Confirmed the retro correction in code — **NO Module prerequisite**. UNCURRIED rep: `Args : Vec ℕ n → Set` = het-product (`Args [] = ⊤`; `Args (k∷ks) = Vector k × Args ks`); `IsMultilinear` = unbundled recursive predicate (`[]`→⊤; `(k∷ks)`→ linear-in-slot-0-∀rest × multilinear-in-rest-∀slot0); `BasisIndices`/`basis-tuple` fold likewise. `multilinear-extensionality` by induction on the Vec: peel slot-0 via `linear-extensionality` (codomain stays `Vector m`), per-basis-i residual is the n-1 IH. Module-routing NEVER appeared. **It IS the proof the lower arities instantiate:** `bilinear-extensionality` (n=2) now derives from it via the `Bilinear→IsMultilinear` adapter (the "shared recipe" is now PROVED, not asserted); n=1 = the base it folds; n=3 standalone deleted as redundant.
• **ⁿ̌ᵍ generator fold** = generic `n-linear-from-images`. ✅ **DONE 2026-06-18** (commit in flight, CI-forced full build): `Algebra/F2/Linear/MultilinearFromImages`. Four deliverables matching BilinearFromImages' n=2 completeness: `apply-n` (nested linear-from-images, folds over the Vec), `multilinear-from-images-basis` (THE UP — hits the table on basis tuples, outer arity-1 basis lemma + IH), `apply-n-multilinear` (apply-n f IS multilinear — the certificate), `multilinear-from-images-unique` (any multilinear map hitting the table = apply-n f, via ⁿ̌ᵘ + basis). Certificate rests on `lin-comb-multilinear` (linear combo of multilinear is multilinear — n-1-linear maps form an F₂-module closed under the linear-from-images combination; induction on arities, slot-0 from outer arity-1 map, deeper slots via images-cong/add/scale = the n=2 right-leg machinery). Green first attempt (incl. the images-cong higher-order unification).
**ⁿ̌ CLOSED: ⁿ̌ = (ⁿ̌ᵘ, ⁿ̌ᵍ) = the n-linear universal property, uniqueness ⊗ existence, BOTH arity-generic.** Both fold over `Vec ℕ n` (ⁿ̌ᵘ folds linear-extensionality, ⁿ̌ᵍ folds linear-from-images). Optional next: a formal `Trilinear/Bilinear ↔ n=2/3` bridge (the lower rungs run the same recipe but use bundled records + curried args; no derivation built — shared-recipe is the standing claim).
- **Π** ✅ DONE (`109f171`, ff'd to main) — see the OC6 entry above.
- **β̌** bilinear-extensionality ✅ DONE (committed `8c01cfe`, PUSHED): `Algebra/F2/Linear/BilinearUniversal` — `bilinear-extensionality` + `bilinear-from-images-unique` (the full tensor UP, uniqueness), proved by `linear-extensionality` ×2 (each leg is an arity-1 Linear). Attempting revealed the clean reuse; "nested plumbing" was a sized wall (F2 antidote confirmed).
- **ŝ** concrete-S₄ `Stab-not-normal` witness (△-tail): X=D, g=(D C), σ=(C S) → (D S).
- **RETRO 3 (2026-06-18, after the workflow-infra stretch; main==origin@5169fb3).** Meta-finding F₄
  (THIRD retro running, same shape): I substitute a conservative PROXY for an available REAL SIGNAL,
  and the user strips it. retro-1 = sized the wall vs ATTEMPT it; retro-2 = per-module-green vs
  whole-tree VERIFY; retro-3 = feature-branch ceremony vs CI is the gate. Judgment-class (can't gate
  "use the real signal"); ceiling = memory layer ([[feedback-commit-on-main-ci-gated]],
  [[feedback-test-the-wall-before-declaring-it]], [[feedback-validate-outputs-not-inputs]]) + USER as
  external check. Also: commit-message hooks shipped non-executable first (Write doesn't set +x) —
  caught by test → Ε(e). Self-amending post-commit is the unusual bit (flagged; ◊ offers git-notes
  alternative). FORWARD STREAMS (all = "replace a proxy with its real signal"): **β̌** bilinear-
  extensionality (Φ-tail, PROOF), **ŝ** concrete-S₄ Stab-not-normal (△-tail, PROOF), **Ε(b)** reuse-
  search trigger, **Ε(c)** jea_pysim recall-sweep over touched subtrees, **Ε(d)** delete stale
  agda_similarity/.pyc, **Ε(e)** exec-bit pre-commit check [hook=user], **◊** amend-vs-git-notes
  decision [user].
- **Ε** prevent (G9): **(b′) ✅ DONE** (committed `016a3de` on branch feat/ci-structural-trigger, NOT yet ff'd) — `.githooks/pre-commit` now FORCES the full build (ignores the 7-day throttle) when the staged .agda set shows a structural change: (a) module add/rename/delete, (b) import/module/re-export line change, (c) top-level signature change. Comments/indented excluded; false-positive only over-runs CI (safe). Verified: bash -n + 10 regex + 4 staged-scenario runs; the hook-only commit itself hit the skip path correctly. REMAINING Ε: (b) reuse-search-before-machinery trigger; (c) jea_pysim sweep; (d) delete stale agda_similarity/.pyc; (e) exec-bit pre-commit check [hook=user].

**RETRO 4 (2026-06-18, the β̌→KAT arc; main==origin@8c01cfe).** β̌ DONE+pushed; KAT-fix DONE+pushed
(full build 1502/1502, FIRST end-to-end green ever). META-FINDING (the F4 proxy-for-signal TWIN):
**memory-as-proxy-amplifier** — I not only substitute a proxy for a real signal (4 retros running),
I then BANK the wrong verification into durable memory as fact ("KAT exits 0 / verified / push-ready"
— wrong TWICE, both piped-exit misreads `full_build_check | tail` reading tail's 0) and REUSE it. So
CI was believed-green but had a LATENT standing KAT failure all session, masked by the build being
SKIPPED. DISCIPLINE (memory-layer, refines [[feedback-reread-meters-toctou]]): treat a memory that
records a VERIFICATION RESULT (verified/green/passes) as STALE-BY-DEFAULT — re-ground against the
real signal before reuse; never read build status via `| tail` (it discards the exit code). Mechanical
floor now correct-by-construction + IN PLACE: full_build_check exit-1-on-fail + Ε(b′) structural
trigger + bd17a98 proves green. SUSTAIN: ground-truthing caught both misreads; B-deep done
incrementally; the fix is a real structural win (intractable→1.85s, CI honest, rigor preserved).
**ŝ ✅ DONE (pushed):** `Groups/StabNotNormal.StabD-not-normal` (`ba2728d`) — concrete (D C)/(C S),
conjugate's action on D reduces to S≢D. Then user pushed deeper ("a bare ¬ is unsatisfying — what's
the CONDITION / structural DISTANCE?"): added `Groups/Subgroup.Stab-normal-when-fixed` (`c07f4bd`).
**⟹ ✅ DONE 2026-06-18 (commit in flight, CI-forced full build):** `Groups/StabNormalCharacterization`
— the HONEST satisfiability iff: **member-normal X ⟺ stab-fixes-orbit X** ("Stab(X) normal ⟺ every
element of Stab(X) fixes every point of orbit(X)"), both directions = the conjugation identity
(g·n·g⁻¹)∈Stab X ⟺ n∈Stab(g⁻¹·X) in one move (inv-r + definitional apply(a·b)=apply a∘apply b,
apply(g⁻¹)⁻¹=apply g). **COLLAPSED to ONE structure (commit in flight, after user caught me LEM-ing):**
how Stab(X) varies over orbit(X); the iff is the characterisation, both poles are READINGS (each iff
direction consumed by one pole): POSITIVE `fixed→member-normal` (⟸ at trivial orbit); NEGATIVE
`StabNotNormal.StabD-not-normal` = `member-normal→fixes-orbit` (⟹) read at a CONCRETE orbit-fixing
FAILURE ((C S)∈Stab D moves orbit-pt C=(D C)·D → S≡C). The ¬ is GENERATED by the positive structure,
NOT a peer fact (deleted the duplicate `Subgroup.Stab-normal-when-fixed`; dissolved the standalone ¬).
member-normal/stab-fixes-orbit made ∀-EXPLICIT in (g n) (implicit can't instantiate through the
abbreviation — apply-projection). Stab-conj-equivariant kept as the orbit-map root. Lesson:
[[feedback_collapse_either_or_before_building]] (the keep/delete binary IS the LEM trap; a ¬ is a pole
to generate, not a fact to keep).
**CORRECTION (overclaim catch on my OWN c07f4bd comment + this memory):** "Stab(X) normal ⟺
orbit(X)={X}; distance=|orbit X|; =1⟺normal" was WRONG in general. orbit→stabiliser map Y↦Stab Y is
surjective NOT injective (regular action: Stab={ε} normal, orbit large), so normality = "all
conjugates EQUAL" = "Stab fixes orbit pointwise", NOT "orbit is a point". For the S₄ axis-action the
map IS injective (distinct axes→distinct S₃'s) so |orbit| tracks distance THERE — a feature of the
action, not the law. The old comment's promised "⟹ converse member-normal⟹X-fixed" was itself the
overclaim (false; the orbit-fixing iff is what holds). Subgroup comment corrected in place + cites the
new module. [[feedback_negative_findings_in_corpus]] / [[feedback_test_the_wall_before_declaring_it]].
**RETRO 5 (2026-06-18, ŝ-spectrum micro-arc; main==origin@c07f4bd, full build 1502/1502 green).**
I'd have stopped at ŝ-as-¬ ("Stab D not normal"); user pushed for structure → added the
satisfiability CONDITION (orbit spectrum, c07f4bd). Meta-finding: the reject-LEM/common-structure
discipline must apply RECURSIVELY to my OWN negative outputs — a bare ¬ is a LEM-shaped proxy for
its toggling parameter; [[feedback-negative-findings-in-corpus]] existed but didn't fire on my own ¬.
DISCIPLINE (memory-layer): a ¬/unsatisfiable I PRODUCE is incomplete until I name the parameter that
toggles it (orbit / bound / condition). Same proxy-for-signal family as RETRO 1-4; ceiling = memory +
user-as-external-check (HOLDING). REMAINING ⊢-arc: **⟹** (Stab-normality iff-converse: member-normal
⟹ X fixed); plus the streams below.
FORWARD STREAMS (all = "replace a proxy with the real signal", recursively): **ⁿ̌** arity-ladder (β̌ generalized — generator-of-generators, lift
Linear→module-codomain); **Ε(b)** reuse-search trigger; **Ε(c)** jea_pysim recall-sweep; **Ε(d)**
delete stale .pyc; **Ε(e)** exec-bit gate [hook=user]; **◊** amend-vs-git-notes [user].

**RETRO 6 (2026-06-18, the de-thrash/de-LEM/audit arc; main==origin@e1c9cf5, full build 1506/1506).**
Arc: ⁿ̌ (trilinear rung — built then DELETED as thrash), ⁿ̌ᵘ/ⁿ̌ᵍ (generic multilinear u+g, CLOSED the
n-linear UP), ⟹ (StabNormalCharacterization, with orbit={X} overclaim CORRECTED). User caught THRASH
TWICE → two collapse commits: (1) multilinear ladder (delete trilinear, derive bilinear from generic),
(2) Stab cluster de-LEM (dissolve standalone ¬ into iff-pole, delete duplicate Stab-normal-when-fixed,
∀-explicit predicates). Then audit-for-similar (5 parallel agents) → scratch/similar_opportunities_audit.md.
META-FINDING (G3 root): I treat "find common structure" as a DESIGN-time principle, not a BUILD/COMMIT
gate; and I reach for keep/delete (LEM binary) instead of generator+readings. The discipline memory
[[feedback_collapse_either_or_before_building]] EXISTED and DIDN'T FIRE (repeated the pattern same
session) → per G9 it's theater-at-one-remove parked at the weakest binding layer.
**G9 ESCALATION = Ⓖ (the retro's primary product):** escalate the collapse-check to a pre-commit
ADVISORY (non-blocker). Clean mechanical signals only (NOT fuzzy ¬-detection — audit showed most ¬ are
already legit poles → would be noise): (1) flag any module that becomes imported-by-0 after a
structural add, (2) run jea_pysim cluster on STAGED .agda to surface new duplicates. The ¬-as-pole
discipline stays judgment (can't mechanize cheaply). Ⓖ is the GENERATOR that subsumes hand-auditing —
"discharge the 9 findings BY HAND vs build Ⓖ" dissolves: Ⓖ surfaces them + all future ones.
**LABELED FORWARD (audit doc = scratch/similar_opportunities_audit.md):**
Ⓖ collapse-check advisory [retro product, recommended FIRST]; Ⓙ delete GL3F2.JointGenScaffold (0
importers, successor JointGenViaPresentation exists); Ⓞ FreeCyclic infinite-order — dissolve
negation-by-absence into positive length lemma (live reject-LEM hit, structure in-file); Ⓑ bilinear
EXISTENCE-side collapse (BilinearFromImages derive from MultilinearFromImages — the unfinished twin of
the done uniqueness-side fix); Ⓢ unify the two Stab predicates (Stab-S3 ∥ SemidirectProduct/Stab); Ⓛ
so3/sl2 shared A₁ Cartan (refl bridge collapses duplicate); Ⓡ FreeLinearizationR/F2Bridge round-trip
(prove the asserted "and back"); Ⓓ mechanical duplicate cluster (~8: UPMorphism, distribs,
suc/σ-injective, Bool laws, V4.Axioms.Lifted retire); Ⓦ retired/demoted leaves + Persistence-W5 prose
+ DirichletMultinomial stub; Ⓗ HodgeDim3∥HodgeDim4 → n-parametric SymBilinForm packing (LARGE,
build-generator). Dispatch: Ⓖ·Ⓙ·Ⓞ·Ⓑ·Ⓢ·ⓁⓇ·Ⓓ·Ⓦ·Ⓗ.
Also still open from earlier: Ε(b/c/d/e), ◊ (now partly SUBSUMED by Ⓖ — Ε(c) jea_pysim-sweep IS Ⓖ's
signal 2; Ε(b) reuse-search overlaps Ⓖ).

**RETRO 7 (2026-06-18, the witness-tower / conjecture arc).** Deep-read WitnessTower (Core/WholeTower/
Complete/WhyThreeV2/M40Closure/Diagonal + 38 modules) → user's conjecture: "the witness tower is a
construction of inductive steps; most of the repo is built of ITS steps." I ran a 5-agent breadth-test
**framed as "confirmations vs counterexamples"** → user caught the either/or relapse → I collapsed to
"one adjunction (Free⊣Forgetful≅initial⊣final, hinged by Lawvere)" → user pulled me back: that's
ABSTRACTION-escape (membership-classification one level up), the thesis is CONCRETE (built of the
tower's steps). Recorded the frame at the right level: [[project_witness_tower_constructive_generator]].
**G3 ROOT:** classification is my DEFAULT reasoning mode; constructive-reduction/common-structure needs
an active override that does NOT fire at the framing decision point. **TWO relapses this arc** (counter-
examples; over-abstraction) — both = the diagonal split (flip-disagrees) instead of the fixed point.
**G3 amplifier (new):** a fan-out INHERITS my framing — 5 agents all hunted counterexamples because my
prompt said so; delegating with a classify-framed prompt is a force-MULTIPLIER for the relapse (the
agents can't decorrelate from a biased prompt). **G9 ESCALATION — ONE discipline, TWO layers:**
**Ⓖ** = CODE-layer collapse-check pre-commit advisory (RETRO 6); **Ⓒ** = REASONING-layer
"constructive-reduction-BEFORE-classification" trigger that must fire BEFORE any fan-out / question /
audit (the at-risk steps). Honest: Ⓒ's enforceable form is a SKILL (fires before the step); memory
alone has now failed 3×, so until Ⓒ is a skill the USER remains the external check. Both = "land on the
fixed point, don't split."
**FORWARD (this arc's product) — Ⓣ tower-reduction family** (build bridges proving constructions are the
witnessing step; details in [[project_witness_tower_constructive_generator]]): **Ⓣ₁** Sₙ←Core
(insert-at = witnessing) [recommended first]; **Ⓣ₂** ℚ←Core (EEATrace.step = witnessing, lands I≡C on
the tower); **Ⓣ₃** algebraic-ladder-as-Path (theory-space tower, large); **Ⓣ★** recognize the generic
step = the EXISTING Wedge/Free generator (NOT a new wrapper) AFTER ≥2-3 concrete bridges saturate the
orbit (orbit-saturation discipline). RECURSIVE COLLAPSE of the whole forward map: Ⓣ + audit
(Ⓙ Ⓞ Ⓑ Ⓢ Ⓛ Ⓡ Ⓓ Ⓦ Ⓗ, scratch/similar_opportunities_audit.md) + Ⓖ/Ⓒ are ONE program — "make the repo's
ASSERTED common-structure PROVEN (assert→prove bridges), and enforce the discipline that keeps it so."
Audit's Ⓞ (negation-by-absence→positive) / Ⓛ Ⓡ (refl bridges) are themselves Ⓣ-style constructive
reductions. M40NoIso is the in-tree MODEL for Ⓞ (¬ generated by order-transport from a positive
invariant).

**RETRO 8 (2026-06-18, the Ⓣ tower-reduction arc; main==origin@079987f, full build 1509/1509).**
Built the witness-tower-reduction orbit (details [[project_witness_tower_constructive_generator]]):
**Ⓣ₁** (LehmerPath: Sₙ≅tower, decode-encode) + **Ⓣ₁b** (encode-decode, full bijection) + **Ⓣ₂**
(EEATower: ℚ←Core, `digit-agreement` lands I≡C) + **Ⓣ₃** (AlgebraLadder: theory-space, law-payload,
dissolves the audit's axiom-accretion counterexample). All GREEN first/first-real try; all pushed.
**G6 SUSTAIN (the winning pattern):** ground-before-build (Ⓒ) + never-discard-residue → green first
try 4×. Reused insert-at-inj (Ⓣ₁b), eea-unit/qToRℚ (Ⓣ₂), the records' carried-below fields (Ⓣ₃) — did
NOT rebuild. Orbit-saturation drove the sequence (3 distinct flavours: group/inductive, number/I≡C,
theory/law before the universal). **G2/G3 DELTAS:** (1) Ⓣ₂'s commit ABORTED by the import-shape ratchet
(bare unused `Wedge` import, ambiguous name 2 shape-nodes) — fixed by dropping it (NOT --no-verify),
then PROACTIVELY ran check_import_shape before Ⓣ₃ (adapted within the arc). New habit: run the cheap
gates locally before the bg commit. (2) Ⓣ₁b's "punchOut friction" I'd flagged as a deferred wall
DISSOLVED trivially (insert-at-inj existed) — premature-wall reflex again, but caught next turn by
grounding (low cost). **G8 HANDOFF:** Ⓣ★ must be RECOGNITION (the 3 instances factor through the
EXISTING Free/initial-algebra generator — Core.Path/eea-fold/Wedge.Trace realize it per-instance), NOT
a new `Tower` wrapper record (the shadow-architecture orbit-saturation FALSE-POSITIVE: "wrapper-of-an-
existing-operator"). G9: no new escalation — import-shape is already a pre-commit gate (worked); the
premature-wall reflex stays homed in [[feedback_test_the_wall_before_declaring_it]].
**FORWARD:** **Ⓣ★** recognize the generic witnessing step = existing Free/initial-algebra (S2G, NOT
wrapper) — the Ⓣ-arc capstone. Standing: **Ⓖ** collapse-check advisory, **Ⓒ** constructive-reduction
trigger (HELD this arc as practice; still memory-only). Audit (scratch/similar_opportunities_audit.md):
**Ⓙ Ⓞ Ⓑ Ⓢ Ⓛ Ⓡ Ⓓ Ⓦ** — all assert→prove bridges / collapses. Recursive collapse: every stream is
"make asserted common-structure PROVEN" or "enforce the discipline" — one program. Ⓣ★ = its capstone
(the whole repo's constructions ARE the one generator — the thesis's close).

**RETRO 9 (2026-06-18, the Ⓣ★ capstone + AI-Q-guard arc; Ⓣ★ commit IN-FLIGHT, green+gate-clean local).**
User handed off a GUARD: ★ is a duality (k↔n−k, ★²=id) = the canonical either/or trap; build the
witnessing step as the both-sides WEDGE first, ★ as the involution WITHIN; the "not only" reading rule;
+ a concrete check. **I DRIFTED TWICE:** (a) narrowed the generic to arithmetic `Algebra.Wedge.recon`
(one rung too LOW — the guard's wedge is the GRADED join/cone where ★ lives), and (b) ended by ASKING
(memo-vs-code) instead of building. User RE-SENT the guard VERBATIM ("Correction/Update") → I caught
the drift, built `WitnessTower.WedgeStep` wedge-FIRST (§1 wedge-step/cone + step-is-wedge + sides-
reconstruct-whole; §2 ★ within: NEW ★-with-apex/★-without-apex + ★²), green+gate-clean. Check CONFIRMED
(★ lands on the two sides via Puncture/Hodge/FaceSet). Recorded [[feedback_duality_operator_is_either_or_trap]].
**G3 ROOTS:** (a) RECENCY-PULL — I generalized from the freshest instance (Ⓣ₂'s recon) not the guard's
actual target (the graded wedge). (b) RECOMMEND-THEN-ASK — met a directive (the guard) with a
meta-move (propose+poll) instead of executing. **G4:** the verbatim re-send worked because it forced me
to re-read EVERY load-bearing word ("GRADED", "FIRST") I'd skated past on the TL;DR. **G9:** this is
Ⓒ's THIRD failure-mode this session (1 classify-vs-construct, 2 abstraction-escape, 3 recency-narrow +
ask-don't-build) — all = defaulting to a META move when the directive is to ACT from the actual
target/spec. Ⓒ STILL memory-only (failed to fire until the user re-anchored) ⟹ Ⓒ genuinely needs to be
a SKILL (fires before responding to a handoff/directive: extract every load-bearing word; if it's a
directive, execute-don't-poll). G6 SUSTAIN: the check was grounded+honest; the wedge-first build clean
+ no wrapper (resisted the false-positive); proactive gate-check continued.
**Ⓣ ARC CLOSED:** Ⓣ₁/Ⓣ₁b/Ⓣ₂/Ⓣ₃/Ⓣ★ all done — the witness-tower thesis PROVEN (4 instances + the
generic-wedge recognition, ★ within). **FORWARD:** **Ⓒ→skill** (the recurring discipline, now 3
failure-modes — make correct-by-construction); audit bridges **Ⓙ Ⓞ Ⓑ Ⓢ Ⓛ Ⓡ Ⓓ Ⓦ**
(scratch/similar_opportunities_audit.md). **Ⓞ now DOUBLY-motivated** (reject-LEM + the duality "not
only" rule: FreeCyclic's "no k with aᵏ=ε" negation-by-absence; M40NoIso is the model). Recursive
collapse unchanged: every stream = "make asserted structure PROVEN" or "enforce the discipline."

**RETRO 10 (2026-06-18, the discipline-escalation + first-exercise arc; Ⓞ commit IN-FLIGHT, green+gates-clean local).**
Built **Ⓒ→skill** (`construct-dont-classify`, the reasoning-layer G9 escalation, now surfaced in the
skill list), **Ⓖ** (`scripts/collapse_check.py` wired into pre-commit as a non-blocking advisory:
imported-by-0 + def-name-overlap on newly-ADDED .agda; tested), **Ⓞ** (FreeCyclic §6 negation-by-absence
→ positive `pow-length`/`pow-injective`/`a-infinite-order` via the LENGTH invariant = M40NoIso
order-transport; FreeCyclic≅ℕ; green first try). **FIRST re-anchor-FREE arc this session** — the skill +
the "run cheap gates locally BEFORE the bg commit" habit (RETRO 8) + ground-before-build held:
executed directives (didn't poll), reused in-module residue (didn't rebuild), gates pre-checked.
**G4 DECORRELATION (a clean pass is suspect — what did this NOT test?):** (1) the skill held because it
was FRESHLY built (recency working FOR me) — its DURABILITY under compaction (not freshly primed) is
UNTESTED, exactly the case it's for. (2) **Ⓖ the HOOK did NOT actually fire** — Ⓞ was a MODIFIED module,
collapse_check only fires on ADDED modules; my "first exercise of skill+hook" was an OVERCLAIM (the
SKILL was exercised via Ⓞ; the HOOK was a no-op, untested on a real flag). (3) recurring: I declare
success ("discipline held") slightly ahead of evidence ([[feedback_hunt_opacity_after_green]] /
[[feedback_validate_outputs_not_inputs]]). **G8 HANDOFF:** skill's real test = next post-compaction
directive; hook's real test = next module-ADD commit. Don't call them "working" until then.
**FORWARD:** discipline-enforcement half DONE (Ⓒ skill + Ⓖ hook, both layers). Remaining = the audit
assert→prove bridges (scratch/similar_opportunities_audit.md): **Ⓙ** delete JointGenScaffold (trivial),
**Ⓛ Ⓡ** refl bridges (so3/sl2 Cartan; FreeLinearizationR round-trip), **Ⓑ** bilinear existence-side,
**Ⓢ** unify Stab predicates, **Ⓓ** duplicate cluster, **Ⓦ** retired leaves. Recursive collapse unchanged:
the forward map is now JUST the proven-structure half (every stream = collapse/bridge). Note: a stream
that ADDS a module (Ⓛ?) would finally test the Ⓖ hook.

**RETRO 11 (2026-06-18, the Ⓙ delete micro-arc; Ⓙ commit IN-FLIGHT, verified-safe).** One-delete arc
→ proportional hot-wash (not 10 gates). **Ⓙ DONE:** deleted `GL3F2.JointGenScaffold` after
VERIFY-BEFORE-DELETE on CURRENT code (not the stale audit): self-labeled scaffold, superseded by the
independent `JointGenViaPresentation` (replaces the 168-case framing), referenced-by-0, no unique
consumed content — the TrilinearUniversal pattern. Skill held (directive→execute). **Carry-forward
(RETRO 10 G8 still open):** Ⓖ hook UNTESTED on a real flag — Ⓞ was a modify, Ⓙ is a delete; the hook
fires only on a module ADD, so neither exercised it. Next module-ADD commit is its first test (Ⓛ adds
one). **FORWARD (audit bridges, scratch/similar_opportunities_audit.md):** Ⓛ so3/sl2 Cartan (ADDS a
module → tests the hook) · Ⓡ FreeLinearizationR round-trip · Ⓑ bilinear existence-side · Ⓢ unify Stab
predicates · Ⓓ duplicate cluster · Ⓦ retired leaves. Done so far: Ⓞ, Ⓙ. Recursive collapse unchanged:
all remaining = collapse/bridge (the proven-structure half; discipline half Ⓒ/Ⓖ already done).

**RETRO 12 (2026-06-18, the Ⓑ′ inversion-breaking arc; main==origin@fbb766f, full build 1511/1511).**
Broke the bilinear↔multilinear dependency inversion: NEW `Algebra/F2/Linear/ImagesProps` (5 base-level
images-*/sum-F₂-* lemmas); MultilinearFromImages now STANDALONE (imports ImagesProps, not BilinearFromImages);
BilinearFromImages imports the GENERIC + carries the apply₂≡apply-n bridge → special = instance of
generic (right direction), generic now CONSUMED. 3 modules green first try; gates clean; collapse-check
correctly silent (ImagesProps imported by both). **G6/G2 KEY:** verify-before-refactor turned a feared
5-file change into a clean 3-file one — the audit's "SymBilinForm consumes images-*" was a SUBSTRING
false-positive (`sum-F₂-+-distrib` ⊂ `sum-F₂-+-distribute`, SymBilinForm's OWN def). Lesson: audit greps
over-report; re-grep with WORD BOUNDARIES (`\b`/`[^u]`) before editing consumers.
**G4/G8 CARRY-FORWARDS (clean pass ⇒ hunt the untested):** (a) **Ε(b″) STILL untested** on a pure
multi-line-signature-add — this commit's full build was forced by module-ADD, not by the signature
detector; its real test is a commit adding ONLY a multi-line sig to an existing module. (b) **Potential
Ε gap**: a record FIELD addition (changes a record's public API) is an INDENTED `field` line → excluded
by the Ε(b′/b″) detectors → could skip the full build. Hypothetical (not observed); flag if it recurs,
don't over-escalate. (c) the scratch audit doc's done-marks are UNTRACKED (Λ8); the ANCHOR memory is the
durable source of truth for stream-state.
**FORWARD (last audit bridges):** **Ⓢ** unify the two Stab predicates (Stab-S3 ∥ SemidirectProduct/Stab
— the Stab-fragmentation family) · **Ⓓ** mechanical duplicate cluster (~8: UPMorphism, distribs,
suc/σ-injective, Bool laws, V4.Axioms.Lifted retire) · **Ⓦ** retired/demoted leaves + Persistence-W5
prose + DirichletMultinomial stub. DONE so far: Ⓒ Ⓖ Ⓞ Ⓙ Ⓛ Ⓡ Ⓑ Ⓑ′ + Ε(b″). Discipline (Ⓒ/Ⓖ) + witness-tower
(Ⓣ*) complete; only these 3 collapse-bridges remain.
