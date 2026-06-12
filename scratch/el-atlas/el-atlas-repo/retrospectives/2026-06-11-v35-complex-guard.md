# Retrospective R-V35: the blanket complex guard (nine gates)

Subject: the v3.5 patch's central `_memo` V-guard for `coeff='complex'`.
Frozen actual: commit 10aabbe (run S_f117b7f53a8e retained in-tree).
External finding F₁ arrived from the author within one turn.

## G0 — Precommit (recoverable, verbatim from the turn)
"coeff extension needs a V-pending-port guard so unported claims stay
honest under complex (no silent fall-through to the real branch: that
would be Caveat 2.4a's sin at the instrument level)." Expected outcome:
an honest all-V complex slice + three new claims P at base. NOTE: the
precommit itself contains the flawed premise — "fall-through =
semantically wrong," asserted globally, reading undeclared. Gate passes
(a real prior expectation exists, in the record); the finding is that
the precommit was wrong, not absent.

## G1 — Freeze
Commit 10aabbe, write-once: the patch, the run output
(tools/el-atlas-depsort-v3.5-run.txt), the regenerated edition. The
artifact's signature is IN the frozen record: Break-2 lists 'coeff' in
the sensitivity row of all 24 claims, contradicting _CLAIM_DEPS in the
same module (ADJ declares ('adj',) yet shows coeff-sensitive).

## G2 — Delta
Expected "honest unstatability" vs actual: the central wrapper OVERRODE
eleven claims' declared coeff-independence (ADJ BAL CDC CRS PUR PRO LOC
L26 NOE PR2 IDC) — their tests never read coeff, yet the wrapper forced
V. Second divergence: 'complex' was admitted with provenance but WITHOUT
a declared reading (base-field ℂ vs CD-rung vs other); the "wrong"
verdict presupposed one. Third: the smoke test displayed the bug
(ADJ: 'V' under complex) and was read as confirmation — its expected
output was written by the same assumption that wrote the code.

## G3 — Cause structure
- TRIGGER: the sentence "falls through to the REAL branch, which is
  semantically wrong," written against the coeff-usage grep.
- ROOT CAUSE (systemic): the knob-admission procedure has no
  reading-declaration gate and no per-claim stance-derivation step;
  and the central wrapper made blanket semantics a one-line change
  while derived semantics cost thirteen — the architecture priced the
  wrong move cheapest.
- CONTRIBUTING: (a) the contradicting information (dep-tuples) was in
  the module and unconsulted; (b) payoff-turn momentum; (c) the
  S_8fecfdc135c8 lesson ("helpers are semantics") primed toward central
  enforcement; (d) Caveat 2.4a cited while being violated in dual form
  (non-support assumed instead of support tested).

## G4 — Decorrelation (iterated subtraction; F₁ external)
- F₁ (author, independent): blanket guard; complex≠CD necessarily; the
  fix must hinge on injected breakers — "feature flagging as
  epistemological model derivation."
- F₂ (F₁ subtracted): the deps-contradiction is mechanically checkable
  (Break-2 vs _CLAIM_DEPS) — the frozen run's sensitivity table and
  complex-slice verdict distribution are partly ARTIFACTUAL; ledger
  annotation owed (verdict change).
- F₃ (F₁∪F₂ subtracted): the interrupted spec import was about to bank
  S_f117b7f53a8e indices into §5.7e/§5.8 — imports must cite the
  corrected space (verdict change to the import plan). F₃b: smoke tests
  for knob changes lack independence from the patch's intent — they
  must include a deps-EXCLUDING claim whose expectation is derived from
  the declaration, not from the patch (process commit).
- F₄: even post-fix, no stance can reach 'extends' without a breaker
  harness; reasons must name their breakers or the table fossilizes
  (commit: breakers named per stance entry).
- F₅: ∅ — fixpoint (exhausted-from-inside, NOT verified).

## G5 — Blameless rewrite
Not "the assistant was hasty": the loop had no step forcing the question
"wrong under WHICH reading?", and the cheapest available edit was the
blanket one. Fix the loop and the price gradient, not the narrator.

## G6 — Sustain (co-equal)
(1) The fingerprint discipline worked: the artifactual run is INDEXED
(S_f117b7f53a8e), not anonymous. (2) Per-claim dep declarations existed
— the bug was detectable in the module's own terms. (3) The
author-review cadence caught F₁ in one turn. (4) The new claims' own
in-body guards were correctly per-claim and reasoned — the right
pattern was in the same patch; only the retrofit was blanket. (5) The
freeze was cheap because the state was uncommitted and git is the
write-once medium.

## G7 — Commits
1. [this session, today, verifiable by rerun] Replace the central guard
   with _COMPLEX_STANCE applied ONLY where 'coeff' ∈ declared deps;
   every entry carries its reason AND its named breaker; coeff-
   independent claims untouched. VERIFY: Break-2 shows ADJ without
   coeff; ADJ('complex' model) == 'P'.
2. [same] Knob provenance text declares the reading UNDECLARED as a
   registered alias circumstance (base-field ℂ vs CD-rung); declaring
   it is itself a named breaker.
3. [same] PRIOR_LEDGER annotates S_f117b7f53a8e with the blanket-guard
   caveat (precedent: the S_8fecfdc135c8 entry).
4. [same] Spec imports cite only the corrected space.
5. [cotype, standing] Smoke tests for knob changes must include a
   deps-excluding claim with declaration-derived expectation.
6. [standing] No stance may move to 'extends' except by its named
   breaker passing — feature flags as epistemological model derivation.

## G8 — Handoff (the cross-pass blind spot)
Every pass — and the fix — trusts (a) my reading of what each claim's
test "needs" (the stance reasons are my readings of my own test code)
and (b) the correctness of the dep-tuple declarations themselves (a
claim secretly reading an undeclared knob would corrupt memoization,
the bug, AND the fix identically). External review should audit the
stance table against claim sources, and an instrumentation pass should
record ACTUAL knob reads per claim. Labeled: exhausted-from-inside.
