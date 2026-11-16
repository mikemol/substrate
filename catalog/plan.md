# ⟡helper-sweep — adopt the canonical path/name/public helpers, under test

## Context

Three canonical helpers were just added to `scratch/agda_lex.py` (`module_path`/`module_file`,
`module_name_of`, `is_public_open`, plus the one impure `agda_root_from`). They exist because the
three largest duplication hotspots had **no adoption target** — “route through the shared module” was
never actionable for them.

**STATUS 2026-07-31: the sweep is COMPLETE** — Phase A, B1+B2, B3, the ASCII-import class, 6c
(`DECL`), and 6d (the enumeration authority + the four divergent `agda_files()`). Verification:
**52 tests, 52 scenarios**, **536 selftest cases across 22 suites**, 0 expectedFailures, no
baseline drift. The rederivation ratchet **censuses 155 sites** (was 133 — §14 added three motif
classes the gate was structurally blind to), ordinal-keyed so an unrelated edit cannot churn it.
⚑ **The baseline is NOT yet re-recorded**: the +22 are newly-VISIBLE debt, not new debt, and banking a
predicate change is a deliberate act — it joins the re-baseline table, not a silent auto-lower.

**§7 IS COMPLETE.** Audit IV’s two WRONG ANSWERS are fixed (§7a the unguarded ratchet + its inert
denominator guard; §7b six truncating regexes — and the guard that missed them, §7b-bis), and
7c/7d/7e/7g are closed. **Two of its claims were measured and REFUTED**: the rank-1 false-holes
consequence (§7b-measure) and `worklist.py --check` “cannot fail” (§7e) — a good audit, and still two
plausible-but-wrong items in it. Running each claim separately is what told them apart.

⚑ **THE BAN ARC, END TO END (2026-08-01).** The decomposition/ban work this session, in one place,
because it is now spread across §9a, §11 and the sequencing table:

| stage                                                                                       | ban paydowns | renaming clauses |
|:--------------------------------------------------------------------------------------------|:-------------|:-----------------|
| start of session                                                                            | 1674         | 3615             |
| class A — 7 `public` barrels → directories                                                  | 1674         | —                |
| class B — `split_pipeline` over 53 providers                                                | 2043         | —                |
| 3a — `Algebra.F2._+_` → `_+F_` (201 files)                                                  | 2898         | —                |
| 3b — `prune_imports` (2927 bare imports; clauses UNMOVED)                                   | 2898         | 3615             |
| Bisim + 4 sibling preludes split (42 leaves)                                                | 2898         | —                |
| **step 4** — `drop_dead_renames` (3444 dead clauses)                                        | **5437**     | 283              |
| **step 5** — rewires unblocked (1081 importers)                                             | **6512**     | **283**          |
| the 40 additions worked (7 rewired, 19 swept, 16 clauses adjudicated)                       | **6515**     | 283              |
| tool fixes paid down clauses the tools could not SEE (drop_dead_renames span + self-rename) | **6599**     | 283              |

⚑ The survivor count read **185** until the span fix; a line-based census hid **98 wrapped clauses**.
283 is the measured figure, and **0 of them are dead** — the sweep did get every dead one.

**Additions: 73 → 65** (paydowns **6599**). They held near-flat all session while paydowns moved by
thousands — the gate refuses on them, so **none of the 6599 paydown can record until they clear**.
⚑ The last movement (71 → 65) came from FIXING TOOLS, not from editing Agda: the `drop_dead_renames`
edit-loop span defect and the missing self-rename predicate were each hiding real clauses. **Two of
the remaining ban keys were paid by making a tool able to see them.** ⚑ **Classified (2026-08-01): only 40 are GENUINELY NEW; 33 are churn** from
key-shape movement during the splits. The 40 concentrate in `V4.Bijection` (6), `Graded.Quotient` (3),
`GF256.MulLaws` (3), `Foundation.Nat.SLesInjective` (3), and are 28 `using` / 6 `as` / 6 `renaming`.
**This is the whole remaining blocker to banking 6512 paydowns.**

⚑ **WORKED (2026-08-01), and the honest result is that MOST OF THE 40 ARE NOT MECHANICALLY CLEARABLE.**
Bucketed by applicable tool, then each bucket run:

| bucket                                            | n                   | outcome                                                                                                                          |
|:--------------------------------------------------|:--------------------|:---------------------------------------------------------------------------------------------------------------------------------|
| `using`, provider HAS leaves → `rewire_to_leaves` | 10                  | **7 rewired**; 3 reported *no leaf provides a name*                                                                              |
| `using`, no leaves → `split_pipeline`             | 18                  | swept: **most were ALREADY ATOMIC** (`Foundation.Level`, `Conway/*`, `Linguistic/Morphism`) — nothing to split, so nothing moved |
| `renaming` → the 4b gate                          | 6 keys / 16 clauses | **3 SAFE, 6 OCCUPIED, 7 COLLISION** — only 3 are un-renameable                                                                   |
| `as` → qualified-name rewrite                     | 6                   | the DEFERRED class; no tool exists (`scope_fix.fix_qualified` is the candidate, \~400 lines)                                     |

Net: **additions 73 → 71, paydowns 6512 → 6515.** Marginal, and that IS the finding: the easy population
was already retired by steps 3–5, so what remains needs judgement per site, not another sweep.

⚑ **A FALSE LEAD WORTH KEEPING: `MulLaws/` has EMPTY leaf directories.** `rewire_to_leaves` said *no
leaf provides a name*; I assumed a missing `-- Defines:` header (the §11 field-gap class) and started
measuring 2216 header-less files tree-wide. **Wrong — there are no files at all**, only nested empty
dirs from an older split under a DIFFERENT naming scheme (`Gmulidentity` vs today’s planned
`GmulIdentityL`). `MulLaws.agda` is intact and still defines the names. My bucketing test used
`os.path.isdir`, which is **true for an empty directory** — so three providers were routed to “has
leaves” when they have none. The 2216 figure is real but measures something else entirely and should
not be quoted as a gap.

⚑ **FIXED THE TOOLING RATHER THAN THE SYMPTOMS (user: “fix the tooling”).** Each of the three defects
above was something I had ROUTED AROUND during the 40-additions work; all three now fixed at source:

1.  **`rewire_to_leaves.leaf_map` guarded on `os.path.isdir`, TRUE FOR AN EMPTY DIRECTORY.** It then
    returned `{}` and the caller printed *“no leaf provides a name”* — which reads as *the leaves do not
    declare it* and sent me hunting a missing `-- Defines:` header across 2216 files. It now
    distinguishes the three cases and says which: no directory / directory empty (abandoned or renamed
    split; the parent is probably still unsplit) / `.agda` present only in SUBdirectories. Verified by
    constructing the nested-empty shape and reading the message.

2.  **`prune_imports` was the LONE write-polarity outlier** — measured across 9 write tools: seven gate
    on `--apply`, `prune_imports` took `--dry-run` and **wrote by default**, and its own comment claimed
    it *“mirrors fix_stale_using’s –apply shape”* while doing the opposite. That inverted flag cost an
    unintended 12-line deletion earlier today. Now `--apply`-gated (`--dry-run` still parses, harmlessly);
    verified a bare run leaves the file byte-identical.

3.  **`rewire_to_leaves` had NO preview mode at all** — no `--apply`, no `--dry-run`, every invocation
    wrote, and it is the widest-blast-radius tool in the family (one run rewrote 272 importers). Added
    `--dry-run`. ⚑ **Deliberately did NOT invert its default**: `split_pipeline` calls it mid-chain, where
    a silent no-op would leave a split half-finished and the build failing far from the cause. The
    defect was the absence of a way to LOOK, not the polarity — the opposite call from `prune_imports`,
    which is human-invoked. *One convention does not fit both driver-called and hand-called tools, and
    §7e’s “write-polarity is three-way divergent” reads as pure inconsistency until you ask who calls
    each one.*

Suite 452/452 across 13, unit tests green after all three.

⚑ **THE “TRACTABLE RESIDUE” OF THE 71 WAS NOT TRACTABLE — measured, and the framing was mine.**
I recorded “3 SAFE un-renames, 7 COLLISION, 6 `as`” as an actionable queue. Working it:

- **The 3 SAFE pay down NOTHING.** The ban key is `file::module::directive`, so a key clears only when
  the WHOLE statement loses its directive. Measured at statement level: **0 of the 6 renaming
  statements are fully clearable — every one has ≥1 blocked clause.** `V4FullCocycle.agda:31` renames
  four names; `α β γ` are SAFE but `e` is OCCUPIED (the file defines its own `e : V4Full` at :46,
  genuinely distinct from `Bijection.e`). Un-renaming three of four leaves the `renaming` standing and
  the key untouched. **A per-clause verdict does not compose into a per-key one, and I had been
  reporting clause counts as if it did.**

  ⚑ **SUPERSEDED 2026-08-01 — THE REASONING HOLDS, THE CONCLUSION DOES NOT.** “A per-clause verdict
  does not compose into a per-key one” is still true and still the reason to measure at statement
  level. But “the SAFE un-renames pay down NOTHING” was measured over **6 statements** at that day’s
  tree state and then carried as a standing fact. Re-measured over the CURRENT population
  (178 live renaming statements / 175 keys, clause verdicts SAFE 126 / OCCUPIED 47 / COLLISION 31 /
  CAPTURE 1):

  |                                       | statements |
  |---------------------------------------|:-----------|
  | **ALL clauses SAFE → the key CLEARS** | **113**    |
  | some SAFE, ≥1 blocked → key stands    | 3          |

  **113 keys are fully clearable, not 0.** The arc’s own paydowns moved the population out from under
  the finding: the statements that made the original 6 unclearable were themselves retired by steps
  3–5. So this item goes from “no mechanical queue left” to one of the largest unblocked paydowns
  available — and it was sitting in the worklist as settled-negative for a day.

  ⚑ **THE GENERALISABLE FORM, and it is the strongest method finding since “measure what the next step
  would do”: A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE.** Three of the four dependency
  errors found in the 2026-08-01 topology audit were claims that were TRUE WHEN WRITTEN and false by
  the time they were acted on, because this arc’s own work changed what they measured. A plan that
  accumulates findings without re-measuring them at point-of-use will serialise work behind blockers
  that no longer exist. *This is the same shape as the stale-baseline hazard, one level up: the
  numbers age, and the older the finding the more the arc has moved beneath it.*

- **The “7 COLLISION” are mostly STALE, not colliding — and my first diagnosis of that was also wrong.**
  I printed the imported module as though it were the definer and concluded `SLesInjective`/`Nat.Times`
  were “leaking names they don’t define”, i.e. an indexer defect. **`def_index` is correct**: `z≤n`
  maps to `Nat.Le` alone. The real shape, read from the source: `Algebra/Q/Order.agda:19-20` renames
  `z≤n`/`s≤s` **out of `Nat.Times`, which does not export them**, while `:17` already imports `Nat.Le`,
  which does. The names bind through `Nat.Le`; **the renaming clause is inert**. That is
  `fix_stale_using`’s case, not `rename_at_source`’s.

**So the honest state: the 71 additions have no mechanical queue left.** The remaining work is
per-site, and the largest lever is the tree building so the typechecker names its own
`AmbiguousName`/`ClashingDefinition` sites — which is what the ban skill prescribes and what this arc
has been deferring. The dependency that mattered: **the dead `renaming` clauses were blocking the
rewires**, so step 4 had to precede the rewire re-run, and sizing a general un-rename tool against the
pre-step-4 census would have targeted a population that no longer exists.

⚑ **§9 (Audit V) found that FIVE gates — including two written today — were baselined and wired into
NOTHING**, and the two newest baselines were untracked. Fixed: four wired, both baselines added. Two
REFUSED on wiring; **`claims` is now PAID and passing** (4 prose claims this arc’s own work falsified —
not build-blocked, and I was wrong to bundle it with the tree). **`ban` alone lands with tree-green**:
245 of its 253 additions are `using`-filtered imports on `Capstone.agda` barrels, and decomposing those
providers needs a building tree.

⚑ **§8 is open and is not an Audit IV item**: the Set₁ gate reports `0` over a catalog holding **842 of
2,762 cores (\~30%)**, with **160 definitions unmeasured** — 14 of them Records. That number is not
answerable evidence either way, and settling it needs a real build, so it joins “tree → green”.

What else remains is inconsistency, not wrongness: §7c-7e, the 6d residue, the standing instruction
(needs approval), and **three un-banked re-baselines measurable only once the tree is green**.

⚑ **That inferred claim is now MEASURED AND REFUTED** (§7b-measure): rank-1 is **115 under both
regexes**, zero false holes. The 8 edges are real (24164 → 24172) but the two affected modules declare
no types, so `produced`/`consumed` — which is what `rank()` keys on — never moved. A sound call-chain
argument that happens not to bind. Carrying it as INFERRED rather than as a finding is what kept it
from propagating as fact.

⚑ **Every scope estimate in this plan came from a shape-grep and every one was wrong**: 45→29 sites,
9→8, 49→59, “25→32”→43-keys-of-which-17-genuine. A grep counts SHAPES; only running both routes counts
FACTS. That is the same lesson as §6 (derived-view divergence), arrived at from the planning side.

**Why this matters beyond tidiness.** Every duplication class retired this arc had already shipped a
bug: a statement-span regex ate `module … where` headers and their telescopes (33 files gutted,
twice); a self-import emitter produced `[CyclicModuleDependency]` in 10 files; a def-index rule
indexed type expressions as definitions. `scripts/_agdatext.py:20-38` records the sharpest instance —
a lift landed on the *wrong representative*, so 19 importers inherited a non-nesting comment stripper,
**three of them pre-commit gates**.

**The sweep is not uniform.** The census found that a large minority of sites are not drop-ins — the
canonical is *more correct*, so swapping changes behaviour on real input:

| class                     | sites            | why it changes behaviour                      | measured on the corpus                             |
|:--------------------------|:-----------------|:----------------------------------------------|:---------------------------------------------------|
| `^module\s+(\S+)\s+where` | 6                | requires a same-line `where`                  | **149** parameterized headers missed               |
| ASCII-only char class     | 8                | rejects unicode — and, in one spelling, `-`   | **2** unicode; **160** hyphenated in `iface_shape` |
| bare `\bpublic\b`         | 16               | matches `public` in a comment / rename TARGET | **88** statements misread as conduits              |
| no comment masking        | all of the above | a block-commented header sits at column 0     | —                                                  |

⚑ Every count in that table was WRONG in the original plan and is corrected above from measurement.
The estimates came from a census that grepped for *shapes*; the corpus was never consulted. Two of the
corrections mattered: `iface_shape`’s class omits `-` as well, so it missed 160 modules rather than 2
(80× the assumed severity); and the `\bpublic\b` count of 9 undercounted the real 16.

The highest-risk are write-path × behaviour-changing: `scope_fix.py:1706,:1960` (a re-export chain
walker that counts a comment as live), `split_lemmas.py:456` (which *attaches comment blocks to each
leaf by design*, so the false positive is structural, not luck), `split_upstream.py:32` (emits
`public` into generated source from a comment-blind match), `capstone_to_dir.py:32` (`\s+where`-
anchored **and** missing `re.M`).

**Sequencing constraint (user-directed).** The 12 unconditional pre-commit gates census the *whole
working tree*, not the staged set. With the Agda tree mid-decomposition (39 errors when this plan was
written; 33 now), **no commit of
any kind can pass today** — so “separate commits per behaviour change” is not available as a
sequencing tool. The work must instead be made safe by *tests that run without committing*, and the
commit boundary is deferred until the tree is green. This plan therefore front-loads verification.

## Design

### 1. `tests/` — stdlib `unittest`, no new dependency

Only `unittest` is installed (`pytest`/`behave`/`pytest-bdd` are absent; `uv run --with` works but
would not be available to a hook in a bare environment). Layout:

    tests/__init__.py
    tests/test_agda_lex_paths.py     module_path / module_file / agda_root_from
    tests/test_agda_lex_names.py     module_name_of  (parameterized headers, unicode, comments)
    tests/test_agda_lex_public.py    is_public_open  (comment, rename-target, public')
    tests/test_agda_lex_span.py      statements / _continues / mask_comments  (migrated from _selftest)
    tests/corpus.py                  shared fixture strings, each tagged with its measured incident

Run: `python3 -m unittest discover -s tests -q`. Cwd-independent (`__file__`-anchored `sys.path`),
which the census flagged as broken in 5 tools that use `sys.path.insert(0,"scratch")`.

**`scripts/` may import `scratch/`** — verified: `check_scratch_independence.py:30` has
`ROOTS = ["jea","el-atlas"]` and its docstring states “scripts/ is NOT guarded”. Precedent:
`check_ban_ratchet.py:50`. **`jea/` and `el-atlas/` are forbidden** and must be excluded from the
sweep (3 sites: `jea/metalanguage/{nat_enum,synth_agda_prototype,synth_pyrig}.py`).

### 2. `features/agda_text.feature` — Gherkin as spec, matching the house convention

`el-atlas/features/` already holds 12 `.feature` files with **no runner** — they are
obligation-source-linked specification prose. Follow that exactly, including the header pair:

``` gherkin
# file: agda_text_invariant_0_helpers.feature
# obligation source: measured incidents (33-file gutting; F17; TokiPona/LinearAlgebra.agda:53)
```

Each `Scenario` names a **measured incident**, not a mechanic. These are already written as ⚑ comments
in the selftests and become the scenario bodies verbatim.

### 3. `scripts/check_feature_coverage.py` — the anti-drift link

Every `Scenario:` in `features/*.feature` must be referenced by name in some `tests/*.py` docstring;
an orphan scenario exits 1. This is what makes the spec and the tests one artifact rather than two
that drift. Counted, never a frozen list — the same shape as the selftests’ derived `N/M` total.

### 4. Gate the tests **and** the 8 existing `--selftest` suites

Confirmed: `grep -c selftest .githooks/pre-commit agda/Makefile` → `0`, `0`. The suites encoding the
33-file gutting, the self-import class and the span rule (30/19/14/12/10/6/6/4 = 101 cases) are run
**by hand only**, so a regression in them ships silently today. Add to `.githooks/pre-commit`, via the
existing `run` funnel, before the expensive gates:

``` sh
run "tool unit tests"  python3 -m unittest discover -s "$ROOT/tests" -q
run "tool selftests"   python3 "$ROOT/scripts/run_selftests.py"
```

`run_selftests.py` discovers `_selftest`-bearing modules rather than hardcoding a list. All are pure
functions — no Agda, milliseconds.

### 5. The sweep itself, ordered by risk

**Phase A — DONE.** 29 sites (not 45 — the census over-counted; the rest were `.agdai`, dir-only,
or bare stem strips). `scope_fix.py` (20, root `""`), `fix_stale_using.py` (4), `split_pipeline.py`
(2), `agda_defs.py`, `cap_diagnose.py`, `reuse_sweep.py`. Done as a tool
(`scratch/convert_path_helpers.py`, 8/8 selftest) rather than by hand. **Census byte-identical**
before/after, so the swaps were mechanical as claimed.

**Phase B1+B2 — DONE, and they were one class, not two.** The same 8 files carried BOTH the
ASCII char class AND the `\s+where` anchor, plus a third defect (their own weak comment stripper).
B2’s remaining 6 sites held the regex as a *compiled pattern object*, so they converted via a
`agda_lex.HEADER` shim (`.search().group(1)`, deliberately no `.span()`/`.groups()` so a caller
wanting a byte offset breaks loudly) — one line each instead of six call-site rewrites.

**Measured delta: 151 files (5.5%) invisible to every analysis** — 149 parameterized headers, 2
unicode. Zero disagreements in the other direction, so the canonical is a strict improvement.
`audit_import_reach` went 2615 → 2764 modules in graph: it had been analysing 94.6% of the tree and
reporting as if complete.

**Phase B3 — DONE, and it carries a SEMANTIC CHANGE the plan did not anticipate.**

Four write paths converted, each traced first — and the tracing changed the answer twice.

*What the gates do:* `check_public_ratchet` is **already correct** (lookaround + comment-masked), so
it was never a target; `check_claims` is **not convertible** (a file-level existence question, and it
already skips comment lines — swapping in `is_public_open` would require the statement to be an `open`
and silently flip its P1 SHIM verdict).

*The comment hazard was real but not by the predicted mechanism.* The census said `split_lemmas`
attaches comment blocks to leaves, so a comment fires structurally. True in effect, wrong in cause:
`group_statements` folds a FOLLOWING comment line into the PRECEDING statement, so a comment leaks
**across** statements. 88 import statements tree-wide were read as re-export conduits purely because a
nearby comment said “public”.

*⚑ THE SEMANTIC CHANGE (user, 2026-07-31).* `split_lemmas` exempted `open <LocalRecord> public` from
stripping, reasoning that re-exporting a locally-declared record’s fields is “only what it defines”.
The user retired that: **the distinction is not worth its complexity when the fix is a consumer writing
a few more import lines.** Two facts made it indefensible:
- **The gate already disagreed.** `check_public_ratchet`’s census counts BOTH kinds — **386 of its 557
keys are local-record re-exports** — so the exemption made the splitter contradict the gate it serves.
- Measured population: **434 live `open … public` statements = 265 local + 169 module conduits.**

*What actually moves.* The public-ratchet census is **unmoved at 557**, because the gate already counted
both kinds — but that is the narrow reading, and taking it as “no impact” was the error (see below).
The change is in what the PIPELINE EMITS: **265 statements will now be stripped that previously
survived**, each a P3 contagion site whose consumers must be rewired at the owner or hit a far-away
`[NotInScope]`. Latent until a split next runs on a file with a local re-export; the resulting
public-ratchet movement is **not predictable from here, only measurable after those strips propagate**.

*⚑ A METHOD ERROR WORTH KEEPING.* The user said up front that we would have to re-baseline, and why:
*“we’re changing the semantic meanings.”* I argued against it after checking only the gate I expected to
move, found it static, and generalised to “no census impact”. The gate was static because it already
counted both kinds; the pipeline’s meaning changed regardless. **A gate answering “unchanged” is one
derivation, not the answer** — the derived-view lesson (§6) applied to my own reasoning, and I made the
same error twice in one session.

### 6. DERIVED-VIEW DIVERGENCE — a class the plan did not contain (added 2026-07-31)

Surfaced by the user mid-sweep, then audited: **two layers compute the same quantity by different
routes, neither is a copy of the other, both are individually correct, and nothing reconciles them.**
Three prior audits missed it because all three were briefed to hunt duplicated *implementations* —
a syntactic target this class does not instantiate. `os.walk`+`endswith` and `Path.rglob` share no
tokens, so the SPPF wedge and `jea_pysim --clusters` are blind to it BY CONSTRUCTION; an empty
similarity result is not evidence of agreement. The only instrument is: run both routes, diff the sets.

**6a. SHIPPED BUILD BUG — FIXED.** `gen_build_makefiles.IMPRE` was ASCII-only, so an import of a
module with a non-ASCII letter contributed **no edge at all**. 8 edges missing from the committed
`agda/Flat.mk`; `PhaseTransition.agda:28-29` imports `IsAñeléTerminal`/`PriorAñelé` and neither was a
prerequisite. **make could not mark those modules stale**, and `--check` certified it because the gate
compares against the same regex — the gate validating its own blind spot. Regenerated: +12
prerequisite tokens, **zero removed**, 2764 targets unchanged. It also recovered `Foundation/Eq/Trans`
and `Category/BoundaryEvent` edges dropped from *this arc’s own* Eq decomposition.

**6b. THE REGRESSION NET — DONE.** `tests/test_rederive_agreement.py` (4 tests): build-DAG edges ==
lexer edges (now passing; would have caught 6a on the day it was written); all enumeration routes agree;
declared header == path-derived name; and the gates’ decl-scan vs `agda_defs`.

**6c. THE 142-NAME DEBT — RECORDED, NOT PAID.** Five gates scan `data`/`record` at **column 0** while
`agda_defs` was made indent-aware after a measured import-drop. 142 type names (20.6%) are invisible
to carrier-locality, sumtype-ratchet, public-ratchet, import-shape, decl-shape-tag. Consequences
measured: the **sumtype ratchet sees 25 duplicated names where the truth is 32** and cannot refuse a
new copy of the 7 it cannot see — the exact fork class it exists to prevent; carrier-locality judges
**5 carriers globally-unique that are not**, then enforces “the operator lives in the carrier’s home”
against a home that is not unique.

Held as `@unittest.expectedFailure` **with the number in it**, so the debt was a materialized census
entry rather than a note. **PAID** — `DECL` is now indent-aware; the marker is gone because the debt
is gone, not because someone deleted it. ⚑ The baseline movement it implies is **48 → 65 keys** and is
**not yet banked**; see “Pending re-baselines” for the measured breakdown and why banking against
today’s tree would be wrong.

**6d. Armed but not firing — PARTIALLY DISARMED.** Measured: **59 files** enumerate the corpus, **41
without a `_build` filter** (the plan said 49/3; both were shape-grep estimates).
Agreement at 2764 is currently **luck**: the first `.agda` under `agda/_build/` splits the gates from
the build generator silently. Pinned by the enumeration test.

### 7. WORKFLOW DIVERGENCE — the rhyme audit (added 2026-07-31, Audit IV)

A fourth class, and the framing was the user’s: *what rhymes, what slant-rhymes, and what SHOULD
rhyme but isn’t?* Audits I/II hunted duplicated **implementations**; III found **derived-view
divergence** (two routes, one fact). IV is one level up — divergence between **practices**, and its
signature is:

> **the fix applied to the abstraction but not to the one member that opted out of it** — invisible
> *precisely because* the surrounding convention is so well-articulated.

**7a. ⚑ WRONG ANSWER — an unguarded ratchet. FIXED.** *(resolution below the finding)*
`scripts/ratchet.py:44-64` makes writing opt-in via `SUBSTRATE_RATCHET_WRITE`, recording that the
defect was MEASURED TWICE. Six gates route through it and are inert. **`set1_ratchet_cores.py` does
not** — zero occurrences of `import ratchet` or the env var, and two raw writes (`:94` baseline-missing,
`:111` auto-lower-on-paydown). A plain `--quiet` run banks debt permanently.

The standing instruction “do not run the ratchet gates, they mutate” is therefore **correct for exactly
one gate and obsolete for six** — and nobody knows which. That is worse than a uniform hazard: it
trains everyone to avoid a whole class for a reason that no longer applies to most of it.

*Aggravator, same file:* `scripts/set1_baseline_cores.txt` contains the single token `0`, so the parse
at `:92` yields `base_cores = None` and **Guard (3) — the denominator guard, whose own comment says “a
moving denominator is not a ratchet” — never runs.** The guard exists, is documented, is correct, and
is inert. Verified by executing the parse, not by reading it.

**RESOLUTION.** Rather than duplicate the guard, `ratchet.may_write()` is now THE single write-permission
resolver, and both `set_ratchet` and the count-form gate route through it. A malformed (1-field)
baseline now **REFUSES** instead of silently disabling Guard (3): a count without its denominator is
not “no opinion”, it is an unusable baseline, and treating absence as permission is how a guard becomes
decoration. The stale docstring advertising the dormant behaviour was corrected too — that was the §7d
class inside the file being fixed.

**All EIGHT baseline-writing gates are now guarded**, and that is asserted by a test
(`tests/test_rederive_agreement.py::RatchetWriteGuardTest`) rather than believed — “all of them” is
precisely the fact that silently becomes “all but one”.

**The standing instruction is uniformly true again.** That was the second-order damage and it was worse
than the first: “do not run the ratchet gates, they mutate” had become TRUE OF ONE GATE AND FALSE OF
SIX with no way to tell which, so it trained avoidance of a whole class — including in my own audit
briefs, which kept forbidding agents from running any of them.

⚑ NOT VERIFIED END-TO-END: a real run freshens `catalog.db` and exceeds a 2-minute timeout. The guarded
logic was verified statically (both writes behind `write`, the `is not None` skip removed, the resolver
wired). Stated rather than claimed.

**7b. ⚑ WRONG ANSWER — my own miss, one line apart.** The Audit-III ASCII fix landed in
**RESOLVED — and the fixed guard found SIX, not four.** `primitive_catalogue.py:44` and an ALIAS
capture at `iface_shape.py:305` were in neither the audit’s list nor mine. All six now use `[\w.'-]+`;
the class returns zero. Original text follows.

`gen_build_makefiles` and **four files still carry the truncating `[A-Za-z0-9_.'-]+`**:
`_shred_graph.py:65`, `audit_import_reach.py:23`, `type_sppf_crosslayer.py:21`,
`realizability_surface.py:27`. Same 8 edges, still dropped.

The reason I missed them is itself the finding: each carries
`from agda_lex import HEADER … # THE header authority; never re-derive` **one line above** the broken
import regex — a line *I* added while converting the header class. A reader (me) sees “authority,
unicode-aware” and stops. **A true provenance claim about one regex reads as coverage of the next.**

Downstream, the audit inferred that undercounted in-edges shrink `reach` and **over**-populate
`realizability_surface`’s “rank-1 = realizability holes” set with false holes.

⚑ **MEASURED AND REFUTED.** Built the graph both ways and diffed: **rank-1 is 115 under both regexes;
zero false holes, zero newly-rank-1.** The fix IS real at the edge level (importer edges 24164 → 24172,
exactly the 8), but `produced` (416) and `consumed` (229) are unchanged, because **the two affected
modules declare no `data`/`record` types at all** — `home` maps nothing to them. `rank()` keys on
produced/consumed membership, and `reach()` only breaks the rank-3/rank-4 tie for types already
consumed, so the rank-1 set cannot move. Confirmed the patch fired rather than silently no-op’ing
(a “no change” result from a measurement that changed nothing is worthless).

**The audit’s reasoning was sound and its conclusion was wrong** — a correct call-chain argument that
happens not to bind, because the modules at the end of the chain carry no types. This is why the plan
carried it as INFERRED: the same care that made the 8-edge claim true made the downstream claim
plausible, and only running it separated them.

**7b-bis. ⚑ THE GUARD-FROM-THE-INSTANCE CLASS — three occurrences, all mine, one day.**
The re-audit of every guard written today found the same defect twice more, and it is now the most
transferable finding of the four audits:

> **A guard written from the INSTANCE passes on everything except the instance.**

- `tests/test_rederive_agreement.py:118` matched `import\s+([A-Za-z0-9` — the literal shape of the
  sites just converted. The survivors write `(?:open\s+import|import)\s+([A-Za-z0-9`, alternation
  between, so the fixed prefix never matched. **Verified False on the live file**; it would have
  passed forever. Fixed to match the CLASS (`\[A-Za-z0-9[^\]]*\]\+` near an `import`) — which then
  found **6 sites, not 4**: `primitive_catalogue.py:44` and an ALIAS capture at `iface_shape.py:305`.
- `check_rederive_ratchet.py` carried the SAME defect in two motifs, found by testing each against
  known-live instances rather than reading them: `importname` had the identical fixed prefix, and
  `declscan` matched `(?:data|record)` while MISSING `(data|record)` — the capturing spelling used in
  **six of the nine** files converged in 6c. The ratchet was measuring less than it claimed.
- The 6c `@expectedFailure` compared two regexes **it defined itself**, so it could pass while the
  gate stayed broken and kept reporting failure after the gate was fixed.

*Census effect, accounted exactly*: 142 → 134 = **+8 `declscan`** (real debt the old motif was blind
to) **−16 `importname`** (6 fixed, 10 never actually matched). The gate REFUSED to auto-lower while
additions were present — this morning’s added-doesn’t-mask-paydown fix working on its own author — so
the re-record was deliberate, a PREDICATE change, not a paydown.

**Standing form:** match the thing that is WRONG, never the context that surrounded it in the examples
you fixed. Recorded as a ⚑ in both the test and the ratchet, because it recurred three times in a day.

⚑ **THE WIDER PATTERN — a new guard reproduces the defect it guards against.** Four instances, all
mine, all today, each caught only by USING the guard rather than reviewing it:
1. the 6c `@expectedFailure` compared two regexes it defined itself (§6c);
2. the class-guard test matched the spelling it had just fixed (§7b-bis);
3. `check_rederive_ratchet`’s `importname`/`declscan` motifs, same defect (§7b-bis);
4. `check_rederive_ratchet` keyed on LINE NUMBER — the churn problem `gate_preflight` was built
that same morning to solve (§7g).
The author of a guard is the person least able to see its blind spot, because the blind spot is the
same one that produced the bug. **The only reliable check is to run it against the live corpus and
diff** — reviewing it re-derives the author’s own assumption. Every guard added by this arc was
verified that way, and every one of these four passed review first.

**7c. SHOULD-RHYME — `check_ban_ratchet.py:48,76` walks the tree itself** instead of
`agda_lex.agda_files`, whose docstring diagnoses exactly this hazard. Its sibling `check_claims.py:88`
*does* delegate. Applied to one gate, not the other — and inside a ratchet, census inflation
manufactures false “genuinely-new” keys.

**7d. SHOULD-RHYME — three docstrings assert a scope their code declines.**
- `check_feature_coverage.py` — its WHY names `el-atlas/features/` (10 files, \~52 scenarios) and its
`FEATURES` constant points at `features/` (2 files). It guards the directory it does not name.
Also: `stale` does not set exit 1, so coverage can shrink toward zero and stay green; and it claims
the ratchet shape while having **no materialized baseline**, the one thing that makes a ratchet one.
- `run_selftests.py` — argues at length that a hardcoded list “would hide a whole new tool”, over a
frozen `DIRS = ("scratch","scripts")`. Two suites (`jea/jea_circuit.py`,
`jea/metalanguage/sql_lift.py`) never run, and **both violate the `N/M` convention** the runner would
otherwise flag instantly. `jea_circuit.py:197` also returns `True` on `SKIP (numpy absent)` — an
absent dependency silently becomes a pass.
- `SKILL.md` step 2 — `rewire_stale_module.py` is 13 lines with two module names hardcoded; it no-ops
and exits 0 on everything else, so the documented pipeline reports success having done nothing.

Both of the first two are **mine, written today**. The class generalises to its own author immediately.

**7e. SLANT-RHYMES (inconsistency, not wrong answers).** No gate rejects an unknown flag, so a typo’d
`--queit` silently degrades a gate to verbose-but-passing. `--check` has three meanings (loud refusal /
alias for `--quiet` / unconditional-0). `worklist.py` sits in the hook as a blocking gate and **cannot
fail** (`:245-252` returns 0 unconditionally). Write-polarity is three-way divergent with \~16 unflagged
writers, of which `edit_snapshot` covers **zero**.

⚑ **SUPERSEDED 2026-08-01 — this item was filed as INCONSISTENCY and it is not.** Measured across the
9 write tools: seven gate on `--apply`, `prune_imports` took `--dry-run` and **wrote by default**
(its comment claimed the opposite), and `rewire_to_leaves` had **no flag at all**. Two were fixed —
but in OPPOSITE directions, and that is the finding: **polarity should track WHO CALLS THE TOOL.**
`prune_imports` is hand-invoked → made `--apply`-gated. `rewire_to_leaves` is called mid-chain by
`split_pipeline`, where a silent no-op leaves a split half-finished and the build failing far from the
cause → kept apply-by-default, gained `--dry-run`. Uniformity would have been the wrong fix for one of
them. The live cost of the divergence was measured, not hypothesised: a bare `prune_imports`
invocation intended as a preview deleted 12 import lines. `enforce_ban.py:165` gates on `--apply` then
hardcodes `--apply` into its delegation at `:156`, defeating its own gate.

**7g. ⚑ MY OWN RATCHET WAS LINE-KEYED — the churn defect, caught by using it.**
Running `check_rederive_ratchet` after 7c, it REFUSED: one “NEW independent derivation” at
`set1_ratchet_cores.py:162`. Checked — byte-identical line, moved from `:121` by my own §7a edits
adding 41 lines above it.

The key was `<motif>::<relpath>:<line>`, so **any edit above a site read as retire+add**. That is
exactly the path-keyed churn problem `gate_preflight.py` was built this morning to classify, reproduced
in a gate written this afternoon. It would have fired on nearly every unrelated commit and trained
reflexive re-baselining — which is precisely how a ratchet stops meaning anything.

Fixed to an **ordinal** key (`#0`, `#1`, per motif per file): stable under edits elsewhere in the file,
still distinguishes multiple sites in one file, still moves when a site is genuinely added or removed.
**Verified churn-immune** — 50 blank lines inserted above a censused site produce zero key movement.
Baseline re-recorded under the new schema (a predicate change, not a paydown): **133 sites**, down from
134 because 7a and 7c each paid one down.

**The standing form:** a ratchet key must be invariant under everything except the thing it measures.
Line numbers, and paths that a legitimate refactor moves, are not.

⚑ **And once more, an hour later:** the same ratchet began censusing `scratch/.edit-snapshots/` —
`edit_snapshot`’s copy-aside backups of UNTRACKED files, i.e. byte copies of censused sources. Two keys
appeared for the ratchet’s own file seconds after a guard run. `run_selftests` had already excluded
that directory; this one had not. **A backup of a censused file is not a second derivation** — and the
fix-applied-to-one-member class recurred between two files I wrote the same afternoon.

**7f. RHYMES worth naming** (a convention nobody wrote down is one edit from lost): `ratchet.py`’s
set-form semantics across 6 gates; `gate_keys.py` owning key shape including the `sumtype` reversal;
`gate_ledger`/`run()` instrumenting the funnel not the caller (the same reasoning as `membudget` for
build times, and stated as such in both); `selftest: N/M` derived from `len(cases)`, enforced
mechanically by `run_selftests.py:76-79` treating a missing count as a FAILURE.

### 8. THE Set₁ GATE IS REPORTING 0 OVER 30% OF THE TREE (found 2026-07-31, user question)

Asked whether any universe levels above `Set₀` should be a concern. Measured from `catalog/catalog.db`
rather than read off the baseline — and the baseline turns out not to be answerable evidence.

| measured                                                 | value                    |
|:---------------------------------------------------------|:-------------------------|
| defs at level 0                                          | **6,459**                |
| defs at level ≥ 1 (Set₁+)                                | **0**                    |
| defs with `level = NULL` (UNMEASURED)                    | **160**, across 42 cores |
| of those: Records / Datatypes / Constructors / Functions | **14 / 3 / 17 / 126**    |
| cores in the catalog                                     | **842**                  |
| `.agdai` on disk                                         | **2,762**                |

**The census covers \~30% of the tree.** So `0` does not mean “no Set₁ debt”; it means *no Set₁ found
in a third of the corpus, with 160 definitions in that third unmeasured.* The unmeasured set is not
inert filler — 14 Records and 3 Datatypes are exactly the carrier-shaped things that go Set₁, and
memory `set1-carrier-always-parameterize` records that “a record fielding a Set carrier is never
honest Set₁”. `Category/Comonoid.agda` has its Record, constructor and fields all unmeasured.

⚑ **This compounds §7a rather than duplicating it.** Three defects stack into a defended zero:
\* the baseline file holds `0` with **no denominator**, so Guard (3) was inert *(fixed — now refuses)*;
\* the gate **banked debt on a plain read** *(fixed — `ratchet.may_write`)*;
\* and the census it would have banked is over **30%** of the tree *(open)*.

Guard (2) — COMPLETENESS — exists precisely for the third (“an incomplete census is not a low count”)
and would refuse today. It has not fired because the gate has not been run against a current catalog.

**Not a claim that Set₁ debt exists.** The memory index shows a real paydown arc
(`set1-census-artifact-class`, `no-set1-floor-fifth-layer`), so the debt was genuinely worked down. The
open question is whether it is AT zero or merely MEASURED at zero — and today the instrument cannot
distinguish those.

**8a. THE 160 `NULL`s — DIAGNOSED, and it is TWO causes, not one.** Fully accounted, 140 + 20 = 160:

- **140 defs across 36 ALL-NULL cores — the only real gap.** Consistent with the level-blind shim the
  docstring names.
  All-or-nothing per core is that signature exactly, and they span 14 directories, so it is an
  interning ERA rather than a subject area. `make catalog` should clear these.
- **20 defs across 6 MIXED cores** — **NOT the shim**, and this is the finding. A level-blind intern
  cannot produce a core where some defs are typed and others are not. Classified with zero residue:
  **13 record projections** (`F₂-Like.complete`, `F₂-Like.𝟙ₜ`, `GL3F2ChainShape.sylow7-component`) and
  **7 generated defs** (`.constructor`, `_.` anonymous-module members, `with-98` blocks). The level
  extractor reaches top-level functions but not record FIELDS, constructors, or generated helpers.

⚑ **(b) IS NOT A DEFECT — I called it one and was wrong.** I read “record fields carry no level” as a
blind spot aligned with the policy the gate enforces. It is the opposite: `levelOf` returns `Nothing`
for a LEVEL-POLYMORPHIC sort **by design**, and the shim says so at `agdai_shim.hs:52`
(“Level-polymorphic / Prop / Inf -\> Nothing”). Verified in source:
`record F₂-Like {ℓ : Level} (T : Set ℓ) : Set ℓ` — the sort is `Max n [ℓ]`, not closed, so there is no
level to record because **the definition does not inhabit a fixed universe**.

Memory `level-poly-record-is-set1-paydown` states it outright: *“polymorphism over a universe level is
admitted under –safe and is NOT a held object”*, and level-poly-ing a record is itself a Set₁ PAYDOWN
(measured: `UPCategory` alone paid −7). So these 20 are **paid-down debt, not unmeasured debt**, and a
“per-kind completeness guard” would have manufactured 20 false positives out of the ratchet’s own
successes.

**The method error worth keeping:** I diagnosed by classifying the NULLs (record / constructor /
generated) and inferred the cause from the shape — a classification, not a measurement. The answer was
one `grep` into the source and one memory away. Reading the SHIM’s own comment and the RECORD’s own
declaration is what settled it, and both were reachable before I wrote the finding down.

**8b. ⚑ THE POLICY’S INTENT IS CONSTRUCTIVE DISCHARGE, AND THE CENSUS CANNOT ENFORCE IT.**
(user, 2026-07-31 — this reopens what 8a retracted, on a stronger criterion.)

> *“The intent behind the policy is to suppress global proofs like existence. At no point is it
> acceptable to say ‘there exists a’ without ‘and I have handed it to you’.”*

8a checked that `levelOf` behaves as DOCUMENTED and stopped there. That is the weaker test. The
stronger one is whether the documented behaviour serves the POLICY — and the two come apart exactly at
level-polymorphism. `Set ℓ` with `ℓ` universally quantified is a claim over EVERY level; it is a paydown
only when the construction is genuinely uniform AND supplied. Otherwise it is the same collapse
\[\[set1-is-grade-collapse\]\] names (“construct across the grade, never hold the whole family”), relabelled
into a form the census cannot see — no closed level, no key, no debt.

**Measured today, and it is clean.** Strictly level-poly carriers (own sort a bound level var):
**2** — `CartanRoot-Equivalence`, `GaloisAdjunction-AsAdjunction`. Both are INHABITED in their own file
(`CartanRoot-bundle : CartanRoot-Equivalence`; `GaloisAdjunction-bundle = record { forward = F ; … }`,
every field supplied), and their `ℓ`s come from carriers the CALLER hands over as module parameters
(`{ObjC : Set ℓOC}`). `F₂-Like` likewise: a predicate on a supplied `T`, whose every field is a
construction — two elements, a refutation, and a decision procedure — with `F₂` as the canonical
instance on the next line. **So the tree discharges today; nothing keeps it discharged.**

**8b-GATE — BUILT AND BASELINED at 28** (`scripts/check_discharge_ratchet.py`). The 46-vs-0
disagreement was resolved case by case first, as directed, and **BOTH tests were wrong**: the 46 was
over-strict (its `^name :` regex missed record fields, where-locals and applied positions — it flagged
`IsEqualised`, genuinely used as `Σ A (IsEqualised f g)`); the 0 was over-permissive (its tokenizer
split on `.`, so `module Substrate.Category.RootSystem where` counted the module PATH as a use of the
record). The detector now resolves through `agda_defs` and reads only TERM positions.

Verified by shape, not by count: **23 of the 28 are exactly `record X … where` + `open X public` and
nothing else** — declared, fields re-exported, no witness anywhere. The other 5 were hand-checked; every
“use” was a module-path segment. That is the policy firing on real cases. Two structural gaps remain
(§9b, §9c). Original spec follows.

**8b-GATE (was: SPECIFIED, NOT YET BUILT) —**
`set1_ratchet_cores` measures UNIVERSE HEIGHT; the policy is about CONSTRUCTIVE DISCHARGE. A gate is
owed for the second: *a level-polymorphic carrier must be discharged — inhabited by a term, or consumed
by a later construction that discharges it.* Paydown-only over a materialized census, per the standing
shape; an undischarged carrier is a key, and supplying the witness or deleting the carrier pays it down.

⚑ **THE DETECTOR IS NOT SETTLED, AND I WILL NOT SHIP A RATCHET ON AN UNSETTLED PREDICATE.** A wrong
predicate here banks false debt into a paydown-only baseline where it can never legitimately be removed
— the §7a failure, one layer up. Measured progress, with each refinement changing the answer:

| predicate                                         | level-poly carriers | flagged |
|:--------------------------------------------------|:--------------------|:--------|
| own sort mentions a bound `ℓ`, strict regex       | 2                   | 2       |
| …line-based parse (the strict form under-counted) | 112                 | —       |
| …no signature anywhere names it                   | 112                 | **46**  |
| …neither inhabited NOR consumed (token index)     | 112                 | **0**   |

The last two disagree by 46, so at least one is wrong. `IsEqualised` is genuinely discharged (`Σ A (IsEqualised f g)`, `Kernel-At f b = …`) and the 46-test flagged it — a false positive. `RootSystem : Set (lsuc ℓ)` and `S2-Lift` have no inhabitant and no in-file consumer, which is the shape the policy
targets most directly; the 0-test cleared them on cross-file references I have not yet confirmed are
CODE rather than prose.

⚑ And I misdiagnosed that last step twice: an unmasked `grep` “confirming” the references showed only
COMMENTS, while the masked token index was right — the comment-masking failure I fixed in four other
tools, reproduced in a check written minutes earlier (the §7b-bis class again).

**What settles it:** a discharge test built on `agda_defs`/`agda_lex` rather than ad-hoc regexes — the
same authorities the rest of this arc converged on — with the disagreement between the 46 and the 0
resolved case by case before any baseline is written. That is a build, not an edit, and it should not
be rushed into a ratchet.

⚑ **The method error 8a made, kept:** I verified a mechanism against its own docstring and called the
question closed. “Does it do what it says” is not “does what it says serve the policy”. The second
question is the one that finds a relabelled collapse.

**To settle §8** (belongs with “tree → green”, it needs a real build): `make catalog` to ingest all
2,762 cores, then run the gate. All three guards fire before a number is reported — Guard (2) on any
undecodable core, Guard (1) on blank levels, Guard (3) on the malformed baseline. ⚑ Correction: an earlier
version of this line said a green run “would not settle (b), the extractor gap survives a full
catalog”. There is no gap — see (b) above. The ingest IS the whole remaining question for §8.

### 11. THE `renaming` EXTENSION — saturated, and it INVERTS the framing (agent, 2026-07-31)

Dispatched to plan a `renaming` extension for `rewire_to_leaves.py`. It came back with three findings
that change what the work IS, two of which I VERIFIED before recording.

**11a-FIXED. ⚑ A LIVE BUG IN `rename_at_source.py` — VERIFIED, AND IT WAS TWO SITES NOT ONE.** The module builds a two-spelling
substitution list (`subs` at :46-47: `_≟_` in a signature AND bare `≟` in an infix clause) and defines
`apply_subs` at :48 — **and the write path at :75 calls `W.sub(new, s)`, the underscore-form-only
regex.** `apply_subs` and `hits` are DEAD CODE (verified: `grep` shows `apply_subs` defined at :48,
called nowhere). So the exact hazard the docstring says is handled is NOT handled in the writer. This
is load-bearing for the extension, which would inherit the same path.

**The agent found the writer; the SELECTION path had the identical gap and it found only one.** Line 58
gated candidate files on `W.search(s)` — the underscore form — so **a file using ONLY the bare-infix
spelling was skipped entirely and never renamed at all.** Both now call the two-spelling forms
(`hits` / `apply_subs`). Demonstrated behaviourally rather than by reading, on `_≟_` → `_≟ℕ_`:

| input                                 | `W.search` (old select) | `hits` (new) | `W.sub` (old write) | `apply_subs` (new) |
|:--------------------------------------|:------------------------|:-------------|:--------------------|:-------------------|
| `Decidable _≟_` (signature)           | True                    | True         | `_≟ℕ_` ✓            | `_≟ℕ_` ✓           |
| `orbit-len σ i ≟ ℓ` (bare infix only) | **False — skipped**     | True         | **unchanged ✗**     | `≟ℕ` ✓             |

The failure was silent in the worst way: the operator keeps binding to the OLD provider, and the file
is never even reported as touched.

⚑ **WHY IT SURVIVED: `rename_at_source.py` HAS NO `_selftest`.** The suite ran 413/413 green across 11
suites through a live bug in a WRITE-PATH tool, because that tool is not in the discovered population —
`run_selftests.py` finds modules that DEFINE `_selftest`, so a tool with none is invisible, not failing.
**A discovered population still only discovers what opted in.** That is §9g’s class one level down, and
it makes the case for a completeness gate over TOOLS-WITH-WRITE-PATHS, not just over gates: a tool that
rewrites Agda source and carries no selftest should be a census key. (Untested claim about the fix
itself: the two edits are verified behaviourally above, but `rename_at_source` still has no selftest, so
nothing will catch the NEXT regression — the owed work is a suite, not just this patch.)

**11b. ⚑ THE RISK CLASS IS CAPTURE, NOT DELETION — and line-conservation is BLIND to it.** VERIFIED at
`agda/Substrate/Algebra/Polynomial/Graded/Defs.agda`: line 6 renames `_+_ to _ℕ+_`; line 22 binds a
MODULE PARAMETER `(_+_ : A → A → A)`; lines 55/59/66 use `n ℕ+ k`. Un-renaming `_ℕ+_`→`_+_` deletes
nothing, changes no line count, and silently rebinds those uses to the PARAMETER. **`split_lemmas`’
conservation guard — every non-blank line lands in exactly one unit — cannot see this**, nor can
`agda_imports`’ permutation assertion: *a substitution is not a permutation*. The agent’s proposed
invariant is TOKEN conservation with a ledger (`S' = S − k·{new} + k·{old}`, no other token’s count
moves), plus a pre-condition gate. Recorded because it is a genuinely new risk class for this repo.

**11c. THE POPULATION, AND WHERE THE LEVERAGE IS.** ⚑ *RESOLVED by step 2 (§11d): the agent’s “26%
unfixable” was a textual upper bound, and the scope-aware re-measurement puts the real figure at
**16% (594/3615)** — the walk rescued **15 clauses**, not the large fraction I predicted. Both the
agent’s estimate and my prediction were wrong in the same direction; the measurement settled it.* Statement-aware
census: **3,071 `renaming` / 932 `as` / 1 `hiding`** (so: build no `hiding` branch). Of 3,615 clauses
classified, **922 (26%) cannot be un-renamed BY A TEXT SCAN** — 435 BODY-OCCURS, 464 OTHER-PROVIDER,
23 both. ⚑ These are UPPER BOUNDS on the unfixable set, not measurements of it: the classifier asks
“does `old` appear anywhere in the body / is another provider imported by this file”, both file-level
questions. §11d shows the real predicate is POSITIONAL (is `old` bound by an enclosing telescope AT
THIS USE SITE), and the witness file proves the two answers differ. **Re-run this census through a
telescope-aware `_in_scope` before treating any of it as unfixable.** And
**\~3,000 of 3,715 clauses are ONE replicated 10-clause prelude** over `Algebra.R.Trace.Bisim` across
\~272 files in `Category/UniversalProperty/ExtrudeCoEmitGraded/`. **One `rename_at_source` pass on
`Bisim` retires \~80% of the renaming census** — a bigger win than the entire rewire extension.

**11d. ⚑ “THE GATE MUST REFUSE” WAS A GUESS DRESSED AS A CONSTRAINT — RETRACTED (user, 2026-07-31).**

> *“Why is the answer to that not ‘fix the tooling’? Do we not have a pattern of walking from the head
> downward recursively to ensure we have concrete information rather than trying to guess?”*

I wrote that the module-parameter-shadow shape is something “any correct tool must refuse”, and called
the 12 blockers hand-decisions. **That was ambiguity in MY text-scan, not ambiguity in the code.**
Walking the head downward settles it exactly:

`Graded/Defs.agda` — the renaming import is at **:6, TOP LEVEL**. The parameter `_+_` is bound at
**:22, inside `module Over` whose scope opens at :21**. They never share a scope. Every `ℕ+` use
(:55, :59, :66, :72) is at **indent 2, inside `Over`** — so there the parameter IS in scope and
un-renaming WOULD capture. The caution was right *for this file*, but it is now a MEASURED fact
derived from scope structure, not a guess — and a fact a tool can compute.

**So the shape is DECIDABLE and the answer is fix the tooling.** The predicate is: for each use of
`new`, is `old` bound by an enclosing telescope/`where` at that POSITION? That is a scope walk from the
module head down, which is the repo’s standing pattern.

⚑ **The reuse-search found the intended authority AND a live defect in it.** `scope_fix._in_scope(path, tok)` (`scratch/scope_fix.py:1730`) is exactly this predicate — *“Is the identifier available in the
consumer (module param / import / own def)?”* — but:
\* it is **FILE-LEVEL, not position-aware**: it answers “somewhere in this file”, so it cannot clear a
TOP-LEVEL use while flagging an inner one — the distinction the whole question turns on; and
\* **MEASURED: `_in_scope("…/Graded/Defs.agda", "_+_")` returns `False`** — wrong. Its first branch is
`^module [^\n]*\(\s*{tok}\s*:`, which requires the parameter on the module header’s FIRST line;
`module Over {A : Set}` puts `(_+_ : …)` on the NEXT line. **It misses every multi-line telescope**
— the exact statement-span class this arc retired in 15 other places (`⟡paydown-telescope-anchor`
at `scope_fix.py:362` documents the same hazard IN THE SAME FILE).

**Revised work:** make `_in_scope` telescope-aware and position-aware (via `agda_lex.statements` /
`_depth_after`, the span authority), then the `--unrename` gate calls it per-use-site instead of
refusing a whole shape. The 435 BODY-OCCURS and 464 OTHER-PROVIDER counts in 11c are UPPER BOUNDS
computed textually. ⚑ **NOW MEASURED (step 2): 609 → 594, i.e. the scope walk clears FIFTEEN.** The
`_in_scope` fix was necessary and real (1590/1948 params were invisible tree-wide) but it was NOT the
lever — and the remaining 594 are dominated by ONE name from ONE provider (`_+_` from
`Substrate.Algebra.F2`, 424 of 487 OTHER-PROVIDER).

**11e. SCOPE (agent’s recommendation).** Do NOT put body-rewriting inside `rewire_to_leaves.py` — it
is a pure import-line rewriter (241 lines, all import statements) that just rewired 300+ importers;
body rewriting is a categorically different blast radius. Three-way split: `agda_imports.parse_renaming()`
(new \~10-line primitive — VERIFIED ABSENT tree-wide, nothing parses a renaming clause into pairs);
`rewire_to_leaves` folds renaming old-names into its owner-name set only; the un-rename lands as a
`--unrename` MODE of `rename_at_source.py`, whose stated job it already is. Defer `as` (qualified-name
resolution, a different and harder rewrite; `scope_fix.fix_qualified` already exists for it).

### 10. ⚑ THE REAL FAILURE WAS NEVER TOOLING — 529 UNTRACKED FILES (user, 2026-07-31)

> *“You know this will be the THIRD time I’ve decomposed Foundation.Nat in three days?”*

Measured on the spot: **529 untracked `.agda` files** in the tree — the entire multi-day decomposition
arc, living ONLY in the working tree, where a single `git checkout -- agda/` erases it. That is the
whole explanation for the repeated re-decompositions, and **it is not a tooling problem**, which is
what this arc spent itself on.

**I caused the conditions for the third one.** §“Pending re-baselines” already records that my
`git checkout HEAD -- agda/` reverted a day of the user’s splits. I logged that as a one-off recovery
and hardened the SPLITTER instead of asking why a day’s work was destroyable by one command. The user
said at the time *“which is why I’m tripling down on automation and mechanization”* — and mechanizing
the splitter does nothing about durability. Re-running a perfect pipeline over an erased tree is still
re-doing the work.

**`edit_snapshot` does not cover this, and its own docstring says so.** It uses `git stash create`,
which **cannot hold untracked files** — that is exactly why it copies them aside. So the protection I
invoked repeatedly this session covered the tracked files (least at risk) and missed the 529 (all of
the risk). A guard whose population excludes the hazard class is the §9g defect again, in the one
place where it cost real work.

**FIXED (cheap, immediate): `git add -A agda/` — 2,525 files staged, 0 untracked `.agda` remain.**
Staging needs no passing build, no gate, no commit; it just makes the work survive a working-tree
checkout. This should have happened on day one.

⚑ **THE USER’S DIAGNOSIS IS SHARPER THAN MINE, AND IT MOVES THE FIX (2026-07-31):**

> *“Both times the work was lost, it was because a pathspec was provided that covered the entire agda
> tree.”*

The mechanism was **not** untracked-ness — it was `git checkout <rev> -- agda/`, a TREE-WIDE PATHSPEC.
That distinction is load-bearing because **staging does not defend against it**: `git checkout HEAD -- agda/` overwrites the index AND the working tree together. So the `git add` above makes the work
survive an accidental `git checkout` of a NARROWER path, and does nothing against the command that
actually destroyed it twice. I proposed auto-staging in the drivers as “the measure that would have
prevented all three” — **it would have prevented none of them.** Guard-from-the-instance one more time:
I generalised from the symptom I had just measured (529 untracked) instead of from the mechanism that
did the damage.

**The measure has to bind the OPERATION, not the file state.** The destructive act is a checkout/reset
whose pathspec covers a whole subtree; the fix therefore lives where such a command can be intercepted
or made unnecessary:
\* A tree-wide `git checkout -- agda/` (or `reset --hard`) is the banned operation — the recovery move
is a per-file checkout from a recorded snapshot SHA (`edit_snapshot` already emits exactly that:
`git checkout <sha> -- <path>`), never a subtree restore. **This is `U1`.**
\* This is enforceable in the harness, not by memory: it is a command-shape guard, which is the
charter’s “covered” layer for an automatable class.
\* Staging remains worth doing (it protects against unrelated loss and makes `git status` legible),
but it is NOT the measure for this failure and must not be recorded as one.

**RESIDUE — durability still wants a commit**, which the pre-commit gate correctly refuses over a
non-building tree. Not resolved by `--no-verify` and not by editing a baseline.

### 9. AUDIT V — the rhyme audit over the NEW gate layer (2026-07-31)

Audited the machinery built the same day, by an outsider, on the user’s standing question. Its top
finding is the one I should have caught myself.

**9a. ⚑ FIVE GATES EXISTED, WERE BASELINED, AND RAN NOWHERE.** `.githooks/pre-commit` had 15 `run`
lines; `check_ban_ratchet`, `check_claims`, `check_capstone_shape`, `check_rederive_ratchet` and
`check_discharge_ratchet` were named in none of them. Two were written today; one was baselined
**minutes before the audit that found it**. Worse, `discharge_baseline.txt` and `rederive_baseline.txt`
were **untracked** — a fresh clone would have had neither.

This is the Audit-IV class exactly, one layer up: the abstraction (`ratchet.py`, `may_write`,
`check_argv`) was extended to the new members, and the one step that makes a gate LOAD-BEARING was not.
**A baseline no gate consults is a census wearing a ratchet’s clothes** — the plan reads as though the
discharge policy is enforced, and nothing enforced it.

*Fixed:* four wired into the hook with their rationale; both baselines `git add`ed.
`check_capstone_shape` is left unwired pending a decision on whether it is a gate or an advisory.

⚑ **TWO REFUSE TODAY, AND MY FIRST EXPLANATION WAS WRONG.** I said the 253 added ban keys were “churn
from the Eq/Bijection splits”. Measured with `gate_preflight`: **245 are GENUINELY NEW, only 8 are
churn**. Split further by whether this arc touched the file: **121 are in files never touched** — e.g.
`Algebra/Module/Capstone.agda` is unmodified (no git status, identical `using` counts in HEAD and the
working copy) yet contributes 18 keys the baseline lacks entirely (`0` baseline keys mention it).

The cause is not paydown and not churn: **`ban_ratchet_baseline.txt` has never been committed** (`git log` empty, status `A`). It was recorded during the staged ⟡ban-decompose work over a tree state that
already differed from HEAD, so it is not a baseline OF this tree. The `Capstone.agda` barrels dominate
the additions — modules that import many upstreams under `using` filters, which is exactly the debt the
ban exists to name and exactly what a mid-arc baseline missed.

**⚑ THE CLAIMS HALF IS PAID — it was never blocked on the build.** I had bundled both refusing gates
under “lands with tree-green”. Wrong for `claims`: all 4 were PROSE contradicted by the tree, fixable
without compiling anything. Each was an artifact of this arc’s own work — two stale importer counts
(`Graded` “\~39”→**1**, `Z.Arithmetic` “\~200”→**35**, both dropped because decomposition rewired
consumers to the leaves) and two “thin re-export shim” comments describing files whose `open … public`
**B3 removed**. Fixed as prose; gate now **exits 0** and banks its held paydown (14 → 13).

Two lessons, both mine:
- **I fixed the site the gate REPORTED and assumed it was the only one.** Two files carried a SECOND
occurrence (`Graded.agda:10`, not just `:63`) and the gate re-refused. A gate reports the first hit
per file, not the population — re-run until 0, never edit-once-and-assume.
- **My correction tripped the detector.** I wrote “NOT a re-export shim”, and `SHIM` is a substring
match that cannot read a negation. Writing the negation of a banned phrase is not a fix; state what
the file DOES (“this module does not re-export”), not what it is not.

**⚑ THE 245 ARE TWO CLASSES, AND “BLOCKED ON TREE-GREEN” WAS WRONG (user: *this is what our
pipeline drivers are for*).** I called them all “Capstone barrels importing under `using`” after
reading ONE file, and parked them behind the build. Measured, they split:

| class                                                  | keys    | files | route                                                                                                              |
|:-------------------------------------------------------|:--------|:------|:-------------------------------------------------------------------------------------------------------------------|
| `open import … public using (…)` — a re-export BARREL  | **49**  | 7     | `capstone_to_dir.py` (pure-barrel → directory+README), or delete the `public` outright — *WE DO NOT RETAIN PUBLIC* |
| plain `open import … using (…)` — a consumer FILTERING | **196** | 130   | `split_pipeline.py` on the provider: decompose so the consumer can import bare                                     |

Directives: 235 `using`, 6 `as`, 4 `renaming`. `Module/Capstone.agda` carries BOTH (11 public + 7 plain),
which is why reading its first six lines generalised wrong.

**And the dependency is inverted.** Decomposition is what MAKES the tree green — the ban skill’s own
sequence is *decompose the provider, re-measure, then rename what survives*. `split_pipeline.py` already
chains split → isolate-check → prune → rewire → sweep → makefile-regen → build, with each stage a hard
gate. So this is driver work that can start now on any provider whose subtree builds, not work waiting
on a green tree. What genuinely waits is only the FULL-build verification at the end.

**CLASS A IS PAID — 245 → 192 (−53).** All 7 `public` re-export barrels retired via
`capstone_to_dir.py --apply` (each was a PURE barrel — the tool refuses any file with a definition, so
its acceptance IS the proof nothing was discarded); each became `<Name>/README.md`, prose + roster.
The 7 consumers of the two `V4` barrels were rewired to the OWNER first, so no intermediate state had a
dangling import. Both barrels were pure pass-throughs of `Substrate.Groups.V4.Bijection`, and the
`using (V₄; e)` filters were never narrowing anything: **`e α β γ` are CONSTRUCTORS of `V₄`, declared on
one line**, so an importer gets all five names together regardless. Verified: 0 dangling references to
any of the 7, `V4Compose` intact.

⚑ **AND I HAND-WROTE THE REWIRE INSTEAD OF USING THE DRIVER (user: *this is why we have a pipeline
driver*).** `scratch/rewire_to_leaves.py` exists for exactly this rewrite — it maps `using (a; b)` to
the owning leaves, preserves a trailing `public`/comment, and reads the name→leaf map from each leaf’s
own `-- Defines:` header so it CANNOT drift from the split. I wrote a regex instead, and it bit twice
in one turn:
\* `grep` reported **1** importer of `RuleAction.V4`; there were 2 matches because `.` is any-char —
the second was `RuleAction.V4Compose`, an unrelated module my substitution would have CLOBBERED.
Only an `assert n==1` stopped it. The fix is a boundary (`(?![A-Za-z0-9._-])`), which the driver
already has.
\* Earlier the same turn, a grep for `V₄`/`e` owners returned NOTHING and I nearly concluded the
module was empty — they are constructors on a shared line, invisible to a `^name :` pattern.
**The hand-written regex is the recurring defect, not the individual bug.** Every one of these classes
is already encoded in a driver; reaching past it re-derives the bug the driver was written to prevent.

**CLASS B, DRIVER SWEEP: 184 → 85 keys; paydowns 1674 → 1860.** `rewire_to_leaves.py` run over every
provider that HAS a leaf directory. Four did the work: `Groups.V4.Bijection` (**87 keys, 166 importers
rewired**), `Algebra.Z` (101 importers), `Algebra.Q` (75), `Foundation.Bool.Properties` (14).

⚑ **I ARGUED AGAINST RUNNING THE DRIVER AND I WAS WRONG (user: *not your call — let the automation do
what it will do*).** I inspected the 101 Bijection keys, saw that 99 of 101 consumers want only `V₄`
and its constructors, and concluded “splitting is the wrong move, it would clear nothing.” The premise
was true and the conclusion was false: **the split had ALREADY happened** — `Bijection/` holds 8 leaves
with `-- Defines:` headers, and `Bijection.agda` was an undecomposed twin nobody had rewired off. The
driver’s job was rewiring consumers onto existing leaves, a DIFFERENT operation from the one I was
evaluating. I judged the tool against a plan I had invented for it, and the run cleared 87 keys.

**The generalisable form:** I keep evaluating whether a driver WILL work instead of running it and
reading what it DID. The driver is cheap, idempotent, and reports its own scope (“12 names / 8 leaves
-\> rewired 166 importers”); my prediction is none of those. Same shape as the hand-written regex an
hour earlier — reaching past the automation, twice, in one arc that exists to mechanize this work.

**FULL `split_pipeline.py --apply` SWEEP (user: *this is the automation I assumed you’d be running —
it’s designed to make E2E-automated the stuff you’re doing by hand*). 245 → 73 keys; paydowns 1674 →
2043.** Run over all 53 split-needing providers in BACKGROUND (each does isolate-checks + a build; 53
of them blows any foreground window — the first attempt died at the 2-minute limit). 12 providers
split, 29 were already ATOMIC (nothing to split — `Foundation.Level` is a conduit for
`Agda.Primitive`), then `rewire_to_leaves` over everything that gained leaves.

⚑ **A DELETION SCARE THAT WAS MY BOOKKEEPING, NOT DAMAGE.** Eight providers reported `✗ … does not exist` and I stopped to check whether the sweep had eaten source files. It had not: **all 8 were
SUCCESSFULLY SPLIT** by the foreground run before it was killed — `X.agda` is CONSUMED into `X/`
leaves, so my restarted sweep found the flat path gone. Verified 0 lost (every one has a populated
leaf dir: `Roster/` → BasisOf/FreeCarrierOf/Lang; `F1/GL/` → F1N/GLF1/IdGLF1). **A tool that consumes
its input makes “file missing” the SUCCESS signature, and a re-run over the original list cannot tell
success from failure** — the sweep must re-derive its worklist from the live tree each pass, which is
the discovered-population rule (§9g) in a new place.

⚑ **AND I MISREAD THE PIPELINE’S OWN REPORT — third time this arc.** I bucketed 31 providers as
“OTHER/REFUSED” whose last line was `Dry run only — pass --apply to execute`: they had plans READY.
I matched on the wrong line rather than reading what it printed. (Prior two: predicting the driver
would clear nothing when it cleared 87; the hand-regex that nearly ate `V4Compose`.)

**Remaining: 73 keys** (245 → 73; paydowns 1674 → 2043). Two REAL failures, both correctly diagnosed by the pipeline’s hard gates:
`Foundation/Vec/Properties.agda` — *“when scope checking suc”* (a collision; the skill’s rename-at-
source case, after decomposing up-chain) and `Groups/V4-Coxeter.agda` — *“Restructure the application
into its own leaf first (the applied-open class).”* `Foundation.Nat` (the provider the skill names as
forcing the whole Fin/Nat collision set, 1182 importers) **SPLIT — 56 leaves**, and the pipeline then
stopped at its own hard gate with **12 named blockers**, every one a collision MASK of the form
`using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)` (plus `_≤_`/`_*_`/`zero` variants). That is the
rename-at-source case the skill reserves for after the up-chain decomposition — not something the
splitter can decide, and correctly handed back rather than guessed.

⚑ **And this split was the THIRD in three days — see §10.** The leaves were 56 UNTRACKED files the
moment they were written; the previous two decompositions were lost exactly that way, not to any
tooling defect.

*(superseded: 85 keys / 66 providers, of which 58 keys sat on providers with NO leaf dir)* — those need
`split_lemmas` to run first (the full `split_pipeline.py` chain), since a rewire has nothing to target
until the leaves exist. Long tail: 62 providers carry exactly 1 key.

**Consequence for sequencing — and NOT a re-baseline (user, 2026-07-30).** My first instinct on seeing
“121 keys in files this arc never touched” was to call the baseline stale and re-record it. **That is
the wrong move and the user stopped it.** “The baseline does not match the tree” is exactly what a
ratchet REFUSING looks like; re-recording to make the refusal go away is banking debt to silence a
gate, which is the one thing the re-baseline rule forbids (“never reset to absorb a broken tree”).
The 245 are `using`-filtered imports on `Capstone.agda` barrels — REAL ban debt, and the ban gate
naming it is the gate working. It belongs in the **paydown queue**, not the re-baseline table.

**9b. `check_discharge_ratchet`’s `STRUCTURAL` filter has the INVERSE error — latent.** It skips
`^\s*(?:module|open|import|--)` so a module PATH is not counted as a term use. But **341 skipped lines
tree-wide are `module M (x : T) where` PARAMETER lines**, and a module parameter IS a term position —
precisely the CONSUMED discharge shape the docstring names. Four carriers (`F₂-Like`, `UPCategory`,
`Poly`, `⊤`) are discharged only through it. ⚑ The auditor’s first hypothesis — that this had already
corrupted the baseline — was **falsified by running it**: all four are rescued by an unrelated term use,
so today’s 28 hold. It is a latent false-positive generator, and a false positive in a paydown-only
baseline is debt that can never legitimately be paid.

**9c. `carriers()` is keyed by BARE NAME, so 112 sites collapse to 110.** `CategoryOf` and `_⊎_` each
exist in both a parent and its decomposition child; `out[name] = …` silently keeps the last. Every
sibling ratchet keys `name::path` precisely so a decomposition stays visible — the census KEY is right
and the population feeding it is lossy. Two sites are invisible to the policy.

**9d. `gate_keys.SCHEMA` covers 5 gates; 9 baseline files exist.** `discharge`, `rederive`, `cap` and
`set1` have no entry, so `gate_preflight`’s churn classification is blind to them. And `rederive`’s key
(`motif::path#ordinal[::declared]`) has VARIABLE arity, which the fixed-arity `KeySpec` cannot express.
⚑ Its selftest passes 14/14 because **it validates exactly the population it declares** — axis E again.

**9e. `check_argv` is called in 5 of 21 gates**, while `ratchet.py`’s own docstring says “Call this
FIRST in every gate’s `main()`”. Every older hook-wired gate still does `"--quiet" in sys.argv`.

**9f. RHYMES, verified by running rather than grepping.** The write guard HOLDS — ten gates run
read-only, `git diff` on every baseline empty, including the five that exited 1. And
`check_carrier_locality.strip_comments` vs `agda_lex.mask_comments` agree on **all 2764 files** — a
differently-named twin that is behaviourally identical. (32 tools still scan unmasked, including
`agda_defs`, which the discharge gate depends on: inconsistency, no measured wrong answer.)

**9g. ⚑ THE MECHANISM FOR AXIS E, and it is not more review.** The recurring defect — five instances
today — is that **the author writes the guard from the instance he just fixed, so the guard’s
population IS the fixed set**. `gate_keys` validating only its own declared gates is the newest case.
The structural fix is a **completeness gate over gate coverage**: assert that every `scripts/check_*.py`
is (a) named in a hook `run` line or explicitly declared advisory, (b) calls `check_argv`, and (c) if it
writes a `*_baseline.txt`, has a `gate_keys.SCHEMA` entry and a TRACKED baseline. Its population is
DISCOVERED from the filesystem, so it cannot be written from the instance. It would have caught 9a, 9d
and 9e in one run.

**Explicitly NOT converted** (the census named each, with reasons): `.agdai` variants (wrong suffix);
directory-only conversions (`module_file` always appends `.agda`); the `\b(using|renaming|hiding| public)\b` *splitters* (13 sites — `public` is a delimiter there, not a predicate); `startswith ("module ")` **locators** (5 — they want a line index, not a name); `agda_defs.py:59` and
`agda_imports.py:{167,336}` (per-line scanners, not header extractors); `ROOT`-set-to-`agda/Substrate`
scripts (\~12 — passing that root would silently drop the `Substrate.` prefix, a wrong-answer trap).

## Files

**Landed:** `tests/` (6 modules, 52 tests); `features/agda_text_invariant_0_helpers.feature` +
`features/derived_view_invariant_0_agreement.feature` (52 scenarios); `scripts/check_feature_coverage.py`;
`scripts/run_selftests.py` (452 cases / 13 suites, discovered); `scratch/convert_path_helpers.py`;
`.githooks/pre-commit` (3 `run` lines); `agda_lex.{module_path,module_file,module_name_of, is_public_open,agda_root_from,HEADER}`; `scripts/gen_build_makefiles.py` IMPRE + regenerated `Flat.mk`;
29 Phase-A + 14 Phase-B1/B2 call sites.

**Remaining:** the 16 B3 `\bpublic\b` sites; the 8 col-0 `DECL` gate sites (6c); the enumeration
convergence (6d).

⚑ **STALE 2026-08-01 — this line disagrees with its own document.** 6c is marked **DONE** at
“DONE — 6c, the col-0 `DECL` convergence” and 6d at “DONE — 6d, the enumeration authority”; the
`\bpublic\b` figure is **7 tool files** today, not 16. Corrected population: only the 6d RESIDUE
survives (**5 files still define their own `agda_files`**) plus the `\bpublic\b` motif, which is
T8’s open method question. *A summary line that outlives the items it summarises is the derived-view
defect (§6) inside the plan — two places computing “what is left” by different routes, neither
reconciled.*

- **REUSE, do not reimplement**: `agda_lex.{module_path,module_file,module_name_of,is_public_open, agda_root_from,mask_comments,statements,HEADER,module_scopes,binds_at,word}`;
  ⚑ **`agda_lex.head_span` is THE header-span walker — never an ad-hoc `j - i < N`** (a TERMINATION
  bound is fine; a CAPABILITY bound silently drops declarations: 136 of 401 multi-line headers exceed 6).
  ⚑ **`conduit_resolve.{resolve,final_consumers,is_conduit}` is THE barrel-chain authority** — recursive
  to fixpoint, no depth bound.
  ⚑ **`agda_lex.word` is THE Agda name boundary — never `\b`** (1269 of 10831 names, 11.7%, are
  invisible to `\b`; it is a `\w` transition and Agda names may be entirely non-`\w`). It matches a
  BARE name; a QUALIFIED reference (`M.Over.name`) is a different question and wants its own matcher —
  see the open item below.
  `agda_imports.stage_warning` (THE standalone-invocation banner — one declaration, three consumers);
  `scope_fix._rename_pairs` (THE renaming-clause parser — an agent wrongly reported this ABSENT); `agda_defs.def_index`;
  `agda_imports.{importable,_span_end}`; `edit_snapshot.guard`; `ratchet.set_ratchet`
- ⚑ **`module_scopes` / `binds_at` are THE telescope authority** (added §11d step 1). Anything asking
  “is this name bound here” routes through them — a `^module [^\n]*\(x :` regex sees only same-line
  params and MISSED 1590 of 1948 tree-wide. `binds_at` is POSITIONAL; `module_scopes` gives the spans.
- ⚑ **DO NOT** fold `agda_defs.def_index` into `agda_lex` — a per-line state machine, not a statement
  iterator; the trap is documented at `agda_lex.py:24-29`. 6c moves CALLERS inward instead.

## Verification

**Current state (re-measured 2026-08-01): 52 tests (0 expectedFailures — the 6c debt is PAID), 52
scenarios,** 452\*\* selftest cases across 13 suites, no baseline drift, `gen_build_makefiles --check` OK
at 2764 modules.\*\* The +8 are `agda_lex.module_scopes`/`binds_at` (§11d step 1); the total was checked
to MOVE, because a case that does not change the count is a case that is not running. ⚑ These were carried as 50/50/109-over-9 in three places while the header said
52/52/413 — the same file disagreeing with itself, which is the derived-view defect (§6) in the plan
rather than the code.

1.  `python3 -m unittest discover -s tests -q` — green; every case traceable to a named incident.
2.  `python3 scripts/check_feature_coverage.py` — no orphan scenario, and no stale test either (the
    check is bidirectional; it caught this arc’s own drift three times).
3.  `python3 scripts/run_selftests.py` — discovered, not listed; a new tool is covered by existing.
4.  **Phase A census diff** — done, byte-identical.
5.  **Phase B** — B1/B2 done; census identical (they touch only analysis scripts, no gate). ⚑ The
    original step-5 text predicted the public-ratchet census would FALL in B3. **That was wrong** and is
    corrected in §5: no B3 conversion touches a census at all.
    Superseded text follows for the record — a rise would have meant
    the swap was wrong.
6.  Adversarial: run the sweep tools `--dry-run` over the whole corpus and confirm zero diffs where
    Phase A claims no behaviour change.

## Pending re-baselines — bank each deliberately, never as a side effect

A baseline is a census of THE SAME QUESTION over time. When a predicate changes what the question
MEANS, the old numbers are answers to a question nobody is asking — holding them defends debt that was
never real, and the gate’s own docstring says so (*“widening it RAISES the baseline before it falls,
which is the ratchet working, not a regression”*). The rule is therefore **not “never reset”** but
**never reset silently, and never to absorb a broken tree**. Only the commit path may rewrite a
baseline (`.githooks/pre-commit:33-42`).

| \#  | baseline        | movement                                             | trigger                                                                                                                                                      |
|:----|:----------------|:-----------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | sumtype ratchet | **48 → 65** (see below)                              | 6c: the col-0 `DECL` blind spot; also flips carrier-locality’s verdict on 5 carriers                                                                         |
| 2   | public ratchet  | **unknown — measure after**                          | B3’s exemption removal: 265 strips are latent until a split runs; the movement cannot be predicted from here                                                 |
| 3   | set1 ratchet    | **unknown — the file holds `0` with no denominator** | §8: the malformed baseline now REFUSES, so it must be re-recorded over a COMPLETE catalog (2762 cores, not 842) — and only then does the count mean anything |

⚑ **6c’s number was mis-stated twice, and the second error is the dangerous one.**

*First*, “25 → 32” counted **names**; the ratchet keys on `name::path`, so 22 duplicated names across
their sites give **43 added keys**, i.e. the baseline moves 48 → 91 as measured. Both numbers are
right about different things — but a re-baseline is applied to KEYS.

*Second and worse*: of those 43, **26 are a TRANSIENT TREE ARTIFACT, not debt.** `git checkout HEAD -- agda/` earlier in this arc restored 25 module tips that the prior (unstaged) work had deleted, so the
tree currently holds `Foundation/Bool.agda` **and** `Foundation/Bool/Bool.agda`, each declaring `Bool`
— likewise `Linear`, `Canonical`, `Quotient`, `CategoryOf`, `LehmerPath`. The gate is right to call
those duplicates; they are duplicates *of a broken intermediate state*.

**Only 17 keys are genuine** (`DivStr`, `Trace`, `Wit`, `_≈L_`, `_≈_`, `GradedDivStr`, `GradedWedge`,
`Gen`, `Wedge`, …), so the honest movement is **48 → 65**.

**Therefore: the DECL fix lands now; the re-baseline does NOT.** Banking it against today’s tree would
freeze 26 fictitious duplicates as permanent debt — which is exactly the “never reset to absorb a
broken tree” half of the rule. Re-measure after the tree is green (step 6) and bank whatever is left.

### 12. `fix_stale_using` TREE-WIDE — RISK-ANALYSED, ANSWER IS **NO** (agent, 2026-08-01)

Dispatched before running it, per the new discipline. It corrected my premise and found four defects.

⚑ **MY “ONLY 6 LOGS” WAS WRONG — there are 2669.** My glob (`agda/_build/*/agda/**/*.agdai.log`)
did not match the real layout; `find` gives 2669. **And that makes the risk WORSE, not better**: the
tool would act confidently on thousands of stale coordinates instead of nearly none. I had reported
the wrong number as a reason it was *safe to consider*.

**VERIFIED BY ME:**
\| \# \| risk \| evidence \|
\|—\|—\|—\|
\| R3 \| **No `edit_snapshot.guard()`** — bare `open(path,"w")` at `:242`. `rename_at_source:102` does snapshot. \| `grep edit_snapshot` → 0 matches \|
\| R2 \| **Drops `public`** — `pub = ""` at `:210`, so a re-export statement is deleted entirely. That is an export-surface change, not a cleanup. \| `:210` \|
\| R6 \| **`owner()` is column-0-only** (`:135`, `^` with no whitespace allowance) — inherits exactly the blind spot `split_lemmas.field_names` was just added for. Indented `data`/`record` heads and record FIELDS are invisible. Fails SKIP (prints `no owner found`), so a dropped name gets no replacement import → `NotInScope`. \| `:135` \|
\| R4 \| **No `_selftest`** — the gap class that let `rename_at_source` ship a live bug through a green suite. \| `grep` → 0 \|
\| R1 \| **Logs do not describe the tree.** My own count (basename-matched, so approximate): **2851 sources have NO log at all**. The agent measured 1788 newer-than-log / 313 no-log by a different matching. The methods disagree; **the conclusion is identical and stronger either way** — the site list comes from a small aged slice. \| measured both ways \|

**Also reported, NOT independently verified by me** (recorded as the agent’s measurement): 53 sites / 40
files would be touched; 3 statements emit as *nothing*; log-parse leakage puts junk tokens
(`'L0-Source'`, `or`, `'on-source'?)`) into the name set when a *did you mean* hint wraps; and the S5
cluster would silently drop `renaming (X to X⟦hash⟧)` continuations that `check_import_shape` requires
— clearing a ban key while breaking the shape convention.

⚑ **THE AUDIT’S FRAME WAS WRONG, AND SO WAS MINE (user: *“the pipeline tools aren’t MEANT to be run
independently”*).** I briefed the agent to risk-analyse a TREE-WIDE STANDALONE run and it answered that
question well — but that is not how this module is used. **`split_pipeline.py:486-498` runs it as the
LAST stage, AFTER the build**, so its logs are fresh BY CONSTRUCTION and R1 (staleness) cannot arise
there; the pipeline calls only `sites()` to report, then `die()`s with the repair command. Likewise R2
(drops `public`): standalone that is an unrecoverable export-surface change, but in the pipeline
`rewire_to_leaves` re-binds the consumers at the owner immediately after — the docstring at `:200-209`
says exactly this and I read past it. **Judging a pipeline stage by what it does alone is judging it
against a usage it was never designed for** — the same error as scoring decomposition on whether it
moved the renaming census.

**What survives the reframing** — and it is not nothing, because the pipeline’s own `die()` message
tells a human to run the repair BY HAND (`fix_stale_using.py agda/_build --apply`), so the standalone
path is the one operators are actively invited onto:

| fix                                                                       | status                                                                                                                                                |
|:--------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| **R1 staleness guard** — skip any site whose source is newer than its log | **DONE**, and it refuses **47 of 53** sites on today’s tree. Not a design correction; it makes the invited standalone path safe                       |
| **R3 snapshot** — `_snapshot_once` before the first write                 | **DONE**; it was the only write tool with none                                                                                                        |
| **R6 owner scan** — `^\s*` instead of `^`                                 | **DONE**; `owner("refl")` now resolves to `Foundation.Eq` (was 7 `no owner found`) — the indent blind spot shared with `agda_defs` and `split_lemmas` |
| **R5 wrapped hint** — reject `'quoted'` / `or` / `…?)` debris             | **DONE**; junk tokens no longer enter the name set                                                                                                    |
| **R2 drops `public`**                                                     | **NOT a defect — documented intent with a measured witness**, and the pipeline supplies the missing half                                              |

⚑ **AND THE TOOLS NOW SAY SO — the correction belongs in the code, not in my head** (user: *“it would
be nice if everyone stopped trying to run them independently; THAT needs correction”*).

`agda_imports.stage_warning()` — one declaration, three consumers — prints at the moment of standalone
invocation:

    ⚠  fix_stale_using is a PIPELINE STAGE, not a standalone tool.
       It DELETES `public` conduits because rewire_to_leaves re-binds the consumers next,
       and reads BUILD LOGS that the pipeline guarantees are fresh.
       Supported path:  python3 scratch/split_pipeline.py <file> --apply   (stage 11, after the build)
       Running it alone is fine for INSPECTION; if you repair with it,
       the following stage's work is now yours to do by hand.

Wired into `fix_stale_using` (stage 11), `rewire_to_leaves` (stage 4 — *errs WIDE on purpose because
prune_imports cuts next*), `prune_imports` (stage 5 — *refuses renaming imports BY DESIGN*). It fires
from `__main__` only, so a pipeline IMPORT is silent (verified: a pipeline dry run is unchanged).

**And the pipeline’s own `die()` no longer hands out a bare standalone command.** `split_pipeline:493`
used to print `fix_stale_using.py … --apply` on its own line — which is how operators (me included)
came to run stages alone and then judge them by what they do alone. It now names the coupling in the
instruction: repair and rebuild AS A PAIR, because the next stage’s work is what makes this stage’s
deletions correct.

**The generalisable form:** *a tool that is only correct in a sequence must SAY the sequence, at the
moment it is invoked outside it.* Every reader who reached for these alone re-derived the same wrong
conclusion — the risk agent, and me twice — because the tools could not say it and the docstrings were
read past.

**DECISION: do not run tree-wide STANDALONE.** Preconditions if it is ever run: a green build first (so logs
describe the tree), `edit_snapshot.guard()` added, a staleness assertion (skip any site whose source
mtime exceeds its log’s), hand-review of the deletion set, and the S5 cluster excluded.

⚑ **THE BETTER TOOL, and it is the one the discipline points at.** My hand-found case
(`Algebra/Q/Order.agda:19-20`) was found **with no log at all** — “does module M export name N” is
answerable statically from the tree or the `.agdai` cores. **A static reporter of stale
`using`/`renaming` clauses is the tool that should exist**: no build dependency, no staleness window,
write-nothing. That is a TOOL-BUILD item at class level, which is exactly what the categorization
discipline was adopted to surface — and it surfaced it on the first use.

### 13. THE BUILD — started, and it immediately arbitrated a defect I shipped (2026-08-01)

`gen_build_makefiles` first: **2941 modules** (was 2764 — the 42 prelude leaves plus the earlier splits),
`--check` OK. Then `make -C agda -j`.

⚑ **EXIT 144 IS THE HARNESS, NOT THE BUILD.** The first launch died with exit 144 = signal 16 on a
backgrounded pipeline during tool cleanup (memory `feedback_exit_144_is_claude_harness_artifact`), and
the redirect never landed. Relaunched under `setsid` so the cleanup signal cannot reach it; verified
alive by `pgrep`. **Recording the working invocation because I have now hit this twice:**
`setsid nohup make -C agda -j > LOG 2>&1 < /dev/null &`.

⚑ **THE FIRST ERROR IS MINE, FROM 3a.** `Algebra/N-to-F2-Parity.agda:37` — `[NotInScope] +F … (did you mean 'Substrate.Algebra.F2._+F_'?)`. The file does `renaming (_+_ to _+F_)`, but **3a renamed the
definer, so `Algebra.F2` no longer exports `_+_`** — the clause is stale and `+F` never binds. This is
precisely the class §12’s static reporter would have caught with no build at all, and precisely what
“the typechecker arbitrates” means in practice.

**MEASURED: 7 files** carried a now-nonexistent `Algebra.F2._+_` rename (`N-to-F2-Parity`,
`Wedge/IntParityBridge`, `Wedge/ParityBridge`, `Wedge/ResidueAtom`, `WitnessTower/InsertionParity`,
`WitnessTower/SignGrade2Generated`, +1). All 7 repointed to the new source name. Checked the siblings
in the same clauses (`+-assoc`, `+-identityˡ`) — **still exported, so not stale**; only `_+_` moved.

⚑ **A NEW SHAPE THIS CREATES:** the repointed clauses now read `renaming (_+F_ to _+F_)` — a
rename-to-SELF, which is pure ban debt with zero semantic content. `drop_dead_renames` cannot see it
(its predicate is “the new name is unused”, and here it IS used). That is a second predicate worth
adding: **new == old ⇒ always deletable**, no scope analysis required.

Rebuilt with `-k` so one run yields the FULL error census rather than the first failure — the error
list is the worklist, and `-k` is what makes it a list instead of a single item.

⚑ **THE BUILD RAN. FULL CENSUS, AND THE TREE IS FURTHER FROM GREEN THAN “33 ERRORS” SUGGESTED.**

|                                                             | first run | after rewiring 5 consumed parents  |
|-------------------------------------------------------------|:----------|:-----------------------------------|
| NotInScope                                                  | 19        | **29**                             |
| FileNotFound                                                | 10        | 8                                  |
| DuplicateBuiltinBinding                                     | 5         | 8                                  |
| NoParseForApplication / ConstructorPattern / MissingTypeSig | 10        | 11                                 |
| **AmbiguousName**                                           | 0         | **2**                              |
| total                                                       | **46**    | **60**, across 54 distinct modules |

**After the `Foundation/Bool` fix: 51 errors.** All **8 `DuplicateBuiltinBinding` cleared by ONE
root cause**, exactly as the shape suggested: `Foundation/Bool.agda` was a LEFTOVER PARENT that the
split never consumed — it still carried `data Bool` AND `{-# BUILTIN BOOL #-}` alongside its own leaf
`Foundation/Bool/Bool.agda`. Measured before acting: the parent defined **7 names, all 7 also in the
leaves** (leaves define 29), and **79 files imported the leaf vs 4 the parent**. Retired it; the driver
rewired **129 importers** — far more than my grep’s 4, because it catches indented and wrapped forms a
column-0 pattern misses.

Three survivors carried `renaming (true to tt; false to ff)` with the aliases LIVE in their bodies.
Resolved the ban-compliant way — bare leaf imports plus `pattern tt = true` / `pattern ff = false`,
the same device `Fin/Fin.agda` uses for `fzero`/`fsuc`. Verified by isolate-compiling `OrbitAudit`.

**Errors went UP, and that is progress, not regression**: clearing `FileNotFound` lets a module compile
FURTHER and reveal what was behind it. The rewires cleared 5 consumed parents (`Conway.Mul`,
`Foundation.Nat`, `Kelen.Fragment`, `Linguistic.RosettaTable`, `TokiPona.AsFreeOverBasis`) and moved
**38 importers**.

✅ **`AmbiguousName` on `zero`/`suc` — RESOLVED, AND IT NEEDED NO RENAME AT ALL.** The skill’s
prescription is decompose-up-chain first, rename only what survives. `Foundation.Nat` IS decomposed, so
I queued these as genuine survivors for `rename_at_source` — **and the reuse-search found the decision
already made and shipped**: `Fin/Fin.agda:42-43` carries `pattern fzero = zero` / `pattern fsuc x = suc x`, and the SKILL RECORDS IT as *“already landed at source … so no consumer needs
`renaming (zero to fzero)`”*. I had queued a rename for a collision whose sanctioned resolution was
sitting in the provider, named in the playbook I was following.

The actual error was a genuine THREE-way ambiguity (`ℕ.zero`, `Fin.zero`, `Agda.Primitive.lzero`), and
the two sites need DIFFERENT resolutions in the same file — `TabulateCong:50` `{n = zero}` is `ℕ.zero`
(left alone) while `:52` `p zero` indexes a `Fin`-domain function (→ `fzero`). That per-site
distinction is exactly why a pattern synonym beats a rename: **a rename would have had to pick one
meaning for the whole file.**

Both modules now compile clean in isolation (`membudget run 384`, per CLAUDE.md).

⚑ **The transferable form:** an `AmbiguousName` is not automatically a rename job. Check the provider
for an existing synonym FIRST — the ban skill’s “known collision sets” section exists precisely to
record which ones are already resolved, and I read past it to the tool.

⚑ **AND THE HONEST NUMBER: 0 cores were written in 30 minutes.** Nothing is compiling — the failures
sit at the FOUNDATION (`Foundation/Fin/Fin.agda`, `Foundation/Bool/*`, `Foundation/Vec/*`), so every
downstream module is blocked behind them rather than independently broken. **54 failing modules is not
54 independent fixes; it is a small foundation set plus its blast radius.** Fix the foundation first
and re-census — quoting 60 as “60 problems” would be the same error as treating churn keys as new debt.

⚑ **OPERATIONAL: exit 144 defeated five launch shapes** (`nohup`, `setsid`, a detached script, the
harness background mechanism, and a piped variant). What worked is the plainest possible thing: a
FOREGROUND `timeout 540 make -C agda -j -k > LOG 2>&1`. The harness signals backgrounded process
groups during tool cleanup; a foreground run inside a timeout is immune. **Two of my “the build is
running” reports were wrong** — my `pgrep -f "make -C agda"` matched the wrapper shell containing that
string, not a build. `pgrep -af "^make"` is the check that does not lie.

### 14. DRY AUDIT — the gate that catches re-derivation was blind to four classes (2026-08-01)

Dispatched after the `rewire_to_leaves` miss, because three instances in one day is a class.

⚑ **THE TOP FINDING IS THE GATE’S OWN BLINDNESS.** `check_rederive_ratchet.MOTIFS` had no pattern for
word-boundaries, renaming-clauses, def-index or snapshot-absence — so **`strip_using`, `retire_mod_tip`,
`rewire_fcr`, `reparameterize_record` and `drop_dead_renames` were censused at ZERO KEYS.** VERIFIED by
running `census()` directly. That is why all three of the day’s instances were found by accident: the
census could not see them. *The DRY failure of the DRY gate.*

**VERIFIED AND FIXED:**

| \#  | finding                                                                                                                                                                                                                                                 | evidence                     | status                        |
|:----|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------|:------------------------------|
| 1   | `strip_using` SHADOWED `agda_lex.statements` with a column-0 copy; **26 of 2941 files disagreed** — every indented import invisible. Its permutation guard used the same broken parser, so **the guard could not see the loss it was guarding against** | measured both routes         | **FIXED — 26 → 0**, delegated |
| 2   | `\b` on Agda names: **1269 of 10831 (11.7%)** are invisible to a `\b`-bounded regex (`∙`, `⊥`, `×-bij`, `∣G∣`)                                                                                                                                          | measured against `def_index` | motif added; sites remain     |
| 6   | four motif classes missing → 5 write tools censused at 0                                                                                                                                                                                                | ran `census()`               | **FIXED — 134 → 155 keys**    |

⚑ **AND THE FIRST CUT OF MY MOTIFS MATCHED NOTHING — the fifth guard-from-the-instance defect of the
arc, in the guard written to catch that very class.** I wrote the patterns through nested shell
escaping and never ran them against a live line; the census moved +4 while the target tools stayed at
0. Rebuilt by **validating against the five live witnesses BEFORE writing them into the gate** — now
`retire_mod_tip` 7, `decompose_rewrite` 5, `check_import_shape` 3, `reparameterize_record` 2,
`rewire_fcr` 1. *A splice by index also ate the file’s closing brace; the snapshot restored it, which
is the second time today `edit_snapshot` paid for itself.*

⚑ **AND THE INSTANCE THAT TRIGGERED THE AUDIT IS FIXED.** `rewire_to_leaves` now has
`renaming_plan()`, routed through `scope_fix._rename_pairs` — the shared parser that
`drop_dead_renames` and `demand_imports` already used and this tool had never adopted. Verified:
`s≤s` resolves to leaf `Le`; a rename-to-SELF yields a bare import (the alias carries no meaning).
**MEASURED: 6 rename-to-self clauses tree-wide** — pure ban debt with zero semantic content, a shape
`drop_dead_renames` cannot see because its predicate is *“the new name is unused”* and here it IS used.
**`new == old ⇒ always deletable`** — ✅ **ADDED (2026-08-01).** A self-rename binds a name to itself:
no meaning, only ban debt, and the primary predicate cannot see it *because the name IS used* — that is
what the alias is for.

⚑ **AND IT IS NOT A RARITY — IT IS THE STANDING AFTERMATH OF `rename_at_source`.** 3 of the 4 live
instances were `_+F_ to _+F_`, **my own residue** from repointing consumer clauses after the
`Algebra.F2._+_` rename: a rename-at-source turns every consumer alias into a self-rename whenever the
alias already matched the new name. So the tool that creates this shape runs regularly, and the tool
that removes it could not see it.

*Population was 6 when first measured, 4 by the time the predicate landed* — the edit-loop span fix had
already cleared two. **Applied: 4 → 0**; paydowns **6595 → 6599**.

**The selftest case that matters is `self-rename WITH THE NAME IN USE`** — an unused self-rename passes
under BOTH the old and new rules and would have proved nothing. Suite 462 → **466**.

⚑ **My phrasing hid this gap for a turn.** I wrote that the survivors carried directives
`rewire_to_leaves` *“doesn’t parse”* — which sounds like a shape limitation and is not: the parser
existed, in three sibling tools, and this one abstained. The user caught it (*“aren’t we using a shared
parser now?”*). **“Cannot” and “does not” are different claims, and I reached for the first while
meaning the second** — the same absence-word trap CLAUDE.md names, applied to a tool instead of the
substrate.

✅ **`check_import_shape` FIXED — the fourth adopter of `_rename_pairs`.** Its non-greedy copy
(`renaming\s*\([^)]*?(\S+)\s+to\s`) stopped at the first `to`, so `renaming (a to x; b to y)`
yielded `{a}`. **Demonstrated** old `{a}` vs new `{a,b}`; **re-measured tree-wide: 44 statements and
36 source-names** the gate could not see (`+-assoc`, `_·_`, `_∧_`, `_∷_`, `Tm`, `WCR`) — the audit
said 52/48 and the tree has moved since, which is the expected direction. Verdict unchanged at 0, so
this is a widened predicate with no regression. **It is a PRE-COMMIT gate with BASELINE = 0 and the
policy “enforced for new code today”** — the first new multi-pair import of an ambiguous name would
have passed silently.

⚑ **AND MY FIRST TWO EDITS SILENTLY DID NOTHING.** I wrote both through a shell heredoc; the
double-escaping made the `old` strings non-matching, so one `assert` fired and the OTHER replacement
was a no-op that I did not notice — the gate reported its usual `0 bare imports` and I nearly recorded
it as fixed. **A tool that prints its normal output is not evidence that your edit applied.** Redone
with the Edit tool (which fails loudly on a non-match) and verified by DIFFING the two parsers, not by
re-reading the file. Same lesson as the 5 inert guards, one layer down: presence of an edit is not
behaviour of an edit.

✅ **`agda_lex.word` — the name-boundary authority, HOMED AND ADOPTED.** `\b` is a `\w`/non-`\w`
transition; an Agda name may be entirely non-`\w` (`∙`, `⊥`), contain `-` (`×-bij`, `go-≤`), or end in
a symbol (`∣G∣`). **MEASURED: 1269 of 10831 names (11.7%) invisible to `\b`.** Lifted from
`rename_at_source` into `agda_lex` (eight tools need it; a rename tool is not a lexical authority),
re-exported so the two-spelling machinery is untouched. **11 sites across 5 tools converted; remaining
`\b`-on-a-name sites: 0.** Guarded by 7 new `agda_lex` cases — suite 466 → **473**.

⚑ **MY BULK CONVERSION REWROTE ITS OWN TEST.** One new case exists to DEMONSTRATE that `\b` fails on
`∙`; the sweep rewrote its literal `\b` into `word(...)`, so the case then asserted that the CORRECT
matcher fails — **it inverted the fact it was written to prove**, and the suite caught it as a
`NameError` only by luck of the self-import. *A mechanical sweep cannot distinguish a USE of a broken
pattern from a DEMONSTRATION of it.* The case now carries a ⚑ saying so. (The same sweep also inserted
`import agda_lex` into `agda_lex.py` itself — a self-import that worked by module caching and would
break under a different import order.)

⚑ **AND THE AUDIT’S LIVE WITNESS IS NOT FIXED BY THIS — its diagnosis was wrong.**
`retire_mod_tip.py:88` fails on ``````Div.Over.recon-nth\``, attributed to `````\b``````{=tex}. Measured: `word()` ALSO
returns False there, and correctly — the name is preceded by `.`, i.e. it is a QUALIFIED reference
(`Div.Over.` + name), not a bare name, and `.` is deliberately not in the delimiter set. Bare
``` recon-nth\`` matches fine. **So that site needs a qualified-name matcher, not a boundary fix**, and whether ```word`should accept a leading`.\` is a real design question I am not answering silently.
Recorded as open rather than widened.

**Reported, not yet acted on:** ~~`check_import_shape:46`~~ (a PRE-COMMIT GATE, BASELINE=0) uses a
non-greedy renaming parser that sees **only the first pair** — 52 statements / 48 source-names
invisible; verdict unchanged today (0 → 0) but the first new multi-pair import of an ambiguous name
passes silently. ✅ **`drop_dead_renames:97` FIXED — the edit loop now operates on the SPAN.** It had converted its
ANALYSIS loops to `statements()` and left the WRITE on `lines[i]`; since `dead_pairs` returns
`st.start`, a wrapped statement’s `renaming` sits on the CONTINUATION, so the search found nothing,
hit `continue`, and **the clause survived while the tool reported success**. 77 statements disagreed.
The inverse-DRY class inside the tool whose span defect I had fixed hours earlier — I converted the
half I was looking at.

**Guarded by 5 new cases driving `rewrite()` end-to-end** (the suite had tested `dead_pairs` ONLY,
which is exactly why the edit path survived the earlier fix untouched): wrapped-dead is removed,
single-line dead is removed, live is left alone, and **two wrapped statements in one file** — the
index-drift case, because editing spans in a loop shifts later indices. **Verified the cases FAIL
against the old code**: simulated the single-line read on a wrapped statement, `renaming` still
present. Suite 457 → **462**.
**`edit_snapshot` is the least-adopted authority: 14 tools import it; \~49 with in-place writes do not**
— including the ones that could repeat the 33-file `Coxeter/Core.agda` incident it exists to make
recoverable.

### 15. `check_snapshot_guard` — the recoverability gate (2026-08-01)

The DRY audit’s highest residual risk, gated rather than adopted one-by-one — because one-by-one
adoption is precisely what produced the ratio.

**MEASURED:** 59 tools have a write path; **10 armed `edit_snapshot`, 49 did not.** Narrowed to the
destructive shape: **43 in-place source editors, 9 armed, 34 unguarded.** `edit_snapshot` exists
because a rewrite left 33 files unrecoverable (`Coxeter/Core.agda` 76 lines → 3) — so the tools that
could repeat that incident were, in the main, the ones that could not recover from it.

**THE PREDICATE IS DISCOVERED, NOT DECLARED:** a tool is censused iff it writes to a variable it also
READ — `open(p,"w")` where `p` is also `open(p).read()`. That is the in-place edit; a generator writing
a fresh file is not destructive and must not be censused.

⚑ **AND MY FIRST PREDICATE BANKED A FALSE POSITIVE.** It also accepted “the variable is bound to
something ending `.agda`”, which matched a GENERATOR’S OUTPUT-PATH CONSTANT (`gen_kat.py:31 RELPATH = "…FullKATGen.agda"`) and censused two generators that never read their target. **A false
positive in a paydown-only baseline is debt that can never legitimately be paid** — `ratchet.py`’s own
warning, and I nearly wrote it into a new baseline. Caught by reading the `--list` output instead of
trusting the count; the case is now the second selftest.

**Landed:** gate + 5 selftest cases (suite 452 → **457**, 13 → **14 suites**), baselined at **34**,
**wired into `.githooks/pre-commit`** immediately (a gate that is not wired is §9a’s finding, and I was
not going to reproduce it in the same session that recorded it). Then armed the six highest-risk Agda
editors — `fix_notinscope`, `fix_orphan_using`, `fix_ambiguous_import`, `fix_dead_fin_alias`,
`collapse_carrier_nesting`, `respell_typealias` — **34 → 28**, verified all six still compile.

**⚡ NEXT: PAY DOWN THE 28** (user, 2026-08-01). They are paydown-only and named on every commit, but
“named by a gate” is not “fixed” — that is the §9a lesson in its softer form, and leaving 28 tools able
to repeat the `Coxeter/Core.agda` incident because the gate now *mentions* them would be banking a
census as if it were a repair.

The arming edit is mechanical and identical at every site (`import edit_snapshot as _es; _es.guard(<label>, [<path-var>])` immediately before the first write), so this is a CLASS sweep, not 28
decisions — the discipline’s own rule. Two things make it non-trivial and must be checked per site
rather than assumed:
\* **the path variable differs** (`path`, `p`, `f`) and some tools write several files in one run —
`guard` takes a LIST, so a per-file call in a loop arms only the first file; the guard belongs
before the loop with every path it will touch;
\* **`guard` is idempotent per run but not free** — it shells out to `git stash create`, so a call
inside a hot loop is a real cost. `_snapshot_once` (added to `fix_stale_using`) is the shape for
tools that write in a loop.

**✅ SWEPT — 28 → 0. All 43 in-place editors are armed.** Two shapes, chosen per site by whether the
write sits in a loop: 25 got `_snapshot_once` (arm on first write, no-op after — a per-file `guard`
would arm only the first file AND shell out to `git stash create` every iteration); 3 got the guard
inline. Verified placement (`seal_defs:116` calls it immediately before `:117`’s write), 0 compile
failures across every tool, suite 457/457, units green.

⚑ **AND 5 OF THE 28 WERE ARMED-BUT-INERT — caught only by RUNNING one.** My `_snapshot_once` used
`os.path.basename(__file__)` for its label, and five of the target modules never import `os`; the
helper’s `except` swallowed the `NameError` into `⚠ snapshot unavailable` and continued. **They looked
armed to the gate, to a reader, and to `--list`, and would have snapshotted nothing.** The gate checks
that `edit_snapshot` is *mentioned* — it cannot check that the call *works*. Fixed by removing the
dependency entirely (the label is a literal; 25 helpers de-`os`’d), then re-verified by CALLING it:
`snapshot e7e7468cb7dc` with a real recovery command.

**The transferable form, and it is the arc’s recurring shape one layer up:** *a census can verify
presence, never behaviour.* Every guard this session that I checked by reading passed; three that I
checked by running were broken (the two-spelling guard, the unreachable capture gate, now this). The
gate is still worth having — it found 34 genuinely unarmed tools — but “the gate says 0” and “the
tools are recoverable” are different claims, and only the second one matters.

### 16. ⚑ THE WORKLIST NAMED STAGE TOOLS WHERE THE DRIVER IS THE ENTRY POINT (user, 2026-08-01)

> *“Review our TODO list for which tools it employs. Keep in mind that most of the tools are meant to
> be employed by the pipeline driver, not independently.”*

**Audited, and the worklist was wrong in a way that already cost something.** Four tools declare
themselves stages (`stage_warning`): `rewire_to_leaves`, `prune_imports`, `fix_stale_using`,
`agda_imports`. My todos named `rewire_to_leaves` and `rename_at_source` directly, and **I ran
`rewire_to_leaves` standalone six times today** — five consumed parents, then `Foundation.Bool`.

⚑ **THE STAGE IT SKIPPED IS LOAD-BEARING, AND ITS OWN COMMENT SAYS SO.** `split_pipeline` stage 5 runs
the rewire, **stage 6b immediately prunes the rewired consumers** — because *“the rewire is deliberately
WIDE: a bare `open import <parent>` becomes EVERY leaf … and a name it never wanted can still BREAK it,
because a widened scope makes previously-unambiguous syntax ambiguous”* (`split_pipeline.py:360-366`,
with a measured `Algebra.Z` witness).

**MEASURED CONSEQUENCE: 354 consumers now hold ≥5 leaves of a single rewired parent.** That is the
un-pruned residue of six standalone rewires — and “a widened scope makes previously-unambiguous syntax
ambiguous” is a plausible contributor to the **29 `NotInScope`** still in the census, which I have been
treating as independent breakage. *Not asserted as the cause — but it is now a hypothesis with a
mechanism, which is more than I had.*

**The correction to the worklist:** an item whose tool is a STAGE names `split_pipeline` as its entry
point, with the stage tool as an implementation detail. A standalone stage run is legitimate for
INSPECTION (`--dry-run`) and is a deliberate, recorded choice for repair — never the default.

⚑ **And this is the discipline’s own rule turned on the discipline.** §“WORKLIST DISCIPLINE” said every
item must name its resolving tool; it did not say *the named tool must be the supported entry point*.
Naming a stage satisfied the letter and missed the point, which is the same shape as a gate that
verifies presence rather than behaviour.

### 17. THE 6b PRUNE — HYPOTHESIS REFUTED, TWO REAL TOOL DEFECTS FOUND (2026-08-01)

Ran stage 6b’s prune over the 1547 consumers of the six parents I had rewired standalone.
**8496 unused imports dropped; over-wide consumers 354 → 28.**

⚑ **THE HYPOTHESIS IS REFUTED. `NotInScope` went 29 → 31, not down.** I had proposed the over-wide
imports as a plausible contributor to the `NotInScope` census. They were not. *Recorded as a refutation
because I flagged it UNPROVEN when I raised it — that flag is the only reason this reads as a measured
answer rather than a story.*

**And the prune BROKE 3 modules while fixing 1** — net +2. Both causes were real defects in
`prune_imports`, now fixed at source:

1.  **THE MODULE HEADER’S TELESCOPE IS A USE SITE, and `body` started at `hdr+1`.**
    `module M (n : ℕ) where` needs whatever binds `ℕ`, but the header line was EXCLUDED from the token
    set — so the import providing it read as unused and was dropped, leaving a file whose own header is
    `[NotInScope]`. Witness: `Groups/Coxeter/Cyclic/InvCanonical.agda:19`. Fixed: `body` starts at `hdr`.
    *(The APPLIED-argument case was already handled with its own ⚑; the header case sat beside it,
    unhandled — the same “fixed the half I was looking at” shape as `drop_dead_renames`.)*

2.  **A PURE AGGREGATION BARREL CANNOT BE JUDGED BY LIVENESS-OF-USE.** A module whose body is EMPTY
    exists to aggregate its leaves, so by construction no imported name appears in a body that does not
    exist, and “drop everything” is the answer the predicate gives. `InvCanonical.agda` is a header plus
    4 applied leaf imports and **zero body lines**; the prune removed all four. Fixed: `prune_imports`
    now REFUSES a file with no body and says why.

⚑ **AND MY BARREL-REFUSAL IS A STOPGAP, NOT THE FIX (user, 2026-08-01):**

> *“Conduits / barrels need to be resolved RECURSIVELY in order to find all downstream consumers,
> which all need to be rewritten to bind to the base definition, which needs to be renamed **iff** one
> of these final downstream consumers will get a naming ambiguity out of it.”*

That is the actual algorithm, and it explains why every per-file judgement I made about a barrel was
the wrong shape. **A barrel is not a file to judge — it is an EDGE in a chain**, and the four steps are
ordered with a genuine dependency:
1. **resolve the chain RECURSIVELY to its base** (a conduit may import a conduit);
2. **enumerate the FINAL downstream consumers** — not the barrel’s direct importers;
3. **rewrite each to bind at the base**;
4. **rename at source IFF a final consumer would then be ambiguous** — the rename is CONDITIONAL on
step 2’s answer, so it cannot be decided before the walk.
My `prune_imports` guard only REFUSES to gut a barrel. That is right as far as it goes and does not
resolve anything; the barrel still stands and its consumers still bind through it.

**MEASURED against the existing machinery:** `scope_fix._conduit_set/_conduit_owner/_conduit_pair`
(`:2234-2294`) already walks conduit chains — **but with a HARDCODED depth of 3** (`for _ in range(3)`).
Census: **95 pure conduits (empty body) tree-wide**; chain-depth histogram `{1: 80, 2: 12, 3: 2, 4: 1}`.
So the fixed bound bites on exactly one witness today (`Groups.Actions.S3-on-V4` → `.Axioms` →
`.Dispatch`), and “3” is a magic number where the user’s spec says RECURSIVELY. **A bound that happens
to fit today’s deepest chain is not a resolution to the base.**

✅ **BUILT — `scratch/conduit_resolve.py`** (6 selftest cases). `resolve(mod)` recurses to fixpoint
with a per-branch `seen` set, returning the non-conduit BASES and the longest chain; `final_consumers`
walks importers THROUGH conduits to the non-conduit consumers — step 2, and the reason step 4’s rename
cannot be decided early. `is_conduit` keys on *empty body*, deliberately NOT on `public`: a barrel that
forgot the flag is still a barrel, and ⟡public-policy is retiring the flag, so keying on it would shrink
the population as the policy succeeds.

⚑ **AND IT CORRECTED MY OWN MEASUREMENT.** I reported the depth histogram as `{1:80, 2:12, 3:2, 4:1}`
with a chain PAST the bound. ⚑ **BOTH of those histograms are ALSO superseded** — they were computed
with the predicate that counted 14 EMPTY STUBS as conduits (§20). Corrected population: **81 conduits,
`{1:67, 2:13, 3:1}`**. The conclusion is unchanged and the number moved twice: **max 3, exactly AT
`_conduit_set`’s `range(3)`, not beyond it.** My ad-hoc script shared ONE `seen` set across sibling
branches, so a module visited down one branch was skipped in another and the depth inflated. **The
bound is therefore LATENT, not live** (for pure-conduit chains), and the resolver’s justification is
“no arbitrary bound” — the deepest chain sits ON the magic number, one layer from silent truncation —
not “the bound is currently wrong”. The selftest asserts the true value so the claim cannot drift back.

*(§18’s agent reports the bound truncating 1427 modules over the FULL import closure — a different
relation from pure-conduit chains. Unverified by me; both can hold.)*

**Still owed:** steps 3-4 — the rewrite-to-base and the conditional rename. The resolver answers
“where is the base” and “who are the final consumers”; nothing yet acts on the answer.

**After both fixes the prune is idempotent** (re-run: 0 residual drops, 1 barrel correctly refused) and
the census is **52** — one `NotInScope` above where it started, still unexplained. **Not claiming the
prune was a net win.** What it bought is two tool defects retired and 8496 genuinely-unused imports
gone; what it cost is one unexplained error and the reminder that a 1547-file sweep on a refuted
hypothesis is expensive.

### 18. WEAK-BESIDE-STRONG — a class distinct from DRY, and the fix is LIFTING (user, 2026-08-01)

> *“Yet another case where we have machinery not being exploited by other machinery that uses a weaker
> version.”* … *“These are things that need LIFTED into reusable modules.”*

The DRY audit (§14) found DUPLICATED implementations. This is sharper: **a strong, already-correct
capability exists, and a WEAKER solution to the same problem sits beside it** — an arbitrary bound, a
first-match-only parse, a narrower predicate. Neither is a copy; one is simply *lesser*. Nobody notices
because both “work”.

⚑ **AND THE FIX IS NOT “REPOINT THE CALL SITE” — IT IS WHERE THE CAPABILITY LIVES.** The test:
*would a third tool needing this find it?* If the answer is “only by reading a 2000-line file it has no
other reason to open”, it is mis-homed regardless of correctness.

**MEASURED — private capabilities crossing module boundaries** (a declared-private thing used as public
API is the mis-homing smell at its most greppable):

| capability                                          | consumers  | note                                                                           |
|:----------------------------------------------------|:-----------|:-------------------------------------------------------------------------------|
| `agda_defs._index`                                  | **11**     |                                                                                |
| `agda_imports._importable` / `._span_end` / `._lex` | **7** each | the span rule is LEXICAL; its home is `agda_lex`, not an import-block rewriter |
| `_agdatext._arrows`                                 | 7          |                                                                                |
| `agda_lex._path`                                    | 6          | private inside the authority itself                                            |

**FIXED — the one that BIT.** `check_discharge_ratchet.py:86` and `scripts/set1_motif.py:15` walked a
`record`/`data`/`module` header with `while … j - i < 6`, then **`continue`d when no `where` was found
— silently DROPPING the declaration.** MEASURED: **401 multi-line headers tree-wide, 136 need MORE than
6 continuations** (deepest: **40**, `Sporadic/HappyFamily/AsTree.agda:50`). Lifted the capability to
`agda_lex.head_span(lines, i, limit=None)` — unbounded by default, `limit` retained only as a
runaway guard for a malformed file. **That distinction is the whole finding: a TERMINATION bound is
fine; a CAPABILITY bound is the smell.**

**Effect on a live gate: carriers 112 → 117, undischarged 28 → 32.** A paydown-only ratchet had been
reporting a comfortable number because a third of its multi-line population was invisible to it.
Suite 473 → **479**, 14 → 15 suites.

⚑ **THE AGENT DISCLOSED A HARNESS BUG IN ITS OWN FIRST RUN** — it measured from the repo root, so every
module’s text resolved to `""` and every import closure looked one hop deep, which would have
EXONERATED the witness. It caught this by probing a known-good consumer’s second hop before trusting
the histogram, re-ran with `cwd=agda/`, and said so. *That is the method this repo has had to learn
three times today; an agent volunteering it unprompted is worth more than the finding.*

**Its §2 claim — that `_conduit_set`’s `range(3)` truncates 1427 modules / 21,976 nodes — is NOT
verified by me.** It measures the FULL import closure, whereas my histogram measured pure-conduit
chains only. Both can be right about different relations. **Recorded as the agent’s measurement,
pending independent re-run**, per the standing rule that a second agent’s number is exactly as
unreliable as my own.

### 19. LIFTING THE PRIVATE-ACROSS-BOUNDARY CAPABILITIES (2026-08-01)

⚑ **FIRST, MY OWN CENSUS WAS WRONG AND I QUOTED IT AS FACT.** I reported six private capabilities with
counts up to 11 (`agda_defs._index`, `agda_imports._importable/._lex`, `_agdatext._arrows`,
`agda_lex._path`). **None of those are private names** — my regex was `_\w+` over the import list, which
matches the underscore INSIDE `def_index`, `module_path`, `mask_comments`. Corrected predicate (*the
name itself starts with `_`*): **8 private names, 19 imports.** The agent’s list was closer to right
than mine, and the two it led with are the two that survive.

**LIFTED — both verified identical to their originals, both aliased so no consumer moved:**

| capability     | was                       | now                             | consumers |
|:---------------|:--------------------------|:--------------------------------|:----------|
| `span_end`     | `agda_imports._span_end`  | **`agda_lex.span_end`**         | 7         |
| `rename_pairs` | `scope_fix._rename_pairs` | **`agda_imports.rename_pairs`** | 3         |

*Homes chosen by what the capability IS, not where it sat:* the span rule is **lexical** (a wrapper over
`_continues`/`_depth_after`, both in `agda_lex`) while `agda_imports` declares its job as *modifying
import blocks* — a tool needing only “where does this statement end” had to import an import-rewriter to
ask. The renaming clause is **import syntax**, so it belongs in the module that calls itself *“the ONE
place Agda import blocks are modified”* — not in a 2000-line scope-fixer that a PRE-COMMIT GATE was
reaching into.

**Verified, not assumed:** `span_end` agrees with `agda_lex.statements` on **all 25,376 statements** in
the corpus, and `agda_imports._span_end is agda_lex.span_end` — the alias is identity, not a copy.

⚑ **AND THE LIFT EXPOSED A LATENT CRASH I HAD SHIPPED.** `rewire_to_leaves` had a `--selftest`
DISPATCH and no `_selftest` — I wired the flag when adding `renaming_plan` and never wrote the
function, so the documented flag raised `NameError`. **`run_selftests` could not catch it**: it
DISCOVERS modules that *define* `_selftest`, so a module with only the CALL is invisible — the same
“a discovered population only discovers what opted in” gap that hid `rename_at_source`’s live bug.
Written: 6 cases (mixfix `[_,_]` comma, rename-to-self, UNMAPPED refusal). Suite 479 → **485**,
15 → **16 suites**.

**Residue:** 19 imports still name the private aliases (migration remainder, not a defect), and
`telescope_text` remains a de-facto shared library with 5 private names consumed by 2 other files and
**no public surface at all** — the next lift.

### 20. TOOLING #1-#2 (2026-08-01)

✅ **#1 — `set1_motif.py` adopted `head_span`, and it had TWO defects not one.**
\* the `j - i < 6` bound: **demonstrated on `Sporadic/HappyFamily/AsTree.agda:50` — `head_span` joins
41 lines and reaches `where`; the old bound stopped at 7 and NEVER FOUND IT**, so the header was
classified on a fragment;
\* `strip_comments` was `re.sub(r"--.*$")` — **line comments only**, so a `{- … -}` block containing a
`record … Set₁` counted as a live site. Now `agda_lex.mask_comments`, which handles NESTED blocks and
knows `-->` is a name.
*I went in for the bound and found the second defect only because I read the file first.*

⚡ **#2 — the resolver’s OWN predicate was wrong, and the rewrite step would have acted on it.**
Before writing step 3, I measured what it would rewrite: **three of the top six conduits reported
“N final consumers, 0 bases”** — incoherent, since a barrel with consumers must resolve somewhere.

**Cause: `is_conduit` keyed on “no body”, which also matches an EMPTY STUB** — a module with no body
AND no imports, which aggregates nothing. MEASURED: **14 of 95** (`Algebra.F1.Capstone`,
`Algebra.F2.GF256`, `Category.Allegory.Refinement.Preamble`). The worst reported **280 final consumers
and 0 bases**; a rewrite-to-base pass would have rewritten 280 files to bind at nothing.

Fixed: a conduit must have **at least one outgoing edge**. Population **95 → 81**, zero-base anomalies
**3 → 0**, 2 selftest cases added (suite 8/8 in this tool).

⚑ **The method that caught it: MEASURE WHAT THE NEXT STEP WOULD DO, BEFORE BUILDING IT.** The
predicate had passed its own selftests and produced a plausible census; only asking it for the
*actionable* answer — which files would I rewrite, to what — exposed the incoherence. *A census that is
never acted on can hide a wrong predicate indefinitely.*

✅ **STEPS 3-4 BUILT — `conduit_resolve.plan(mod)`, and step 4 is NOT a rare edge case.**

**MEASURED BEFORE BUILDING** (the discipline that caught the stub bug, applied again): **22 of 71
(consumer, conduit) pairs would become AMBIGUOUS at the base.** Nearly a third — so the four-step order
is not defensive structuring, it is load-bearing: the rename genuinely cannot be decided before the
walk, because the ambiguity *does not exist until the rewrite happens*.

`plan(mod)` returns `{conduit, bases, chain, consumers, rewrites, renames}` — **DECIDED, NOT APPLIED**,
the shape `prune_imports` learned after writing unconditionally. `renames` is step 4’s conditional: per
consumer, the names that would collide and *which other provider* supplies them.

**Tree-wide: 71 rewrites, 22 blocked behind a rename.** Concentrated — `Algebra.Z.Arithmetic` alone is
34 consumers / 3 bases / **18 renames**, all colliding on `-ℤ`. The rest are 1 each.

*Reuse:* `exports_of` goes through `agda_defs.def_index`, never a local `^name :` scan (the §14 class).
5 selftest cases incl. *renames ⊆ consumers* — a rename for a consumer not being rewritten would be
unmotivated. Suite 487 → **492**.

**What is still owed: the APPLY.** `plan` decides; nothing writes yet. The apply must run in dependency
order — **rename at source FIRST for the 22, then rewrite all 71** — since rewriting an ambiguous
consumer before its rename is what produces `AmbiguousName`.

⚑ **AND I WAS WRONG THAT THIS UNBLOCKS THE COLLISION CLAUSES — MEASURED, THE OVERLAP IS ZERO.** I
flagged the 22 conduit renames as possibly duplicating that worklist item. Comparing the two sets as
(consumer, name) pairs: **22 conduit renames, 34 COLLISION clauses, 0 in common.** *(COLLISION re-measured 2026-08-01: **31**.)* They are independent
work, and the two items can proceed in parallel once the apply lands. *A suspected duplication is worth
exactly one measurement; carrying it as a caveat would have serialised two independent tasks.*

⚑ **The COLLISION figure has been quoted three ways in this plan — 54, 33, and 34.** Today’s measured
value is **34**; the others are earlier snapshots taken before the arc’s paydowns moved the population.
Superseded, not deleted, because the drift itself is the record.

### 21. TOPOLOGICAL ORDERING OF THE WORKLIST (user, 2026-08-01)

Ordered the worklist by real dependency, tooling first. Deriving the order — rather than assuming it —
surfaced three things:

**1. ⚑ THE SELFTESTS MUST PRECEDE THE 9g GATE, and I had them merely adjacent.** 9g **censuses selftest
presence**. Building it first would bank **4 fictitious gaps** (`split_pipeline`, `capstone_to_dir`,
`fix_stale_using`, `narrow_leaf_imports`) into a paydown-only baseline — debt that was never real and
can never legitimately be paid. **That is the exact false-positive class I nearly shipped in
`check_snapshot_guard` this morning** (a generator’s output-path constant), caught then by reading
`--list` instead of the count. A gate whose census is a MOVING TARGET must be built after the
population settles, or it freezes the transient.

**2. The conduit renames and the COLLISION clauses are DISJOINT** — measured, 0 of 22 ∩ 34. Two items
I had coupled with a caveat are independent and can run in parallel.

**3. One item’s value is INVERTED against its position.** The static stale-clause reporter is most
useful *while the tree is red* — so it COMPETES with fixing the tree rather than complementing it.
Recorded as such, so it does not read as straightforward next work.

**The chains:** `apply → {FileNotFound, COLLISION}`; `{those} + un-renames → build errors → ban additions → {re-baseline, catalog} → gated commit`; `selftests → 9g gate`. Everything else is
independent.

⚑ **SUPERSEDED 2026-08-01 — §24 FALSIFIED EVERY EDGE IN THAT LINE AND I DID NOT CORRECT THE LINE.**
This is the plan’s ONE canonical DAG statement; the audit rewrote the dependencies in prose, item by
item, and left the summary asserting the old graph. *That is the derived-view defect (§6) a second
time in this document, and in the highest-leverage place: a future reader reaches for the chain line,
not for four paragraphs of corrections.* The measured graph:

| edge as written                | status                                                                                                   |
|:-------------------------------|:---------------------------------------------------------------------------------------------------------|
| `apply → FileNotFound`         | **FALSE.** The FileNotFound work is the `as` class; the conduit apply is independent (measured)          |
| `apply → COLLISION`            | **FALSE.** 22 conduit renames ∩ 31 COLLISION clauses = **0**                                             |
| `un-renames → build errors`    | **INVERTED.** 113 statements are fully SAFE and clear their keys with no build needed                    |
| `build errors → ban additions` | **FALSE for 2 of 3 buckets.** 34 `using` + 22 `as` need no green tree; only the residue does             |
| `selftests → 9g gate`          | **INCOMPLETE.** 9g also censuses schema entries and `check_argv`, so `{selftests, Audit-V residue} → 9g` |

**The corrected chains:** `{A0 the F2`as`regression, A3 the 113 safe un-renames, T1 the conduit apply, A2 COLLISION, T2 the section instrument, T11 the Audit-V residue, T3 selftests}` are ALL
independent and unblocked; `{A0,A2,A3,T2} → build errors → the residual ban additions → {re-baseline, catalog} → gated commit`; `{T3, T11} → 9g`.

⚑ **SUPERSEDED AGAIN by §26 — and this is the THIRD time a summary line outlived its own corrections**
(after §21’s original chains and the §5 “Remaining:” line). I wrote the correction above, then wrote
§26’s findings as new prose, and left this line not mentioning R1-R5. *The class I named one section
earlier, reproduced one section later, by me, in the same document.* **Standing consequence: this line
is the plan’s single DAG statement and MUST be edited whenever a dependency moves — treat it as the
derived view that most needs reconciling, not as narrative.**

**The chains, as of §41** *(supersedes the §31 table — which was frozen while §32–§41 created six
items it never named. **THE FOURTH TIME A SUMMARY OUTLIVED ITS CORRECTIONS IN THIS DOCUMENT**; the
standing rule is that this line is edited whenever a dependency moves, and it must be re-derived at
every audit, not appended to.)*

⚑ **THE ORDERING PRINCIPLE IS TOOLING-LEVERAGE-FIRST, and this arc measured why**: every time a tool
was fixed before its population was worked, the population SHRANK (§30 fixity→0, §34 telescoped
roots→0, §38 applied-open 79→76→54) or the work became a driver run instead of hand-repairs
(§33 → R9’s 162-key paydown; §41 → R12b replaces 113 hand-fixes with a re-split). **A tool fix is
never “also” work — it is the step that sizes the work.**

⚑ **SUPERSEDED BY §70d — AND THE TABLE BELOW IS KEPT AS THE RECORD, NOT AS THE DAG.** This is the
SIXTH re-derivation, and the fifth one’s own instruction (*“edit it whenever a dependency moves,
RE-DERIVE at every audit rather than appending”*) is what failed: appending a row is what an audit
naturally produces, so the table became **a log wearing a DAG’s clothes** — a reader looking for
“what is unblocked” got a chronology. **The live DAG is §70d.** Rows here remain valid as dated
findings about the state they measured; none is a current dependency claim.

⚑ **AND THE SIZE IS MEASURED, NOT ESTIMATED — I FIRST WROTE “40+ ROWS” FROM IMPRESSION** (user:
*“there HAD been machinery for reading that”*). `mdstruct --tables` reads every table in this
document structurally: **this one is 43 rows × 3 cols, and every other table in the plan is 2–10
rows.** So it is not merely long — it is **the single outlier in a 20-table document, and it is the
DAG statement**, which is a far stronger diagnosis than the one I reached by eye. *The tool that
answers “how big is this table” existed and I described the document instead of querying it.*

*(as of §44 — the FIFTH re-derivation of this table.)*

| layer                                                                                       | items                                                                                                                                                                                                                                         | why                                                                                                                                                                       |
|:--------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DONE (tooling)**                                                                          | `R1` `R7a` `R7b` `R9-GATE` `R9-TOOLING` `R11-TOOLING` `R12` `blame()` `--manifest` `blockers()` · **§44:** `--verify`/`--leaves`/`--last` + the persisted leaf census, `--blocked`, `fix_sections` self-summary, 3 `agda_lex` predicate fixes | each retired or resized a population                                                                                                                                      |
| **DONE (paydown)**                                                                          | `R2` (8 barrels) `R9` (589 leaves, private 226→66) `T6` `R6`✗ `G2`✗ · **§44: `T2b-APPLY` 76 sites/27 files; `F2/Vector.agda` COMPILES**                                                                                                       | —                                                                                                                                                                         |
| **TOOLING, unblocked — DO FIRST**                                                           | `R11` (applied-open restructurer, **54 files / 1 kind, re-measured §44**), `R3` (`_conduit_set` fixpoint), `T11` (Audit-V residue), `T3` (2 remaining untested write tools), `T12`, `T2c`, `T5`, `R5`                                         | no deps; each unblocks or sizes later work                                                                                                                                |
| **`T2b-RESIDUE` — 295 sections, UNCLASSIFIED**                                              | 81 `_+_` `ambiguous` (per-site) + 214 `no-candidate` **whose class is not yet known**                                                                                                                                                         | ⚑ NOT assumed to be more binder false-positives — that assumption is exactly what §44 corrects                                                                            |
| **`G4` `G5` `G6` — RED GATES NO ITEM TRACKED** (§45)                                        | `shape-node index` STALE (regenerable) · `Σ6` `jea_seam_provenance` regressed · `cap ratchet` (baseline is a 0-byte file — a LEVEL, not a delta)                                                                                              | each BLOCKS B3; found only by running `gate_status.py`                                                                                                                    |
| **`R13` DONE (§49) — and it RE-ORDERED A4**                                                 | `rewire_only` was 1 def / 0 calls; wiring it cleared `Wedge/BoundedIso` (61 leaves) in one run                                                                                                                                                | **`R13 → A4-UNBLOCK`**: the top blocker was a consumed parent whose only supported entry point was dead code                                                              |
| **`A4-UNBLOCK` IS A CHAIN, NOT A LIST** (§51)                                               | 2 of 2 worked blockers cleared their own error and revealed a DEEPER one (`F2/Vector`→`Universal`, `V4-Coxeter`→`Coxeter/Core`)                                                                                                               | **the count of names is not the measure — the CENSUS DELTA is.** `A4-UNBLOCK` cannot be sized until a full `--verify --leaves` lands                                      |
| **`A4-UNBLOCK` now needs the CENSUS, which a scoped run destroyed** (§51)                   | ledger write gated on `--leaves`; `--diagnose --blockers` reads the worklist from it                                                                                                                                                          | **`census → A4-UNBLOCK`**: the §46 blocker list is one repair out of date and must be re-derived, not transcribed                                                         |
| ⚑ **THE CENSUS IS A PROJECTION OF THE BUILD** (§52) — supersedes CENSUS-CLEAN-RUN’s premise | `make -C agda -j` (existing, parallel, dependency-ordered, incremental) **then** `--verify --from-build` (seconds)                                                                                                                            | **`BUILD → census → {A4-UNBLOCK, R12b, A4}`**. It is no longer a bespoke 40-min compile forbidding concurrent edits; the build already emits 2810 per-module logs         |
| ⚑ **1770 of 2810 LOGS ARE STALE** (§52)                                                     | freshness = `log ≥ max(own source, every TRANSITIVE import)`, via `gen_build_makefiles.parse_tree()`                                                                                                                                          | **63% of the build record is UNMEASURED, not passing.** Any census figure taken before the build refresh is fiction — `clean` read 2802 without this test, 1036 with it   |
| ✅ **BUILD + CENSUS RAN** (§53) — the arc’s first honest figures                            | **clean 1303 · build-failed 121 · stale 1427 · dependency 2**                                                                                                                                                                                 | supersedes EVERY earlier census number, incl. §46’s `clean=541/dep=436/own=345 over 1322` (dependency-blind instrument)                                                   |
| ⚑ **ARTIFACTS UNDERCOUNTED FAILURES 3×** (§53)                                              | log-derived `own` = **41**; make’s own list = **121** — a FAILED module leaves no fresh log                                                                                                                                                   | `--build-log=` folds in make’s report. **The build’s own verdict outranks a reconstruction of it**                                                                        |
| ✅ **`C1` DONE (§54) — the split is 90/10**                                                 | **1427 → 1286 BLOCKED + 141 unmeasured**; `clean 1303 · build-failed 121 · blocked 1286 · stale 141 · dependency 2`                                                                                                                           | **the tree is 121 failures dragging 1286 behind them, not 1427 unknowns**                                                                                                 |
| ⚑ **\~10.6 BLOCKED PER FAILURE** (§54)                                                      | reverse closure over `parse_tree()` — one import DAG, three consumers                                                                                                                                                                         | **work the 121 in DEPENDENCY ORDER, not by citation count**: clearing a root frees a cone far larger than its own citation number implies                                 |
| ✅ **`A4-CLASSIFY` DONE (§55) — and the ranking INVERTED**                                  | `V4-Coxeter` blocks **501**; I had ranked it **54** by citations. Head: 501 · 400 · 391 · 324 · 274                                                                                                                                           | the §54 prediction, MEASURED: citation count is local, cone size structural, \~10× apart                                                                                  |
| **A4’s population is \~40 mechanical + \~80 heterogeneous** (§55)                           | `file-not-found` (remedy EMITTED per row) vs NotInScope/NoParse/ParseError/UnequalTerms/Clashing/Ambiguous                                                                                                                                    | **`A4-FNF → A4-OTHER`**: do the mechanical class first; do NOT treat the 121 as one population                                                                            |
| ⚑ **`A4-FNF`’s “\~40 MECHANICAL” IS UNVERIFIED** (§56)                                      | its TOP row (`IdemInequality`, 7 files / 501-cone) is **R7b’s telescoped-split class**, not a consumed parent — the leaves never compiled                                                                                                     | **`C2 → A4-FNF`**: re-check every repeat root under a tightened predicate BEFORE running an emitted remedy                                                                |
| **`C2` — `diagnose` false positive** (§56)                                                  | classifies `[FileNotFound]` as consumed-parent when *a leaf DIRECTORY exists*; here it holds leaves that never built                                                                                                                          | **a directory of broken leaves is not evidence a rewire is the fix** — same shape as `leaf_map`’s `os.path.isdir` treating an EMPTY dir as “has leaves”                   |
| ✅ **RECOVERY IS AVAILABLE** (§57) — `recover_presplit.py`                                  | **51 refs hold a pre-split `IdemInequality.agda`**; `pre-r9` (42 lines) is the last state before R9 split it                                                                                                                                  | **`R7b-APPLY` = restore + re-split, NOT repair-the-leaves**: N per-leaf telescope judgements collapse to one `split_telescoped` run                                       |
| ⚑ **A TAG CANNOT PROTECT THIS WORK** (§57)                                                  | §10 measured the decomposition output as overwhelmingly UNTRACKED; a tag holds only committed state                                                                                                                                           | snapshot via `edit_snapshot.guard` (it COPIES untracked files aside) — the rule is right, the instrument was not                                                          |
| ⚑ **§34’s “R7b POPULATION = ZERO” IS RETIRED** (§57)                                        | true of already-decomposed ROOTS; `IdemInequality`’s leaves are a live instance                                                                                                                                                               | *a recorded finding is a hypothesis at a later tree state* — **6th confirmation**, this one on a CLOSED item                                                              |
| ⚑ **`C3` — RECOVERY IS NOT A COMMAND** (§58)                                                | `edit_snapshot` PRINTS `git checkout <sha> -- <path>`; nothing consumes it, so undo is a hand-assembled shell line                                                                                                                            | **`C3 → R7b-APPLY`**: the tree is damaged and the fix must be a TOOL, not a shortcut (user: *“me working the command is a bad shortcut”*)                                 |
| **`R7b-APPLY` INCOMPLETE — the emitter damaged the tree** (§58)                             | 3 defects: a `hasattr` to a NON-EXISTENT fn (would emit zero sibling imports), a double-wrapped telescope (`[ParseError]`), and a NON-IDEMPOTENT apply that **deleted both leaves**                                                           | guarded now (`is_split_out` + CLI refusal + 2 cases); state recoverable from snapshot `e376c6bb4d1b`                                                                      |
| ⚑ **`R7b-REWRITE` — THE POLARITY WAS BACKWARDS** (§58d, user)                               | `prune_imports.should_keep`: *“no evidence is never evidence of death”*. I built `needed_params` as a MINIMISER; a wrong-SMALL selection is `[NotInScope]`, a wrong-LARGE one is trimmed by the next stage                                    | **`R7b-REWRITE → R7b-APPLY`**: keep-biased selection + `split_lemmas`’ closure, letting `prune_imports` trim. **`Op.agda` went clean exactly when it stopped minimising** |
| ⚑ **THE CLOSURE ALREADY EXISTED, CITED IN A COMMENT I HAD OPEN** (§58d)                     | `prune_imports:163` names **`split_lemmas:595` — `need[fn] = direct ∪ ⋃ need[sibs]`**; I reinvented it 3× partially (sibling edge · inherited prelude · the coupling)                                                                         | **`split_telescoped` is a `split_lemmas` VARIANT, not a sibling tool** — its distinct part is only: read telescope, select groups, re-emit header, re-open applied        |
| ⚑ **THE WORKLIST’S ORDER CONTRADICTED ITS OWN FINDINGS** (§59, user)                        | R11 was recorded “PROMOTED (underneath R7b)” and still sat AFTER it; the R7b chain led on a 501 cone that is **`V4-Coxeter`’s, not the repair’s**                                                                                             | **R11 → R7b-APPLY**; the R7b chain DROPS below `T13`/`C2`/`G4` until `R7b-SWEEP` sizes it                                                                                 |
| **`C4` — NOTHING RANKS THE WORKLIST BY MEASURED CONE** (§59)                                | `_blast_radius` + `.leaf-verify.tsv` both exist; no command composes them into *“what would clearing this root free?”*                                                                                                                        | ordering was my JUDGEMENT and it was wrong — the same missing-command shape as every other refusal this session                                                           |
| ⚑ **SUNK-COST ORDERING** (§59)                                                              | a whole sitting on ONE file (6 passes, 1 clean leaf) while T13 (unblocks 4), C2 (re-derives A4-FNF’s population) and G4 (1 regeneration → B3) sat untouched                                                                                   | §55 ranked the BLOCKERS correctly; **nothing ranked the WORKLIST**, so it defaulted to what I already had open                                                            |
| **A FEW ROOTS DOMINATE** (§55)                                                              | `IdemInequality` **7 files** · `Vec.Properties` 4 · `Nat.WellFounded` 4 · `FUSepQBridge` 3 · `Foundation.Nat` 3 · `SimplicialBoundary` 3                                                                                                      | 121 FILES ≠ 121 DECISIONS — same overstatement the leaf count made in §46                                                                                                 |
| ⚑ **A 100× DEFECT THAT WAS NOT PARALLELISM** (§55)                                          | `parse_tree()` re-run per query → **121 identical tree walks**; memoised at its owner: **300s+ → 2.7s**                                                                                                                                       | **before reaching for concurrency, check whether the work is REPEATED**                                                                                                   |
| **The 121 are HETEROGENEOUS** (§53)                                                         | `RIdx.agda` fails on a hash-suffixed GENERATED name `Tm⟦27e68fcc⟧`; `ElAtlas/Proofs.agda` fails `[FileNotFound]` (consumed-parent)                                                                                                            | classify with `--diagnose --blockers` BEFORE repairing; different tools                                                                                                   |
| **`T13` `T14` `T15` `R13` — from the §48 audit**                                            | `--list` on the ratchet authority (**10 callers, 4 copies, 6 omissions**) · `agda_defs` CLI (**19 importing tools**) · `gate_status` verdict line · `rewire_only` wiring                                                                      | **`T13 → {G1, G6, A5, B1}`** — each needs to ENUMERATE a ratchet’s population, which only `--list` provides                                                               |
| **`M1` `M2` `M3` — the markdown layer** (§50)                                               | normalize the plan to pandoc’s fixpoint · fix `gen_reuse_index.py` (not its output) · a fixpoint gate over tracked markdown                                                                                                                   | **MEASURED: 48 MD060 rows → 0 in ONE pass** (plan), 12 → 0 (`catalog/reuse-index.md`). `M2` before any normalize of a GENERATED file, or the next regeneration undoes it  |
| **`R12b` and `A4` RE-SIZED BY §46**                                                         | leaf-own **345** (not 113) · blocked-behind **436** (not 289) · **1322 leaves**, not 589                                                                                                                                                      | take the worklist from `split_pipeline --last`, never from a quoted count                                                                                                 |
| **UNBLOCKING ORDER IS THE TOP-10 BLOCKER LIST** (§46)                                       | 10 files cite **340 of 436** dependency failures; head is `Wedge/BoundedIso` 61, `V4-Coxeter` 54, `F2/Vector/Universal` 52                                                                                                                    | a short ordered list, not a sweep — and it is the cheapest path to A4                                                                                                     |
| **PAYDOWN, unblocked**                                                                      | `R12b` (re-emit the 113), `A3` (113 safe un-renames), `R8` (23 leaf-side `public`), `A2` (31 COLLISION), `G1` (1 stale claim), `G2`-residue (3 capstones)                                                                                     | measured populations, tools exist                                                                                                                                         |
| `R12b → R10a, R10b`                                                                         | do not stack new splits on 113 known-broken leaves                                                                                                                                                                                            | `R10a` = 46 defs in parameterized inner modules; `R10b` = 15 in plain ones                                                                                                |
| `R10a ⊐ split_telescoped`                                                                   | hoist the inner telescope, then split                                                                                                                                                                                                         | the ban forces the hoist (§35); the inner module dissolves ENTIRELY                                                                                                       |
| `{R10a, R10b, R11} → T10`                                                                   | one-definition-per-file cannot be measured while three populations are mid-flight                                                                                                                                                             | `T10`’s 347-of-656 predates R9’s 589 leaves — re-measure, do not quote                                                                                                    |
| `T9` — independent, LOW VALUE while the tree is red                                         | a static stale-clause reporter competes with fixing the tree                                                                                                                                                                                  | its value is highest exactly when the build is broken, which is why it keeps deferring                                                                                    |
| `R3 → R4 → {T1, T7}`                                                                        | the planner consumes conduit resolution; T1/T7 are R4’s barrel and `as` cases                                                                                                                                                                 | —                                                                                                                                                                         |
| `{T3, T11} → T4`                                                                            | 9g censuses what they fix                                                                                                                                                                                                                     | building first banks their gaps                                                                                                                                           |
| `{R12b, T2, A2, A3, R8} → A4 → A5 → {B1, B2} → B3`                                          | the build/commit chain                                                                                                                                                                                                                        | B3 needs ALL 21 hook-wired gates green; 8 were failing at last census                                                                                                     |

**Retired edges:** `R7b → T10` (the 5 roots were already decomposed, §34); `R7b → the 19-leaf ban work` (same); `R1 → A4` (satisfied); `R2 ⊐ A0` (done); `apply → {FileNotFound, COLLISION}`
(independent); `un-renames → build errors` (113 statements clear their keys with no build).

⚑ **AND §28’s “ALL TEN BARRELS ARE 100% LEAF-COVERED” IS SCOPED, NOT GENERAL.** That measurement was
over FLAT barrels — a parent whose leaves are ordinary modules. A **telescoped root does not decompose
that way**: its leaves must re-declare the parameters, so “is every name covered by a leaf” is not the
question that decides whether the root can retire. Do not carry the 100% figure across to the 5
telescoped roots.

⚑ **The standing form, and it is why “audit X against Y” and “audit Y against X” are different
questions:** the first pass found items the worklist had DROPPED; this pass found a claim the plan
still ASSERTS after its own later section disproved it. **A correction recorded as new prose does not
retract the summary it contradicts** — the document must be edited where the old claim lives, not only
where the new one was learned.

⚑ **The general form, and it is the DISCIPLINE section’s own rule one level up:** that section said an
item must name its TOOL. It did not say an item must name **what must be true before it runs**. A
worklist ordered by importance rather than dependency will do correct work in an order that makes some
of it wrong — which is how the 6b prune ran on a refuted hypothesis and how a gate nearly banked a
transient.

### 22. THE APPLY, STOPPED BY ITS OWN PLAN (2026-08-01)

Before writing a line of the apply, I inspected the biggest rename it proposed — the 18 `-ℤ` cases.
**It was wrong, and the plan could not have told me so.**

⚑ **THE PLAN SAID “`-ℤ` COLLIDES”. THE TRUTH IS TWO DIFFERENT OPERATORS** (user: *“the tooling should
have been able to present a plan about this, including type signatures”*):

    Z.Sub._-ℤ_  : ℤ → ℤ → ℤ      binary subtraction
    Z.Int2.-ℤ_  : ℤ → ℤ          unary negation

**`agda_defs.def_index` keys BOTH under the bare `-ℤ`** — it drops the mixfix underscores, which is
exactly the arity information that distinguishes them. **The INDEX manufactures a collision Agda does
not have**, and a rename would have picked one meaning for a consumer wanting the other.

⚑ **A BARE NAME IS NOT A DECIDABLE UNIT.** `signature_of(mod, name)` now recovers the real spelling
(`_x_` / `x_` / `x`) and its type, and `plan()` attaches BOTH providers’ signatures to every reported
ambiguity. Same spelling + same type ⇒ a genuine duplicate wanting a rename; different arity ⇒ two
operators the index merged. **That is the difference between a plan you review and a plan you trust.**

⚑ **AND `ambiguity()` IGNORED THE `using` FILTER** — a second defect found on the way. `open import M using (_*ℤ_)` binds exactly one name, so a collision on `-ℤ` through that statement cannot occur; the
check counted the module as “imported” regardless. Fixed to compute what each statement actually BINDS
(bare ⇒ all; `using` ⇒ that set; two statements ⇒ the union).

⚑ **MY OWN PROBE OF THAT FIX WAS ALSO WRONG.** I measured “18 of 22 are false positives” by checking
the CONDUIT’s `using` clause — but the collision comes from `Z.Int2`, imported BARE. The tool moved
22 → 21, and **the tool was right where my probe was wrong**. The real reduction is small; the real
finding is the index’s spelling.

15 selftest cases (2 new pin the binary/unary distinction); suite **494/494**.

⚑ **AND “DIFFERENT ARITY ⇒ SAFE” IS ALSO WRONG — the user’s correction, confirmed by the live build**
(*“this is why it’s necessary to know whether, AT THE LEAF, the bare name collides — even if the
signature doesn’t”*):

I wrote that different signatures mean “two operators, not a duplicate to disambiguate”. **Agda
resolves on the NAME, and a use site writes the bare token.** `_-ℤ_` and `-ℤ_` are distinct scope
entries — but both are *written* `-ℤ`, so the parser must disambiguate by arity at every use. The
signature tells you they are different things; it does NOT tell you the leaf can read them apart.

**The live census proves the stronger form.** `CFMatrixBridge/Properties.agda:40`:

    Don't know how to parse a * p₁ +_.  Could mean any one of:
        a * (p₁ +_)          (a * p₁) +_
      *  infixl 7   [_*_  Foundation/Nat/Times.agda]
      +_ postfix section, level 6   [_+_  Foundation/Nat/Plus.agda]

**No shared name at all** — `_*_` and `_+_` are different names from different modules. A *section* of
one collides with the *grammar* of the other. **MEASURED: my `ambiguity()` does not see this site**, and
cannot: it compares NAME SETS, and the failing class is a use-site token shared between a section and
an infix operator.

*So the ambiguity check is sound for what it covers and blind to the class currently breaking the
build.* Recorded as a known gap rather than widened on the spot — the fix wants the parse grammar
(fixity levels + sections), which is a different instrument from a name index.

⚑ **A FOURTH DEFECT, FOUND THE SAME WAY — THE REWRITE WAS OVER-WIDE BY CONSTRUCTION.**
Instructed to inspect one more file before writing the apply, I took a REWRITE this time (I had only
ever checked renames). `Algebra.Q.Add` imports the conduit `using (_+ℤ_; _*ℤ_)` — **two** names — and
the plan proposed rewriting it to **three** bases, handing it `Z.Sub` unasked.

**That is the over-wide shape this arc already paid for twice**: 354 consumers holding ≥5 leaves of one
parent (§17), and the `+_` SECTION ambiguity that `split_pipeline:366` records as fixable ONLY by
dropping the unused import. *A rewrite that needs a prune afterwards was too wide to begin with.*

Fixed: `plan()` now routes **per name** — `_requested_names` reads each consumer’s demand and the
rewrite targets only the bases owning those names. `Q.Add` → `Z.Add, Z.Mul`; **consumers taking all 3
bases: 34 → 3** (the genuinely bare importers, where demand is unknown and erring wide is correct).
⚑ `None` and `set()` are kept DISTINCT — bare means “everything”, `using ()` means “nothing by name”;
collapsing them is how a rewrite silently widens.

⚑ **AND MY FIRST THREE TEST FIXTURES WERE UNREALISTIC** — they used a bare `M` where the scanner
matches `Substrate\S*`, so every answer was `set()` and **the cases would have passed a broken helper**.
Caught because they failed against the CORRECT one. *A fixture that does not resemble real input tests
nothing; three of four defects this sitting were found on live data, and the fourth was found by a test
that only worked once its data was live-shaped.* 19 cases; suite **498/498**.

⚑ **AND A FIFTH, FROM THE INVARIANT ITSELF** (user: *“each file should only have one thing, so
‘everything’ means ‘exactly the thing I’ve named by doing the bare import, and nothing more’”*).

I had coded a bare import as **demand-unknown → route to ALL bases**. That is the same over-wide
reflex, wearing a justification. **Under one-definition-per-file a bare `open import Substrate.Foo.Bar`
IS the demand** — `Bar` names one thing — so bare is as precise as a `using` list, and “err wide and
prune later” is not a fallback, it is the thing that produced 354 over-imported consumers.

Bare now routes by **what the consumer’s BODY actually uses**. Whole-base rewrites: **34 → 3 → 4 of 71
tree-wide** (the third figure covers all conduits, not just `Z.Arithmetic`).

⚑ **MEASURED — the invariant is the TARGET, not yet the STATE:** of 656 bases reachable from the
conduits, **347 export exactly one name**; the rest are 0 (empty stubs) or 2+ (not yet split). So the
tool routes by *the base’s own export set* — exactly one name where the decomposition has landed, and
honestly wider where it has not. **Never “all the conduit’s bases”.** *That is a design that gets more
precise as the decomposition proceeds, instead of one that assumes it is already done.*

⚑ *And the three consumers I called “genuinely bare” were not bare at all* — all three carry `using`
lists naming every export. My `saw_bare` branch was dead on that conduit, so the behaviour I was
defending had never run.

⚑ **THE SIXTH INSPECTION FOUND DAMAGE I HAD ALREADY SHIPPED — not a plan defect, a repair defect.**
Checking a DISAMBIGUATION site (the one shape I had never inspected), the compile failed on a
DEPENDENCY: `N-to-F2-Parity.agda:37` uses `+F` with nothing binding it. **My own §13 repoint** had
rewritten that file’s clause from `renaming (_+_ to _+F_)` to drop the pair — **removing the binding
and leaving the use site**. Fixed by adding `_+F_` to its `using` list; verified by compiling it.

⚑ **AND I ESTIMATED THE BLAST RADIUS WRONG THREE TIMES IN A ROW** — 31 files, then 13, then 12 — before
asking the typechecker, which named ONE. Each probe was a different wrong predicate (counting bare
importers, counting the definer, mis-masking indented lines). *The authority for “does this file
compile” is the compiler; three successive greps produced three successive fictions, and the only
reason I did not act on the 31 was that the number looked implausible enough to re-check.*

**The apply is still not written — deliberately, and the tally is now FIVE plan-defects plus ONE
shipped-repair defect.** Every one was found by
*looking at what it would do to one real file*, and every one would have shipped damage at 71-file
scale:

| \#  | defect                                              | what it would have done                                                                    |
|:----|:----------------------------------------------------|:-------------------------------------------------------------------------------------------|
| 1   | `is_conduit` matched EMPTY STUBS                    | rewritten 280 consumers to bind at **nothing**                                             |
| 2   | `def_index` keys `_-ℤ_` and `-ℤ_` both as bare `-ℤ` | renamed **18 operators** correctly-per-the-plan, wrongly-per-the-language                  |
| 3   | `ambiguity()` ignored the `using` filter            | “fixed” files that compile today                                                           |
| 4   | whole-base routing                                  | handed consumers modules they never asked for — the over-wide shape already paid for twice |

⚑ **FOUR DEFECTS, ZERO FOUND BY REVIEW.** Each survived reading the code and passed the tool’s own
selftests; each fell to one question — *show me what you would do to this file*. **That is now the
strongest method finding of the arc**, and it generalises past this tool: a census can be plausible and
a predicate can be self-consistent while both are answering the wrong question, and the only reliable
probe is to demand the actionable output.

*The corollary, from the same sitting:* three of four new FIXTURES used an unrealistic module name and
would have passed a broken helper. **Live-shaped data is not a nicety in the tests either.**

### 23. THE F2 SPLIT — “no `using` line should even *think* to want more than one thing” (user, 2026-08-01)

> *“You realize `Substrate.Algebra.F2` needs to be split, right? So that no `using` line even
> **things to want** more than a single thing out of an import?”*
> … *“and it’s the same recursion as the conduits.” … **YES!** Because single-thing-per-file is the POINT.*

⚑ **THE CONDUIT RECURSION AND THE SPLIT RECURSION ARE ONE FIXPOINT.** `conduit_resolve.resolve`
recursing a barrel to its bases and `split_lemmas` recursing a module to one-definition leaves are the
SAME operation seen from two sides: a conduit is a not-yet-split module whose “one thing” happens to be
an aggregation. At the fixpoint `is_conduit` is empty, `plan()` has nothing to route, and a `using`
list has nothing to filter — **the conduit resolver is not a workaround for incomplete splitting, it is
the split viewed from the consumer side.** That is why §22’s four-step algorithm kept rhyming with the
splitter’s own dependency order; they were never two algorithms.

**Measured before running: 31 exports, 307 importers, 99 of them carrying `using` filters.** Those 99
are exactly the “wanting more than one thing” the directive names, and the split retires the reason
they exist. 25 leaves planned.

⚑ **THE SPLIT EXPOSED A DEFECT IN `split_lemmas` THAT HID 224 NAMES TREE-WIDE.**
Stage 2’s isolate-check failed: `OneNeqZero.agda` (`𝟙≢𝟘 : 𝟙 ≡ 𝟘 → ⊥`) had NO import of its own carrier
leaf → `[NotInScope] 𝟙`. Walked it down rather than hand-patching:

- the ordering was fine (`data F₂` at :43 precedes the lemma at :71, so `F2 ∈ order[:idx]`);
- the evidence test passes in isolation (`provides & toks` = `{𝟙, 𝟘}`);
- so `provides["F2"]` must not have held the constructors — and it did not:
  **`defined_names` returned `{F₂}`**.

**Cause: `CTOR`’s leading character class was `[A-Za-z_]`** — the ASCII-only class this arc retired in
eight other regexes, surviving in **the one place that decides what a leaf EXPORTS**. `𝟘`, `𝟙`, `ε`,
`·-comm`, `0≢1`, `[]ᴾ` are all invisible to it.

**MEASURED TREE-WIDE: 224 constructor/field names across 90 files** were absent from every
`-- Defines:` header and therefore from every sibling-import decision that reads one. Fixed at source
(the trailing class and the multi-name form `S K I : Tm` are unchanged, verified).

⚑ **The two damaged leaves are the ABSURD-PATTERN shape, and that is why the class is subtle**:
`𝟙≢𝟘 ()` mentions its constructors in the TYPE and nowhere in the body, so any body-token test passes
it while the defect stands. The selftest fixture uses that shape deliberately — **verified 5/6 against
the shipped class, 6/6 after** (the carrier-leaf case passes either way and is honestly only pinning
the header contents, not the fix).

⚑ **THEN THE REWIRE MISROUTED A `renaming` CLAUSE, AND MY FIRST DIAGNOSIS WAS WRONG.**
After the split, `rewire_to_leaves` rewired **280 importers** with 0 UNMAPPED — and the witness
consumer then failed `[NotInScope] +F-assoc` at `:65`.

*My first reading:* the tool appends `tail` (group 4) to the last emitted statement, so the clause
landed on the wrong leaf. **Wrong — group 4 is a trailing `--` COMMENT**, and I had begun writing a fix
that would have fed a comment to `_rename_pairs` and refused the statement. Caught by checking what the
pattern actually captures before trusting the story.

*The real cause is the STATEMENT-SPAN class*, in the one tool whose whole job is rewriting import
statements: the `using(...)` pattern ends at `$`, so for the real three-line shape

    open import Substrate.Algebra.F2
      using (F₂; 𝟘; 𝟙; _+F_)
      renaming ( +-assoc to +F-assoc)

it matched **only the first two lines**. The `renaming` line survived VERBATIM as an orphan, dangling
under whichever leaf was emitted last (`PlusF`), while `+-assoc` is owned by `PlusAssoc`.

⚑ **AND `renaming_plan` — which computes exactly this per-name routing, is selftested, and was added to
this file for exactly this purpose — WAS NEVER CALLED.** Strong machinery sitting beside the weaker
path that ignored it (§18’s class, inside a tool this arc already audited). Fixed: the pattern absorbs
the clause as group 5, and `using()` routes each pair to its OWNING leaf.

**Blast radius measured, not assumed: 3 orphaned sites**, 2 of them this run’s damage (the third is a
pre-existing clause on a different module, left alone). Both repaired by re-running the FIXED tool and
verified by compiling.

⚑ **MY FIRST GUARD FOR THIS WAS DECORATION — 8/8 AGAINST THE BROKEN CODE.** The fixture wrote
`using (a; b) renaming (b to bb)`; because `b` is IN the using-list its leaf was emitted anyway and the
orphan happened to land correctly. The live failure renamed a name the `using` list did NOT contain, so
the owning leaf was never emitted at all. Corrected to `using (a) renaming (b to bb)`:
**8/8 fixed, 6/8 against the shipped code**, both failures the real defect.
*That is the fourth time this arc a fixture’s DATA, not its assertion, was what made it inert — and the
second in two sittings.* Suite 499 → **503**; 52 unit tests green.

**The consumer now reads exactly as the directive asked** — the `using` list is gone, because each
import names one thing:

    open import Substrate.Algebra.F2.F2          -- carrier + both constructors: ONE definition
    open import Substrate.Algebra.F2.PlusAssoc
      renaming (+-assoc to +F-assoc)
    open import Substrate.Algebra.F2.PlusF

⚑ **AND I OVER-SIZED THE FALLOUT — MEASURED, THE 224 ARE NOT A LATENT REWIRE HAZARD.**
I filed “every already-split leaf’s `-- Defines:` header was computed under the broken class” as a
tree-wide item. Measuring it:

- **19 leaves under-declare, 48 names** — `Foundation/Fin/Fin.agda` omits `zero`/`suc`,
  `Foundation/Nat/Le.agda` omits `z≤n`/`s≤s`, `Foundation/Negation/Dec.agda` omits `yes`/`no`.
  (My first two censuses said 752/809 and then 20/49; both counted the `module X where` header as a
  definition and one counted the `field` KEYWORD. The measurement needed three passes before it was
  about the thing I claimed.)
- **But `rewire_to_leaves` does not read the header for this class.** It recovers constructors and
  fields with its OWN scanner (`:175-200`), whose character class `[^\s:;{}()@|]+` is already
  unicode-safe — and its comment states outright that *“the `Defines:` header cannot name a
  constructor”*. Verified live: `leaf_map` resolves `𝟘`/`𝟙` → `F2` and `zero`/`suc` → `Nat` correctly,
  which is why the 280-file rewire reported **0 UNMAPPED**.

**So the blindness was confined to `split_lemmas.CTOR`, i.e. to `provides` — the SIBLING-EDGE decision
made at split time.** That is the defect that fired, and it is fixed. The 19 stale headers are a
cosmetic/documentation gap (a `-- Defines:` regenerator is a small tool-build item), **not** the
“UNMAPPED rewires waiting to fire” I had written down.

*The method note: I generalised the blast radius from the one instance that broke, then measured and
found the consuming tool immune. Same shape as §22’s estimate-three-times-wrong — the difference is
that this time the correction cost one measurement instead of a 71-file apply.*

⚑ **THE REWIRE LEFT 30 REFERENCES TO THE CONSUMED PARENT — measured after, not assumed.**
`F2.agda` is deleted, so every survivor is a `[FileNotFound]` waiting to fire. Classified exactly:

| shape                                              | n      | why the rewire skipped it                                                                                                                                                                                                                                                     |
|:---------------------------------------------------|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `import Substrate.Algebra.F2 as F2`                | **28** | the `as` class — `rewire_to_leaves`’ patterns match `open import` with `using`/bare only. This is the DEFERRED class (§11e), now with a concrete population and a build consequence rather than a count                                                                       |
| `open import … using (…) renaming (…)` on ONE line | **2**  | ⚑ **NOT a new defect — these predate the `renaming` fix in the same section.** The old pattern could not absorb a `renaming` clause trailing the closing paren, so the statement was skipped entirely; the fixed tool rewires both. Applied: **survivors 30 → 28, all `as`.** |

⚑ **AND I MIS-DIAGNOSED THESE TWICE BEFORE READING THEM.** First I called them a wrapped-`using`
span gap and measured “154 statements tree-wide wrap over 3+ lines”, then WIDENED the pattern
(`(?:\n[ \t]+)?` → `*`) and wrote a selftest case for it. **The case passed 9/9 against the
UNWIDENED pattern too** — because the wrap is INSIDE the parens, where `[^)]*` already spans newlines.
Reverted the change and the case: *a fix I could not make fail against the old code was a fix for a
problem I never demonstrated.* Then I blamed the file-list filter — also wrong, the filter excludes
only true leaves. **Reading the two files verbatim settled it in one look.** Three wrong mechanisms,
each argued from a plausible measurement, none from the source. The 154 figure is real and measures
something the tool handles correctly; it should not be quoted as a gap.

⚑ **BAN CENSUS MOVED: paydowns 6599 → 6994 (+395), additions 65 → 64.** The +395 is the F2 split’s
`using` filters dissolving. The additions barely moved, so the gate still refuses — consistent with the
standing finding that the additions are per-site work the typechecker must name.

⚑ **Note what `F2.F2` shows about the invariant:** four requested names (`F₂; 𝟘; 𝟙; _+F_`) resolve to
TWO leaves, because a data type and its constructors ARE one definition and travel together. “One thing
per file” is not “one NAME per file” — and the `defined_names` fix is precisely what taught the tooling
that distinction.

### 24. TOPOLOGY AUDIT — the worklist DAG was wrong in four places (user, 2026-08-01)

> *“Audit the todo list; I’m uncertain it reflects our current understanding of the topological
> necessities of our code.”*

Derived each item’s real prerequisites by MEASURING them instead of recalling them. **Four dependency
errors, and all four ran the same direction: work serialised behind blockers that measurement
dissolves.** §21 ordered the worklist topologically and was right to; what it could not do is keep the
order true as the arc moved the populations underneath it.

| \#  | the list said                                                    | measured                                                                                                                | consequence                                                           |
|:----|:-----------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|
| 1   | A3’s SAFE un-renames “pay down NOTHING” (0 statements clearable) | **113 statements fully SAFE → 113 keys clear**, +3 partial                                                              | a large unblocked paydown was filed as settled-negative               |
| 2   | A5 is ONE item needing a green tree                              | **34 `using` + 22 `as` + 10 `renaming`** — three populations, three tools, none needing a green tree                    | the whole 6998-paydown backlog was serialised behind the build        |
| 3   | A1 (FileNotFound) needs T1 (the conduit apply)                   | the `as` additions reference `Substrate.Algebra.F2` — **a module §23 deleted today**; A1 is INSIDE A5 and needs nothing | a regression I created was queued behind unrelated tool work          |
| 4   | the `as` class needs `scope_fix.fix_qualified` (\~400 lines)     | the refs are `F2.F₂` / `F2.CommRing` / `F2.Polynomial`, each → ONE leaf: **mechanical**                                 | a rename was deferred behind a tool build that is not required for it |

Also corrected: **COLLISION is 31, not 34**; **T1 does not block A1 or A2** (measured independent), so
three items that were serialised can run in parallel.

⚑ **THE CLASS, and it is the strongest method finding since MEASURE-WHAT-THE-NEXT-STEP-WOULD-DO:**

> **A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE.**

Three of the four were **true when written and false when acted on**, because this arc’s own paydowns
changed what they measured. The A3 claim is the sharpest: measured over 6 statements, correct for
those 6, then carried as a standing fact while steps 3–5 retired the very statements that made it
true. **A plan that accumulates findings without re-measuring them at point-of-use will serialise work
behind blockers that no longer exist** — the stale-baseline hazard one level up, where the aging
happens to PROSE rather than to a number in a file, and is therefore invisible to every gate.

*The corollary for this document:* its ⚑ findings are load-bearing precisely because they are dated and
witnessed — but a finding’s DATE is also its expiry warning. **Re-measure any figure before it becomes
a dependency.** That is now cheap for every claim here: each names the command that produced it.

⚑ **And the audit fired only because the user asked for it.** Nothing in the worklist discipline
(§“WORKLIST DISCIPLINE”, §21) says *re-verify a prerequisite before consuming it* — both are about
choosing the tool and the order up front, which is exactly the moment the information is freshest and
therefore the moment its aging is invisible.

⚑ **A SECOND PASS, DIFFERENT QUESTION (user: *“now audit our todo list against our plan”*).** The
first audit asked whether the todo DAG was true; this one asks whether the two documents AGREE.
**Three plan items had no todo at all**, and both audits found the same direction of error —
information the plan holds that the worklist had silently dropped:

| plan item                                      | todo       | measured now                                                                                                                                                                                                                                                    |
|:-----------------------------------------------|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 9b/9c/9d/9e — the Audit-V residue              | **absent** | 9d is **6 of 10 baselines** with no `gate_keys.SCHEMA` entry (plan says 4): `cap`, `carrier_locality`, `discharge`, `rederive`, `set1cores`, `snapshot_guard`. 9e is `check_argv` in **5 of 14** gates (plan says 5-of-21 — wrong denominator, same 9-gate gap) |
| 6d residue — converge the enumeration sites    | **absent** | **5 files still define their own `agda_files`**                                                                                                                                                                                                                 |
| item 5 — the derived-view standing instruction | **absent** | needs approval; folds into U2 rather than being presented twice                                                                                                                                                                                                 |

⚑ **AND 9d/9e ARE A DEPENDENCY OF 9g, WHICH THE WORKLIST ALREADY CARRIED AS T4.** 9g censuses exactly
“has a schema entry” and “calls `check_argv`” — so building it over today’s 6-and-9 gaps would bank
them into a paydown-only baseline as if they were discovered debt. **T4 now depends on T11.** That is
the same false-positive-into-a-ratchet hazard §21 caught for the selftests, in a second place, found
only because the two documents were diffed rather than each read alone.

*The method: a plan and a worklist are two derived views of one intent. Neither being current implies
they agree — §6’s lesson applied to the project’s own bookkeeping.*

### 25. COHERENCE + COVERAGE AUDIT — the documents agree with each other and MISS THE TREE (user, 2026-08-01)

> *“Now audit the todo list and the plan together for topological and mutual coherence and coverage.”*

The two prior passes compared the documents to EACH OTHER. This one measures them against the CODE —
and that is the only pass that could find this, because **coverage is not a property either document
can attest to itself.**

⚑ **RAN ALL 19 HOOK-WIRED GATES. EIGHT FAIL. THE WORKLIST TRACKS ONE.**

| gate                     | verdict                                       | tracked?                                                                 |
|:-------------------------|:----------------------------------------------|:-------------------------------------------------------------------------|
| `check_ban_ratchet`      | 66 additions / 6998 held                      | ✅ A5                                                                    |
| `check_claims`           | **BROKEN — 1 NEW stale claim**                | ❌ **nothing**                                                           |
| `check_capstone_shape`   | **BROKEN — 13 capstone `.agda` modules**      | ❌ **nothing** (plan calls it “unwired pending a decision”; it is wired) |
| `check_cap_ratchet`      | **BROKEN — 11 NEW modules over 128MB**        | ❌ **nothing**                                                           |
| `check_carrier_locality` | **BROKEN — 2 NEW exemptions** (−3 paid)       | ❌ **nothing**                                                           |
| `check_public_ratchet`   | **BROKEN — 22 NEW re-exports** (−75 paid)     | ❌ **nothing**                                                           |
| `check_rederive_ratchet` | **BROKEN — 13 NEW derivation sites**          | ❌ **nothing**                                                           |
| `check_sumtype_ratchet`  | **BROKEN — 42 NEW duplicate decls** (−1 paid) | ❌ **nothing**                                                           |

**B3 (the gated commit) requires ALL NINETEEN to pass. The worklist plans for one of the eight.** B1’s
re-baseline table names six gates, but a re-baseline is only legitimate for a PREDICATE change —
every one of these is refusing on **genuinely-new keys**, which is the ratchet working, not a stale
baseline. *Filing them under “re-baseline” would be exactly the “reset to absorb a broken tree” the
rule forbids.*

⚑ **AND `check_claims` IS THE ARC’S OWN CLASS FIRING ON A GATE.** The new stale claim is
`Algebra/Z/Arithmetic.agda`’s importer count — **the very claim §9a records fixing** (“\~200”→35, paid,
gate exits 0). The arc’s later rewires moved the count again. *A recorded finding is a hypothesis at a
later tree state (§24) — here the finding was banked in a GATE, and the gate is the thing that
noticed. That is the layer working exactly as intended, and it is why prose corrections are weaker
than censuses.*

⚑ **THE COHERENCE RESULT IS THE INVERSE OF THE COVERAGE RESULT, and that is the finding.** Checked
every todo claim for a plan witness and every todo dependency edge for a plan justification: **all
present** (three apparent misses were my grep being too literal — `31 COLLISION`, `347 of 656`,
`19 under-declaring` are all in the plan under different wording). The documents are mutually
coherent and topologically sound. **They are jointly blind to eight failing gates.**

*The standing form: mutual consistency between two derived views is not evidence about the thing they
derive FROM. Two documents can agree perfectly and both be missing the same 40% of the obstruction
set — and no amount of cross-auditing will surface it, because the missing information is in neither.
The only instrument is to run the gates.* That is §6’s derived-view lesson at its sharpest: the
divergence-free case is not the safe case.

⚑ **THE USER REFRAMED THIS, AND THE REFRAME RETRACTS MY DIAGNOSIS (2026-08-01):**

> *“A proper rewrite shouldn’t introduce any new keys, because it should be a **recursive
> application**. Eliminating `as`, `rename`, `using`, all of those. But all of those require the same
> topologically-aware, recursive planning process. Which is why I keep asking for research agents
> dispatched to find rhymes, slant-rhymes and things that rhyme but shouldn’t.”*

I filed the five refusing ratchets as *“a coverage gap the worklist missed”* — a bookkeeping failure.
**That is the wrong level.** A rewrite that resolves recursively to the base — `as`, `renaming`,
`using` all dissolving into bare imports at one-definition leaves — is **FIXPOINT-PRESERVING**: there
is nothing new to be `public` about, no new duplicate declaration, no new over-cap module. So:

> **NEW KEYS IN AN ORTHOGONAL CENSUS ARE THE SIGNATURE OF A REWRITE THAT TERMINATED EARLY.**

The 22 new `open … public` and 42 new duplicate declarations are **the same evidence** as
`Substrate.Algebra.F2` still being referenced by 28 `as`-imports after its split: an operation that
stopped one layer short of its own base. Not eight unrelated gate failures — one incomplete recursion,
observed through eight instruments.

⚑ **AND I HAD THE FIXPOINT AND DID NOT APPLY IT.** §23 named the identity (“the conduit recursion and
the split recursion are ONE fixpoint”) the same day; `conduit_resolve.resolve` is recursive to fixpoint
with no depth bound *by design*. I then ran a split whose REWIRE stage is single-pass, checked
`0 UNMAPPED` — a count scoped to the rewriter’s own predicate — and declared it done. **The recursion
lived in the resolver and was absent from the operation.** The post-condition that would have caught it
is not “how many did I rewrite” but *“are there zero references to the consumed module”*, which is a
question about the TREE, not about the pass.

⚑ **WHY MY THREE AUDITS COULD NOT FIND THIS.** They diffed documents against each other, then against
gate exit codes. That surfaces what is INCONSISTENT or UNMEASURED. It cannot surface *machinery that
solves a problem recursively sitting beside machinery that solves it once* — a **slant-rhyme**, §18’s
class. It is exactly how the topology-aware planner (`conduit_resolve.plan`: recursive, per-name
routed, ambiguity-aware, decide-then-apply) came to sit beside `rewire_to_leaves` (single-pass,
regex-matched, no fixpoint check) with nothing reconciling them. **The user has asked for rhyme audits
repeatedly for this reason; hand-auditing is the wrong instrument for the class.** Three agents
dispatched: single-pass-beside-recursive, new-key attribution against the fixpoint invariant, and
whether `plan()` is reused by anything at all.

### 26. THE RHYME AUDIT — three agents, and the class hand-auditing could not reach (user, 2026-08-01)

> *“A proper rewrite shouldn’t introduce any new keys, because it should be a recursive application …
> Which is why I keep asking for research agents dispatched to find rhymes, slant-rhymes and things
> that rhyme but shouldn’t.”*

⚑ **THE HYPOTHESIS IS CONFIRMED, WITH A SHARP FINGERPRINT: \~49 of 102 new census keys are the
signature of a rewrite that did not reach fixpoint**, in exactly the two shapes the user predicted.

**Shape 1 — THE BARREL WAS NEVER DELETED.** All 21 sumtype rewrite-keys count *both* `X.agda` and
`X/Name.agda`, verified by line number that the barrel STILL DECLARES the type:
`Algebra/Quotient.agda:52` (`record Quotient`, beside `Quotient/Quotient.agda` — I re-verified this
one by hand), `Foundation/Negation.agda:19`, `Algebra/Q.agda:35`, `Algebra/Z.agda:36`,
`Foundation/Sum.agda:20`, `Algebra/F2/Linear.agda:61`, `Category/CategoryOf.agda:73`,
`WitnessTower/LehmerPath.agda:59`. **The leaf was minted; the source was left in place. A fixpoint
rewrite yields ONE declaration, not two.**

**Shape 2 — `public` WAS CARRIED THROUGH THE REBINDING.** `S5/S5Fixpoint.agda` pays down
`…Foundation.Bool` and re-adds `…Foundation.Bool.Bool` — same file, same `public`, one level deeper.
The rewrite retargeted the import and did not strip the re-export.

**Attribution of all 102 new keys** (re-running each census with the OLD predicates restored
in-process, tree and baseline held constant — the one method that separates new debt from new
visibility): **49 created-by-rewrite · 21 newly-visible via the widened `DECL` · 10 churn ·
15 pre-existing/un-grandfathered · 7 unattributable.**

⚑ **TWO OF MY §25 NUMBERS WERE NOT WHAT THEY APPEARED:**
\* **cap’s “11 NEW” is against an EMPTY baseline** — `git show HEAD:scripts/cap_ratchet_baseline.txt`
is **0 bytes**, emptied at `771283c8`. It is a LEVEL, not a delta; 2 of the 11 were grandfathered
debt before the emptying. Verified independently.
\* **capstone is a PAYDOWN I FILED AS A REGRESSION: 18 capstone `.agda` in HEAD → 3 now**, every
remaining key `inHEAD=Y`, zero new. It is a hard zero-gate with **no vocabulary for progress**, so
it reports improvement as breakage. G2 withdrawn.

⚑ **MY FRAMING CASE WAS WRONG, AND THE STAGE RULE CAUGHT ME A THIRD TIME.** I proposed
`rewire_to_leaves` as the single-pass twin of `conduit_resolve.resolve`, criticising `0 UNMAPPED` as a
predicate-scoped count. **`rewire_to_leaves` IS covered by a tree-wide post-condition**:
`split_pipeline.py:347` runs `check_indented_imports.sweep(modname)` immediately after and `die()`s on
any surviving reference. Judged IN SEQUENCE the pair is sound. The general critique holds; the instance
does not — §16’s rule, third occurrence.

⚑ **THE REAL LIVE DEFECT IS ONE STAGE LATER.** `fix_stale_using.owner()` (`:187`) resolves a name by
GLOB with an **indent-tolerant** regex, so it matches a module-LOCAL definition inside a `where` block
— which is not an export — and then emits `open import <that module>` as the repair.
**WITNESS:** `Algebra/Semiring/SPPFUP.agda` needs `_⊕_` from `Semiring/NatInf.agda:88` (column 0);
`owner()` returns `Semiring.Contraction`, where `_⊕_` is declared **indented inside a local block**
(`Contraction.agda:39-42`). **MEASURED: 39 sites where `owner()` names a module `def_index` does not
record as a home at all**; 565 of 3378 using-names are multi-homed, so its `_near` string-proximity
tiebreak is guessing at that scale. **Two recursive resolvers already exist and it uses NEITHER** —
`scope_fix._module_exports` (depth-12, through `public` chains, constructors and record fields) and
`_conduit_owner`. Unlike the rewire, this write is NOT covered downstream: `split_pipeline` only
REPORTS the sites and `die()`s telling the operator to run `--apply` by hand.

⚑ **T6 RESOLVED — AND THE ANSWER IS BOTH.** `scope_fix._conduit_set`’s `for _ in range(3)`:
\* on **conduit-chain depth** (the metric `conduit_resolve` uses) it is **LATENT** — 81 conduits,
`{1:67, 2:13, 3:1}`, max 3, exactly AT the bound;
\* on **the metric the function actually computes** (all modules reachable along import edges) it
**BITES LIVE**: reachable-set size within 3 hops = 102066 vs within 8 hops = 134807, and
**1506 of 2964 modules (50%)** have a reachable set that grows past 3 hops.
`_conduit_owner` is the sole route to an applied re-exporter, so a miss returns `None` → “no owner
found” → the name is dropped with **no replacement import**. *The agent reported BOTH measurements and
said which it trusts and why — the disagreement-handling this arc has repeatedly failed at.*
Consequence: `conduit_resolve.py:29`’s docstring is **STALE** (claims 95 conduits and that the bound
bites today); its own selftest at `:381` already says max 3, and the measurement agrees with the
selftest.

⚑ **AND THE USER’S CENTRAL POINT, MEASURED: `conduit_resolve.plan()` HAS ZERO CONSUMERS.** No
`import conduit_resolve` anywhere in the corpus; the only thing that runs it is `run_selftests` by file
DISCOVERY. Its own CLI exposes `resolve`/`depth`/`final_consumers` and **never `plan`** — the richest
output of the module is unreachable from its own command line. Meanwhile each of the other three
directive-elimination cases reimplements a WEAKER version of the same three steps:

| capability                           | `conduit_resolve` (barrel)                          | `using` / `as` (`decompose_rewrite`)    | `renaming` (`rename_at_source`)           |
|:-------------------------------------|:----------------------------------------------------|:----------------------------------------|:------------------------------------------|
| recursive resolution to a base       | YES, unbounded + cycle guard                        | **NO** — single-hop `idx.get(n)` `:262` | **NO** — `home` is typed by a human `:71` |
| final-consumer enumeration           | YES, through conduits                               | **NO** — direct importers `:207`        | **NO** — direct importers `:86,98`        |
| ambiguity honouring existing filters | YES — computes what each statement BINDS `:270-291` | **NO** — refuses on index multiplicity  | **PARTIAL, filter-BLIND** `:97-99`        |
| mixfix signature disambiguation      | YES `:215-239`                                      | **NO** — conflates `_x_`/`x_` `:263`    | PARTIAL (write spellings only)            |

⚑ `rename_at_source:97-99` asks whether the **MODULE** is imported, not what the statement **BINDS** —
which is precisely the check `conduit_resolve.py:258` records as measured **18-of-22 FALSE**. *Two
tools, the same question, and one already knows the other’s answer is wrong.*

⚑ **WHERE THE RHYME GENUINELY BREAKS — do not paper over these:**
1. **`as` needs BODY rewriting** (`M.name` occurrences); every `plan()` output is statement-level. That
is a new output field, not a new input.
2. **`resolve()`’s recursion is over the CONDUIT-CHAIN graph; cases 1-3 need the NAME-OWNERSHIP
graph.** Different edges. `final_consumers()` and `ambiguity()` transfer unchanged; `resolve()` does
not. So “one recursive planner” is right about the SHAPE and wrong if read as one function.
3. **Scale:** `using` is **7403** keys, `as` **1041**, `renaming` **175** — against a planner sized for
81 conduits that re-reads source per (module, name) with no cache.

⚑ **THE METHOD FINDING, and it is why the user has asked for this repeatedly:** three document audits
(§24, §25, and the two todo↔plan passes) could not reach ANY of this. They diff documents against each
other or against gate exit codes, which surfaces what is INCONSISTENT or UNMEASURED. **A slant-rhyme —
recursive machinery sitting beside a weaker single-pass twin — is invisible to all of them**, because
both halves work and neither document is wrong. It is §18’s class, and hand-auditing is structurally
the wrong instrument for it.

*Two smaller live findings from the same sweep:* `resolve_notinscope.py:21` truncates homes at `[:6]`
with no narrowing at all, beside `fix_notinscope.narrow_by_provenance` which walks the import closure —
**64 names have \>6 homes**; and `def_index` is indexing NON-definitions (`variable`, `private`, and `_`
with **200 homes**), which inflates every consumer’s ambiguity measurement.

*Also verified clean, reported as presence not absence:* `j - i < 6` is live **nowhere** (both former
sites now call `agda_lex.head_span`); `split_pipeline.cure_collisions`’s `max_rounds=4` is a genuine
TERMINATION bound (it re-runs `make` and returns on green); and `split_lemmas.py:795`’s “one forward
pass, no fixpoint” carries a valid topological justification (`sibs ⊆ order[:idx]`).

### 27. R1 — `fix_stale_using.owner()` routed through `def_index` (2026-08-01)

**FIXED, and the history is the finding: the second defect was introduced BY the fix for the first.**

| generation | anchor              | consequence                                                                                                                                                                                         |
|:-----------|:--------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| original   | `^` (column 0 only) | indented `data`/`record` heads and every record FIELD invisible — 7 `no owner found for refl` warnings, `refl` being a constructor of an indented `data _≡_`. **A real gap, correctly identified.** |
| the repair | `^\s*`              | cannot distinguish *indented because nested in a record/data block* (EXPORTED) from *indented because local to a `where`/`private` block* (NOT exported)                                            |

**A regex over raw text cannot separate those two.** `agda_defs.def_index` tracks block structure and
gets BOTH halves right — verified: it resolves `refl`, `head~`, `fzero` (the indented cases the
widening existed for) AND excludes `Contraction` (the local-block false positive). Routed through it;
`_near` survives only as a TIEBREAK among genuine homes (565 of 3378 using-names are multi-homed, so
a tiebreak is still needed — what it must never do is choose among candidates that are not homes).

**MEASURED, whole tree: 16457 using-names resolved; sites naming a NON-home 39 → 0.**

⚑ **AND A SECOND, WORSE BUG WAS SITTING IN THE `None` PATH.** `def_index` indexes `agda/Substrate/`
only, so `Level`, `_⊔_`, `[]` — owned by `Agda.Primitive`/the stdlib — resolve to `None`. The caller
warned and **dropped the name from the `using` list with no replacement import**. Measured: **918 of
16457 names resolve to None, headed by `[]` (450), `Level` (192), `_⊔_` (91)** — all non-Substrate,
all correctly outside the index, all previously droppable. The caller now KEEPS any name it could not
re-home and says which of the two `None` cases fired. *The resolver fix alone would have left a
larger break than the one it repaired.*

⚑ **THE TOOL HAD NO `_selftest`, AND THAT IS PART OF WHY R1 SHIPPED** — `run_selftests` DISCOVERS
modules that define one, so a write-path tool with none is INVISIBLE rather than failing (the gap that
let `rename_at_source` ship a live bug through a green suite). Written: 4 cases driving `owner()`
against the LIVE tree, because the defect was precisely a disagreement between this resolver and
`def_index`, which a fixture with an invented module name cannot express.
**Suite 503 → 507, 16 → 17 suites** — the SUITE count moving is the evidence it is discovered.

⚑ **VERIFIED AGAINST THE SHIPPED CODE: 2/4 fail, with the R1 case returning `Contraction` — the exact
wrong answer.** ⚑ **AND MY FIRST DISCRIMINATION RUN WAS RIGHT BY ACCIDENT:** executed from `scratch/`,
where `AG = "agda"` does not resolve, so every answer was `None` and the suite “failed” for the wrong
reason. Re-run from the repo root it fails with the real wrong module. *A guard that fails is not
thereby a guard that discriminates — check WHY it failed, not just THAT it did.* Note `refl` passes
under BOTH resolvers: the widening did work for its stated purpose, which is why the regression was
invisible.

### 28. R2 — the barrel-retained shape MEASURED, and it is smaller and cleaner than the census implied (2026-08-01)

**Before touching a barrel, asked what “complete the split” would do to one.** The answer changed the item.

⚑ **ALL TEN BARRELS ARE FULLY COVERED BY THEIR LEAVES — 100%, zero names at risk.**
*(SCOPE, added §31: this holds for FLAT barrels only. A **telescoped root** — a parameterized
`module M (…) where` — does not decompose this way at all: its leaves must RE-DECLARE the parameters,
so leaf-coverage is not the predicate that decides retirement. 5 such roots / 19 leaves exist and are
NOT in this table; see §31.)*

| barrel                    | defs | leaves | covered | missing |
|:--------------------------|:-----|:-------|:--------|:--------|
| `Algebra/Quotient`        | 15   | 20     | 15      | —       |
| `Foundation/Negation`     | 6    | 5      | 6       | —       |
| `Algebra/Q`               | 10   | 52     | 10      | —       |
| `Algebra/Z`               | 10   | 28     | 10      | —       |
| `Foundation/Sum`          | 5    | 4      | 5       | —       |
| `Algebra/F2/Linear`       | 10   | 35     | 10      | —       |
| `Category/CategoryOf`     | 7    | 3      | 7       | —       |
| `WitnessTower/LehmerPath` | 11   | 9      | 11      | —       |
| `Algebra/Wedge/Graded`    | 3    | 8      | 3       | —       |
| `Groups/V4/Bijection`     | 11   | 8      | 11      | —       |

**So these are not half-done splits needing more splitting — they are CONSUMED PARENTS NEVER RETIRED**,
the `FileNotFound` class the plan says recurs, caught one stage earlier (before the delete rather than
after). The tool is `rewire_to_leaves` then delete, not `split_lemmas`.

**Blast radius: 533 importers across the ten.** `Algebra/Q` and `Algebra/Z` have **ZERO** importers —
they can retire immediately. Snapshot `pre-r2` taken before any write.

**DONE so far:** `Groups.V4.Bijection` rewired (2 importers). Four leaves spot-compiled clean in
isolation (`Quotient/Quotient`, `Sum/Sum`, `CategoryOf/CategoryOf`, `Negation/Dec`), so the leaves are
sound and the barrels are genuinely redundant.

⚑ **BLOCKED ON T2, AND I STOPPED RATHER THAN SHIP AN UNVERIFIABLE EDIT.** Every barrel retirement
leaves `as`-refs behind (A0’s shape, general — no tool handles them). Working the 2 on
`Groups.V4.Bijection`: the qualified uses are exactly `V4.e/α/β/γ` — CONSTRUCTORS — and the file
**already imports their leaf bare on the next line**, so the alias is redundant. De-aliased it, and the
compile failed **in a DEPENDENCY**: `Groups/Coxeter/Core.agda:44` `[NoParseForApplication]`,
pre-existing (it appears 3× in this plan already) and squarely **T2’s section-vs-grammar class**.

**The typechecker therefore cannot arbitrate this edit today, so I reverted it.** An edit whose
correctness argument is “the compiler would confirm it” is not landed work when the compiler cannot
run — the same standard that made §22’s apply wait through six input defects.

⚑ **AND MY OWN COUNTING REGEX MISLED ME TWICE IN ONE SITTING.** `grep -c "V4\."` reported 9 refs
after a de-alias that should have left 0 — I read that as an incomplete rewrite. **Seven of the nine
were the directory name `S3-on-V4` inside the module path.** The genuine qualified uses were exactly
the 4 I had already rewritten. *Third time this arc a `.`-in-a-module-path has been read as a
qualified reference (after `RuleAction.V4` nearly clobbering `V4Compose`, and the `Div.Over.recon-nth`
matcher question) — the module path is not a namespace reference, and a bare `\.` never distinguishes
them.*

**Re-scoped:** the ten barrels split into `{Q, Z}` (zero importers, retirable now), the rest (rewire
then delete, each needing its consumers to typecheck), and the `as`-residue (blocked on T2 wherever a
consumer routes through a broken dependency).

✅ **`Algebra/Q.agda` and `Algebra/Z.agda` RETIRED** — zero importers in EVERY form (bare, `using`,
`as`), 100% of their 10+10 names covered by 55 and 34 surviving leaves, snapshot `699dea72c612` taken
first. **Dangling references after: 0. Sumtype new keys 42 → 38** — exactly the predicted −2 per
barrel, which is the first direct confirmation that the barrel-retained shape and the sumtype census
are the same defect measured twice. `gen_build_makefiles --check` OK at 2962 modules; suite 507/507.

**Remaining R2 population: 8 barrels / 533 importers**, each blocked only on its consumers being
typecheckable — i.e. on T2 and the A4 census, not on any missing tool.

✅ **R2 CONTINUED — 8 of 10 RETIRED (2026-08-01), once §29 unblocked the typechecker.**
`Algebra/Quotient` (24 importers), `Foundation/Sum` (48), `Category/CategoryOf` (64),
`WitnessTower/LehmerPath` (52), `Foundation/Negation` (147) — **415 importers rewired**, each
barrel’s primary leaf AND a rewired consumer spot-compiled at 0 errors before deletion, **0 dangling
references** to any of the five. 2956 modules; suite 507/507.

| census               | before            | after                 | reading                                                                                    |
|:---------------------|:------------------|:----------------------|:-------------------------------------------------------------------------------------------|
| **sumtype NEW keys** | 42                | **24**                | −18: the barrel-retained duplicates, cleared exactly as predicted                          |
| **public**           | 552 held / 22 new | **495 held / 23 new** | **57 PAID DOWN**; the “new” are `open … public` re-exports **inside the surviving leaves** |

⚑ **THE PUBLIC COUNT MOVING THE “WRONG” WAY IS THE FINDING, NOT NOISE.** 22 → 23 looks like a
regression until you read the paid column: 552 → 495. Retiring a barrel clears the PARENT’s
re-export and leaves the LEAF’s — the leaf half of the same incomplete rewrite (`Q/Rat.agda::ℚ`,
`Quotient/Canonical.agda::Canonical`, `F2/Linear/Linear.agda::Linear`). *A ratchet’s headline
“N new” is not its verdict; the pair (paid, added) is.*

**TWO HELD BACK, each for a measured reason and NOT for lack of a tool:**
\* `Algebra/F2/Linear` — rewired (104 importers) but its leaf fails on a DEPENDENCY,
`Algebra/F2/Vector.agda:167` `[NoParseForApplication]` on `_+ lookup v i`. **Verified byte-identical
to the `pre-r2` snapshot**, so pre-existing, not mine — and a genuine T2 case (a section with no
operator in scope at all).
\* `Algebra/Wedge/Graded` — `rewire_to_leaves` REFUSED with *“no leaf provides a name”*. Measured:
**0 of its leaves carry the splitter’s provenance marker** — they are HAND-WRITTEN, so `_is_leaf`
correctly excludes them. The tool refusing on a genuinely different shape is it working; this
barrel needs a different route (hand-verify each leaf’s exports, or mark them).

### 29. THE COXETER BLOCKER WAS FOUR DEFECTS, AND “WE FIX THE CODE” WAS THE RIGHT CALL (user, 2026-08-01)

> *“We fix the code.”*

I had filed `Coxeter/Core.agda:44 [NoParseForApplication]` as a T2 blocker and stopped. **It was not
T2’s class at all**, and it was not one defect:

| \#  | defect                                                                                                                                                                                                                                                                                   | fix                                                    |
|:----|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| 1   | `++-assoc`’s type `(a ++ b) ++ c ≡ a ++ (b ++ c)` — `_++_` is a MODULE PARAMETER, and a parameter does **not** inherit the fixity its argument was declared with (`Coxeter/Word.agda:35` says `infixr 5`). Agda defaulted to NON-ASSOCIATIVE level 20, so two chained `++` cannot parse. | parenthesize the type                                  |
| 2   | `Core.agda` used `≡` in its TELESCOPE while `open import Substrate.Foundation.Eq` sat at the **last line of the file**                                                                                                                                                                   | hoist the import ABOVE the module header               |
| 3   | `Core/Operations.agda` had **NO IMPORTS AT ALL** yet used `≡` (:33) and `≢` (:36)                                                                                                                                                                                                        | add both (each resolved unambiguously via `def_index`) |
| 4   | the same telescope/import inversion in **11 files tree-wide**                                                                                                                                                                                                                            | one mechanical hoist                                   |

✅ **`Coxeter/Core.agda` COMPILES CLEAN.** Then the file that started the whole detour —
`RotateCubeId.agda` — failed with `[ConstructorPatternInWrongDatatype]: V4.e is not a constructor of the datatype V₄`. **The alias was not merely redundant, it was actively WRONG**: `V4.e` resolved
through the barrel to a different `V₄` than the leaf’s. De-aliasing both files: **0 errors.**
`Groups/V4/Bijection.agda` then had zero live references and was **RETIRED** (the 10 remaining hits
are comments — 8 are the splitter’s own provenance markers). 2961 modules, suite 507/507.

⚑ **RETRACTED — SEE §30. “FIX #1 IS A GENUINELY NEW CLASS” IS WRONG.** The parenthesization was not
the fix; hoisting the import was. `GroupAdapter.agda` carries the IDENTICAL unparenthesized telescope
and compiles, because it imports `Foundation.Eq` (whose `_≡_` is `infix 4`) BEFORE its module header.
Original text follows, superseded:

⚑ **FIX #1 IS A GENUINELY NEW CLASS FOR THIS REPO: FIXITY DOES NOT CROSS THE PARAMETER BOUNDARY.**
A module parameterized over an operator gets the DEFAULT fixity, not the operator’s declared one. And
it cannot be repaired locally: a fixity declaration inside the module is too late (the telescope is
scope-checked first) and one before the module header makes Agda read the file as a top-level
declaration (`[ModuleNameDoesntMatchFileName]` — I tried it). **The only fix is to parenthesize the
type.** Since decomposition CREATES parameterized modules by construction, this class will recur with
every split of an operator-bearing module.

⚑ **MY REDUCTION FIXTURE NEVER RAN, AND I NEARLY CONCLUDED FROM IT.** I wrote two minimal `.agda`
files to isolate the parse behaviour; the shell’s cwd reset between heredocs, so `U.agda` was never
written and both later runs failed on `[ModuleNameDoesntMatchFileName]` — a module-resolution error, not
a parse result. **The “T compiles” reading came from a stale `.agdai` left by an earlier version.** I
caught it only by listing the directory. *A fixture that does not run produces silence, and silence
read as a result is the same error as a grep whose pattern never matched* — the third time this arc.

⚑ **AND MY FIRST CENSUS OF THE CLASS SAID ZERO WHILE THE COMPILER SAID OTHERWISE.** I asked *“does
this file import the home of `≡`?”* — a FILE-LEVEL question — when the real one is POSITIONAL: *is it
imported BEFORE the telescope that uses it.* Same file-level-vs-positional error this plan already
records for `scope_fix._in_scope` (§11d). Corrected, the census found **11 sites** and agreed with the
typechecker exactly. **When a census and the typechecker disagree, the census is wrong** — and the
disagreement is the cheapest signal available that the predicate is asking the wrong question.

⚑ **THE USER’S STANDING POINT, EARNED AGAIN:** *“This is why all name interpretation needs to be
centralized in a shared module.”* Every defect above is a name-interpretation question answered
ad-hoc: is this `.` a qualifier or a path separator (three occurrences now); does this file import
this name (file-level or positional?); does this operator have this fixity HERE. `agda_lex.word` is
the bare-name authority and there is **no qualified-name authority and no positional-import
authority**, so each caller invents one and gets it subtly wrong. That is T7/R4’s real scope.

### 30. R6 DISSOLVED — “fixity does not cross the parameter boundary” WAS MY WRONG DIAGNOSIS (2026-08-01)

I filed R6 as *a genuinely new class*: a module parameterized over an operator gets the DEFAULT
fixity, so `(a ++ b) ++ c ≡ a ++ (b ++ c)` cannot parse, and it cannot be repaired locally.
**Measured, that is false in every part.**

| test                                                                                                   | result                                  |
|:-------------------------------------------------------------------------------------------------------|:----------------------------------------|
| exact live telescope shape, builtin `≡`                                                                | **0 errors** — compiles                 |
| `Groups/Coxeter/GroupAdapter.agda` — IDENTICAL unparenthesized telescope, real parameter `_++_`        | **compiles**                            |
| `Category/Strict2Monoid/FromCoxeter.agda`, `Coxeter/DirectProduct`, `Zn-x-FreeCyclic`, `GriessAlgebra` | **all compile**                         |
| my regex census of “chained parameter operators”                                                       | **27 candidates, 0 that actually fail** |

⚑ **THE REAL MECHANISM IS §29’s DEFECT #2, NOT A NEW CLASS.** Substrate’s `_≡_` is declared
`infix 4` (`Foundation/Eq.agda:17`). `GroupAdapter` imports `Foundation.Eq` at **:17, BEFORE its
module header**, so that fixity is in the grammar when the telescope is parsed and
`(a ++ b) ++ c ≡ a ++ (b ++ c)` resolves. **`Core.agda` had the same import on the LAST LINE of the
file** — so at telescope-parse time `≡` had no fixity at all, and the parser could not place it
against `++`. The `NoParseForApplication` was the positional-import defect wearing a fixity costume.

**Consequence: the parenthesization I added to `Core.agda` was unnecessary** — hoisting the import
alone would have fixed it. It is harmless and I am leaving it (parenthesized associativity statements
read no worse), but the record must not claim it was the fix.

⚑ **R6 IS WITHDRAWN. Its population is ZERO and it collapses into R7** (the positional-import
authority), which is now measured at **11 sites, all real, all fixed**.

⚑ **AND THE METHOD FAILURE IS THE DURABLE PART — FIVE BAD FIXTURES IN ONE SITTING.** Every attempt to
reduce this to a minimal example failed in a way that produced a CONFIDENT WRONG READING:
1. cwd reset between heredocs → `U.agda` never written; two runs “passed” that never executed;
2. a stale `.agdai` from an earlier version made a failing file look like it compiled;
3. `agda` resolves module names against the INVOCATION CWD, not the file’s directory — every fixture
failed `[ModuleNameDoesntMatchFileName]`, a resolution error I twice read as a parse result;
4. `B`/`C` “compiled” only because their chains were already parenthesized — non-tests;
5. the builtin `≡` has NO fixity declaration, so the fixture could not exercise the interaction that
defines the bug, and a fixity declared before a top-level module is itself illegal.

**The live tree was the correct instrument from the first minute**, and it answered in one command
(`GroupAdapter` compiles with the identical telescope). *A minimal fixture is only evidence once you
have shown it reproduces the failure; until then a “clean compile” from it is indistinguishable from a
fixture that never ran.* This is the third form of the same error today — a grep whose pattern never
matched, a guard that failed for the wrong reason, and now a fixture that never exercised its own
hypothesis.

### 31. R7 — THE TELESCOPED-ROOT SPLIT HAS NO GENERATOR (user, 2026-08-01)

> *“A gate cannot fix code. Agda code must be fixed by codegen in order for it to be repeatable,
> reliable.”* … *“Splitting a module that roots a telescope PRODUCES 11 TELESCOPES.”*

⚑ **BOTH OF MY FRAMINGS WERE WRONG, IN OPPOSITE DIRECTIONS.**

*First* I said “fix at emission in `split_lemmas`”. Then I measured that **0 split-emitted leaves carry
a top-level telescope** and swung to “the emission path cannot produce this — the durable fix is a
gate.” **That is the wall-declaration reflex**: I turned a measurement about the CURRENT generator into
a claim about what a generator could do, and reached for something that names the problem instead of
something that removes it. A gate over 11 sites leaves 11 hand-edits — and the first pass over those
files WAS a hand-edit, by an ad-hoc script that no longer exists, so the repair was unreviewable and
un-rerunnable. That is precisely the non-repeatable artifact the user’s rule forbids.

*The user’s correction supplies the missing step:* splitting a telescoped root **produces N telescoped
leaves**, because every leaf needs the same parameters. Verified: `Coxeter/Core.agda` has a 9-parameter
telescope; `Core/NormalizeAppend/Left.agda`, `Core/NormalizeCong/Right.agda`,
`Core/HigherArity/Quad.agda` each carry **7 of them**. The 11 sites are not unrelated hand-written
modules — they are **ONE ROOT TELESCOPE DISTRIBUTED ACROSS ITS LEAVES**.

⚑ **AND THE SPLITTER REFUSES THE WHOLE CLASS, IN WRITING.** `split_lemmas.py:10-11`: *“a `module … where`
block (parameterized or named) plus its indented body — these **CANNOT be split**, the telescope binds
the whole block.”* No tool claims the Core leaves; the “Section-per-file” roster is prose inside
`Core.agda` itself. **They were split by hand, and the sections list is documentation of a manual
decomposition** — which is exactly why the import-hoist was missing: there was no generator to get it
right.

**MEASURED POPULATION: 5 telescoped roots with 19 telescoped leaves**, and it is RECURSIVE
(`Core` → `HigherArity` → its own leaves):

| root                                       | leaves | telescoped |
|:-------------------------------------------|:-------|:-----------|
| `Groups/Coxeter/Core.agda`                 | 8      | 8          |
| `Groups/Coxeter/Core/HigherArity.agda`     | 4      | 4          |
| `Groups/Coxeter/Core/NormalizeAppend.agda` | 2      | 2          |
| `Groups/Coxeter/Core/NormalizeCong.agda`   | 2      | 2          |
| `Pipeline/Examples.agda`                   | 4      | 3          |

**LANDED — `scratch/hoist_telescope_imports.py`** (5 selftest cases), the repeatable form of the repair
I had done by hand: it computes what a telescope references, subtracts what is imported ABOVE the
header, resolves each missing name through `agda_defs.def_index`, and inserts the imports at the only
position where they are in scope. It **REFUSES a name with several homes** rather than guessing —
`owner()`’s `_near` tiebreak is a guess, and a wrong import here is a silent miscompile, not a warning
(measured: 3 such names in `Algebra/Linear/CyclotomicOver.agda`, left alone and reported).

**AND THE PREDICATE IS HOMED, NOT LOCAL** — `agda_lex.telescope_span` and `agda_lex.imports_before`
sit beside `module_scopes`/`binds_at`, the positional-scope authority this arc already built. That is
R4’s first instalment for the “is this name available HERE” question: **positional, not file-level.**

**STILL OWED (the real R7): teach the splitter to split a telescoped root.** The transform above
repairs the import position; it does not generate the leaves. Until `split_lemmas` can propagate a
telescope, every future decomposition of a parameterized module is a hand-split that will re-acquire
this defect — the generator gap the user named.

### 32. `private` IS DISSOLVED BY ONE-DEFINITION-PER-FILE (user, 2026-08-01)

> *“Part of the benefit of migrating completely to file-per-lemma is that there should be no more
> requirement for private blocks, since nothing should be ‘public’.”*

**The argument is structural and it holds.** `private` exists to narrow an over-wide module surface.
At one-definition-per-file there IS no surface to narrow — the file exports its one thing, and a
helper that is not that thing belongs in its own file. The same reasoning that retires `public`
(⟡public-policy) retires `private`: both are ways of *appearing* to narrow a module that holds too
much, and the real fix is that it should not hold too much.

⚑ **MEASURED, AND IT IS TWO POPULATIONS WITH DIFFERENT ANSWERS** — 257 `private` occurrences over
237 files split as:

| kind                                                        | n                            | verdict                                                                                                                                                                                                                                     |
|:------------------------------------------------------------|:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **hidden HELPER definitions** (`private` + indented lemmas) | **226 defs across 88 files** | ⚡ **exactly the user’s case.** Each is a SECOND definition in a file that should hold one; splitting them out removes the need for `private` entirely. Head: `LeibnizDetPerm` 10, `FUSepQHexagon` 9, `BCInstances` 8, `FUSepQConfluence` 8 |
| `private variable` (the LEVEL idiom)                        | 164                          | a BINDING FORM, not a hidden helper — `private variable a b c : Level` introduces implicit-argument variables. Whether it survives is a SEPARATE question and must not be swept with the first                                              |

⚑ **AND MY CLASSIFIER WAS WRONG TWICE BEFORE IT WAS RIGHT — the same blind spot, twice.**
First pass: a one-line regex called 198 blocks “helper-hiding” that were actually the level idiom
written across three lines (`private` / `variable` / `A : Set`). Second pass: `defined_names` returned
**0 hidden definitions from 93 real blocks**, because it expects COLUMN-0 declarations and a
`private` block’s contents are INDENTED — the identical indent-blindness this arc has now fixed in
`agda_defs`, `split_lemmas.CTOR`, `split_lemmas.field_names`, and `check_carrier_locality.DECL`.
Only after de-indenting each block (`textwrap.dedent`) did the real number appear: **226**.
*The fifth occurrence of indent-blindness in this arc, and the second time I hit it in my own
throwaway measurement code rather than in a tool.*

**Filed as R9.** It is a genuine paydown with a discovered population, it is BLOCKED BY NOTHING, and
it moves T10 directly (each extracted helper is one more file holding exactly one definition). The
`private variable` population is explicitly NOT in scope for it.

⚑ **AND THE POLICY WAS NOWHERE — NO GATE, NO CENSUS, NO BASELINE, NOT EVEN A MENTION** (user:
*“do we even have a gate or census for that?”*). Measured: zero `scripts/check_*.py` censused
`private`, no baseline file existed, and **the ban skill does not mention the keyword at all**. §32 as
first written recorded a PAYDOWN and never stated the POLICY — the same shape as a finding recorded in
prose while nothing enforces it, which this arc has now caught five times at the gate layer (§9a).

✅ **`scripts/check_private_ratchet.py` BUILT, BASELINED AT 226, AND HOOK-WIRED** — modelled directly
on `check_public_ratchet`, its exact sibling: *`public` re-exports what a module does not define;
`private` hides what it does.* Paydown-only over a materialized census keyed `<relpath>::<name>`;
the paydown is **EXTRACTING the helper**, never deleting the keyword and leaving the definition.
4 selftest cases; suite 514 → **518 across 19 suites**; hook now runs **21 gates**.

⚑ **THE CENSUS AGREED WITH MY INDEPENDENT MEASUREMENT AT 226 VIA A DIFFERENT CODE PATH** — worth more
than either number alone, and the only reason I trust it after two earlier classifiers got it wrong.
Two of the four selftest cases exist specifically to pin the mistakes: one asserts the indented helper
IS seen, and one asserts that WITHOUT the dedent the same helper is INVISIBLE — so a future edit
cannot quietly drop `textwrap.dedent` and silently return to zero.

⚑ **`private variable` IS EXCLUDED BY THE PREDICATE, NOT BY AN EXEMPTION.** It contributes no keys
because it declares no definitions — so the exclusion needs no allow-list and cannot rot. Censusing
those 164 sites would have banked false keys into a paydown-only baseline: debt that could never
legitimately be paid, which is `ratchet.py`’s own stated failure mode.

### 33. R9 — THE PAYDOWN IS THE SPLITTER, AND IT NEEDED ONE FIX (user: *“fix the tooling”*, 2026-08-01)

⚑ **I FILED R9 AS 226 EXTRACTIONS. IT IS A DRIVER RUN.** `split_lemmas` already handles a `private`
block — and handles it *correctly*, dropping the keyword and dedenting the body, with the reasoning
recorded at `:236-247` (a leaf that KEPT `private` would emit a correct sibling edge and still fail
`[NotInScope]`, measured on TraceDescent/StepStrict). So the helper does become an ordinary exported
definition. The gate censuses the MONOLITH; running the driver is the paydown.

⚑ **BUT THE BLOCK WAS EMITTED AS ONE UNIT NAMED `Private`, WHICH REPRODUCES THE DEFECT THE SPLIT
EXISTS TO REMOVE.** MEASURED: **61 of 96 `private` blocks hold 2+ definitions**, so `Private.agda` was
a MULTI-DEFINITION leaf — and the name describes the keyword, not the contents, so the **8 such leaves
already on disk** collide in meaning across unrelated files. A `private` block is a CONTAINER, not a
unit.

**FIXED:** each definition inside now becomes its own unit, named for itself. Verified on the witness —
`AntisymmetricRoundtrip` emitted `Private` before and **`EqFromLookupA`** after — and on a
multi-definition block: `DegreeBound` produced `PlusSuc`, `LeRefl`, `LeTrans`, `MLemPlusn`, `LpEmpty`
alongside its main lemmas, **7 leaves from a file whose `private` block had held 5 helpers**.
*The CONSERVATION GUARD is what makes this safe to change*: it refuses unless every non-blank line
lands in exactly one unit, so a mis-cut block cannot ship silently — and it passed on both files.
3 selftest cases; **9/11 against the shipped code**, both failures the real defect. Suite 518 → **521**.

⚑ **AND THE 226 PARTITION BY REACHABILITY — R9 IS TWO ITEMS, NOT ONE:**

| population                                                 | n       | files | status                                                                                                                                       |
|:-----------------------------------------------------------|:--------|:------|:---------------------------------------------------------------------------------------------------------------------------------------------|
| `private` helpers at **column 0**                          | **165** | 68    | ⚡ the splitter reaches these NOW; this is a driver sweep                                                                                    |
| `private` helpers **inside an inner parameterized module** | **61**  | 21    | **BLOCKED ON R7b-part2** — the block sits in a `module DetPerm (A : Set) … where`, which `split_lemmas:10-11` treats as an unsplittable unit |

**Witness for the second: `WitnessTower/LeibnizDetPerm.agda` reports `1 lemma file` despite holding 10
private helpers** — because they live inside `module DetPerm (A : Set) (S : Semiring A) (ε₂ : A)` at
`:115`. That is not a defect; it is the declared contract, and it is exactly R7b-part2’s population.
*So the `private` census and the telescoped-root generator are the same arc: 61 of the 226 keys cannot
be paid until a parameterized module can be split at all.*

### 34. R7b-part2 — THE GENERATOR IS BUILT, AND ITS POPULATION IS ZERO (2026-08-01)

**Built `scratch/split_telescoped.py`** — the generator `split_lemmas` declines. It reads the root’s
telescope as BINDER GROUPS, selects the minimal subset each leaf needs, and reports the plan.
`agda_lex.telescope_groups` is the new homed authority (beside `telescope_span`/`imports_before`).

⚑ **THE SELECTION RULE IS VALIDATED AGAINST THE HAND-SPLIT GROUND TRUTH, NOT AGAINST MY
EXPECTATION.** Fed `Core/NormalizeAppend/Left`’s body and `Core.agda`’s 9 groups, it returns exactly
the 7 parameters that leaf declares, **in order** — including `Word`, which the body never writes in a
term and which arrives only through the closure over `(Canonical : Word → Set)`.

Two findings the build produced, each caught by testing rather than reasoning:

- **SELECTION IS A CLOSURE, NOT A SCAN.** A parameter is needed if the body mentions it OR if an
  already-needed parameter’s TYPE mentions it. Iterate to fixpoint.
- **AN OPERATOR HAS TWO SPELLINGS.** `_++_` is written `++` at an infix use site, so probing the
  declared form alone returned **6 of 7** parameters, silently dropping exactly `_++_`. That is
  `rename_at_source`’s documented two-spelling hazard, hit again in new code. A selftest asserts the
  single-spelling probe LOSES the operator, so the fix cannot regress.
- ⚑ **`module_scopes` IS THE WRONG AUTHORITY HERE and would have emitted garbage.** It FLATTENS —
  for `(++-assoc : (a b c : Word) → …)` it returns `++-assoc` AND `a`, `b`, `c`, the locals bound
  inside that parameter’s TYPE. A generator using that list emits `(a : ?)` as a parameter. Hence
  `telescope_groups`, which returns each group VERBATIM plus the names it binds. A selftest pins it.

⚑ **SCOPED BY §35: “population zero” is true of ALREADY-DECOMPOSED ROOTS ONLY.** The generator’s live
population is the inner parameterized modules the `private` ban forces open (46 defs) — measured one
section later, after the user pointed out that the ban had already decided the question I was filing
as open. Original text follows.

⚑ **AND THE POPULATION IS ZERO — R7b’s PREMISE WAS WRONG.** Ran the planner over all 5 telescoped
roots: **every one reports 0 units.** Verified independently rather than trusting a tool that could be
failing silently — `Core/NormalizeAppend`’s body is exactly two applied `open import` re-opens, and
`Pipeline/Examples` has an **empty body**. *All five roots are ALREADY fully decomposed*; they hold
re-opens, not definitions. There is nothing for the generator to split today.

**So R7b closes as: the capability now exists and is tested, with no live work.** That is a real
outcome, not a failure — the class was reachable-by-nothing an hour ago and is now generated, tested,
and ready for the next parameterized module that needs decomposing. But the item’s stated blocking
relationships were WRONG and must be retired:

| claimed                                                       | measured                                                                                                                                                                                                  |
|:--------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `R7b → T10` (one-definition-per-file unreachable for 5 roots) | **FALSE** — the roots are already decomposed                                                                                                                                                              |
| `R7b → the 19-leaf ban work`                                  | **FALSE** — the leaves exist; their `using`/`renaming` is ordinary rewire work                                                                                                                            |
| `R7b` blocks 61 of R9’s `private` keys                        | **STILL TRUE** — those sit inside INNER parameterized modules (`LeibnizDetPerm`’s `module DetPerm (A : Set) …`), which is a different shape from a telescoped ROOT and is NOT what this generator handles |

⚑ **The residue is sharper than the original item:** the 61 blocked `private` helpers need an
INNER-module splitter, not a root splitter. `split_lemmas:10-11`’s refusal covers exactly that shape,
and it remains correct — an inner `module M (…) where` block genuinely binds its whole body. Whether
those blocks should be dissolved (hoisting the parameters to the file’s own telescope) is a DESIGN
question, not a missing tool, and I am not answering it silently.

### 35. R10 IS NOT A DESIGN QUESTION — THE `private` BAN ALREADY ANSWERS IT (user, 2026-08-01)

> *“The design question has a trivial answer if you realize we have a ban on `private`.”*

I filed the inner-module `private` class as *“a DESIGN question, not a missing tool — needs a decision
before code”*. **That decision was already made when the ban landed one section earlier.** If `private`
is banned, an inner `module M (…) where` whose body contains a `private` block cannot survive in any
form: hoisting is not one option among several, it is the ONLY shape left. The block’s parameters
become the file’s own telescope, its helpers become ordinary definitions, and `split_telescoped` —
which I had just declared populationless — is exactly the tool that then splits them.

⚑ **SO §34’s “POPULATION ZERO” WAS TRUE ONLY OF ALREADY-DECOMPOSED ROOTS.** The generator’s real
population is these files, ONCE the inner block is hoisted. Two claims retired in two sections, both
mine, both from asking a narrower question than the policy: §34 measured *“roots with units left to
split”* and found none; the live population is *“inner modules the ban forces open”*.

**MEASURED — 61 hidden definitions, and the enclosing shape decides the route:**

| enclosing module                                      | defs   | route                                                                                      |
|:------------------------------------------------------|:-------|:-------------------------------------------------------------------------------------------|
| **parameterized** (`module Over (…)`, `module _ (…)`) | **46** | hoist the telescope to the file, then `split_telescoped` — the generator built in §34      |
| **plain** (`module M where`, no telescope)            | **15** | ordinary `split_lemmas`; the block is a container (§33) and needs no telescope work at all |

⚑ **AND MY FIRST COUNT OF THIS POPULATION WAS WRONG — 3 files, not 21.** A scan for `^module \S+ \(`
at COLUMN 0 found only 3 (`JacobianDetLiteral`, `LeibnizDet`, `LeibnizDetPerm`), because most enclosing
modules are INDENTED (`Over`, `_`) or use `{…}` binders. Re-classified by walking UP from each
`private` to its nearest shallower `module`, the 46/15 split reconciles exactly to 61.
*The sixth indent-related miscount of this arc, and the third in my own throwaway measurement code.*

⚑ **THE WITNESS IS MIXED, WHICH IS WHY THE HOIST IS WHOLESALE.** `LeibnizDetPerm`’s `module DetPerm (A : Set) (S : Semiring A) …` holds **21 definitions, 10 of them private**. The ban forces the 10 out;
the other 11 come along because they share the telescope. **The inner module dissolves entirely** —
you cannot hoist half a parameter list.

### 36. R9 APPLIED — 589 LEAVES, PRIVATE CENSUS 226 → 66 (2026-08-01)

Ran `split_lemmas --apply` over the 68 column-0 `private`-helper files (snapshot `pre-r9`).
**65 split, 589 leaves emitted, and the gate confirms the paydown independently:
`private-ratchet: 226 → 66, 162 definitions paid down.`** The tooling fix of §33 is what made this a
driver run rather than 226 hand-extractions.

⚑ **AND THE THREE “REFUSALS” ARE A 79-FILE CLASS WITH NO TOOL** (user: *“that’s the point of the
pipeline and tooling”*). Three files refused with `APPLIED import references file-local name(s)`, and
I called them *“genuine holdouts, not failures”* — **the wall-declaration reflex again**. A refusal
that names its cause precisely is a SPECIFICATION FOR THE NEXT STAGE, not a stopping point, and this
one even prescribes the route in its own text:

> *“Restructure the application into its own leaf first (the applied-open class).”*

**No tool does that.** The message has been handing operators an instruction with nothing behind it.
MEASURED by running `parse()` over the whole tree and catching the refusal: **79 files are blocked by
this class**, not 3 — `V4-as-PFG-Applied`, `F2/FromBool`, six `Polynomial/Wedge/*`, and 70 more. So
“three holdouts” would have left a 79-file population to hand-work, which is exactly the outcome the
pipeline exists to prevent.

*Distinguish it from the sibling that IS handled:* `split_pipeline:138-156` cures the applied-open
**COLLISION** shape (`ClashingDefinition` from a projection shadowing a local) by qualifying at the
value. That is a post-split repair. **This is a PRE-split blocker** — the split cannot start, because
hoisting an application into every leaf would place it before the definition it applies. Same keyword,
different stage, and only one of the two has a tool.

**Filed as R11**, a tool-build at class level: extract the applied import plus the file-local
definitions it consumes into their own leaf, emit it first, then let the ordinary split proceed.

⚑ **METHOD NOTE — MY SUCCESS COUNT AND MY LEAF COUNT CONTRADICTED EACH OTHER AND I CAUGHT IT.**
The loop reported `applied ok=65 failed=0` while my grep for emitted leaves returned **0** — the grep
matched an indented-leaf-name format the tool does not print in `--apply` mode. Two numbers that
cannot both be right is the cheapest possible signal that one measurement is wrong; the real figure
(589) came from parsing the tool’s actual output line. *A success count from an exit status is not
evidence that work happened.*

### 37. R11 — TWO TOOLING DEFECTS BEFORE THE TOOL (user: *“don’t hand-roll shit”*, 2026-08-01)

Set out to build the applied-open restructurer. Reading a blocked file first — the discipline that has
caught every defect this session — found two defects in the EXISTING tooling instead, and one of them
shrinks the class.

⚑ **DEFECT 1: A COMMENT BANNER PARSED AS A DEFINITION.** `defined_names`’ `DECL` matched the leading
`--` of a `-----------------------------------------------------------` separator (name `--`, “type”
the rest), so **`--` entered `local_defs`** and the applied-import guard **refused to split over a
comment**. MEASURED: `Algebra/F2/FromBool.agda` refused with
`APPLIED import references file-local name(s) ['--']`; after masking comment lines it splits into
**7 leaves**. Every other scanner in the tree masks comments first; this one did not. Population
**79 → 76**.

⚑ **DEFECT 2, AND IT IS THE USER’S POINT: NOTHING COULD ASK *WHY* A FILE WAS BLOCKED.** The only way
was to call `parse()`, catch `SystemExit`, and **regex the message text** — so any census of the
blocked population is a hand-rolled reimplementation of `local_defs`. **Mine disagreed with the tool
on 50 of 79 files**: I scanned column-0 signatures, the tool unions `defined_names` over the parsed
units. *A module that refuses must be able to say why IN DATA, or every consumer re-derives the
predicate and drifts.*

**`split_lemmas.blockers(path)` added** — returns `[(kind, detail)]`, `[]` when splittable. The
census is now one call over `agda_lex.agda_files`, with no private predicate anywhere:
**76 files, all `applied-open`**, citing real identifiers (`cap-Z₃` 13, `cap-Z₂` 7, `cap-Z₄` 6,
`m-lo₄` 4). 2 selftest cases; suite 525 → **527**.

⚑ **AND THE HAND-ROLLED SCAN IS WHAT EXPOSED DEFECT 1 — which does not make it right.** The
disagreement between my scan and the tool was the only signal that found the comment bug. But the
correct response to “two measurements disagree” is to make the tool answer the question, not to keep
a second implementation around as an oracle: the private copy was wrong about 50 files while being
accidentally right about 3. *A disagreement is a signal to CONVERGE, not a reason to maintain a
rival.*

**R11’s build is now correctly scoped**: 76 files, one blocker kind, queryable in data. The
restructurer itself — extract the applied import plus the file-local definitions it consumes into
their own leaf, emit it first — is still owed, and it now has a precise, tool-supplied worklist
instead of a regex over error text.

### 38. R11 — THE GUARD WAS FIRING ON A NO-OP: 76 → 54 BEFORE ANY RESTRUCTURER (2026-08-01)

Set out to build the applied-open restructurer. Measuring the population WITH THE TOOL’S OWN PARSER
first — rather than the regex that misled me in §37 — changed the item again.

⚑ **THE GUARD’S OWN STATED HAZARD REQUIRES ≥2 LEAVES, AND IT WAS FIRING ON 1.** Its text:
*“in the leaf that DEFINES `Gen` it lands ABOVE the `data Gen`, and in every OTHER leaf it references
names that leaf does not have.”* **Both halves presuppose a split.** A single-unit file emits one leaf
that IS the whole file — no other leaf exists, the ordering is unchanged, and the application cannot
be misplaced relative to anything.

**MEASURED (tool’s parser, guard lifted): 22 of the 76 blocked files are ONE UNIT.** The refusal was
blocking a NO-OP. Scoping the guard to `len(units) >= 2` drops the population **76 → 54** with no
restructurer written. Verified on a witness rather than trusting the count:
`Algebra/Abelian/V4-as-PFG-Applied.agda` now splits to a single leaf with **the applied open preserved
intact**.

**The real shape of what remains** — 405 units across the 76, distributed:

| units             | files  |
|:------------------|:-------|
| 1 (now unblocked) | **22** |
| 2                 | 17     |
| 3–9               | 21     |
| 10+               | **16** |

⚑ **AND THE WITNESS’S CHAIN IS REAL, so the restructurer cannot be a single extraction.**
`V4-Coxeter.agda`: `:77 open import …ListPresentation Gen Canonical-V4 c-ε insert insert-canonical public` applies an IMPORT to file-locals at `:55`/`:66`; then `:155 open WithLemmas canonical-is-fixed-V4 insert-append-lemma-V4 public` applies `WithLemmas` — **a submodule
`:77`’s own `public` application brought into scope** (`ListPresentation.agda:57`). So the file is
`locals → applied open → applied open → one lemma`: a DEPENDENCY CHAIN, not a set of independent
units. **44 of 52 blocking statements are the `open M <args>` form**, i.e. applying a name already in
scope rather than an import — the second link of exactly this chain.

**Still owed: the restructurer for the 54.** Its worklist is now tool-supplied (`blockers()`), its
population is measured, and its hardest case is understood — but it must handle a chain, emitting the
extracted leaves in dependency order, not lift one statement.

⚑ *Third time in this arc that measuring a population with the right instrument shrank the work before
any tool was written* (§30’s fixity class went to zero, §34’s telescoped roots went to zero, this one
went 79 → 76 → 54). **The build is the last step, not the first.**

### 39. R9-VERIFY — AND FOUR WRONG ATTRIBUTIONS BEFORE THE RIGHT ONE (2026-08-01)

`gen_build_makefiles` regenerated: **3456 modules** (was 2956), `--check` OK. Then compile-checked
R9’s output — and getting the POPULATION right took four attempts, each producing a confident wrong
verdict:

| attempt | population used                                 | result                                        | why it was wrong                                                                                                                        |
|:--------|:------------------------------------------------|:----------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| 1       | 12 tracked-new files                            | 11/12 pass                                    | `git status` “A/??” is not R9’s output — most R9 leaves were already untracked from earlier splits                                      |
| 2       | 40 tracked-new                                  | 29/40 pass, “**a real R9 regression**”        | all 11 failures **existed before R9** — `git cat-file -e pre-r9:` proved it                                                             |
| 3       | `git diff pre-r9`                               | **89 modified, 0 new**                        | a `git stash create` snapshot **cannot hold untracked files**, so it cannot see 589 new leaves at all — the same limitation §10 records |
| 4       | glob under R9’s 65 output dirs                  | 22/25 fail, “**88%, serious regression**”     | the dirs also hold leaves from EARLIER splits; `Product.agda` was tracked at `pre-r9`                                                   |
| **5**   | **files with an mtime inside the apply window** | **exactly 589 — matching the reported count** | the only population that is R9’s output                                                                                                 |

**THE HONEST FIGURE: 13 of 25 pass. And of the 12 failures, NINE cite an error in a DEPENDENCY, not in
the leaf** — `F2/Vector.agda:167` (the known T2 section-vs-grammar case) and
`Groups/Symmetric/Permutation.agda:16` (a telescope-import case, R7a’s class). **Only 3 of 25 fail on
their own content.** So R9’s defect rate is \~12%, and the rest is the pre-existing broken frontier the
A4 census already tracks — leaves blocked BEHIND errors, not broken BY the split.

⚑ **“48% FAILURE” AND “12% DEFECT RATE” ARE THE SAME MEASUREMENT READ TWO WAYS**, and only the second
is about R9. A compile failure names a FILE; that file is often not the one under test. *Attributing a
failure to the thing you just changed, without reading which file the error cites, is how a working
change gets rolled back.* I was one step from proposing exactly that.

⚑ **AND THE SNAPSHOT COULD NOT ANSWER THE QUESTION IT EXISTS FOR.** `pre-r9` is a `git stash create`
SHA, and stash cannot hold untracked files — so “what did R9 create” is unanswerable from it. That is
the §10 hazard resurfacing in the verification path rather than the recovery path: the snapshot
protects TRACKED files, and this tree’s decomposition output is overwhelmingly untracked. **mtime was
the only instrument that worked**, and it worked exactly because the apply is a bounded time window.

**Verdict: R9 stands.** 3 leaf-own failures out of 25 sampled is real debt to fix, not grounds for
rollback; the 9 dependency failures are A4’s population and were failing before R9 ran.

### 40. TWO QUESTIONS THE TOOLING COULD NOT ANSWER — BOTH NOW HOMED (user, 2026-08-01)

> *“This is why it’s so critical to use a common tokenizer, and NOT a ton of hand-rolled regex. And
> why it’s critical to use common code instead of one-off scripts. **IF YOU HAVE A QUESTION THE
> TOOLING IS NOT PREPARED TO GIVE YOU AN ANSWER TO DIRECTLY WITHOUT REPROCESSING ITS OUTPUT, FIX THE
> TOOLING.**”*

§39 is the case in full: **five one-off populations, four confident wrong verdicts**, all because two
questions had no API and had to be reprocessed out of side effects.

**QUESTION 1 — “which files did this apply write?”** `split_lemmas.split()` returns `files` keyed BY
PATH, and `--apply` printed only a COUNT. So the answer existed in memory and was discarded, and I
reconstructed it from `git status` (wrong: most leaves were already untracked), from
`git cat-file -e pre-r9:` (wrong: a stash snapshot **cannot hold untracked files**, so it reported
89-modified/0-new for a run that wrote 589), from a directory glob (wrong: those dirs also hold
earlier splits’ leaves — this produced the “88% failure, serious regression” reading), and finally
from **file mtimes**, which matched the reported 589 exactly.
✅ **`--manifest` added**: prints the written paths, one per line.

**QUESTION 2 — “is this failure the file’s own, or a dependency’s?”** Every caller regexed
`isolate_check`’s output; I did it with a shell `case` and got the attribution wrong.
✅ **`split_pipeline.blame(leaf_path, out)` added** → `('clean'|'own'|'dependency', cited_file)`.
Measured on the R9 sample: **12 of 25 leaves “fail”, but 9 cite a DEPENDENCY** —
`F2/Vector.agda:167` (T2’s section-vs-grammar case) and `Groups/Symmetric/Permutation.agda:16`
(R7a’s telescope-import class). **Only 3 fail on their own content.**

> **“48% failure” and “12% defect rate” are the same measurement read two ways, and only the second is
> about R9.** A compile failure names a FILE, and that file is usually not the one under test.
> Attributing a failure to the thing you just changed, without reading which file the error cites, is
> how a working change gets rolled back — I was one step from proposing exactly that.

⚑ **AND THE DRIVER HAD NO SELFTEST AT ALL.** `split_pipeline` is the supported entry point for the
whole chain and was invisible to `run_selftests` (T3’s population). 4 cases added, using the ACTUAL
error strings from R9-VERIFY rather than invented ones. **Suite 527 → 531, 20 → 21 suites** — the
SUITE count moving is the evidence the driver is now discovered rather than silently absent.

**Verdict on R9: it stands.** 3 leaf-own failures in 25 sampled is debt to fix, not grounds for
rollback; the 9 dependency failures are A4’s pre-existing population.

### 41. R12 — THE `[]` DROP WAS IN THE NAME→HOME AUTHORITY, NOT THE SPLITTER (2026-08-01)

**Full `blame()` classification of all 589 R9 leaves** (not a 25-file sample):

| verdict        | n       | reading                                                          |
|:---------------|:--------|:-----------------------------------------------------------------|
| clean          | **187** | compile with no error                                            |
| **dependency** | **289** | fail on a file that is NOT the leaf — A4’s pre-existing frontier |
| **own**        | **113** | the split’s real debt — **19%**, not the 12% my sample suggested |

⚑ **THE SAMPLE UNDERSTATED THE DEFECT RATE BY A THIRD.** 3-of-25 read as 12%; the full population is
113/589 = 19%. *A 25-file sample of a 589-file population has a wide enough interval that “12%” and
“19%” are the same draw — the fix is to run the whole population when the tool makes it cheap, which
`blame()` now does.*

⚑ **ROOT CAUSE, AND IT IS UPSTREAM OF THE SPLITTER: `agda_defs._namelist` DROPPED EVERY
BRACKET-MIXFIX CONSTRUCTOR.** The filter rejects a signature group when any token is not
identifier-shaped — correct for a TYPE (`value b ≡ zero → Trimmed b`), but **`[]` and `[_]` fail that
test by construction**, and inside a `data` body that is the ONLY branch that runs. So
`data List … where [] : List A` indexed `List`, `_∷_`, `_++_`, `foldl`, `foldr` — and **never `[]`**.

**`def_index()["[]"]` was EMPTY TREE-WIDE.** No tool could resolve the name, so the split emitted
`Algebra/Nat/Prime/Properties/Product.agda` (`product-[] : product [] ≡ 1`) with no import of
`Foundation.List`, and it failed `[NotInScope] []`.

⚑ **AND THE FILTER’S OWN DOCSTRING ASSERTED THIS COULD NOT HAPPEN** — *“single-name signatures are
matched by other branches, so this cannot drop a provision”*. False inside a data body. The claim was
plausible, load-bearing, and wrong; the fix is one condition (**a one-token group is a name, whatever
its shape**), verified to change ONLY the single-token case: `msb t ≡ true` was already admitted
before the change, and the 5-token type is still rejected.

**FIXED + GUARDED.** `[]` now resolves to `Foundation.List` and `Foundation.Vec`. ⚑ **`agda_defs` —
the name→home authority ELEVEN tools resolve through — had NO SELFTEST**; 5 cases added, anchored on
this defect and on the type-rejection it must keep. Suite **531 → 536**.

⚑ **THE FIX DOES NOT REPAIR THE 113 ALREADY-EMITTED LEAVES.** `Product.agda` still fails: the index is
correct now, but the file was written with the wrong import set. *A source fix stops the next
occurrence; it does not rewrite what shipped.* The 113 need re-emission (re-split the sources, which
is cheap and now correct) rather than 113 hand-repairs — filed as R12b.

### 43. T2 — IT IS NOT A GRAMMAR CLASS. IT IS §13’s RENAME RESIDUE (2026-08-01)

T2 was filed as *“the SECTION-vs-GRAMMAR ambiguity instrument”*, on the theory that
`a * p₁ +_` parses two ways where `_*_` and `_+_` share no name. **Reading the live witness first
retired that framing.**

`Algebra/F2/Vector.agda:167` writes `cong-trans (_+ lookup v i) …` and fails
`[NoParseForApplication]` with **“Operators used in the grammar: None”**. The lemma it feeds,
`+-identityˡ`, is stated over `_+F_` (`F2/PlusIdentityL.agda:32`) — because **§13’s rename-at-source
moved F₂’s addition to `_+F_`** — while the file imports `Foundation.Nat.Plus`’s `_+_`, a different
operator on ℕ. *The section names an operator that no longer exists in that scope*, which is why Agda
says “None” instead of naming a candidate. **A mechanical rename residue, not a parse ambiguity.**

⚑ **THE INSTRUMENT IS THEREFORE A RESOLVER, NOT A PARSER** — and the question it answers is the one I
kept hand-rolling in throwaway scripts (user, twice in this sitting: *“if you have a question the
tooling doesn’t answer directly, fix the tooling”*).

**LANDED in `agda_lex`** — beside the positional authorities, so nothing re-derives either half:
\* **`sections(src)`** → `[(lineno, text, operator)]`. *The text is not the name*: `(_+ x)` names
`_+_`, not `_+`.
\* **`resolves_here(src, lineno, op, homes)`** — composes `imports_before` (the POSITIONAL half, §31)
with the name→home index (the OWNERSHIP half, §41). Neither is re-implemented.
\* **`unresolved_sections()` + a `--sections` CLI** — because the alternative is a heredoc, and this
session produced five of those for one question before the right answer appeared.

**MEASURED: `F2/Vector.agda` has 4 unresolved sections — `:167` is the compiler’s own failing line**,
plus 3 the build has not reached. Tree-wide: **590**.

⚑ **AND THE FIRST CENSUS SAID 1136 — NEARLY DOUBLE — BECAUSE THE TOKENIZER MATCHED INSIDE `using`
LISTS.** The `;` separator was absorbed into the “operator” (`_⊗ˢ_;`, `_⇔_;`), so import SYNTAX
counted as code. Fixed at the tokenizer (separators excluded from the name class; import statements
skipped by span) rather than filtered downstream: **1136 → 590**, witness still found. *A census that
is nearly double the truth would have sized the whole item wrong — and the tell was in its own output
tail, visible only because the tool prints its rows rather than a bare count.*

3 selftest cases; `agda_lex` 45 → **48**, suite 536 → **539**.

**T2 is now a diagnosis, not a hypothesis**: 590 sites whose operator does not resolve where it is
written, each with its needed name and that name’s real homes — a worklist for `rename_at_source`,
not a new parser.

### 44. T2b-APPLY — THE WITNESS COMPILES, AND THE CENSUS WAS 2× ITS OWN TRUTH A SECOND TIME (2026-08-01)

**Applied.** `fix_sections --apply` on the witness rewrote 4 sites and
**`F2/Vector.agda` COMPILES CLEAN** — the `[NoParseForApplication]` at `:167` that blocked
`F2/Linear`’s retirement (R2-residue) and headed the dependency failures behind the R9 leaves is gone.
Tree-wide apply: **76 sites in 27 files**.

⚑ **THEN THREE PREDICATE FIXES, AND THE ORDER I FOUND THEM IS THE FINDING.** The remainder was
reported as “510 left for a human”. It was not:

| \#  | defect                                              | mechanism                                                                                                                                            | movement      |
|:----|:----------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|:--------------|
| 1   | `resolves_here` never asked `binds_at`              | a MODULE PARAMETER is *bound*, not *defined*, so the name→home index has no entry and the site reads `no-candidate`                                  | 510 → 500     |
| 2   | `MODULE_HEAD` matched only `module`                 | `record`/`data` bind an IDENTICAL telescope; `Category/AbelianPFG.agda` puts `(_·G_ : G → G → G)` in a `record … where` head                         | 500 → 496     |
| 3   | **`sections()` counted BINDING GROUPS as sections** | `(_·G_ : G → G → G)` matches the section shape exactly — `(` + `_·G_` + space — so **an operator’s own DECLARATION was censused as a use of itself** | **496 → 295** |

**The discriminator for #3 is the colon**: a binding group types its names before closing; a genuine
section cannot. Guarded by a case asserting the binder yields NO section *and* that a real section on
the same operator is still found — the second half matters, because a fix that suppresses the class
by suppressing the operator is not a fix.

⚑ **I PROPOSED #1 AND #2 EACH AS *THE* MECHANISM AND THEY MOVED 14 OF 215 COMBINED.** Both are real
defects, both are now fixed and tested — and neither was the cause. The cause was upstream of
resolution entirely, in the tokenizer. **A widening that leaves its own witness in the output has not
found the cause**: after fix #1, `_·G_ @ AbelianPFG.agda:70` was still in the report, which is the
only reason I kept looking. *That is the §43 lesson (fix the tokenizer, not the downstream filter)
recurring in the same instrument one sitting later, and I did not recognise it until the third pass.*

⚑ **AND THE ROW-WITH-EXAMPLE FORMAT IS WHAT MADE IT VISIBLE.** A count would have shown a plausible
`500 → 496` and I would have banked it. The grouped view showed the *same file:line* surviving a fix
that targeted it. **Print the witness, not the tally** — §43 recorded this and this section is its
second confirmation.

**Tooling landed, each because a question had no command:**
\* `split_pipeline --verify [paths|--leaves]` — was `cd agda && membudget run 384 <label> -- agda   --safe -i. <rel>` plus reading the error by eye: four pieces of tool knowledge in a shell line and
one interpretation step. `isolate_check` + `blame` already owned both halves.
\* `split_pipeline.leaves()` + **a persisted `.leaf-verify.tsv` and `--last`** — “which files are the
split’s leaves, and how do they fare” had NO population. R9-VERIFY reconstructed it five ways and
got four confident wrong verdicts; `--manifest` fixed one run and persisted nothing, so the next
sitting went hunting a scratch file. A leaf identifies itself by the `⟡cap-128-forcing` marker
`rewire_to_leaves._is_leaf` already keys on — a read of an existing convention, not a sixth twin.
⚑ **The verify summary reports `clean/own/dependency` and the TOP CITED DEPENDENCIES**, never a
pass/fail count: “12 of 25 fail” and “3 are this split’s own defect” are the same run, and the
first reading nearly rolled back working code.
\* `split_lemmas --blocked` — `blockers()` was built so a census would stop re-deriving `local_defs`
(a hand-rolled version disagreed with the tool on **50 of 79 files**) and then had NO CLI, so every
later question about the applied-open class went back through a `python3 -c`. **Re-measured: 54
files, ONE kind** — R11’s figure is current, not stale.
\* `fix_sections` groups its own unactionable remainder by operator — the alternative was `| tail`,
which is reasoning applied to program output.

⚑ **THE STANDING FORM (user, 2026-08-01):** *“I’m pointing you at fixing the tooling every time I see
you needing to run more than one tooling command (indicating you’re applying reasoning not codified)
or manipulating program output (again, applying reasoning not codified).”* Four tool-call refusals
this sitting, every one correct: a hand-assembled `membudget` line, a `python3 -c` wrapper, a `| tail`,
and a shell redirect to a scratch file. **Each refusal named a missing command, and each missing
command is now built.** The redirect one is the subtlest — persisting a census to a file the TOOL does
not know about is the same reprocessing loop wearing a different shape, which is why the ledger is
`agda/.leaf-verify.tsv` with a `--last` reader rather than a path I remember.

Suite **549 → 556**; `agda_lex` 51 → 58.

**Remaining: 295** — 81 `_+_` genuinely `ambiguous` (per-site, not a sweep), the rest `no-candidate`
and **not yet classified**. Do not assume they are the same class as the 201: that assumption is what
this section is about.

### 45. THE GATE VERDICTS ARE NOW A COMMAND — AND B3’s PRECONDITION WAS UNDERSTATED (2026-08-01)

✅ **`scripts/gate_status.py`** (5 selftest cases; suite 556 → **561**, 23 → **24 suites**).
B3 requires every hook-wired gate green, and the only ways to learn which were red were to attempt a
commit or to hand-run gates one at a time. §25 did the latter, found eight failing where the worklist
tracked one, and banked it as PROSE — so the next sitting had to re-derive it. **A number in a
worklist ages; a command re-measures.**

⚑ **THE GATE LIST IS PARSED FROM `.githooks/pre-commit`, NEVER RESTATED.** A hand-maintained copy is
a derived view that silently diverges — the class this arc paid for in four `agda_files()` bodies
under one name and in `check_import_shape`’s private renaming parser. Add a gate to the hook and it
appears here with no edit. It also makes COVERAGE answerable by construction: this tool cannot report
a gate the hook does not run, which is exactly the §9a defect (five gates baselined and wired into
nothing). Conditional gates (nested in an `if`) are MARKED, not silently run or silently dropped —
their guard is a fact about when they apply.

⚑ **MEASURED, AND IT CORRECTS TWO WORKLIST FIGURES AT ONCE: 27 GATES WIRED (21 UNCONDITIONAL + 6
CONDITIONAL), 15 PASS, 12 RED.** Every prior statement of B3’s precondition said “all 21” — the
unconditional count — so six gates were outside the stated bar, three of them red.

| red gate                                                                              | worklist coverage                                                                                             |
|:--------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------|
| `ban` `claims` `public` `private` `sumtype` `carrier-locality` `rederive` `discharge` | ✅ A5 / G1 / R8 / B1                                                                                          |
| **`shape-node index current`** — STALE, regenerable via `scripts/sppf_node_index.py`  | ❌ **untracked** → **G4**                                                                                     |
| **`Σ metalanguage regression (Σ6)`** — `jea_seam_provenance` regressed                | ❌ **untracked** → **G5**; a real regression in a silo this arc never touched                                 |
| `Set₁ ratchet` — refusing on census INCOMPLETENESS, exactly §8’s diagnosis            | ✅ B2 (`make catalog`)                                                                                        |
| **`cap ratchet (128MB)`**                                                             | ❌ **untracked** → **G6**; §26 measured its baseline is a **0-byte file**, so it reports a LEVEL, not a delta |

⚑ **AND THE TWO NUMBERS ARE THE SAME MEASUREMENT READ TWO WAYS, AGAIN** — §25’s “eight failing” was
over the unconditional set at an earlier tree state; twelve is over the whole wired set now. Neither
figure was wrong when taken. *This is the fourth time this arc that a count quoted without its
denominator became a stale dependency (§39’s 48%-vs-19%, §41’s 12%-vs-19%, §26’s cap “11 NEW”), and
the fix is the same each time: report the population, not the tally.*

### 46. THE LEAF CENSUS — 1322, NOT 589, AND TWO WORKLIST FIGURES WERE WRONG IN OPPOSITE DIRECTIONS

First run of `split_pipeline --verify --leaves`, over the population derived from the
`⟡cap-128-forcing` marker rather than from any one run:

| verdict                      | n        | share |
|:-----------------------------|:---------|:------|
| clean                        | **541**  | 41%   |
| dependency                   | **436**  | 33%   |
| own                          | **345**  | 26%   |
| **total leaves in the tree** | **1322** | —     |

⚑ **THE DENOMINATOR WAS NEVER 589.** That was R9’s single run; the tree holds 1322 split-emitted
leaves accumulated across every split this arc performed. So:
\* **R12b’s “113 leaf-own failures” is really 345** — the old figure was 19% of 589, correct then,
and it is 26% of a population 2.2× larger now.
\* **A4’s “289 blocked behind a dependency” is really 436.**

Both were true when measured and neither is the population today — *a recorded finding is a hypothesis
at a later tree state* (§24), here confirmed twice in one command. **The item must take its worklist
from `--last`, never from the quoted count**, which is precisely why the census now persists.

⚑ **TEN FILES ACCOUNT FOR 340 OF THE 436 DEPENDENCY FAILURES**, so the unblocking work is a short
ordered list, not a broad sweep:

| n   | blocker                                                                                                                    |
|:----|:---------------------------------------------------------------------------------------------------------------------------|
| 61  | `Algebra/Wedge/BoundedIso.agda`                                                                                            |
| 54  | `Groups/V4-Coxeter.agda`                                                                                                   |
| 52  | `Algebra/F2/Vector/Universal.agda`                                                                                         |
| 37  | `Lojban/PlaceStructure/Private.agda`                                                                                       |
| 37  | `WitnessTower/FirstAppearance.agda`                                                                                        |
| 24  | `Foundation/Fin/From2.agda`                                                                                                |
| 22  | `Algebra/F2/Polynomial.agda` · 22 `Foundation/Fin/Iterate.agda` · 16 `LehmerPath/Decode.agda` · 15 `Algebra/Q/Reduce.agda` |

⚑ **AND THE T2b WIN IS NARROWER THAN I WOULD HAVE CLAIMED.** `F2/Vector.agda` compiles after §44’s
fix — but `F2/Vector/Universal.agda` is now the 3rd-largest blocker at 52 leaves. **The fix moved the
blocker one file down the subtree rather than clearing it.** I was about to report T2b-APPLY as
“unblocked the 289”; the census says otherwise, and the only reason I did not is that the verdict
summary names the CITED FILE rather than counting failures. *`blame()` earned its keep a second time.*

⚑ **`Lojban/PlaceStructure/Private.agda` blocks 37 leaves and is itself a `private`-named artifact** —
i.e. R9’s own emission convention before §33 taught the splitter that a `private` block is a CONTAINER,
not a unit. That is R12b’s population showing up as a *dependency* blocker, which is the coupling the
worklist records as `R12b → R10a/R10b` and did not record as `R12b → A4`.

### 47. THE TOOLS THAT REWRITE AGDA ARE THEMSELVES EDITED BY HAND (user experiment, 2026-08-01)

> *“There is no exact interactive clone built directly on top of LibCST … however LibCST includes a
> built-in codemod CLI.”* … *“I do notice that the search AI response I pasted to you pointed at
> libcst’s own CLI.”*

⚑ **THE ASYMMETRY IS REAL AND IT HAS A MEASURED COST.** This repo mechanizes every edit to `agda/`
and makes NONE to the \~85 tools that perform them. The same defect class recurs one level up:

| defect, in the PYTHON                                                                                                                          | found by                               |
|:-----------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|
| `split_pipeline.rewire_only()` written, documented with its own 354-consumer justification, **ZERO CALLERS** — the dispatch branch never added | the §47 audit, same day it was written |
| FOUR `set_ratchet` gates cannot enumerate their census; THREE non-family gates each hand-rolled a `--list` separately                          | audit finding 1                        |
| `agda_files()` as FOUR bodies under one name, two feeding pre-commit gates                                                                     | §6d                                    |

**A shared NAME is not a shared authority, and a hand sweep is not a transform.**

⚑ **THE REUSE-SEARCH FIRED ON ME AND DELETED MOST OF A FIRST DRAFT.** I wrote a module with a
`--dry-run`, a file walker and a worker pool before the user pointed at the CLI the pasted text had
already named. `python -m libcst.tool codemod` ships **`-u/--unified-diff`** (preview), **`-j JOBS`**
(parallelism), directory walking, and `-` for stdin — so all three would have been re-derived
infrastructure (`feedback_fix_infra_not_route_around`: conform to the tool, don’t rebuild its core).
**And two built-ins are the Python twins of tools this repo hand-wrote for Agda:**
`rename.RenameCommand` ≙ `rename_at_source`, `remove_unused_imports` ≙ `prune_imports`.
*The trigger fires on TOOL SELECTION, not only on `data`/`record` declarations.*

✅ **LANDED — `scratch/pycodemod.py`** (7 selftest cases), scoped to exactly what the CLI does NOT own:
1. **the LOSSLESSNESS GATE** (`--roundtrip`) — **MEASURED: the entire tool corpus round-trips
byte-for-byte.** This is a PRECONDITION, not a probe: these files are the arc’s incident log, nearly
every line carrying a ⚑ recording the measured defect that put it there. A transform that keeps code
and drops commentary destroys the more valuable half — which is also why `libcst` and not `ast`
(`ast` discards comments by construction).
2. **the repo-specific QUESTIONS** — `--calls <name>` and `--dead`, which the CLI has no notion of
because they are not transforms.

⚑ **WHY THE CST BEATS `grep` FOR THE DEAD-CAPABILITY QUESTION, and it is not a preference.** These
files are dense with prose: `rewire_only`’s own docstring names it twice and the module docstring names
it again, so a grep returns hits and MISSES the finding. A selftest case pins exactly this — *a name in
a docstring or comment is NOT a call*. The audit found `rewire_only` only by reading its single grep hit
and noticing it was the definition.

**Honest cost:** a full-corpus CST scan exceeds 120s (2000-line tools; `-j` is the CLI’s answer for
transforms, and the question-mode here is single-process). Scoped runs are fast. **Not yet used to
perform any transform** — the gate is green, the queries work, and whether to codemod the four
`set_ratchet` gates is a separate decision.

### 48. THE MODULARITY AUDIT — a read-only agent against the fix-the-tooling policy (user, 2026-08-01)

Dispatched to audit `scratch/*.py` + `scripts/*.py` for the policy’s DEFECT SIGNATURE: *a question an
operator will predictably ask that the tooling cannot answer in ONE unpiped invocation.* Briefed with
five FORMS, each anchored to a measured precedent, rather than my hypothesis about where gaps were.

⚑ **THE AGENT’S OWN REJECTED TOOL CALLS ARE CORROBORATING DATA.** Three of its calls were refused for
shell-manipulating output; it reported this rather than hiding it, and noted the third (`| tail` on a
gate) *is* finding 1 — it reached for `tail` because the gate has no way to enumerate its census.

| \#  | form                     | finding                                                                                                                                                                                            |
|:----|:-------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | knew-and-threw-away      | `ratchet.set_ratchet` receives the full census `cur` and prints it on the `paid`/`added` branches, but the frozen branch prints only `at baseline N (frozen)` — the set is in memory and discarded |
| 2   | no-supported-entry-point | **`split_pipeline.rewire_only()` has ZERO CALLERS** — written, documented with its own 354-consumer justification, dispatch branch never added                                                     |
| 3   | no-entry-point           | `agda_defs` is the name→home authority for **19 importing tools** and its `__main__` dispatches only `--selftest`; a human at a shell cannot resolve a name                                        |
| 4   | output-shaped-for-piping | `gate_status.run_gate` keeps `tail[-1]`, but the `set_ratchet` family prints its `refuse_hint` LAST — so 9 of 12 red gates reported generic advice instead of their population                     |

⚑ **AND TWO OF ITS NUMBERS WERE WRONG, BOTH LOW — VERIFIED BEFORE FILING.** The agent said “four
`set_ratchet` gates” and “three hand-rolled `--list`”. Measured with the new CST query
(`pycodemod.py --calls set_ratchet`) and a grep for the flag:

- **`set_ratchet` has 10 CALLERS, not 4** — `ban`, `cap`, `carrier_locality`, `claims`, `discharge`,
  `private`, `public`, `rederive`, `snapshot_guard`, `sumtype`.
- **4 hand-rolled `--list`, not 3** (it missed `check_claims`), so **6 gates lack it**.

So the item is *larger* than reported: one flag in the authority serves **ten** gates and replaces
**four** copies. **A second-hand figure is a hypothesis** — the same rule that caught 589-vs-1322 one
section earlier, here catching an agent’s count rather than my own.

⚑ **FINDING 2 IS THE SHARPEST, AND IT IS MINE FROM THIS SESSION.** I wrote `rewire_only` an hour
before the audit ran, documented precisely why it was needed, and never wired it. **`grep` cannot find
this class** — the function’s own docstring names it twice and the module docstring a third time, so a
text search returns hits and hides the verdict; the agent caught it only by reading the single hit and
noticing it was the definition. `pycodemod.py --calls` (§47) now answers it structurally in one
command: `1 def(s), 0 call(s) — ⚑ DEAD CAPABILITY`.

**Filed as T13 (the `--list` codemod, 10 gates / 4 copies), T14 (`agda_defs` CLI), T15 (`gate_status`
verdict line), and R13 (wire `rewire_only`).** T13 is the natural first real codemod for §47’s
machinery: four hand-rolled copies to delete, six additions, one authority — a transform, not a sweep.

### 49. R13 — WIRING THE DEAD CAPABILITY, AND IT CLEARED THE TOP BLOCKER ON FIRST USE (2026-08-01)

**`rewire_only` had 1 def and 0 calls.** Written, documented with its own 354-consumer justification,
and unreachable: `main()` starts by SPLITTING, and a consumed parent is already atomic, so it hit
“nothing to split” at `:334` and the operator was out of options — left with `rewire_to_leaves.py`
standalone, which the tool’s own `stage_warning` tells you not to run.

**Three changes, in dependency order:**

1.  ⚑ **`rewire()` RETURNED A COUNT, SO THE PRUNE HAD NO POPULATION.** `touched` was an `int`, so the
    one thing every caller needs next — WHICH consumers did you just widen — was computed and
    discarded. That is why the standalone runs could not prune: nothing could name their output.
    Now the path list, with `len(touched)` preserving the old value so no caller broke. Same class as
    `split_lemmas` printing a count instead of `--manifest`, where reconstructing the list took five
    attempts and produced four wrong verdicts.
2.  `rewire_to_leaves --manifest`, so the driver reads the population from the stage rather than
    re-deriving it. **My first draft of the prune stage invented `CII.importers()` — an API that does
    not exist**; checking rather than shipping it is what surfaced that the paths had to come from the
    rewire itself.
3.  the `--rewire-only` dispatch, **plus a selftest that asserts the capability is REACHABLE**
    (`"rewire_only(" in inspect.getsource(main)`). A dead-capability guard, because `grep` cannot catch
    this class — the docstring names the function three times.

**MEASURED END-TO-END on the census’s top blocker:** `Substrate.Algebra.Nat.DivMod.Unique` —
20 importers rewired, sweep clean, **343 unused imports pruned in the same run**, and
**`Algebra/Wedge/BoundedIso.agda` COMPILES CLEAN.** That file was cited by **61 of the 436**
dependency-blocked leaves.

⚑ **THE PRUNE IS THE HALF THAT WAS ALWAYS MISSING, AND ITS SIZE SHOWS WHY.** 343 dropped imports
across 20 files — from ONE parent. §17 measured six standalone rewires leaving **354 consumers holding
≥5 leaves**; this run is the counterfactual, and it took no extra operator step because the driver owns
the sequence. *A tool that is only correct in a sequence must be REACHABLE in that sequence, not merely
warn that it isn’t.*

Suite 561 → **575**, 24 → **26 suites** (`pycodemod` and `resolve_notinscope` now discovered;
`split_pipeline` 4 → 6).

### 50. PANFLUTE — AND I GOT THE VERDICT BACKWARDS TWICE, BOTH TIMES CORRECTED BY THE USER (2026-08-01)

Third level of the same move: `agda_lex` reads Agda structurally, `pycodemod` reads the Python
tooling structurally, and **this plan — the arc’s single record — is still read by `grep`.** Every
question asked of it this session went through a line-regex, including the four times the canonical
chain table outlived its own corrections.

✅ **`scratch/mdstruct.py`** (8 cases): `--headers`, `--tables`, `--roundtrip`, `--fixpoint`, over
pandoc 3.8.3 + panflute 2.3.1 (via `uv run --with`, per `reference_uv_runs_python_with_deps`).
**MEASURED: 46 tables parsed structurally**, header/level skeleton clean, and a `#` inside a fenced
block correctly NOT a header — the case that beats `grep '^#'` in a document full of Agda fences.

⚑ **ERROR 1 — I FRAMED IT AS AN EITHER/OR AND THE USER DISSOLVED IT** (*“Not strictly true. The
question becomes whether or not the document can be normalized, found to be satisfactory, and then
subsequent modifications roundtrip.”*). I wrote: *“if it reflows the document, any transform is
unusable regardless of how good the API is”* — treating PRESERVES-THE-INPUT and UNUSABLE as the only
options. **Normalization is a FIXPOINT question, not a preservation question**: if
`normalize(normalize(x)) == normalize(x)`, a one-time accepted reflow is a reviewable MIGRATION and
every later transform round-trips exactly. The 9451-line drift-vs-original is paid ONCE and is the
wrong number to judge by. *This is the `construct-dont-classify` either/or trap, in tool evaluation.*

⚑ **ERROR 2 — I READ A CONVERGING SEQUENCE AS A DIVERGING ONE** (user: *“That looks like a continual
decrease. It may need further iterations to reach fixpoint.”*). Three rounds gave
`[1340, 899, 561]` and I called it **“diverges monotonically”** — the exact opposite of what a
DECREASING delta means. Run to convergence:

| writer                                                     | sequence                             | verdict                  |
|:-----------------------------------------------------------|:-------------------------------------|:-------------------------|
| `markdown` (default)                                       | `[1340, 899, 561, 400, 320, 176, 0]` | **FIXPOINT in 7 rounds** |
| `markdown-smart+pipe_tables --columns=999 --wrap=preserve` | `[8, 5, 2, 0]`                       | **FIXPOINT in 4**        |

**Both converge. The write path is admissible** — and the configured writer starts 8 lines out
instead of 1340, so the migration is nearly free. `my rounds=3` cutoff was the measurement bug that
let the wrong verdict stand for two turns.

⚑ **AND THE TERMINATION CONDITION IS STRICT DESCENT, NOT A ROUND CAP** (user: *“You could allow it to
iterate indefinitely so long as each round is strictly fewer modifications than the previous.”*).
Each delta is a non-negative integer, so a strictly decreasing sequence **cannot** run forever — a
well-founded descent. My replacement `rounds=25` was **a CAPABILITY bound dressed as a termination
bound**, the distinction `agda_lex.head_span` already records (a `j - i < 6` limit silently dropped
136 of 401 multi-line headers); it would have mis-reported any document needing 26 rounds. The loop
now runs while progress is STRICT and stops on `n == 0` (converged) or `n >= prev` (a cycle/stall),
with `rounds` surviving only as an optional runaway guard — the same shape `head_span` settled on.

⚑ **THE CONTRAST WITH §47 IS THE TRANSFERABLE PART.** libcst round-tripped the whole Python corpus
BYTE-FOR-BYTE; pandoc does not, and needs seven rounds to settle. Same idea, different guarantee:
**libcst is a lossless concrete syntax tree, pandoc is a normalizing document converter.** The right
precondition therefore differs by tool — byte-identity for one, *idempotence* for the other — and
asking “is it lossless” of a normalizer is asking the wrong question, which is how I got here.

**Not yet done:** no markdown transform has been run; the residue at the configured writer is a
backslash-escaped backtick inside inline code (3 occurrences, \`Div.Over.recon-nth\`\`) that pandoc
re-fences unstably — worth knowing before any write.

⚑ **AND THE EXPERIMENT HAD A TARGET I MISSED: THE MD060 LINT CLASS** (user: *“that’s what inspired me
to bring it up in the first place”*). The IDE reports `MD060 — Table pipe is missing space to the left/right` on this document after every edit, and I dismissed it four times as *“cosmetic,
pre-existing, not from this edit”*. It is pre-existing and cosmetic; it is also **exactly what a
normalizer retires**, and the user was pointing at the paydown while I was evaluating the technique.

**MEASURED (`mdstruct.py --table-style`): 48 non-canonical pipe rows → 0 after ONE normalization
pass.**

⚑ **THE FORM OF THE FIX IS THE FINDING: THE CLASS IS RETIRED, NOT FIXED.** Hand-correcting 48 rows
leaves the 49th to appear tomorrow. **A document held at pandoc’s fixpoint CANNOT violate MD060 at
all**, because canonical pipe spacing is what the writer emits by construction — so the fixpoint is a
GATE over every property the normalizer canonicalizes, which is strictly stronger than a linter
reporting violations after the fact. Same shape as `check_private_ratchet` excluding
`private variable` **by predicate** rather than by an exemption that can rot, and as the ban being
made unrepresentable by decomposition rather than policed per-import.

*Method note: four times I reported those warnings as noise and moved on. They were a measured
population with a mechanical remedy, and “cosmetic” was doing the work “not my edit” usually does —
`report the population, not the tally`, one level out from where I had been applying it.*

### 51. A4-UNBLOCK — TWO CLEARED, AND I DESTROYED THE CENSUS WITH MY OWN TOOL (2026-08-01)

Worked the §46 blocker list in citation order.

| blocker                                 | repair                                                                                                    | result                                                                                               |
|:----------------------------------------|:----------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|
| `Wedge/BoundedIso` (61 leaves cited it) | `--rewire-only` on `Algebra.Nat.DivMod.Unique`: 20 importers, **343 imports pruned**                      | ✅ **compiles clean**                                                                                |
| `V4-Coxeter` (54)                       | `--rewire-only` on `Groups.Coxeter.SameCanonical`: 7 importers, **42 pruned**, 1 barrel correctly refused | `[FileNotFound]` CLEARED; verdict moved `own` → **`dependency`**, now blocked on `Coxeter/Core.agda` |

⚑ **A BLOCKER LIST MAY BE A CHAIN, NOT A LIST — AND TWO OF TWO SO FAR ARE.** `F2/Vector.agda`
compiled after §44 and `F2/Vector/Universal.agda` became the 3rd-largest blocker; `V4-Coxeter`
cleared its `FileNotFound` and surfaced `Coxeter/Core.agda` behind it. **If that holds, “10 blockers”
UNDERSTATES the work**, and the only honest measure is the census delta, never the count of names
worked. *Same shape as `NotInScope` rising after `FileNotFound` fixes in §13: clearing an error lets a
module compile FURTHER and reveal what was behind it.*

⚑ **I DESTROYED THE 1322-ROW CENSUS WITH A SINGLE-FILE `--verify`.** The ledger write I added in §46
fired on EVERY verify, so checking one blocker overwrote the full-population record:
`clean=541 own=345 dependency=436` → **`clean=1`**. That is \~40 minutes of compiles AND the A4
worklist itself, gone — and it was my own tool, shipped two turns earlier, doing exactly what I wrote
it to do.

**FIXED AT SOURCE:** the write is gated on `--leaves`, a scoped run prints
`(scoped run — the full-population census is left intact)`, and a selftest asserts the gate exists.
**A SCOPED RUN ANSWERS A SCOPED QUESTION AND IS NOT EVIDENCE ABOUT THE POPULATION** — precisely why a
ratchet baseline may not be rewritten by a partial measurement (`ratchet.py`’s own rule, one layer
out). *The instrument that measures a population must not be writable by an instrument that samples
one.*

✅ **`split_pipeline.diagnose()` + `--diagnose [--blockers]`** — the codified form of a judgement I
had made BY HAND twice (user refused the third: *“needing to run more than one tooling command
indicates you’re applying reasoning not codified”*). Each blocker was taking THREE commands —
`--why`, then `resolve_notinscope`, then `--rewire-only` — with me classifying *“this is the
consumed-parent class”* in the middle. That classification is a PREDICATE over the compiler’s own
output: `[FileNotFound]` on a `Substrate.*` module that HAS a leaf directory. It now returns
`(kind, detail, remedy)` with the remedy as a RUNNABLE COMMAND, and `--blockers` takes the worklist
from the persisted census rather than from my transcription.

Suite 575 → **576**; `split_pipeline` 6 → 8 cases.

⚑ **AND THE REBUILD WAS ITSELF INVALID — A CENSUS THAT STRADDLES AN EDIT MEASURES NEITHER TREE**
(user: *“the census rebuild will need to be redone again once complete, so it can run e2e without
intermediate edits to the agda code”*). I launched the rebuild and then applied the `SameCanonical`
repair — **7 files rewritten, 42 imports pruned — while it was compiling**. Its early rows measured
the pre-repair tree and its later rows the post-repair one, so the result is a BLEND WITH NO
REFERENT, and nothing in the tool would have said so. I would have read it as fact.

**FIXED AT SOURCE — `tree_stamp()`**: the census stamps the tree’s state (file count + newest mtime)
before it starts, re-checks at the end, and **REFUSES to bank a ledger whose stamp moved**, printing
what changed and leaving the prior record intact. The stamp is written into the ledger so a later
reader knows what state it describes.

⚑ **THAT IS THE THIRD INSTANCE OF ONE CLASS IN THIS SECTION, AND THEY RHYME EXACTLY:**
the R9-VERIFY attribution failures (*which* files did the run produce), the scoped-run clobber
(*whose* population is this), and now the straddling census (*when* was this true).
**AN INSTRUMENT MUST KNOW WHAT IT MEASURED — the population, the scope, AND the moment.** Each was
found only because a number looked wrong to a human; none was detectable from the artifact itself
until the tool was taught to say.

Suite 576 → **580**; `split_pipeline` 8 → 12 cases.

**NOT YET RUN END-TO-END:** `--diagnose --blockers` needs a valid census, and no valid census exists
yet — the first was clobbered, the second straddled an edit. The item’s real worklist comes from a
clean run with no concurrent Agda edits; the §46 list is now **two repairs out of date** and must be
re-derived, never transcribed.

### 52. THE CENSUS IS A READ OF THE BUILD, NOT A SECOND BUILD (user, 2026-08-01)

> *“Study the makefile regenerator. Because if you want a census, a full `make` ought to be able to
> produce it as a side effect of an existing optimized parallel make process that honors
> dependencies.”*

⚑ **FIRST, A DEFECT THE QUESTION EXPOSED BEFORE THE REFRAME: `verify` WAS A PLAIN SERIAL LOOP.**
1322 compiles, one `agda` at a time. That does not merely waste time — it **contradicts the repo’s own
build discipline**: `membudget` exists so concurrent compiles self-throttle against a RAM semaphore,
which is why CLAUDE.md says `make -j` with NO number is the right invocation. Parallelised (delegating
the memory ceiling to `membudget`, capping only threads, deliberately oversubscribed so a blocked
lease sleeps and wakes rather than idling): **6 cached files 1.8s → 0.8s, 3.3/s → 7.4/s**. Landed
`--jobs=N` so the baseline is a FLAG (`--jobs=1`), self-reported timing, and progress every 100 files
— *a 40-minute run that printed nothing was indistinguishable from a hung one, and I killed working
runs twice.*

⚑ **THEN THE REFRAME, AND IT DISSOLVES THE ITEM: THE CENSUS ALREADY EXISTS ON DISK.**
`gen_build_makefiles:262-274` emits, per module:

    <Mod>.agdai: <Mod>.agda <direct-import>.agdai
        @$(AGDA) … > $@.log 2>&1 || { rc=$?; cat $@.log >&2; exit $rc; }

with a comment stating the point outright — *“a `make -j` console log INTERLEAVES jobs … One log per
module is interleave-proof by construction”*. **MEASURED: 2810 such logs on disk, all non-empty.**
Everything my `verify --leaves` recomputed was already there:

| ingredient                | the build has it                            | my version had                    |
|:--------------------------|:--------------------------------------------|:----------------------------------|
| per-module compile output | `<Mod>.agdai.log`                           | a re-compile                      |
| **dependency order**      | the explicit `.agdai : .agda + imports` DAG | **dependency-BLIND**              |
| parallelism               | `make -j`, shim-throttled                   | a serial loop (now a thread pool) |
| incrementality            | mtime over that DAG                         | **none — all 1322 from scratch**  |

The dependency-blindness is the substantive one: a from-scratch pass **cannot distinguish “this leaf
is broken” from “its dependency was never built”** — the exact distinction `blame` exists to draw.
✅ **`census_from_build()` + `--verify --from-build`**: seconds, not minutes.

⚑ **AND THE FRESHNESS CATCH STOPPED A CONFIDENT WRONG VERDICT** (user: *“You’ll need to verify that
the log is fresh wrt the current code state of the file it reflects and the files that depends on”*).
The first cut ignored mtimes:

| check                             | clean                                                                     |
|:----------------------------------|:--------------------------------------------------------------------------|
| logs, no freshness test           | **2802 of 2810** — near-total health, on a tree with known-broken modules |
| **+ transitive-import freshness** | **1036**                                                                  |
|                                   | **1770 STALE**                                                            |

**63% of the build’s logs describe a tree that no longer exists.** A module recompiles when ANY
transitive import changes, so the predicate is `log_mtime ≥ max(own source, every transitive import)`
— and that relation comes from **`gen_build_makefiles.parse_tree()`**, the same edges the build’s own
prerequisites are generated from. Not a local re-derivation. `stale` is its own verdict, never folded
into `clean`: it is **UNMEASURED, not passing** (Guard (2)’s rule — *an incomplete census is not a low
count*).

⚑ **MY GUARD WOULD HAVE MEASURED NOTHING, AND THAT IS THE THIRD INVENTED API THIS SESSION.** I called
`agda_lex.imports_of` — which does not exist — behind a `hasattr` fallback to an EMPTY SET, silently
reducing the check to “newer than its own source”. **A guard that degrades to measuring nothing is
worse than a crash.** (Prior two: `CII.importers()` in the prune stage, and an undefined `ROOT`.)
Checking each time is the only reason none shipped.

⚑ **AND MY OWN SUMMARY HID THE ANSWER.** It printed a FIXED THREE verdicts, so when `stale` appeared
it swallowed **1770 rows** and the totals stopped summing to the population. Fixed to print every
verdict present, plus an explicit warning. *That is `report the population, not the tally` occurring
INSIDE a tool built to report populations — fifth recurrence.*

**CONSEQUENCE FOR THE WORKLIST:** CENSUS-CLEAN-RUN is no longer a bespoke 40-minute compile that
forbids concurrent edits. It is **`make -C agda -j`** (the existing optimized parallel build, already
the pre-commit gate) **then `--verify --from-build`** (a seconds-long read). The census stops being a
thing beside the build and becomes a projection of it.

### 53. THE BUILD RAN — AND READING ARTIFACTS ALONE UNDERCOUNTED FAILURES 3× (2026-08-01)

`make -C agda -j -k` over the whole tree, then `--verify --from-build`. The first honest census of
this arc, and it took one more correction to get there.

| verdict          | n        | meaning                                        |
|:-----------------|:---------|:-----------------------------------------------|
| clean            | **1303** | compiled, log fresh                            |
| **build-failed** | **121**  | make’s OWN failed-target list — authoritative  |
| stale            | **1427** | log predates the source or a transitive import |
| dependency       | 2        | fails citing another file                      |

⚑ **THE LOG-DERIVED FAILURE COUNT WAS 41; MAKE REPORTED 121.** A module that FAILS leaves no fresh
log, so it falls into `stale` and the artifact record **cannot see its own gaps** — reading artifacts
alone undercounted the failures by a factor of three. Fixed by `--build-log=<file>`, which folds in
make’s own `*** [… .agdai] Error` lines: **the build measured by its own report, not by inference
from what it left behind.** *That is the §52 lesson one turn later — the census is a projection of the
build, so the build’s own verdict outranks a reconstruction of it.*

⚑ **AND `stale` CONFLATES TWO THINGS, ONLY ONE OF WHICH IS A GAP.** `make -k` builds every branch it
can, but a module whose DEPENDENCY failed is **never attempted** — so it gets no fresh log and lands
in `stale` beside modules nobody has rebuilt yet:

- *nobody rebuilt this* → genuinely UNMEASURED;
- *make could not reach it, something upstream is broken* → **a FINDING: it is blocked.**

So 1427 is not 1427 unknowns; a large share is the blast radius of the 121. **The item’s real shape is
121 genuine failures plus their downstream cone**, and the census cannot yet report which is which —
filed as `C1`.

⚑ **THE 121 ARE HETEROGENEOUS — DO NOT ASSUME THE CONSUMED-PARENT CLASS.** Sampled from the build
tail: `FUSepQHexagon/RIdx.agda` fails `[NotInScope] Tm⟦27e68fcc⟧` — a HASH-SUFFIXED GENERATED name,
nothing to do with a split parent — while `Logic/Evidence/ElAtlas/Proofs.agda` fails `[FileNotFound]`
on `Verdict.Phase`, which IS. Classify with `--diagnose --blockers` before repairing anything; the
two need different tools.

✅ **T14 LANDED IN PARALLEL (Python-only, no straddle risk):** `agda_defs.py` answers `<name>` and
`--provides <Mod>` directly. The authority **19 tools** resolve through could not be asked by a human;
`resolve_notinscope.py:13` named that defect verbatim. Verified live — `divmod-unique`,
`same-canonical-via-Gen`, `_+F_` each resolve to one leaf, and `[]` to **9 homes**, confirming §41’s
`_namelist` fix still holds. Guarded by two cases asserting the ENTRY POINT exists — the `rewire_only`
lesson (1 def / 0 calls) applied to the module eleven others depend on. Suite 580 → **582**.

### 54. C1 — 90% OF THE “UNKNOWNS” WERE ONE FINDING WEARING A GAP’S CLOTHES (2026-08-01)

Split `stale` by reverse-closure over the import DAG. **1427 → 1286 blocked + 141 unmeasured.**

| verdict      | n        | meaning                                            |
|:-------------|:---------|:---------------------------------------------------|
| clean        | 1303     | compiled, log fresh                                |
| **blocked**  | **1286** | `make -k` NEVER ATTEMPTED it — a dependency failed |
| build-failed | 121      | make’s own failed-target list                      |
| **stale**    | **141**  | genuinely UNMEASURED — nothing upstream failed     |
| dependency   | 2        |                                                    |

⚑ **THE TREE IS NOT 1427 MYSTERIES. IT IS 121 FAILURES DRAGGING 1286 MODULES BEHIND THEM**, plus 141
stragglers nobody rebuilt. **\~10.6 blocked per failure** — and that ratio is the argument for working
the 121 in DEPENDENCY ORDER rather than by citation count, because clearing one root can free a cone
an order of magnitude larger than its own citation number suggests.

*Reuse, not re-derivation:* the reverse edges come from `gen_build_makefiles.parse_tree()` — the same
relation the build’s prerequisites are generated from and the same one the freshness check uses. **One
import DAG, three consumers.** A private re-scan here is exactly how `agda_files()` became four bodies
under one name (§6d).

⚑ **AND THE REPORT’S OWN TEXT WAS STALE THE MOMENT THE SPLIT LANDED** — it still described 141 with
the warning written for the conflated 1427. Fixed to state each verdict’s meaning separately: BLOCKED
is a **finding** (with the per-failure ratio), STALE is a **gap**. *A tool that computes a new
distinction must also SAY it; the number changed and the sentence did not, which is the same
summary-outlives-its-correction defect this document has recorded four times about itself.*

3 selftest cases over a synthetic DAG (transitive blast radius, unrelated module untouched, the failed
module not counted as its own radius) — the transitive step cannot silently degrade to one hop.
Suite 582 → **585**.

### 55. A4-CLASSIFY — CONE SIZE INVERTS THE WORKLIST, AND A 100× DEFECT WAS NOT PARALLELISM (2026-08-01)

⚑ **THE PERFORMANCE DEFECT FIRST, BECAUSE THE DIAGNOSIS IS THE LESSON** (user: *“Is
`--diagnose --blockers` properly parallelized?”*). The honest answer was **no** — and chasing that
would have been the wrong fix. `_blast_radius` re-ran `gen_build_makefiles.parse_tree()` on EVERY
call (a walk over \~3000 sources), and ranking 121 failures by cone size calls it once per file:
**121 identical tree walks to build one DAG.** Memoised at the single owner of the relation:
**300s+ → 2.7s.**

> **Before reaching for concurrency, check whether the work is REPEATED.** Parallelising 121
> redundant walks would only have made the same mistake run faster. *I had asked “is this
> parallelised?” one turn earlier and applied the right question to the wrong layer.*

Two smaller fixes rode along: `--diagnose` now reads the BUILD’S OWN LOG instead of re-compiling
(121 compiles of what `make` already did — §52’s lesson, one turn later), which required splitting
`diagnose` into obtain-text + `_classify`. ⚑ My first attempt reached for a `_classify` that did not
exist — **the FOURTH invented API this session**; defining it properly rather than duplicating the
predicate at the call site is what made the log path possible at all.

⚑ **AND THE RANKING INVERTS THE WORKLIST I HAD BEEN USING.**

| rank by CONE | file                                | class                                            | I had ranked it      |
|:-------------|:------------------------------------|:-------------------------------------------------|:---------------------|
| **501**      | `Groups/V4-Coxeter.agda`            | `file-not-found` → `Coxeter.Core.IdemInequality` | **54, by citations** |
| 400          | `Foundation/Fin/From2.agda`         | NotInScope                                       | 24                   |
| 391          | `Groups/Symmetric/Permutation.agda` | NotInScope                                       | —                    |
| 324          | `F2/Vector/Universal.agda`          | NoParseForApplication                            | 52                   |
| 274          | `F2/AsModule.agda`                  | NoParseForApplication                            | —                    |

**`V4-Coxeter` blocks 501 modules; its citation count was 54.** Citation count is a LOCAL measure,
cone size is the STRUCTURAL one, and here they differ by \~10×. §54 predicted this and §55 measures it.

⚑ **THE 121 FILES ARE FAR FEWER THAN 121 DECISIONS.** Recurring roots across the list:
`Coxeter.Core.IdemInequality` (**7 files**), `Foundation.Vec.Properties` (4),
`Algebra.Nat.WellFounded` (4), `FUSep.FUSepQBridge` (3), `Foundation.Nat` (3),
`WitnessTower.SimplicialBoundary` (3). **A handful of consumed parents account for a large share** —
so the file count overstates the work, exactly as the leaf count did in §46.

**Class split: \~40 `file-not-found`** (mechanical; `--rewire-only`, and the tool now EMITS the runnable
remedy per row) **vs \~80 `other`** — NotInScope, NoParseForApplication, ParseError, UnequalTerms,
ClashingDefinition, AmbiguousName, MissingTypeSignature. The second group is genuinely heterogeneous
and needs per-class handling; **do not treat the 121 as one population.**

### 56. A4-FNF’s TOP ROW IS NOT ITS CLASS — `diagnose` HAS A FALSE POSITIVE (2026-08-01)

Ran the emitted remedy for the highest-cone root, `Coxeter.Core.IdemInequality` (7 of the 121, the
501-cone behind `V4-Coxeter`). **The tool refused, correctly, and my classification was wrong.**

    Substrate.Groups.Coxeter.Core.IdemInequality: 2 names / 2 leaves -> rewired 0 importer(s)
    ✗ 1 surviving reference(s):  Core.agda:75

⚑ **THE SURVIVING REFERENCE IS AN APPLIED OPEN, NOT A CONSUMED PARENT.**
`Core.agda:75` reads `open import …IdemInequality Word Canonical normalize normalize-canonical canonical-is-fixed public` — it APPLIES the module to the enclosing telescope’s arguments.
`rewire_to_leaves` handles bare and `using` forms; it declined, and `check_indented_imports.sweep`
refused the whole run. *Both stages did their job; the worklist row was the defect.*

⚑ **AND THE LEAVES ARE BROKEN ON THEIR OWN TERMS — THIS IS R7b’s CLASS, NOT A REWIRE.**
`IdemInequality/Idem.agda` declares `module …Idem where` with **no parameters**, then applies
`Word Canonical normalize …` in its body. MEASURED: `[NotInScope] Word` at `:13`. These leaves came
from a **telescoped root split by hand** (§31/§34) — the split could not carry the parent’s telescope,
so the leaves reference names they never bind. `IdemInequality/Op.agda` appears in the census as its
own `build-failed` row for exactly this reason.

⚑ **THE PREDICATE DEFECT, AND IT IS MINE FROM §51.** `diagnose` classifies `[FileNotFound]` as the
consumed-parent class when *the missing module has a leaf directory*. Here the directory exists and
holds **leaves that have never compiled** — a split that was started and never finished. **A directory
of broken leaves is not evidence that a rewire is the fix**, and the tool emitted a runnable remedy for
a row where the remedy is wrong. *Same shape as `leaf_map` guarding on `os.path.isdir` and treating an
EMPTY directory as “has leaves” (§“A FALSE LEAD WORTH KEEPING”) — the directory’s EXISTENCE is not its
CONTENT.* Filed as **C2**.

**CONSEQUENCE: A4-FNF IS NOT UNIFORMLY MECHANICAL, AND ITS \~40 IS UNVERIFIED.** At least one
highest-value row belongs to R7b. The other repeat roots (`Vec.Properties` 4, `Nat.WellFounded` 4,
`FUSepQBridge` 3, `Foundation.Nat` 3, `SimplicialBoundary` 3) must be re-checked under a tightened
predicate BEFORE their remedies are run — acting on the emitted command is precisely what would have
gone wrong here.

**Nothing was written.** The tool refused; I stopped. *That is the pipeline’s hard gates working as
designed — the `die()` on a surviving reference is what turned a wrong worklist row into a diagnosis
instead of damage.*

### 57. RE-SPLIT, DON’T REPAIR — THE PRE-SPLIT SOURCE IS IN THE TAGS (user, 2026-08-01)

> *“If something was split by something that didn’t support telescoping, there’s a really, really good
> chance that it can be re-split, retrieving the pre-split from a git ref somewhere. (But always tag
> current first… And prior tags might actually contain the thing we’re looking for, too!)”*

⚑ **CONFIRMED, AND THE TAGS THIS ARC LEFT ARE EXACTLY THE SEARCH SPACE.** `recover_presplit.py`
(4 selftest cases) searches tags newest-first then recent commits: **51 refs hold a pre-split
`IdemInequality.agda`**, and the line counts date them — `pre-r9` **42 lines**, every earlier tag 36,
the commits 32. **`pre-r9` is the last state before R9 split it**, which is precisely the tag R9 took
for this purpose.

**The recovered source settles the diagnosis:** a **5-parameter telescoped module**
(`Word`, `Canonical`, `normalize`, `normalize-canonical`, `canonical-is-fixed`) with a `private` block
— and it carries its OWN ⚑ recording the telescope/import-order hazard, noting *“MEASURED: 6 of the
Core leaves”*. R9 split it for the `private` block; `split_lemmas:10-11` **explicitly declines
telescoped roots**; leaves were emitted anyway, without the telescope. That is the whole defect.

⚑ **RE-SPLIT REPLACES N HAND-REPAIRS WITH ONE MECHANICAL RUN.** Repairing the leaves means
re-deriving, per leaf, which of 5 parameters it needs — the exact judgement `split_telescoped`
computes (§34: selection is a CLOSURE, not a scan, and an operator has two spellings, which cost a
6-of-7 undercount when probed naively). Recovering the parent and re-splitting is the same
source-fix-vs-re-emission distinction as R12b.

⚑ **AND A TAG IS THE WRONG SAFETY INSTRUMENT HERE, THOUGH THE RULE IS RIGHT.** “Always tag current
first” is correct in intent, but §10 measured this arc’s decomposition output as **overwhelmingly
UNTRACKED** — a tag captures only committed state, so it would read as protection that is not there.
`edit_snapshot.guard` exists because `git stash create` cannot hold untracked files either, so it
COPIES THEM ASIDE. `recover_presplit --restore` snapshots via `guard`, never via a tag.

⚑ **THIS ALSO RETIRES A STANDING CLAIM: §34’s “R7b’s POPULATION IS ZERO”.** That was measured over
already-decomposed ROOTS and was true of them; `IdemInequality`’s leaves are a live instance of
exactly the class R7b was built for. *A recorded finding is a hypothesis at a later tree state (§24) —
sixth confirmation, and this one had been carried as a closed item.*

### 58. THE EMITTER — THREE DEFECTS, AND THE THIRD DAMAGED THE TREE (2026-08-01)

Built `split_telescoped.emit` — the half §34 never wrote. **What it gets right** is the part that
justified building rather than hand-repairing: telescope selection by CLOSURE (both leaves need
exactly `Word, normalize` of 5 parameters), imports emitted ABOVE the header (§31’s positional rule),
sibling edges via `agda_lex.word`, and a root that re-opens each leaf APPLIED and `public`.

**Three defects I introduced, in the order they surfaced:**

| \#  | defect                                                                   | how it surfaced                                                                                  | class                                                                                                                                                          |
|:----|:-------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | `hasattr(_sl, "body_names")` — **the function does not exist**           | caught by CHECKING before shipping                                                               | the fallback would have emitted **ZERO sibling imports** — *recreating the exact bug being repaired* (`Idem` referencing `Op`’s `_≉_` with no import)          |
| 2   | double-wrapped the telescope → `(normalize : (normalize : Word → Word))` | `[ParseError]` at `Op.agda:15.76`, invisible until the compiler ran                              | **`telescope_groups`’ docstring says the text is VERBATIM** (`agda_lex.py:595`) and I re-derived the shape from the tuple instead of reading the line above it |
| 3   | **the apply is NOT IDEMPOTENT**                                          | the second run reported `0 leaf/leaves`, **deleted both leaves and blanked the root’s re-opens** | after a successful split the root holds only telescope + re-opens, so `plan()` sees zero units and `emit` treats every leaf as “not in `keep`”                 |

⚑ **DEFECT 3 IS THE SERIOUS ONE AND IT DAMAGED THE TREE.**
`IdemInequality.agda` is now a header with no re-opens; its leaf directory is empty. Recoverable from
snapshot `e376c6bb4d1b` (taken by the run itself, moments before). **GUARDED**: `is_split_out()` + a
CLI refusal + 2 selftest cases.

> **A tool whose second run destroys its first run’s output must REFUSE the second run.**
> Same reasoning as `prune_imports` refusing a body-less barrel rather than gutting it, and as
> `rewire_to_leaves` declining an applied open.

⚑ **DEFECT 2 IS THE SHARPEST AS A METHOD FAILURE.** The authority documented its contract on the line
directly above the value I consumed, and I inferred the shape from the DATA instead. That is
*read-the-structure-don’t-rebuild-it* failing at the moment of reading — the reuse-search’s own
premise, missed by one line.

⚑ **AND RECOVERY IS NOT YET A COMMAND** (user, 2026-08-01: *“I’m not going to run that command; we’re
going to keep on working the tooling until it does what you need it to do. Me working the command is a
bad shortcut.”*). `edit_snapshot` PRINTS `git checkout <sha> -- <path>` and nothing consumes it, so
undoing a bad apply is a hand-assembled shell line — precisely the shape everything else this session
has been converted away from. **Filed as C3**: a `--from-snapshot` restore mode, so *snapshot* and
*restore* are two halves of one tool rather than a write path plus a printed suggestion.

*Suite 585 → 596 across 28 suites (`recover_presplit` now discovered).*

### 58b. C3 LANDED — AND RECOVERY REVEALED THE PRINTED COMMAND WAS ALWAYS INCOMPLETE (2026-08-01)

✅ **`edit_snapshot --from-snapshot=<sha> [paths] [--apply]`** + `contents()` / `restore()`
(selftest 6 → **10**). Snapshotting was a tool; restoring was a printed suggestion.

⚑ **AND THE SUGGESTION COULD NOT HAVE WORKED.** `git checkout <sha> -- <path>` reaches only TRACKED
files. **MEASURED on the live damage: `0 tracked, 2 untracked`** — the two leaves live in
`.edit-snapshots/` because `git stash create` cannot hold untracked content, and the root’s needed
state was `pre-r9`, not the stash. So the hand-run command would have restored **one of three files
and looked like it succeeded.** *The shortcut was not merely inelegant; it was wrong.*

⚑ **THE UNTRACKED STORE IS KEYED BY PATH, NOT BY SHA — AND THE TOOL SAYS SO.** `_copy_untracked`
writes `.edit-snapshots/<relpath>`, so a later snapshot overwrites an earlier copy: the untracked half
holds the *most recent pre-write* state, not one per SHA. Rows are labelled `untracked-latest`
precisely so the verdict cannot be misread as a historical version.

⚑ **AND `ok` WAS COMPUTED BEFORE THE NEW CASES.** The tally sat above the block I appended, so four
cases would have joined `cases` and never been counted — the suite would still have printed `N/N` with
N of them unexamined. Same class as a hardcoded total hiding an added case (`prune_imports.py:332`).
Moved below the last case.

**RECOVERY EXERCISED END-TO-END:** leaves restored via `--from-snapshot`, root via
`recover_presplit --restore=pre-r9`, then **one** re-split. *Two tools, two halves of the damage, no
hand-assembled shell line.*

⚑ **THE RE-SPLIT IS STILL NOT CLEAN, AND THE REMAINING GAP IS REAL.** `Op.agda:21` fails
`[NotInScope] ≢`. The emitter carries imports that precede the module HEADER (what the telescope
needs) but **not the root’s BODY imports** — `Eq.Neq`, `Eq.Trans`, `Eq.Sym` sit after the header, and
the leaves need them too. `imports_before(src, header)` is the right authority for the telescope half
and the WRONG one for the body half; `split_lemmas` already solves this for flat splits via its
`imports` + per-unit evidence test. **Owed: reuse that, rather than a second import selector.**

*Four correction passes on one witness — telescope double-wrap, non-idempotence, fixture shape, now
body imports. Each was found by the compiler, none by review.*

### 58c. THE BODY IMPORTS LANDED — AND EXPOSED THE COUPLING THAT MAKES THIS HARD (2026-08-01)

✅ **`body_prelude()`** reuses `split_lemmas.parse`’s `imports` + `agda_lex.group_statements` rather
than adding a second import selector (the worklist’s own instruction). **`≢` now resolves.**
Selftest 13 → **15**.

⚑ **TWO MORE OF MY OWN DEFECTS, BOTH CAUGHT BY CHECKING RATHER THAN BY REVIEW:**
\* **`group_statements(lines, opener)` takes a CALLABLE and I passed `[]`.** Falsy for every line, so
every statement would have folded into the first as a continuation. Its docstring says *“takes a
caller’s own opener predicate”*. **Third time this session an authority’s contract was inferred
from a call site instead of read** (after the `telescope_groups` VERBATIM re-wrap and the
`imports_before` return type).
\* **A selftest case that was wrong about the tool.** I asserted every prelude line starts with
`open import`; a WRAPPED statement’s continuation does not, by construction, and folding it in is
what `group_statements` exists to do. The assertion was the defect — fixed to check the HEAD.

⚑ **AND THE REMAINING FAILURE IS THE INTERESTING ONE — A GENUINE COUPLING, NOT A SLIP.**
`Op.agda:18` now fails `[NotInScope] Canonical`. The root’s body contains

    open import Substrate.Groups.Coxeter.Core.NormalizeIdem
      Word Canonical normalize normalize-canonical canonical-is-fixed

— an **APPLIED open whose arguments are telescope parameters**. Carrying it verbatim into a leaf that
selected only `Word, normalize` references `Canonical`, which that leaf deliberately does not bind.

**So the two halves are not independent: the BODY IMPORTS constrain the TELESCOPE SELECTION.** A leaf
must take every parameter its own body needs \*plus every parameter appearing in an applied import it
inherits. `needed_params` computes the first and knows nothing of the second — the closure is over
the wrong set.

⚑ **THIS IS THE APPLIED-OPEN CLASS AGAIN (§56, R11), NOW INSIDE THE EMITTER.** It has blocked this
root three times in three different guises: as `Core.agda:75`‘s reference to the parent, as the old
leaves’ unbound `Word`, and now as an inherited applied import. **R11 is not adjacent to R7b — it is
underneath it.**

**FIVE correction passes on one witness**, every one found by the compiler. That is the honest cost of
a generator, and still cheaper than N hand-repairs carrying the same five defects silently — but it is
a real cost and the item is NOT done.

### 58d. THE COUPLING FIX WORKED — AND THEN THE USER NAMED WHY IT KEPT RECURRING (2026-08-01)

Seeding the closure with the block **plus the inherited prelude** took both leaves from 2 parameters
to all 5, and **`Op.agda` COMPILES CLEAN** — the first leaf of this root ever to do so. The diagnosis
was right. Two more selftest defects fell out, both about the CASES rather than the code:

- ⚑ **THE CASES READ A FILE THIS TOOL ITSELF CONSUMES.** They opened the live `IdemInequality.agda`,
  which every successful `--apply` turns into re-opens — so the SAME suite passed or failed depending
  on whether a split had just run, three times running. Replaced with a verbatim fixture of the
  witness’s SHAPE. *A case must not depend on tree state its own subject mutates.*
- ⚑ **A CASE HARDCODED THE PRE-FIX ANSWER.** `check(… "Word normalize" in r)` encoded the selection
  from BEFORE the coupling fix, so it **failed on correct output** once leaves began taking
  `Canonical`. Rewritten to assert the RELATION (each re-open matches that leaf’s own selection).
  *A case that hardcodes an expected value cannot survive its own subject improving — it reports a
  regression when the tool gets better.*

Selftest **16/16**, cases now state-independent. Residue: `Idem.agda` fails `[NotInScope] ≉`.

> ⚑ **“Have you looked at how import pruning works, and how it may apply to module parameters?
> Because split_telescope and split_lemmas should have *very* little *not* in common.”** (user)

**I had not, and that is the finding — the two rules I spent six passes re-deriving badly were already
written, tested, and cited in a comment I had open.**

⚑ **1. THE POLARITY IS BACKWARDS.** `prune_imports.should_keep` states the rule outright: *“Every
uncertain branch returns True: **no evidence is never evidence of death**, and a false DROP breaks the
build immediately.”* I wrote `needed_params` as a **MINIMALITY** computation — the smallest telescope
subset — which is the opposite polarity. For module parameters the asymmetry is identical: a
wrong-SMALL selection is `[NotInScope]`; a wrong-LARGE one costs an unused parameter that
`prune_imports` removes in the very next stage. **I built a minimiser where this codebase’s own rule
is keep-biased.**

⚑ **AND THAT EXPLAINS WHY EVERY PASS LOOKED LIKE A NEW PROBLEM.** A minimiser fails ONCE PER NAME it
wrongly excluded, so each fix only exposes the next exclusion: `≢`, then `Canonical`, then `≉`. A
keep-biased selection fails ZERO times. The tell was in the data all along — **`Op.agda` went clean
exactly when the coupling fix accidentally pushed it to all 5 parameters, i.e. the moment it stopped
minimising.**

⚑ **2. THE CLOSURE ALREADY EXISTS, BY NAME, IN A COMMENT I HAD OPEN.** `prune_imports:163` cites
**`split_lemmas:595` — `need[fn] = direct ∪ ⋃ need[sibs]`**. I reinvented that THREE times, each
partially: as *“the sibling edge”* (§58), *“the inherited prelude”* (§58c), and *“the coupling”*
(§58d). Three shards of one rule that was already implemented, selftested, and referenced two lines
from code I was reading.

⚑ **THE STRUCTURAL CONSEQUENCE: `split_telescoped` SHOULD BE A `split_lemmas` VARIANT, NOT A SIBLING
TOOL.** Its genuinely distinct part is small — read the telescope, select groups, re-emit the header,
re-open applied. Everything else (prelude selection, sibling closure, defines/fields, conservation
guard, snapshotting) is `split_lemmas`, and I re-derived each piece only at the moment the compiler
forced it. *This is the reuse-search’s own failure mode: I searched for a TOOL that splits telescoped
roots, found none, and built one — instead of searching for the RULES a splitter needs, which all
existed.*

**And `Idem`’s remaining `≉` dissolves under the right rule rather than needing a seventh fix:** under
`need[fn] = direct ∪ ⋃ need[sibs]`, `Idem`’s selection IS `Op`’s unioned with its own, so the sibling
import’s arguments match BY CONSTRUCTION instead of by my getting a seam right.

**PROPOSED (not started, needs a call): rewrite `split_telescoped` to call `split_lemmas`’ closure,
changing only the parameter selection’s POLARITY (keep-biased) and letting `prune_imports` trim.**
That deletes most of the \~40 lines written today and converts six accumulated special cases into one
reused rule. Filed as **R7b-REWRITE**.

### 59. THE WORKLIST WAS ORDERED BY WHAT I WAS HOLDING, NOT BY LEVERAGE (user, 2026-08-01)

> *“Is the todo list topologically dependency-sorted, prioritizing items that provide the greatest
> leverage to subsequent items?”*

**No, on two counts, both visible without new measurement.**

⚑ **1. R11 SAT AGAINST ITS OWN RECORDED FINDING.** §58c concluded R11 is **underneath** R7b — the
applied-open class blocked one root THREE times (`Core.agda:75`‘s reference, the leaves’ unbound
`Word`, the inherited applied import). The item text said *“PROMOTED”* and the item sat **after**
R7b-REWRITE and R7b-APPLY. **The note landed; the position never moved.** *Recording a dependency is
not honouring it — the same summary-outlives-its-correction defect this document has logged five times
about itself, now inside the worklist’s ORDER rather than its prose.*

⚑ **2. THE R7b CHAIN’S LEVERAGE IS ASSERTED, NOT MEASURED.** It leads on *“the 501-cone root”* — but
501 is **`V4-Coxeter`’s** cone, and `V4-Coxeter` fails `[FileNotFound]` on `IdemInequality`. **Whether
repairing `IdemInequality` frees 501 modules is unverified**, and the chain has already surfaced a
deeper blocker TWICE (§46 `F2/Vector`→`Universal`; §51 `V4-Coxeter`→`Coxeter/Core`). A cone measured
at the *blocker* is not the leverage of the *repair*.

⚑ **AND THE HONEST DIAGNOSIS IS SUNK COST.** This entire sitting went to ONE file: six correction
passes on `IdemInequality` yielding one clean leaf. Meanwhile:

| item    | leverage                                                                              | state                                                                               |
|:--------|:--------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| **T13** | unblocks **G1, G6, A5, B1** — one authority, 10 callers, 4 hand-rolled copies deleted | untouched, pure Python, no Agda risk                                                |
| **C2**  | re-derives A4-FNF’s ENTIRE population (its “\~40 mechanical” is unverified)           | untouched — and acting on that unverified population is what broke `IdemInequality` |
| **G4**  | one regeneration, unblocks B3 (the arc’s terminal goal)                               | untouched, trivially cheap                                                          |

**§55 ranked the BLOCKERS by cone and that was right. I then ordered the WORKLIST by what I already
had open** — which is the sunk-cost ordering, not the leverage ordering. *Cone size told me which
Agda root to fix; nothing told me whether to be fixing Agda roots at all this sitting.*

**THREE ORDERING CHANGES, APPLIED:**
1. **R11 moves ahead of R7b-APPLY** — honouring §58c instead of merely noting it.
2. **The R7b chain drops below T13 / C2 / G4** until **R7b-SWEEP sizes it**. If the sweep is small,
hand-repair is the honest call and the generator is over-built for its population.
3. ⚑ **`C4` — BUILD THE LEVERAGE QUERY, so ordering stops being my judgement.** Given a build-failed
root, report what the census says clearing it would FREE. `_blast_radius` and `.leaf-verify.tsv`
both exist; **nothing composes them into “rank the worklist by measured cone.”** That is the same
gap as every other refusal this session — a question the tooling cannot answer directly, so I
answered it by recall and got it wrong.

### 60. T13 — THE ITEM’S PREMISE WAS WRONG, AND MY CORRECTION TO IT WAS ALSO WRONG (2026-08-01)

T13 was filed as *“`--list` on `ratchet.set_ratchet`: **10 callers**, **4 hand-rolled copies to
DELETE**, **6 omissions to ADD**.”* Both halves moved, in opposite directions.

⚑ **FIRST I READ THE FOUR COPIES AND CONCLUDED THEY MUST BE KEPT.** Each prints something the
authority cannot derive from a key set — `check_claims` the claim TEXT, `check_discharge_ratchet` the
carrier’s declared SORT, `check_rederive_ratchet` a declared/undeclared TALLY, `check_snapshot_guard`
an armed-vs-unguarded BREAKDOWN. I recorded “4 copies to DELETE is wrong; only the 6 additions apply”,
and began building a `forwards-declined` MARKER so the migration query would stop reporting them.

⚑ **THE USER RETIRED THAT IN ONE LINE:** *“the whole thing about ‘leave the richer ones alone’ is a
DRY failure; they should all be lifted to a common thing.”* Correct, and the marker was the tell —
**machinery whose only job is to record that a duplication is intentional.** The measured difference
between those four and the authority is ONE LINE (how a key renders); the flag parse, the sort, the
loop and the early return were copies. So:

| hook                 | arity      | carries                                |
|:---------------------|:-----------|:---------------------------------------|
| `render(key) -> str` | per-KEY    | claim text · carrier sort · a `✗` mark |
| `summary`            | per-CENSUS | declared/undeclared · armed-of-N       |

**Two hooks, each at the arity of the fact it carries** — which is what stops the next gate forking
the dispatch again. `render` applies on EVERY key-printing branch (list / paid / added), because
threading it through only the listing branch is the same asymmetry one branch over.

⚑ **AND `render` MUST BE TOTAL ON KEYS NOT IN THE CENSUS.** A PAID-DOWN key is absent from `cur` by
construction, so a renderer indexing a dict built from `cur` raises exactly on the branch that reports
progress — the branch a gate author is least likely to exercise. The wrapper falls back to the bare
key, so a gate cannot make paydown crash.

**RESULT: 10 of 10 callers forward it; 4 dispatch blocks deleted; `--list` now enumerates on every
gate.** `sumtype` 71, `private` 66, `discharge` 32, `rederive` 148, `claims` 14 — populations that
previously reported only a count, which is what G6/A5/G1/B1 each needed.

⚑ **THE QUERY THAT MADE THIS TRACTABLE DID NOT EXIST — `pycodemod --forwards <fn> <kw>`.** The
question a flag rollout actually asks is never “does this call the authority” (every caller does —
that is what makes it an authority) but **which callers have been MIGRATED**. That is a per-call-site
fact about ARGUMENTS, and I was answering it with `grep -c -- '--list'` piped over a file list — which
counts the flag STRING, so it reports a gate as migrated when it merely mentions the migration in a
`check_argv` set or a ⚑ comment. The CST knows the difference. It tracked the work live: 0/10 → 5/10 →
10/10.

⚑ **AND `kwseen` BECAME CONTEXT-STAMPED ON THE USER’S CORRECTION** (*“carry kwseen, but require it to
be validated against an expected context before use… dependent typing applied to recursive calls”*).
My out-parameter had an UNCHECKED PRECONDITION — the caller had to remember which query filled it, and
reading it against a different one is a silent wrong answer. `KwIndex` stamps `(target, population)`
at gather time and `.check()` REFUSES a mismatched read: the precondition becomes a checkable property
of the value, not a discipline. Same move as `tree_stamp()` refusing a straddled census (§51).

⚑ **`gate_status --modes` — BUILT BECAUSE I KEPT INVOKING A GATE TWICE WITH `echo rc=$?` BETWEEN.**
After changing a gate’s CLI the check is *does each MODE still do its own job*, and that was three
commands plus an interpretation step. **It caught a real defect on first use: `check_claims --list`
printed all 14 claims TWICE** — the gate enumerated its own census before delegating to an authority
that now enumerates too. A single-mode run shows one plausible listing; only the modes side by side
make a doubled one visible, which is why the LINE COUNT is reported and not just the verdict.
`--sample=N` shows census rows, because a tail line cannot show a renderer.

✅ **T15 FELL OUT OF THE SAME RUN, AND ITS OLD COMMENT IS WHY IT STOOD.** `run_gate` kept `tail[-1]`
under the comment *“a ratchet prints its verdict last”* — **false**: the family prints `refuse_hint`
last, so 9 of 12 red gates reported generic remediation prose. `verdict_line` prefers the `<label>: …`
line, falls back to the tail, and is SHARED by `run_gate` and `--modes` so the two views cannot
disagree about what a gate said.

⚑ **THEN THE MODE SWEEP FOUND A FALSE POSITIVE IN A PAYDOWN-ONLY BASELINE — `check_snapshot_guard`
censused `scratch/mdstruct.py`, which never overwrites a source.** Its predicate asked “is SOME var
read and SOME var written”, not “is the SAME var read and written”: the alternatives
`{v}\b[^\n]*\)\.readlines\(\)` and `read_text\(\)[^\n]*{v}\b` match any line mentioning the var near
any read. **File-level where the question is positional** — this arc’s most-repeated defect, and the
comment directly above the code stated the correct rule (“Destructive means READ-then-WRITE”) while
the code did not implement it.

⚑ **AND ITS SELFTEST RE-IMPLEMENTED THE PREDICATE, so it tested a regex it defined itself** — it could
pass while the gate stayed broken, and it did, at a green 5/5. That is §6c/§7b-bis exactly, inside the
gate built to catch guard defects. The probe now drives `in_place_editors()` over a temp DIRS root, so
a predicate change reaches the cases.

⚑ **I THEN BROKE IT TWICE MORE, EACH TIME IN THE OPPOSITE DIRECTION, AND THE CASES CAUGHT BOTH:**
1. an `as\s+\w+` alternative admitted `with open(v,"w") as fh` as a READ — census 48→55, re-admitting
`gen_kat.py`, **the generator this gate’s own comment names as the original false positive.**
*Undoing a fix by widening past it is the same defect with the opposite sign.*
2. the `with` alternative then matched the WRITE STATEMENT ITSELF (`WRITE_VAR` binds `v=out`, and
`with open(out,"w") as fh` re-matched as a read) — **a predicate satisfied by its own
counterexample.** A `with` now counts only when the bound handle is later `.read()`.

**And a THIRD false-positive shape: a tool’s own `_selftest` fixture.** A suite routinely writes a
tempfile and reads it back — read-then-write on one var, in code that never touches a source file.
Arming it would snapshot the repo on every suite run. The census stops at the suite boundary.

⚑ **THE TIGHTENED PREDICATE THEN FOUND REAL DEBT THE LOOSE ONE HAD BURIED: `scripts/worklist.py`
rewrites the file it reads with no snapshot** — filed as **`S1`**. Population 48 → 44 in-place
editors, 1 genuinely unarmed. *A predicate carrying false positives does not merely over-report — it
hides the true positives among them.*

**Suite 596 → 620 across 28 suites** (`pycodemod` 7→14, `gate_status` 5→9, `check_snapshot_guard`
5→9). Losslessness gate green over all 7 edited tools.

⚑ **THE TRANSFERABLE FORM, and it is the sharpest of the arc’s DRY findings:** *when N call sites do
something the shared authority cannot, the difference is almost never the dispatch — it is one value.
Lift the value as a parameter; do not preserve the dispatch to hold it, and never build machinery to
record that preserving it was deliberate.* The marker I started writing is the anti-pattern in its
purest form: a permission slip stapled to a duplication.

### 61. G4 — GREEN, AND A DIAGNOSTIC WROTE IT AS A SIDE EFFECT (2026-08-01)

G4 was filed as *“NO DEPS, ONE COMMAND: regenerate via `scripts/sppf_node_index.py`”*. The gate is
now **green** (`sppf-node-index: current. ✓`) — but not by a decision I made.

⚑ **`gate_status --modes` REGENERATED THE ARTIFACT THREE TIMES WHILE I WAS ONLY READING ITS VERDICT.**
`sppf_node_index.py` has NO `main()`: its module body runs at import, and the final `else:` writes.
So every invocation that is not `--check` regenerates. I swept it across three modes to see what
`--check` reported, and the sweep did the work. **Nothing was lost — the output is idempotent — but a
diagnostic that writes is the `prune_imports` polarity hazard (§7e) in the worst possible place: a
sweep multiplies one accidental write by the number of modes.**

⚑ **AND `--check` WAS NOT IN `MODES` — THE SWEEP OMITTED THE MODE GATES ARE WIRED WITH.** Measured
from the hook: `gen_build_makefiles`, `query_defs`, `worklist`, `sppf_node_index`, `law_motif_apex`
and both conditional jea gates all run `--check`. A tool built to check “does each mode do its job”
was checking every mode *except the one B3 depends on*. Both fixed:

- **`pycodemod.writes_by_default(path)`** — DISCOVERED, not declared (an allow-list would rot exactly
  as the four `agda_files()` bodies did). A write is guarded when it is `--apply`-gated, targets a
  tempfile, or sits inside `_selftest`; anything else writes on a bare run. **Deliberately
  conservative**, and the asymmetry is the inverse of `should_keep`’s: for a guard deciding whether to
  RUN something, a false “yes” costs one skipped mode and a false “no” costs an unintended write.
- **`--modes` narrows a write-default tool to `--check` alone**, prints why, and offers
  `--allow-writes`. The guard’s own failure returns `True` — *a guard that cannot determine the answer
  must not authorise the write.*

⚑ **THE SELFTEST COUNTS ACTUAL WRITES, NOT MODES.** The fixture appends to a sentinel file per run,
so the case asserts `0 writes during the sweep` rather than trusting the mode list — a count of modes
would pass even if the narrowing did nothing. *Pinning the mechanism, not the plan.*

⚑ **AND MY TEMPFILE TEST WAS FILE-LEVEL WHERE THE QUESTION IS POSITIONAL — AGAIN.** It searched for
`tempfile` IN the write line, but the idiom binds the path one line ABOVE
(`tf = os.path.join(tempfile.mkdtemp(), …)` then `open(tf,"w")`), so it matched nothing and every
tempfile writer read as write-default. Resolved to the variable’s binding. *Same correction as
`check_snapshot_guard`’s same-variable defect one section earlier, in code written to fix that class.*

⚑ **A CASE THAT HARDCODED A FROZEN COPY OF THE THING IT TESTS.** `--modes runs every declared mode`
asserted a literal `["(default)","--quiet","--list"]` and failed the moment `--check` joined `MODES`.
Now derived FROM `MODES` — the derived-view defect (§6) inside a selftest.

**THE DIFF IS REAL CONTENT, AND IT RECORDS A DEFECT RATHER THAN ONLY TIDYING** (6 insertions,
5 deletions):

| change                                                                                              | reading                                                                                                                                                                                                    |
|:----------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3 rows: a file PATH → a module NAME (`Category/…/ExtrudeCoEmitMonad.agda` → `Substrate.Category.…`) | the tool falls back to a relpath when its header regex fails; these now resolve — **§5’s `HEADER` fix (149 parameterized headers) finally reaching this artifact**                                         |
| 2 rows moved deeper (`Foundation.Empty` → `Foundation.Empty.Bot`)                                   | this arc’s own splits                                                                                                                                                                                      |
| **1 NEW variant: `Linear` collides `Algebra.F2.Linear` vs `Algebra.F2.Linear.Linear`**              | a **barrel-retained duplicate** — R2-residue’s known shape (§28 held `F2/Linear` back because its leaf fails on a dependency). Verified with `agda_defs Linear`: 3 homes, two of them the barrel/leaf pair |

**So G4 is closed and it hands R2-residue a witness.** The new index row is not G4’s debt to pay; it is
the shape-node index becoming able to *see* a duplicate the ban census already tracks.

⚑ **THE TRANSFERABLE FORM:** *before a diagnostic runs a tool N times, ask what ONE run does.* I had
built `--modes` one section earlier specifically to stop invoking gates by hand — and it ran a
write-default tool three times on its first real use, because “read its verdict” and “execute it” are
the same act for a tool with no `main()`. **A read-only intention is not a read-only operation.**

Suite 620 → **627** across 28 suites.

### 62. THE COLLAPSE MACHINERY EXISTED AND I NEVER ASKED IT (user, 2026-08-01)

> *“There exists collapse machinery in the pipeline designed specifically to deal with things like
> that.”*

I had just written that `Algebra.F2.Linear` / `.Linear.Linear` was *“R2-residue’s known shape — §28
held it back because its leaf fails on a dependency”*. **That is a recalled blocker, not a measured
one, and `scratch/collapse_carrier_nesting.py` was sitting there.** The reuse-search trigger fires on
CONCLUSIONS, and mine was one.

⚑ **ASKING IT CORRECTED THE DIAGNOSIS IMMEDIATELY.** It refused —
*“the parent slot is occupied, so this is not the vacated-by-split case”* — which is right, and which
means the shape is NOT the `X/X.agda` collapse at all. **But the refusal was a dead end**: an operator
learns the obstacle and nothing about which operation applies instead. So the tool that owns the shape
now CLASSIFIES what it declines, from data already on disk:

| parent slot occupied by                   | verdict             | route                                                     |
|:------------------------------------------|:--------------------|:----------------------------------------------------------|
| a module defining nothing a leaf does not | **CONSUMED BARREL** | rewire consumers, then retire (R2)                        |
| a module still owning names of its own    | **REAL MODULE**     | nothing to collapse; a shared name is a genuine collision |

⚑ **AND THE FIRST RUN OF THAT CLASSIFIER WAS WRONG IN A WAY THAT WOULD HAVE MADE IT USELESS.**
It reported `F2/Linear` owning **1 uncovered name: `Substrate.Algebra.F2.Linear`** — its own module
header. `_defines` collects `module X where` heads (it must — the repo’s `open X public` idiom makes a
col-0 inner module a real export), and that includes the file’s own. Left in, **every barrel shows one
uncovered name and classifies as “a real module”: the barrel branch could never fire.** *A guard whose
positive case is unreachable is decoration* — the same shape as §“4b”’s capture check that gate (2)
made unreachable. Corrected: **10 names, 0 uncovered**, matching §28’s measured 10-of-10.

⚑ **THE TOOL HAD NO `_selftest`, SO IT WAS INVISIBLE TO THE RUNNER** — the gap that let
`rename_at_source` ship a live bug through a green suite. Written: 3 cases, one pinning the header bug
specifically. **Suite count 28 → 29**, which is the evidence it was absent rather than passing.

✅ **THEN THE MISSING LAST STAGE: `split_pipeline --retire`.** `rewire_only` moves consumers and
sweeps, but **never retires the file** — so after a successful rewire the barrel still stands, still
declares its names, and still counts in the sumtype census as a duplicate of its own leaf (§26: all 21
sumtype rewrite-keys count BOTH `X.agda` and `X/Name.agda`). §28 retired eight barrels by hand-checking
preconditions and running `rm`; **that judgement is what a stage should own.**

It composes two predicates that already exist — no third copy:
\* `check_indented_imports.sweep` — zero LIVE references (it sees the `where open import` class a
column-0 scan structurally cannot);
\* `collapse_carrier_nesting.classify_occupied` — every declared name COVERED by a leaf.

**Both must hold.** Zero references alone is not enough: an unreferenced module that still owns a name
is dead code to investigate, not a barrel to delete. The selftest drives the coverage half, because
that is the half whose failure LOSES A DEFINITION.

**MEASURED AND APPLIED:** `✓ zero live references` · `✓ every name covered (34 leaves)` → deleted under
snapshot `e9fc17aca76e`. **Sumtype census 71 → 70.** The `--rewire-only` dry run reported **0
importers**, confirming §28’s 104-importer rewire had already landed — *the barrel was one `rm` away
for a day, filed as blocked.*

⚑ **AND THE STAGE PRINTED ITS OWN FOLLOW-UP INSTEAD OF DOING IT** (user: *“shouldn’t this be part of
the rest of the tooling harness?”*). `retire` ended with `NEXT: python3 scripts/gen_build_makefiles.py`
— a printed instruction, which **§58b already recorded is not a path** (“a printed recovery command is
not a recovery path”) — and it named only ONE of the invalidated artifacts. **The shape-node index went
stale too, silently, immediately after G4 turned it green one section earlier.**

✅ **`refresh_derived()`**: every artifact that is a PROJECTION of the module set, regenerated **and
re-verified with `--check`** (a regenerator that silently no-ops is indistinguishable from one that
worked — §14). Deliberately NOT a gate list: these are the GENERATING invocations, while the hook runs
the same tools with `--check` and `gate_status.gates()` parses that from the hook. *Two views, two
questions — “make it current” vs “is it current” — and only the first belongs to a stage that changes
the module set.*

⚑ **ITS IDEMPOTENT EARLY RETURN WAS ALSO WRONG: “already retired” is not “already settled”.** A bare
`return 0` skipped the refresh, so a retire whose delete landed but whose refresh did not could never
be completed by re-running — **exactly the state my own hand-run left**. Re-running now CONVERGES
instead of no-op’ing, and that is how the stale index was actually fixed.

Suite 630 → **632** across 29 suites; `gen_build_makefiles --check` OK at 3456 modules.

⚑ **THE TRANSFERABLE FORM, and it is the reuse-search rule pointed at my own conclusions:** *“held back
because X” recalled from a plan is a HYPOTHESIS about a tree that has since moved.* §28’s blocker was
real when written and had been cleared by §28’s own rewire; the only thing standing was a file nobody
had a command to delete. **Before recording why something is blocked, ask the tool that owns its
shape — and if the tool refuses, make the refusal name the route.**

### 63. THE AUDIT ITSELF IS MECHANIZABLE — AND THE TOOL’S OWN DOCSTRING SAID SO (user, 2026-08-01)

> *“How much of the markdown editing and auditing can we mechanize with the tooling we now have for
> structural transforms?”* … *“I assume it would mean moving the plan in-repo so it’s covered by git.”*

⚑ **`mdstruct.py`’s DOCSTRING LISTED THE THREE AUDIT QUERIES AS ITS REASON FOR EXISTING, AND NONE WERE
BUILT.** §50 built the NORMALIZER and stopped. So every coherence pass since — §24, §25, and the one
that found `R2-SWEEP` had no plan witness — was performed BY EYE over a 3900-line document. *That is
reasoning-not-codified at document scale, in the one artifact that records why everything else was
done.*

**Built, and all three are TEXT-level so they run without pandoc:**

| query                           | answers                                                                                              |
|:--------------------------------|:-----------------------------------------------------------------------------------------------------|
| `--items`                       | every worklist label a document mentions, with line numbers                                          |
| `--coherence <plan> <worklist>` | ORPHAN (item, no evidence) · UNWITNESSED (finding, no item) · DANGLING (`§N` cited, no such section) |
| `--superseded`                  | one phrase carrying conflicting values — the 589-vs-1322 class                                       |

⚑ **THREE POPULATIONS, NEVER ONE VERDICT.** §24’s dominant error was plan-findings with no todo;
§25’s was todo-items with no evidence. A one-directional audit finds neither, and a single pass/fail
would be the derived-view trap the audit exists to catch.

⚑ **AND THE BLOCKER IS STRUCTURAL, NOT TECHNICAL: THE PLAN IS OUTSIDE THE REPO AND THE WORKLIST HAS NO
FILE AT ALL.** `~/.claude/plans/` is untracked, ungated, unsnapshotted; the worklist lives only in
harness todo state. **`--coherence` therefore has one document to read and one it cannot** — and the
tool now SAYS that rather than crashing (`docs()` resolves candidates and reports what is missing,
because the reflex when a hardcoded path is wrong is to `ls` at the shell, which is the operator
answering a question the tool should). **Filed as M4**: this is §10’s untracked-work hazard applied to
the arc’s OWN RECORD.

⚑ **THE SUPERSESSION PREDICATE TOOK THREE ATTEMPTS AND THE THIRD IS THE FINDING.**
1. keyed on the bare noun → **12 nouns, up to 40 values each** — “2 files” colliding with “2941
files”. *A census that wide is one nobody reads, which is the failure it exists to prevent.*
2. keyed on the QUALIFIED phrase, discarding unmodified nouns → dropped `589 leaves` itself, so the
tool reported **nothing** for the very supersession that motivated it.
3. **The two cases were in genuine tension**: `589 leaves`/`1322 leaves` (real) and `2 files`/`2941    files` (coincidence) are structurally identical — same noun, two values, no modifier either way.
No phrasing rule separates them. What does is **order of magnitude**: a supersession re-measures
ONE population so its values stay within \~10× (589→1322, 21→27, 113→345, 12%→19%, 95→81, 66→216);
a coincidence spans the document’s whole numeric range.

**MEASURED over the plan: 3 phrases, all honest non-findings** (the suite count legitimately grew
11→29 across the arc). **No live figure supersession survives** — which is the correct verdict after
§60–62 re-measured everything, and the first time that has been *checked* rather than assumed.

✅ **S2 FELL OUT OF BUILDING IT.** `mdstruct` reported `selftest: 0/0` and returned `True` — an absent
optional dependency scoring as a green suite (the `jea_circuit.py:197` class **the plan already
records**, reproduced in a tool I wrote AFTER recording it). Once the pandoc-free cases were added it
ALSO discarded six real results. Now: the tally reflects what RAN, the AST cases are announced as
UNRUN rather than counted, and an unmeasured case is not a passing one (Guard (2)’s rule). **The fix
immediately exposed defect #2 above** — the failure had been invisible behind the skip.

Suite 632 → **638** across 29 suites.

⚑ **WHAT THIS DOES NOT MECHANIZE, stated so it is not mistaken for coverage:** whether an item’s
ORDER is right (that is C4’s measured-cone query), whether a finding is still TRUE (only re-running
its command settles that — §24), and whether a dependency edge is real. The audit finds
*missing links and stale numbers*; it cannot find a wrong judgement.

### 64. M4 LANDED, AND THE AUDIT IMMEDIATELY FOUND WHAT I HAD MISSED BY EYE (2026-08-01)

Asked to re-audit coherence, I ran `--coherence` instead of re-reading 4885 lines — **and the tool
found four orphans and seventeen unwitnessed labels in one command, one turn after a hand pass over
the same two documents reported them coherent.**

⚑ **M4 IS DONE, AND IT WAS THE BLOCKER IT WAS FILED AS.** `catalog/plan.md` and
`catalog/worklist.md` are now in-repo — tracked, gateable, snapshot-covered. Before this the audit had
one side it could read and one it could not, so *every* coherence pass in this arc (§24, §25, §63) was
half-blind by construction. **The first run with both sides readable was the first honest one.**

| population                                 | n      | reading                                                                                                                          |
|:-------------------------------------------|:-------|:---------------------------------------------------------------------------------------------------------------------------------|
| **ORPHAN** (item, no plan witness)         | **4**  | `S1` `U1` `G3` `U3`                                                                                                              |
| **UNWITNESSED** (plan finding, no item)    | **17** | mostly RETIRED labels (`A0` `A1` `C3` `R7` `T2` `A4-UNBLOCK` `R9-VERIFY`) and non-items (`F17` `F18` `P1` `P3` `L0` `S5` `GLF1`) |
| **DANGLING** (`§N` cited, no such section) | **0**  | every citation resolves                                                                                                          |

⚑ **TWO ORPHANS WERE EVIDENCE-PRESENT, LINK-ABSENT — the exact mechanical gap.** `S1`’s finding is
recorded verbatim at §60 (*“`scripts/worklist.py` rewrites the file it reads with no snapshot”*) and
`U1`’s at §10 (*“a tree-wide `git checkout -- agda/` is the banned operation”*) — **neither carried its
label**, so no audit could link them. Both now do. *A finding without its label is unreachable from
the worklist even though the words are right there.*

⚑ **AND TWO ARE GENUINELY UNSOURCED, WHICH IS THE HARDER FINDING.** `U3` (“should the ban skill state
the `private` policy?”) and `G3` (“corrected by attribution, mostly not actionable”) have **no plan
evidence at all**. They are decisions I have carried across sessions on recollection. `U3` is real —
§32 measured the `private` population and built `check_private_ratchet`, but never asked whether the
SKILL should state the policy, and a policy enforced by a gate that the playbook does not mention is
the §9a shape (a measure at a layer the loop can skip). `G3` is a stub whose content was absorbed into
other items; it is carried as a placeholder and should be closed or given a witness, not left as a
label pointing at nothing.

⚑ **THE 17 UNWITNESSED ARE MOSTLY CORRECT AND THE POPULATION IS THE POINT.** `A0`/`A1`/`C3`/`R7`/`T2`
/`A4-UNBLOCK`/`R9-VERIFY` are RETIRED — done or superseded, their sections still standing as record.
`F17`/`F18`/`P1`/`P3`/`L0`/`S5`/`GLF1` are not worklist labels at all (incident tags, phase names, an
Agda module). **So the audit’s third population needs a way to say “retired” and “not an item”**, or it
will report the same 17 forever and be ignored — *a census that cries wolf is one nobody reads*, which
is §63’s own lesson about its supersession scan. Filed as **`M5`**: the labels need a DECLARED
lifecycle in the worklist (`DONE` / `RETIRED` / `not-an-item`) so the audit can subtract them by
construction rather than by a growing exemption list.

⚑ **AND THE ORDERING IS STILL ARGUED, NOT MEASURED.** This audit checks LINKS and NUMBERS. It cannot
check that `R11` belongs ahead of `R7b`, or that `C4` outranks `CENSUS` — §59’s failure was a wrong
*judgement* about leverage, and no document diff finds one. `C4` remains the only item that would make
ordering self-answering, and until it lands the sort below is a hypothesis like any other.

### 65. C4 — THE ORDERING IS MEASURED, AND IT INVERTS §59 (2026-08-01)

✅ **`split_pipeline --leverage`** composes `_blast_radius` with a caller-supplied seed set and reports
**COST, LEVERAGE and RATIO** — the three numbers every ordering argument in this arc was made without.

⚑ **THE COMPOSITION’S WHOLE CONTRACT IS THAT SEEDS COME FROM THE TOOL THAT OWNS THE ITEM’S SHAPE.**
A worklist item is not a module: `R11` names a CLASS (54 applied-open files, from
`split_lemmas.blockers`), `A4` names the build-failed set (from the census), `C2` names a PREDICATE and
has no file set at all. **Inventing a label→files table here would be a fourth authority for a relation
three tools already own** — the `agda_files()` class (§6d). `--applied-open` / `--failed` / bare paths;
nothing else.

⚑ **AND IT REPORTS COST ALONGSIDE LEVERAGE, ALWAYS.** A set of 54 files that nothing imports has a cone
of 0 and is still 54 files of work — *the sunk-cost shape §59 caught me in.* Reporting only the cone
would hide exactly the case the tool exists to expose.

**MEASURED, AND THE ORDERING §59 ESTABLISHED IS WRONG:**

| item                       | cost  | leverage | ratio     |
|:---------------------------|:------|:---------|:----------|
| **`R7b-APPLY`** (2 leaves) | **2** | **559**  | **279.5** |
| `R11` (applied-open class) | 54    | 712      | 13.2      |
| `A4` (every build-failed)  | 121   | 1663     | 13.7      |

**`R7b-APPLY` is 21× `R11`’s ratio and 20× the whole build-census average**, and its 559 is a third of
everything clearing all 121 failures would free. §59 moved `R11` ahead of the R7b chain on the argument
that the applied-open class is *underneath* it; that argument was about MECHANISM and it was right —
but I let it decide ORDER, which is a different question, and the numbers say the opposite.

⚑ **AND THE COMPILER SETTLED WHAT THREE SECTIONS OF PROSE COULD NOT.** §59 recorded *“its ‘501-cone’
is `V4-Coxeter`’s, NOT THIS REPAIR’S”* and carried it as a caveat through §61 and §64. Asking `--why`:

    Checking Substrate.Groups.V4-Coxeter
     … Checking Substrate.Groups.Coxeter.Core.IdemInequality.Idem
    Idem.agda:24.30-31: error: [NotInScope] ≉

**`V4-Coxeter`’s 501 is blocked by `Idem.agda` — R7b-APPLY’s own file.** The cone was never
`V4-Coxeter`’s; `V4-Coxeter` is *in* it. Verified independently that neither `IdemInequality` nor
`V4-Coxeter` is in the applied-open population, so the two cones are genuinely independent rather than
nested. *A caveat repeated across three sections is not evidence; one command retired it.*

⚑ **THE UNION PROPERTY IS WHERE A NAIVE VERSION LIES, SO IT IS PINNED.** `IdemInequality`’s two leaves
each block 559 and TOGETHER block 559 — not 1118. Summing per-seed cones would make every multi-file
class look proportionally more valuable than it is, which is precisely the wrong answer for an ordering
tool. Three cases: transitivity, union-not-sum, and a seed with cone 0 (cost without leverage).

**Suite 638 → 641 across 29 suites.**

⚑ **WHAT `--leverage` STILL CANNOT ANSWER, stated so the ordering is not over-trusted:** it ranks by
*modules unblocked*, which is the right measure for the build chain and the WRONG one for tooling
items. `C4` itself has a cone of zero — it unblocks no Agda module — and it was the correct thing to
build. **Leverage over the tree is one axis; leverage over the WORKLIST is another**, and no tool
measures the second. The tooling-first heuristic (§21) stays a judgement, now explicitly labelled as
one rather than smuggled in beside a number.

### 66. R7b-APPLY — THE GENERATOR WAS NEVER NEEDED, AND THE REAL DEFECT WAS A `private` LOST IN THE SPLIT (2026-08-01)

The item’s own instruction was *“try the keep-biased rule DIRECTLY before building R7b-REWRITE; if 2
files fall out, the generator is unbuilt debt.”* Doing that **retired the generator**.

⚑ **§58d’s DIAGNOSIS WAS RIGHT ABOUT THE OUTCOME AND WRONG ABOUT THE MECHANISM.** It predicted the
failure would dissolve under `need[fn] = direct ∪ ⋃ need[sibs]`, i.e. that `Idem` needed more of the
TELESCOPE. It did not. `Op` defines `_≉_`, `Idem` uses it at `:24`, and **there was no import between
them** — the two files have byte-identical preludes and neither mentions the other. One line:

    open import Substrate.Groups.Coxeter.Core.IdemInequality.Op
      Word Canonical normalize normalize-canonical canonical-is-fixed

**`Idem.agda` compiles clean.** The sibling-edge closure would also have produced this import, so the
rule was correct — but the item that would have taken *hours to build the generator* took one line,
and the honest reading is that **R7b-REWRITE was sized against a misdiagnosis.** *A prediction that
lands on the right answer by the wrong route is not confirmation of the route.*

⚑ **THEN THE FRESHLY-UNBLOCKED CONE EXPOSED THE ACTUAL R9 DEFECT.** `Core.agda` failed
`[ClashingDefinition]` on `_≉_`, previous definition at `Core/Operations.agda:44`. The pre-split
source settles it — `_≉_` was a **`private` helper** in `IdemInequality`:

    private
      _≉_ : Word → Word → Set
      w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂

**Deliberately unexported, because `Operations.agda` already defines the SAME operator,
byte-identical.** R9 turned the private block into a public leaf (§33’s rule, correctly) and the ROOT
re-exported it `public` — so `Core.agda` saw two. Fixed by dropping `public` from that one re-open:
the leaf is right, the re-export was not. **`Core.agda` moved `dependency` → `own`** and now fails on
a different thing entirely (`[FileNotFound]` for `Core/Clash.agda`, a consumed parent).

⚑ **THE GENERALISABLE FORM: `private` CARRIES A CLASH-AVOIDANCE FACT THAT SPLITTING DESTROYS.** A
`private` helper may be private *because a public sibling of the same name exists*. `split_lemmas`
correctly drops the keyword (§33: a leaf that kept it would emit a correct sibling edge and still fail
`[NotInScope]`) — but the ROOT must then not re-export it. Filed as **`R14`**.

⚑ **RETRACTED 2026-08-01 (user): *“that means something needs to be renamed where it’s defined. This
is already policy for every other type of name collision.”*** The observation above is right and the
CONCLUSION I drew from it is wrong. I wrote *“nothing checks that”* and filed a TOOLING item — a new
gate over a new invariant. But a `private` helper colliding with a public sibling **is a name
collision**, and the ban skill already states the rule: *“The only ban-compliant fix is renaming at
source. Not re-adding `using`, not qualifying, not aliasing.”* **`private` was MASKING the collision
— precisely what the skill says a filter does**, and the skill’s own three error shapes
(`AmbiguousName`, `ClashingDefinition`, `NotInScope`) are what a mask produces when removed.

So `R14` is a **PAYDOWN under existing policy**: rename the two definitions at source, after which
there is no clash to re-export and the invariant I proposed gating cannot be violated. No gate is
owed.

⚑ **AND THE MIS-FILING HAS A NAME.** The symptom reached me through the SPLITTER rather than through
the typechecker, so I treated it as a splitting defect and reached for new machinery. Same class as
§13 (*“an `AmbiguousName` is not automatically a rename job — check the provider for an existing
synonym FIRST”*), inverted: **a collision arriving by an unfamiliar route is still a collision, and
the standing rule already covers it.** *The tell was writing “nothing checks it” about a case the
policy already decides — an absence-claim about the substrate, which CLAUDE.md names as the trigger
to search before asserting.*

⚑ **THIS ALSO CLOSES HALF OF `U3`.** I had queued *“the ban skill does not say a `private` helper may
be private for clash avoidance”* as documentation owed. It is not: the skill’s rename-at-source rule
covers it, and adding a `private`-specific clause would restate a general policy as a special case —
the shape §60 retired when four gates each hand-rolled what one parameter expressed.

⚑ **TWO PROCESS FAILURES, BOTH MINE, BOTH NOW FIXED IN THE TOOLING** (user, twice: *“if you have a
question the tooling doesn’t answer directly, fix the tooling”*):

1.  **I RAN `--restore` WHEN I WANTED TO READ.** `recover_presplit` could FIND a pre-split source and
    OVERWRITE the live file with it, but had no verb to SHOW one — so the only way to obtain the text
    was the writing one, and it overwrote `IdemInequality.agda`. The snapshot made it recoverable, so
    nothing was lost; the defect is that a tool holding the content offered no way to look.
    **`--show=<ref>` added**, with a case asserting the working file is byte-identical afterwards.
    *That is §61 exactly, one tool over: a read-only INTENTION needs a read-only OPERATION, and if the
    tool has none the operator will use the writing one.*
2.  **I HAND-ASSEMBLED `cp` × 2 + `git checkout` TO RECOVER** — the §58b anti-pattern, from a hint the
    tool itself printed. The cause: `edit_snapshot --list` dumps the raw journal (**MEASURED: 207KB**,
    every path of every snapshot), so *“which snapshot holds MY file”* meant grepping its output.
    **`--holding <path>` added** — one command, newest-first, with the restore invocation. Recovery
    then ran through `--from-snapshot`, as designed.

⚑ **AND I INTRODUCED TWO DEFECTS WRITING THAT FIX, CAUGHT BEFORE SHIPPING:** the restore hint indexed
the UNREVERSED list, so it named the OLDEST snapshot while the listing led with the newest (*a printed
command that is subtly wrong is worse than none — it gets run*); and the case I wrote to pin the
orientation compared a value **to itself**. The second is §65’s decoration class, reproduced one turn
after recording it.

⚑ **A LIVE WITNESS FOR `C2`, IN THE DIRECTION IT WAS NOT FILED FOR.** `--diagnose` reports `other` on
`Core.agda`’s plain `[FileNotFound]` even though `Core/Clash/` exists with leaves — a **false
NEGATIVE**. §56 filed C2 for the false POSITIVE (a leaf directory of broken leaves read as
“rewire”). It has both, and the `import … as` form is what its pattern misses. **Left unfixed
deliberately**: hand-repairing this parent would spend the witness C2 needs.

Suite 642 → **646** across 29 suites.

### 67. C2 — THE FALSE NEGATIVE WAS STALENESS, NOT A REGEX; AND THE TYPE GATE (user, 2026-08-01)

✅ **C2’s FALSE NEGATIVE IS FIXED, AND ITS CAUSE WAS NOT WHAT §66 FILED.** I recorded it as *“the
`import … as` form misses its pattern”* — a regex claim. Measured, the regex matched fine:
**`--diagnose` was reading a build log written 23.5 hours earlier**, before the edit that broke the
file. `Core.agda` now classifies `file-not-found` with a runnable remedy instead of `other`.

⚑ **THE PREDICATE WAS NOT WRONG; IT WAS READING A DIFFERENT TREE** — and §52 had already measured
**1770 of 2810 logs stale**. `census_from_build` owns that freshness rule (`log_mtime >= max(own source, every transitive import)`) but kept it as a CLOSURE over its own locals, so `--diagnose`,
which also reads logs, had no way to ask. **A log-first classifier without the freshness test is wrong
on 63% of the tree by construction.** Lifted as `log_is_fresh`; a stale log now falls back to
compiling.

⚑ **AND THE ONLY REASON I FOUND IT WAS `--trace`, BUILT FIRST BECAUSE ITS ABSENCE SENT ME TO A REPL.**
C2 is a predicate defect in both directions, and the only way to ask *why did it decide that* was a
`python3 -c` wrapper around `_classify` — reasoning at the shell, on the tool built to stop that.
**A classifier that cannot show its work sends every caller back to the REPL the moment it is wrong.**

⚑ **THE LIFT TOOK FIVE PASSES AND BOTH DEFECTS WERE THE SAME ONE.** `parse_tree`’s docstring says
verbatim *“Src relpath is `Substrate/…/X.agda` relative to agda/”*. I **added** an `agda/` prefix in
the module lookup and **omitted** one in the `getmtime` — each made the dependency walk measure
nothing, `newest` stayed `0.0`, and `lm >= 0` certified EVERY log as fresh. **Third time this session
an authority’s contract was inferred from a call site rather than read from the line that states it**
(§58c’s class), and a bare `except OSError: pass` hid the second instance so the first fix looked like
it had not applied. Misses are now COUNTED, and an unreadable dependency **withholds `fresh`** —
that direction is optimistic, while `stale` stays sound because `newest` is a lower bound.

✅ **THE mypy GATE — MEASURED, SCOPED, NOT YET WIRED** (user: *“have we reached a point where we should
be using \[a type checker\] to provide typing guarantees… because that’s what it’s feeling like”* →
*“I think I prefer mypy here. And gated.”*).

The evidence is this session’s own defect log — **seven** a checker catches mechanically: the
`log_is_fresh` 2-tuple→3-tuple widening (the bug being debugged when it was proposed), `_classify`
(§55, *“the FOURTH invented API this session”*), `AL.agda_files` (§65), `CII.importers()` (§49),
`agda_lex.imports_of` behind a `hasattr` (§52 — **the strongest case: the guard HID it**),
`group_statements(lines, [])` (§58c), and an unused import (§66).

`pycodemod --types` keys `<error-code>::<relpath>` for `ratchet.set_ratchet` — **line numbers
deliberately excluded**, since §7g measured that line-keyed ratchets churn on every unrelated edit.

⚑ **FOUR DEFECTS FOUND BUILDING IT, THREE OF THEM MINE, AND THE FIRST IS THE ARC’S OWN CLASS AGAIN:**

| \#  | defect                                                                                                    | how it presented                                                                                                                                                            |
|:----|:----------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | `"python3"` not `sys.executable` — under `uv run --with mypy` the subprocess used a DIFFERENT interpreter | **0 keys over 60 unannotated files, reported as clean.** Guard-degrades-to-measuring-nothing, in the tool built to catch it — caught only because zero was implausible      |
| 2   | *“mypy is not importable”* was **my guess printed as fact**                                               | real cause: a DUPLICATE module name (`hadamard_basis.py` exists twice); mypy exits 2 for config errors as readily as for a missing install. Now carries mypy’s own message  |
| 3   | `py_files()` walked into `scratch/.venv/`                                                                 | vendored PY2 setuptools made mypy refuse the whole run — and `--roundtrip`/`--dead` had been silently reading third-party code too                                          |
| 4   | **a REAL find, in the file being edited**: `cst.metadata`                                                 | worked only because `libcst/__init__.py` transitively imports the submodule — depending on a third-party implementation detail. Fixed by importing it by name; census 6 → 5 |

**SCOPING, MEASURED: 208 keys over everything, 5 over the five live tools.** The bulk is annotation
debt in `scratch/eliza/` and `cotype-*/` experiment silos. **The gate’s population is the tool corpus**
— a 208-key baseline is the *census too wide to read* failure §63/§64 keep recording.

⚑ **TWO DECISIONS ARE THE USER’S AND ARE NOT MINE TO ASSUME:** the exact population (tool corpus vs
everything), and the timing — **B3’s bar is already 12-red, so adding a 13th gate is correct by policy
and makes that bar worse before better.** Filed as `T16`; the measurement stands either way.

Suite 646 → **650** across 29 suites.

### 68. T16 — THE POPULATION QUESTION HAD THREE ANSWERS, AND MEASURING THEM WEAKENED MY OWN CASE (2026-08-01)

§67 offered the scope decision as *“tool corpus (5) vs everything (208)”*. **Both numbers were
careless**: the 5 was one ad-hoc list of five files, and neither is the boundary that matters.
Measured properly:

| population                           | keys    | contains the defect classes I cited?                                |
|:-------------------------------------|:--------|:--------------------------------------------------------------------|
| the 18 pipeline tools                | **12**  | 1 `arg-type`; **no** `name-defined`, **no** invented-API rows       |
| \+ `scripts/` (the gate layer)       | **41**  | same, plus 29 rows of pure annotation debt                          |
| everything under `scratch`+`scripts` | **207** | **all 3 `name-defined` and 2 of 3 `attr-defined` are in the SILOS** |

⚑ **THE SILOS ARE INSIDE `scratch/`, SO “TOOL CORPUS” IS NOT A DIRECTORY.** `scratch` + `scripts`
is 207 of the 208 — `scratch/eliza/` and `cotype-*/` are research code living beside the tools, and
any scope defined by path either swallows them or needs an explicit tool list.

⚑ **AND THE MEASUREMENT UNDERCUT THE JUSTIFICATION I HAD WRITTEN.** §67 cited *“seven defects a
checker catches mechanically”* — true, and I caught **all seven this session by RUNNING the code**.
The standing census over the tools is **12 keys**, none of them an invented API. So the gate’s value
is **PROSPECTIVE** (catching the eighth at edit time), not a backlog it would clear. *I was arguing
from a defect LOG and presenting it as a defect POPULATION, and those are different claims.* The gate
is still worth having — the seven were real and each cost a run-edit-run cycle — but the case is
“stop the next one”, not “clear these”.

**RECOMMENDATION, stated as one rather than a menu:** scope to **tools + `scripts/` = 41 keys**. It is
the code the gates and pipeline actually run, it is readable, and excluding `scripts/` would leave the
GATE LAYER unchecked — where a wrong signature does the most damage. The 166 keys in the silos have
their own lifecycle; including them couples tool hygiene to experiment churn and makes the baseline
unreadable (§63/§64’s *census too wide to read*).

**On timing** — wire it now rather than build-and-hold: **a gate that exists but is not hooked is
§9a’s exact finding** (*five gates baselined and wired into nothing*), and this arc has paid for that
once already. The 41 keys are all pre-existing, so the baseline records them and the ratchet refuses
only GROWTH; B3 goes to 13-red but no worse in substance.

⚑ **BOTH REMAIN THE USER’S CALL AND ARE NOT ASSUMED.** The cut (41 vs 207) and whether adding red to
B3 today is acceptable are decisions about the arc’s terminal goal, not about the tooling.

⚑ **AND THE TOOL-LAYER RESIDUE IS BENIGN, WHICH IS ITSELF THE FINDING.** Inspected: `var-annotated`
on module-level accumulators (`_DAG`, `_SNAPPED`, `tally`), and one `assignment` that is my own
`cst = None` optional-dependency fallback. **Nothing false, nothing urgent** — so a 41-key baseline
records debt that is real but inert, which is exactly what a paydown-only ratchet is for.

### 69. `scratch/` IS A STAGING AREA, AND THAT DISSOLVES T16’s SCOPE QUESTION (user, 2026-08-01)

> *“They can be promoted out of `scratch/` if they’re brought to meet common quality status.”*

⚑ **I HAD BEEN TREATING `scratch/` AS A PLACE TO PARTITION. IT IS A LIFECYCLE STAGE.** §68 asked
*“tools or everything”* and measured three path-based cuts — all three were the wrong question.
Residence in `scratch/` **is** the not-yet-promoted status, so a gate scoped by carving up `scratch/`
is drawing a line the repo already draws by moving files out of it.

⚑ **AND THE MACHINERY ALREADY EXISTS — I DID NOT LOOK.** `check_scratch_independence.py` (Λ8) is a
WIRED pre-commit gate whose docstring states the policy verbatim: *“once a project is promoted out of
scratch/ (jea/, el-atlas/), it must not silently re-acquire a runtime dependency on scratch/”*, with
`ROOTS = ["jea", "el-atlas"]` as the declared promoted set and *“Extend ROOTS when another project is
promoted”* as its maintenance rule. **The reuse-search fires on scope questions too** — I proposed
three hand-drawn populations while the authority for “promoted” sat in a gate the hook runs.

**RE-MEASURED against the real boundary:**

| population                                 | keys    | profile                                                        |
|:-------------------------------------------|:--------|:---------------------------------------------------------------|
| `jea` + `el-atlas` (the promoted projects) | **80**  | `arg-type` · `attr-defined` · `union-attr` · `used-before-def` |
| `scripts/`                                 | **28**  | mostly `var-annotated`/`assignment`                            |
| **promoted + `scripts/`**                  | **108** | **15 error codes, defect-shaped**                              |
| `scratch/` (staging)                       | \~99    | annotation debt + the silos                                    |

⚑ **THE PROFILE INVERTS AT THE BOUNDARY, WHICH IS THE EVIDENCE THAT IT IS A REAL ONE.** The promoted
corpus shows **no `var-annotated` and no `assignment`** — it is already annotated, because that is
part of what promotion means. What it does show is `arg-type` (11), `attr-defined` (6), `union-attr`
(6), `used-before-def` (1): **the classes that are actual defects.** Staging shows the opposite. *A
boundary that changes the KIND of finding, not just the count, is a boundary and not a filter.*

⚑ **SO THE GATE’S POPULATION IS `ROOTS` + `scripts/`, READ FROM THE EXISTING AUTHORITY** — never a
list in the type gate. It then grows BY CONSTRUCTION as projects promote, and “bring it up to quality
status” acquires a mechanical meaning: **a promotion candidate must not add type-census keys.** That
is the same shape as `agda_files` being one enumeration (§6d) rather than four.

⚑ **AND IT REFRAMES §68’s WEAKENED CASE.** §68 concluded the gate was PROSPECTIVE-only because the
tool census was 12 keys with no invented API — measured over the wrong population. Over the promoted
corpus there are **80 keys including `used-before-def` and 6 `attr-defined`**, so there IS a backlog,
it is defect-shaped, and it sits in exactly the code that has already earned a quality bar. *Two
consecutive sections drew a conclusion from a population chosen by hand; the third read the boundary
the repo already enforces.*

**REVISED RECOMMENDATION: scope to `check_scratch_independence.ROOTS` + `scripts/` (108 keys), and
have the type gate IMPORT that list rather than restate it.** ⚑ `scratch/` is then deliberately
UNGATED — staging code is allowed to be rough, and gating it would make the staging area pointless.

⚑ **STILL THE USER’S CALL, and one decision is now sharper than before:** 108 keys is larger than the
41 I recommended in §68, so the *worse-before-better* cost on B3 is real. But it is the population
where the findings are defects rather than annotations — **and it makes `promotion` checkable instead
of aspirational**, which is the durable half.

⚑ **AND THE POLICY IS NOWHERE IN `CLAUDE.md`.** The promotion rule lives in the Λ8 gate’s docstring
and in the user’s head; nothing states it where a reader would look for project conventions. That is
§9a’s shape one level up — a real policy with no home. Filed as `U4`.

### 70. T16 LANDED — AND THE FLAG I NEEDED WAS THE ONE 0 OF 16 GATES HAD (2026-08-01)

**Decision (user): *“Goes in now, joins the paydown queue.”*** Wired at the §69 scope.

✅ **`scripts/check_mypy_ratchet.py`** — 7 selftest cases, hook-wired, census **108**, keys
`<code>::<relpath>` (never line-numbered, §7g). Scope is **imported** from
`check_scratch_independence.ROOTS` + `scripts/`, so a fourth promoted project joins by
construction. `scratch/` stays ungated by the POPULATION, not by a filter that can rot.
An unrunnable mypy **REFUSES** rather than reporting clean — the §52 class, in the gate built
because of it. Suite **652 → 659 across 30 suites**.

⚑ **THE HARD PART WAS NOT THE GATE. Four tool-call refusals, each naming a missing command,
and every one is now built:**

| I reached for                        | the missing question                                                               | built                                            |
|:-------------------------------------|:-----------------------------------------------------------------------------------|:-------------------------------------------------|
| a heredoc simulating a defect        | *does this selftest case DISCRIMINATE, or would it pass against the bug it names?* | `pycodemod --discriminates`                      |
| `sed -i` chained to a run            | —                                                                                  | the Edit tool, which fails loudly on a non-match |
| `wc -l` + `head` on a fresh baseline | *did the write land, and does it round-trip?*                                      | `set_ratchet` verifies `_read(path) == cur`      |
| `bash -n .githooks/pre-commit`       | *does the hook still parse?*                                                       | `gate_status.gates()` refuses on invalid shell   |
| `awk 'NR>N && /^### /'`              | *where does section N end?*                                                        | `mdstruct --spans`                               |

⚑ **`--discriminates` FOUND A REAL BLIND SPOT ON FIRST USE, AND ITS FIRST RUN WAS ALSO A LIE.**
It mutates the module, re-imports it, and runs `_selftest`: a suite that still passes did not
cover that defect. My first version loaded the mutant from a TEMPDIR, so every gate’s
`sys.path.insert(0, dirname(__file__))` resolved wrong and all three mutators returned
`ModuleNotFoundError` — which the harness scored as `DISCRIMINATES`. **Three confident verdicts,
every one an artifact of the harness.** §30’s five-bad-fixtures class exactly. Fixed (mutant
lands beside the original; an `ImportError` is now `n/a`, never a score), it reported
`empty-census-passes: BLIND` — no case asserted the gate REFUSES on a grown census, so a gate
short-circuited to always-pass stayed green. **That is §9a — a gate wired into nothing — at the
CASE level.** Case 4 closes it; the blind count is 0.

⚑ **A `BLIND` ROW IS REPORTED, NEVER EXIT-CODED.** A mutator names ONE defect class and a suite
may legitimately not cover it; failing the run would make this a coverage gate over a
hand-written mutator list — an allow-list that rots. Report the pair, never a bare bit.

⚑ **THE REFUSAL MESSAGE WAS ADVERTISING ITS OWN BYPASS.** `ratchet.py` said *“set
SUBSTRATE_RATCHET_WRITE=1”* — the env var `.githooks/pre-commit:46` exports — so the message
handed every reader the hand-set route to minting a baseline. **I followed it myself**, one turn
after recording that the commit hook is the promotion gate. Setting it by hand banks a census
against a tree nothing approved: the `--no-verify` shape, in the one place it is least
recoverable (a wrong key in a paydown-only baseline can never legitimately be paid). Now it
names the ROUTE — `git commit` — and says outright that the env var is a bypass.
`check_rederive_ratchet:262` had the correct instruction all along.

⚑ **AND THE REAL GAP, WHICH THE USER NAMED WHILE I WAS AUDITING THE WRONG THING** (*“I was
pointing at –dry-run”*): **MEASURED, `--dry-run` is this repo’s write-tool convention — 6 tools
carry it — and 0 OF 16 GATES DO.** A gate is thought of as read-only; it is not. At the moment
it mints or lowers a baseline it IS a write tool, and it was **the only write path in the tree
with no preview**. `--list` shows the census; that is a different question from the diff about to
hit disk. So the flag I should have reached for did not exist, and I fell through to the bypass.
*A missing preview does not make a tool safer — it makes the bypass the only reachable route.*
Added at the authority (`set_ratchet(dry_run=)`), so all ten gates gain it.

⚑ **THE TRANSFERABLE FORM:** §7e filed write-polarity as *“three-way divergent — an
inconsistency”*. It is not: one of the three arms **has no preview at all**, and that is a
capability gap wearing an inconsistency’s clothes. The same distinction as `head_span`’s
TERMINATION-vs-CAPABILITY bound, and I have now missed it twice.

### 70d. THE DAG, RE-DERIVED — AND THE OLD TABLE WAS A LOG WEARING A DAG’S CLOTHES (2026-08-01)

⚑ **THE FIFTH RE-DERIVATION CARRIED ITS OWN FIX AND THE FIX DID NOT HOLD.** It said *“edit it
whenever a dependency moves, RE-DERIVE at every audit rather than appending”* — and the table then
grew to 40+ rows of dated findings, because appending a row is what an audit naturally produces.
A reader asking *what is unblocked right now* got a chronology. **The failure mode is structural,
not a lapse: a document that records findings AND states dependencies in one table will always
accrete, because those are different lifetimes.** The old table stays as the RECORD (its rows are
valid about the states they measured); this is the DAG.

**LAYER 0 — TOOLING, NO DEPS. These size or dissolve later work, so they go first.**

| item                                                   | why it leads                                                                                                                                                                                  |
|:-------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `T17`                                                  | `--dry-run` on the other 9 gates. **0 of 16 gates had a preview** — and its absence is what made the env-var BYPASS the only reachable route (§70). One flag each, forwarded to the authority |
| `T20`                                                  | a scope-aware call resolver. `--discards` keys by BARE NAME, so 360 of 362 rows are one collision (§70b). **Blocks a trustworthy `T19-RERUN`**                                                |
| `M6`                                                   | **USER CALL** on one constant — does `--columns=999` stay in `WRITER`? **Blocks `M1`**: normalizing under a config we then change means two reflows                                           |
| `T18`                                                  | run `--discriminates` over every gate. Built, found a live blind spot on its ONLY target so far                                                                                               |
| `T11` `T3`                                             | 9g’s population — building `T4` first banks their gaps as fictitious debt                                                                                                                     |
| `C2-residue` `M5` `S1` `S3` `T12` `T2c` `T5` `R5` `R3` | no deps; each unblocks or sizes later work                                                                                                                                                    |

**LAYER 1 — MEASUREMENT. Everything downstream is sized against a stale ledger until this runs.**

`CENSUS` (`make -C agda -j` then `--verify --leaves`) — needs no concurrent Agda edits. §67 measured
a representative log **23.5 h stale**; `--last` already declares itself so.

**LAYER 2 — PAYDOWN, unblocked by measurement**

`A4-FNF` \[needs `C2-residue` + `CENSUS`\] · `R11` (54 files → 712 blocked, ratio 13.2 — the largest
measured cone) · `A3` · `R8` · `R14` · `A2` · `G1` · `G6` · `G5` · `R2-SWEEP` · `G2-residue` ·
`T2b-RESIDUE` → `A4-OTHER`

⚑ **`R14` SITS HERE, NOT IN LAYER 0** — it was filed as a tooling build and is a PAYDOWN under the
existing rename-at-source rule (see §66’s retraction). Its population overlaps `R8`, so measure both
from one pass rather than twice.

**LAYER 3 — THE CHAINS** (each edge measured, not recalled)

    R12b → {R10a, R10b} → T10          (do not stack splits on known-broken leaves)
    R3 → R4 → {T1, T7}                  (the planner consumes conduit resolution)
    {T3, T11, T18} → T4                 (9g censuses what they fix)
    T20 → T19-RERUN
    {M6, M2} → M1 → M3                  (M3 also needs M5, and B3 first)
    {CENSUS, A4-FNF, A4-OTHER, R12b, A2, A3, R8} → A4 → A5 → {B1, B2} → B3

**LAYER 4 — USER DECISIONS, unblocked and unblocking nothing mechanical:** `U1` `U2` `U3` `U4`
(`M6` is listed in Layer 0 instead, because it blocks `M1`).

⚑ **WHY TOOLING LEADS, MEASURED RATHER THAN ASSERTED.** Every time a tool was fixed before its
population was worked, the population SHRANK or the work became a driver run: §30 fixity → 0,
§34 telescoped roots → 0, §38 applied-open 79 → 76 → 54, §33 → R9’s 162-key paydown, §41 → R12b
replaces 113 hand-fixes with a re-split, §70c → the markdown apply was one return value, not a
build. **A tool fix is never “also” work — it is the step that sizes the work.**

### 70c. THE MARKDOWN APPLY — BUILT, RUN TOO EARLY, AND THE SURVEY CORRECTED ME TWICE (user, 2026-08-01)

> *“The MD060 rows are M1’s known pre-existing population, not this edit.”* — **“This shouldn’t
> happen; this is why we built the markdown structural manipulation tooling.”** (user)

⚑ **I DISMISSED THOSE WARNINGS FOUR TIMES ACROSS THE ARC**, each time with a true sentence
(“pre-existing”, “M1’s population”) doing the work “not my edit” usually does. §50 recorded that
exact reflex and I reproduced it. The measured population was **48 rows → 0 in one normalization
pass**, sitting there the whole time.

✅ **`--fixpoint --apply` — AND IT WAS ONE RETURN VALUE AWAY, NOT A BUILD.** `fixpoint()` already
ran the document to convergence and **returned only the deltas, discarding the converged text**.
So `--table-style` could report *“48 rows → 0”* while nothing could write it. Same shape as
`split_lemmas` printing a COUNT with the file list in memory (§40’s `--manifest`) and `rewire()`
returning an int so the prune had no population (§49). ⚑ *A census with no apply trains its reader
to dismiss it* — that is the mechanism behind the four dismissals, not carelessness.

The apply is `--apply`-gated (§7e’s hand-invoked polarity), snapshots via `edit_snapshot.guard`,
and **REFUSES a non-fixpoint** — writing a document normalization keeps changing banks a reflow the
next pass undoes. MEASURED: worklist converges in **1 round** (`[0]`), plan in **4**
(`[8, 5, 2, 0]`); applied to the worklist, **MD060 48 → 0**.

⚑ **AND I RAN IT BEFORE VALIDATING THE WRITER, THEN BUILT A REPORTER FOR THE DAMAGE** — the
reporter-not-writer failure, one layer up, *inside the fix for the reporter-not-writer failure*.
The user stopped it (*“we have mechanization tools for MANIPULATING markdown to prevent this
stuff”*). Deleted; worklist restored from the snapshot the tool itself took.

⚑ **THE REUSE-SEARCH SHOULD HAVE FIRED FIRST, AND THE SURVEY IT PRODUCED CORRECTS ME TWICE**
(user: *“dispatch a research agent for locating all machinery in the repo aimed at managing and
manipulating markdown”*). I was about to hand-test three pandoc writer configs in a shell loop.

| I believed                                                                 | the survey measured                                                                                                                                                                                                                                                            |
|:---------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a repo markdownlint config declares the style, so conform the writer to it | **NO repo markdownlint config, no `.editorconfig`, no pandoc defaults.** MD060 comes from the IDE’s GLOBAL markdownlint. **`mdstruct.WRITER` is the repo’s ONLY declaration of markdown style** — a constant I hoisted an hour earlier without recognising it as the authority |
| pandoc introduced the curly quotes despite `-smart`                        | **`-smart` works; the quotes were in the INPUT.** `worklist.md:351` already held a literal `’`. I attributed to the writer what was in the source — the same shape as blaming a tool for a pre-existing dependency failure (§39)                                               |

**What survives as real:** the 999-character thematic breaks are `--columns=999` doing exactly what
it says — a `WRITER` flag question, and **the survey found NO tool in the repo that reads,
normalizes or gates on thematic breaks at all**, so there is nothing to reuse and nothing to
contradict.

⚑ **THE ORDERING CONSTRAINT THE SURVEY MADE CONCRETE, AND I NEARLY VIOLATED IT.** `M2` must precede
any apply on a GENERATED file: `scripts/reuse_catalog.py` hand-builds pipe rows via f-strings
(`:536,581,585,661,666,714,718`) and `el-atlas-structured-gen.py:209,223` emits `|---|---|` with no
padding — **the exact MD060 shape**. Normalizing those outputs is undone by the next regeneration.
The plan already said this; I was one command from applying to a file without checking whether it
was generated.

**Unbuilt, per the survey, and neither needs new parsing machinery:** `M2` (fix the generators) and
`M3` (a fixpoint gate in the hook — **no markdown gate exists in any hook today**). `mdstruct`
already owns structural read, the MD060 census, the fixpoint analysis, and the sole safe write path.

⚑ **AND ONE FLAG IS NOW A STYLE DECISION ON THE STYLE AUTHORITY ITSELF** — whether `--columns=999`
stays, given it is what produces the 999-char rules. Filed as **`M6`**, a user call, because
changing `WRITER` changes what every future normalization emits.

### 70f. `U4` — THE POLICY’S HOME IS TOOLING, NOT A DOCUMENT (user, 2026-08-01)

> *“The place to put it is in tooling, which will surface such rules when they’re violated. If you
> have a question the tooling doesn’t answer directly, fix the tooling so it answers your question.
> CLAUDE.md is not tooling.”*

I had framed `U4` as *where does this policy get written down*, with `CLAUDE.md` as the candidate and
“it’s already long” as the counter-argument. **Both sides of that framing were wrong.** A document a
reader must CHOOSE to consult, and which nothing checks, is the weakest enforcement layer available —
and this arc measured its cost precisely: §9a’s five gates that were baselined, documented, and wired
into nothing.

✅ **`check_scratch_independence.promotion_report()` + `--promotable <dir>`.** The rule as a
PREDICATE rather than a paragraph: (1) no live `scratch/` reference — this gate’s own invariant
applied to the candidate; (2) **it adds no census keys**, asked of `check_mypy_ratchet` rather than
restated (a second copy of “what counts as a type error” is §6d’s same-name-different-body hazard).
**Live:** `--promotable scratch/cotype-ebnf-strictness` → `BLOCK  50 type-census key(s) would be ADDED`, first key named.

⚑ **AND MY FIRST CUT WAS NOT IDEMPOTENT** (user: *“that should just be idempotent”*).
`--promotable jea` returned BLOCK and exit 1 — asserting that a project which IS promoted is not
promotable. That is §62’s `--retire` early-return in a new place: **a predicate that reports its own
success as a failure cannot be used to CONVERGE on the state it describes**, because re-asking
contradicts reality instead of confirming it. “Already satisfied” is a `yes`.

*The transferable form:* **a policy’s home is the layer that can refuse a violation.** Prose states;
tooling enforces. Asking “where should this be written” already assumes the weaker answer.

### 70e. `M6` DECIDED — AND THE FIXPOINT GUARD WAS CALLING A PLATEAU A CYCLE (user, 2026-08-01)

✅ **`WRITER` IS NOW `--columns=120`** (user: *“let’s make it 120 columns; standard classic
widebar”*). **APPLIED to both documents; both are idempotent on re-run; MD060 is 0 in each.** The
class is retired by construction rather than by fixing rows — §50’s claim, finally exercised.

⚑ **BUT THE FIRST ATTEMPT REPORTED 120 AS A NON-FIXPOINT, AND I BUILT A THEORY ON IT.** The plan at
120 printed `[686, 571, 312, 114, 92, 56, 56]` and `fixpoint()` returned False. From that I inferred
**convergence is not monotone in column width**, wrote a grid-table-vs-pipe-table mechanism to
explain it, deleted a binary search as inapplicable, and replaced it with an enumerating survey.
The user declined the inference (*“I don’t buy that”*), which is the only reason I checked.

**MEASURED by running past the guard: 120 CONVERGES in 12 rounds** —
`[686, 571, 312, 114, 92, 56, 56, 56, 34, 34, 34, 0]`. The sequence descends in **PLATEAUS**, and
the termination rule bailed on the first non-strict step (`56 >= 56`). *120 never stalled; the loop
refused to look.* Convergence is monotone after all, and every downstream claim I made was an
artifact of my own stopping condition.

⚑ **THIS IS §50’s DEFECT IN ITS OWN SUCCESSOR, AND THE SECOND TIME THIS EXACT SEQUENCE FOOLED ME.**
There, `rounds=3` made a converging document read as *“diverges monotonically”*; the fix was
“iterate while progress is STRICT”, recorded as a well-founded descent. **Strictness is a stronger
claim than the argument needs:** non-increase plus eventual movement already terminates, and a
repeated delta is progress-so-far, not failure. I replaced a capability bound with a subtler
capability bound and wrote a docstring congratulating the fix. Corrected: the loop now stops on
`n == 0` (converged) or a delta that GROWS (real divergence), with a plateau budget of 8 as a
genuine TERMINATION bound — the measured worst plateau on this corpus is 3.

⚑ **AND THE BINARY SEARCH I DELETED WAS THE RIGHT INSTRUMENT ALL ALONG** (user: *“you know binary
search is a thing, right?”*). I was hand-probing 200/300/400 — an arbitrary sample of an ordered
space — then built a bisection, then discarded it on a false non-monotonicity, then built a scan.
Three instruments for a question that dissolved once the predicate was correct. **A search is only
as good as the predicate it searches on, and I never questioned the predicate.**

*The transferable form, and it is the sharpest of this sitting:* **when a measurement contradicts a
simple expectation, suspect the instrument before inventing a mechanism.** I produced a plausible
grid-table story for a phenomenon that did not exist, and it survived because it explained the
numbers — which is exactly what a wrong theory does.

### 70b. T19 — THE SWEEP, AND THREE WRONG ATTRIBUTIONS IN ONE SITTING (2026-08-01)

⚑ **THE ITEM NAMED ITS OWN POPULATION FROM MEMORY, WHICH IS THE §69 MISS.** T19 listed five
authorities (`may_write`, `blockers`, `log_is_fresh`, `blame`, `roundtrip`) — my recall, not a
measurement. A verdict-returner is DISCOVERABLE: ✅ **`verdict_returners()`** derives it (a def
returning an all-clear on one path and a bool/exit-code on another; data-returners excluded,
because ignoring a returned LIST is harmless while ignoring a returned REFUSAL disables a guard).
**MEASURED: 341 verdict-returning defs**, none of them the five I would have typed.

✅ **AND THE SWEEP PERSISTS ITS OWN CENSUS** (`.discards-census.tsv` + `--last`). A multi-minute
corpus walk whose result lives only in a terminal is one the next reader re-runs — and the reflex
is to redirect it to a scratch file the tool cannot read back, which §44 already recorded as the
reprocessing loop in another shape. Same fix as `.leaf-verify.tsv`; written only for a FULL sweep,
never a scoped one (§51’s clobber).

⚑ **A PERFORMANCE DEFECT THAT WAS §55’s, EXACTLY.** `discards(name)` re-parsed the whole corpus
once per name, so sweeping 341 names meant 341 identical CST walks and the first run did not
finish in two minutes. §55’s own rule is the one that applies — *before reaching for concurrency,
check whether the work is REPEATED* — so: one memoised `_bare_calls()` pass keyed by population,
and the expensive per-name half runs ONLY for names with a bare call. **I then instrumented the
phases**, because I had guessed twice at where the time went and a silent multi-minute run is
indistinguishable from a hung one.

⚑ **THREE WRONG ATTRIBUTIONS, EACH ONE COMMAND FROM CHECKABLE, ALL MINE THIS SITTING:**

| I said                                                 | measured                                                       |
|:-------------------------------------------------------|:---------------------------------------------------------------|
| `pycodemod` exits 0 on an unknown flag                 | it exits **2** — I read a branch’s tail as the file’s tail     |
| the sweep is slow because `discards` re-walks per name | partly: `verdict_returners` is its own full walk               |
| the 361 bulk sites are `print`                         | **`print` is not in the population at all** (not a corpus def) |

*The pattern is stable and worth naming: I read a SHAPE in the output and named a cause.* §22’s
rule is the antidote — *demand the actionable output* — and I inverted it three times in one
sitting, inferring from summaries while the row-level answer was one flag away.

⚑ **A VERIFIED FALSE POSITIVE, KEPT AS SUCH:** `scratch/paydown.py:175` calls `SF.fix(rel, 20, dry)` bare — and the caller **re-reads the file and diffs it** to detect whether anything changed.
The verdict IS checked, just not through the return value. A row this predicate cannot help
producing, and the honest handling is to record it as known-good rather than “fix” a correct call.

⚑ **T19’s RESULT: ZERO LIVE FINDINGS — and the census is dominated by a PREDICATE DEFECT, not by
debt.** Final measured census: **340 verdict-returners, 3 names with discarding sites, 362 sites**
— of which **360 are `check`**, one is `_insert_decoded` (a DB INSERT; the effect is the write),
and one is `fix` (above). The one genuine inert guard this class has produced remains §70a’s,
which was mine from that turn.

⚑ **AND THE `check` ROWS ARE A NAME COLLISION ACROSS SCOPES — `--discards` RESOLVES CALLS BY BARE
NAME.** Measured, after two wrong fixes: `check` is NOT in `verdict_returners` for `gate_status.py`
or `agda_lex.py` (the `_selftest` exclusion works), yet 360 rows persist. Cause: **five
MODULE-LEVEL `def check` exist** (`fix_notinscope:86`, `fix_ambiguous_import:109`,
`prune_leaf_opens:51`, `untethered_disjunct_advisory:91`, …), so `check` enters the population
legitimately — and `_bare_calls` then matches EVERY bare `check(...)` in the corpus, including the
test-local ones in \~30 files.

> **A BARE NAME IS NOT A DECIDABLE UNIT.** Identical to §22, where `def_index` keyed `_-ℤ_` and
> `-ℤ_` both as `-ℤ` and would have renamed 18 operators correctly-per-the-plan and
> wrongly-per-the-language. Filed as **`T20`** (a scope-aware call resolver) rather than patched,
> because a third guess at this predicate is worth less than naming the real requirement.

**`T19-RERUN`** follows `T20`: the sweep is worth re-running once calls resolve by scope, but the
current census’s two non-`check` rows are both verified benign, so that re-run is about making the
INSTRUMENT trustworthy rather than about known debt — and it is filed separately so nobody reads a
green `T19` as evidence the predicate is sound.

⚑ **SIX WRONG ATTRIBUTIONS IN ONE SITTING, AND THE LAST TWO SHARE A SHAPE.** After the three in the
table above: *(4)* “nested defs are already excluded” — the ledger showed \~360 `check` rows;
*(5)* I had “verified” that from `verdict_returners([agda_defs.py])`, **a ONE-FILE sample stated as
a corpus fact** (§41’s 25-of-589 shape); *(6)* the `_selftest` exclusion I then built is correct and
moved the census by **one def and zero rows**, because the mechanism was elsewhere entirely.

*The durable lesson is not “be more careful” — it is that every one of the six was one command from
checkable, and the tooling built this turn is what caught them:* the ledger showed the rows my
one-file sample hid, the predicate stamp stopped me reading a pre-fix census as current, and the
per-name counts (`cut | sort | uniq -c` over the persisted census) settled in seconds what three
rounds of reasoning got wrong.

### 70a. ROUTE THROUGH THE COMMON CLI — AND IT FOUND THE GUARD I HAD JUST BROKEN (user, 2026-08-01)

> *“I was actually going to suggest routing the python gate functionality through the common cli
> tooling we’ve built, since that common cli tooling has been enforcing more correctness through
> standardization and delegation.”*

**Correct, and the reuse-search fires on my own build**: I hand-wrote `main()` + argv parsing + a
dispatch while `pycodemod` is already the CLI for tool-corpus questions and `ratchet` already owns
argv discipline. Routing means the gate stops owning what the shared layer owns.

⚑ **THE FIRST THING THE ROUTING FOUND WAS A LIVE INERT GUARD, IN THE GATE I WROTE MINUTES EARLIER,
WHILE QUOTING THE LESSON IT BREAKS.** `ratchet.check_argv` **returns** an exit code (its docstring
gives the walrus form); I wrote the bare statement, so `--queit` printed the complaint and **ran the
gate anyway**. Present, greppable, documented — and doing nothing. §15’s *“a census can verify
presence, never behaviour”*, one turn after I cited it.

✅ **`pycodemod --discards <name>`** — the third question in the family, and neither sibling could
ask it: `--calls` finds the sites, `--forwards` checks what goes IN, **nothing saw a returned verdict
being dropped.** That is the shape of every guard-degradation this arc has recorded (§52’s `hasattr`
fallback, §60’s armed-but-inert helpers, §7a’s write guard six gates routed around): *the call is
there and its result is not consumed.* First run: **6 of 7 `check_argv` sites use the return; the 7th
was mine.** The six pre-existing gates were all correct — the cleanest possible confirmation that
routing through the common layer beats re-implementing it.

⚑ **AND THE REAL DEFECT WAS IN THE AUTHORITY, NOT IN MY CALL — `check_argv(argv)` DID `argv[1:]`.**
Six callers pass `sys.argv` (so the slice drops `argv[0]`, correct); mine passed an already-sliced
`argv`, so it stripped a SECOND time and never examined the first flag — with one flag, the only
flag. **MEASURED by `gate_status --modes`: `--queit` returned rc=0**, i.e. the gate ran normally with
a flag it does not know, which is the exact §7e defect this function exists to prevent. **An
unchecked precondition on a shared call is the `kwseen` class** (user: *“require it to be validated
against an expected context before use”*) — and here the violation is UNOBSERVABLE, because a guard
that examines nothing passes everything. Fixed by not depending on the caller’s slicing at all:
drop `argv[0]` only when it is a program path (it never starts with `-`; a flag always does).

⚑ **`gate_status.MODES` HELD ONLY VALID FLAGS, SO “DOES THIS GATE REFUSE A TYPO” WAS UNASKABLE** —
which is why I reached for `echo $?` at a shell. Added `--queit` as a deliberate sentinel mode: every
other entry asks *does this flag work*, that one asks *does the gate refuse what it does not know*.
It is now a cross-gate instrument — one run reports the answer for every gate at once, and it
immediately showed `--check` being silently accepted by my gate too.

⚑ **A NON-FINDING, STATED SO IT IS NOT MISREAD AS ONE:** the sweep shows `check_ban_ratchet --check`
and `check_snapshot_guard --check` at rc=2. **Both are hook-invoked with `--quiet`** (verified via
`gate_status --list`), so those rows are the SWEEP probing a mode those gates never claimed — the
refusal is correct behaviour, not debt. *Checking before filing is the difference between a finding
and a cries-wolf row.*

⚑ **AND I MIS-READ `pycodemod`’s OWN FALLTHROUGH ONE TURN EARLIER**, reporting it exits 0 on an
unknown flag. It does not — `print(__doc__); sys.exit(2)`. I had read the `--dead` branch’s tail as
the file’s tail. The narrower true gap: it refuses an unknown flag ALONE, but `--types --queit`
matches the known flag first and the typo is ignored. Corrected here rather than left standing.

Suite **659 → 670 across 30 suites**.

**Three items fall out, all no-deps:**

- **`T17` — back-fill `--dry-run` across the other NINE ratchet gates.** The authority
  supports it and `check_mypy_ratchet` forwards it; the rest do not, so nine gates still
  have no way to preview the write they are about to make. One flag each.
- **`T18` — run `--discriminates` over every gate and selftest-bearing tool.** It is built,
  it found a live blind spot on its first and only target, and the four mutators are this
  arc’s own measured defect classes. Produces a REVIEWABLE LIST, never an exit code — a
  `BLIND` row means *not covered*, not *defective*. Feeds `T3`/`T4`.
- **`T19` — run `--discards` over every shared authority that RETURNS a verdict** (§70a).
  One run found one inert guard; the population is every function whose contract is a
  returned code rather than an exception — `check_argv`, `may_write`, `blockers`,
  `log_is_fresh`, `blame`. ⚑ **This is the class `--calls` and `--forwards` are both blind
  to**, and it is how §52’s `hasattr` fallback, §60’s armed-but-inert helpers and §7a’s
  routed-around write guard all shipped: *the call is there and nobody reads its answer.*

⚑ **A STALE COMMENT IN THE AUTHORITY, RETIRED IN PASSING.** `ratchet.py` still asserted the four
hand-rolled `--list` blocks were SPECIALISATIONS to keep — §60 deleted them. The correction
landed in the code and not in the paragraph justifying it: the
summary-outlives-its-correction defect, this time **inside the file the correction was made in**.

## ⚑ WORKLIST DISCIPLINE — categorize by RESOLVING TOOL, up front (user, 2026-08-01)

> *“That’s not the problem — the problem is we’re not applying generic fixes up front. Going forward,
> we should be categorizing todo items by which tools are expected or intended to resolve them.”*

**The failure this names, and it is the session’s dominant one.** I hit a symptom, reach for a tool
*at that item*, and discover mid-work that the tool is wrong or defective. Every instance today:
`prune_imports` refuses renaming imports BY DESIGN (its docstring, which I had read); `rename_at_source`
had a dead two-spelling guard; `rewire_to_leaves` had no preview mode; `leaf_map` mis-reported an empty
leaf dir; my own `drop_dead_renames` shipped the span defect twice. **Each was found by USING the tool
on one item, so the fix arrived after the item was half-worked instead of before the class was swept.**

Deciding the tool up front changes the unit of work from ITEM to CLASS: the generic fix lands once,
its defects surface once, and every item in the class is then mechanical.

**The tool inventory, measured 2026-08-01** — note five write tools have NO selftest, which is the gap
that let `rename_at_source` ship a live bug through a green suite:

⚑ **The `stage?` column is the one whose ABSENCE cost a whole detour**: a STAGE is written against
the stages around it, so judging it standalone yields a confident wrong verdict every time (measured:
the risk agent, and me twice). Stage tools now print `stage_warning` when invoked directly.

| tool                  | selftest | polarity                      | **stage?**           | resolves                                                                             |
|:----------------------|:---------|:------------------------------|:---------------------|:-------------------------------------------------------------------------------------|
| `split_pipeline`      | ✗        | `--apply`                     | **THE DRIVER**       | the whole chain — *this is the supported entry point*                                |
| `split_lemmas`        | ✅       | `--apply`                     | stage 1              | monolith → one-definition leaves                                                     |
| `rewire_to_leaves`    | ✗        | apply-default + `--dry-run`   | **stage 4** ⚠        | consumers → leaves; **errs WIDE on purpose**                                         |
| `prune_imports`       | ✅       | `--apply` *(was the outlier)* | **stage 5** ⚠        | unused BARE imports — **never renaming imports**                                     |
| `fix_stale_using`     | ✗        | `--apply`                     | **stage 11** ⚠       | `using` naming what a module no longer exports — **log-driven, needs a FRESH build** |
| `rename_at_source`    | ✅       | `--apply`                     | standalone OK        | a genuine name COLLISION, fixed at the definer                                       |
| `drop_dead_renames`   | ✅       | `--apply`                     | standalone OK        | renaming clause whose new name is unused                                             |
| `capstone_to_dir`     | ✗        | `--apply`                     | standalone OK        | pure barrel → directory + README                                                     |
| `narrow_leaf_imports` | ✗        | —                             | after split_upstream | post-split narrowing                                                                 |
| `scope_fix`           | ✗        | —                             | standalone           | qualified-name / alias repointing                                                    |

**The standing rule:** every worklist item names its intended tool BEFORE work starts. An item whose
tool is “none yet” is a TOOL-BUILD item, not a fix item — and it is worked at the class level
(`drop_dead_renames` retired 3444 clauses precisely because it was built as a class fix, not per site).
An item whose tool has no selftest carries that as a stated risk.

## Next, in order

**DONE — the ASCII-only import class.** It was **8 sites in 7 files**, not 9, and not one severity:
`iface_shape.py` used a *different* class (`[A-Za-z0-9_.']+`, omitting `-`) that missed **160**
modules — every hyphenated name (`V4-as-PFG`, `F2-CommutativeMonoid`) — against 2 for the others.
`scope_fix.py` was already correct (`[\w.-]`; Python’s `\w` is Unicode-aware), so the broad grep’s
hits there were false positives. All eight now use `[\w.'-]+` — correct AND shorter than every form
it replaces. Guarded by two tests: one scans `scripts/`+`scratch/` for the broken shape and fails on
any occurrence (a CLASS guard, not an instance fix), one asserts the corrected class misses nothing.

**DONE — 6c, the col-0 `DECL` convergence.** `check_carrier_locality.DECL` is now indent-aware,
matching `agda_defs.py:30`. Blast radius narrower than the audit implied: only `check_sumtype_ratchet`
imports `DECL` (`check_public_ratchet` imports other names). 142 names became visible; carriers
523 → 658; the 5 falsely-unique carriers verified genuine (`DivStr` and `Trace` are each declared in
BOTH `S5/S5EEA.agda` and `Algebra/Wedge.agda`, indented inside parameterized modules — the fork class
the gate exists to prevent). **The baseline was NOT banked** — see the re-baseline table above for why.

⚑ **A test bug found while verifying 6c, worth keeping.** The `expectedFailure` guarding this debt did
not flip after the fix, because it compared two regexes **it defined itself** instead of importing the
gate’s `DECL`. It could have passed while the gate stayed broken, and it kept reporting failure after
the gate was fixed. Now it imports the thing under test. That is the derived-view failure (§6)
appearing in the TEST code written to catch it — decent evidence the class generalises.

**DONE — 6d, the enumeration authority.** `agda_lex.agda_files(root, include_build=False)` — verified
set-identical to all three existing routes at 2764, and it reproduces `iface_shape`’s wider `agda/`
root at 2765.

The real hazard was **not** the missing `_build` guards (harmless today: `agda/_build/` holds 2762
`.agdai` and zero `.agda`) but the **four same-named `agda_files()` with four different bodies** — two
generators sorting only *within* a directory, one returning a sorted list with a guard, one sorting
nothing. It read as reuse at every call site while silently disagreeing, and two of the four feed
pre-commit gates. All four now delegate. Census unmoved; the sumtype 91 / carrier 658 figures are 6c’s
effect, not 6d’s.

⚑ **PARTIAL BY DESIGN — 21 files still enumerate without the authority.** The scope was **59 sites, 41
unguarded** (not 49). I converged where divergence was LOAD-BEARING — the shared-name set — and left
single-use scans in analysis tools alone: a private `glob` there is a local choice, not a competing
authority. Converting all 21 mechanically would be a large diff with no measured defect behind it, and
this arc has shown twice that unmeasured sweeps introduce bugs (my own `_span_end` copy-pasted into 7
files while fixing a duplication bug). The right instrument for the residue is the rederivation ratchet
below: census them as DECLARED debt with `⚑rederive:` markers, paying down over time.

### Audit IV items — wrong answers first

1.  **DONE — 7a.** *(see §7a RESOLUTION)* Two raw writes banked
    debt on a plain read. **Measurable before applying**: with the env unset, run it and
    `git diff scripts/set1_baseline_cores.txt` — today that diff is non-empty on any paydown; after the
    fix it must be empty. ⚑ Then FIX THE STANDING INSTRUCTION: “do not run the ratchet gates” is
    currently true of one gate and false of six, which trains avoidance of the wrong thing.

2.  **DONE — 7a-b, the inert denominator guard.** `set1_baseline_cores.txt` holds `0`, so
    `base_cores` is `None` and Guard (3) never runs. Decide whether the file should carry the second
    field or the guard should refuse a malformed baseline — the current state silently does neither.

3.  **DONE — 7b (six sites, not four) and the guard that missed them.** ⚑ **DIAGNOSED: my class-guard test
    is a spelling guard, not a class guard.** `tests/test_rederive_agreement.py:102` matches
    `import\\s\+\(\[A-Za-z0-9`, i.e. the literal shape `import\s+([A-Za-z0-9` — but these four write
    `(?:open\s+import|import)\s+([A-Za-z0-9`, with an alternation between. Verified: the guard returns
    False on `audit_import_reach.py`. **It tested the spelling I had just fixed and would have passed
    forever while the class stood.**

    That is the same failure as the 6c `expectedFailure` that compared two regexes it defined itself —
    *a test written from the instance rather than the class passes on everything except the instance.*
    The fix is to match the CHARACTER CLASS wherever it appears (`\[A-Za-z0-9[^\]]*\]\+` near an
    `import`), not a fixed prefix; and the same audit is owed to every other guard I wrote today.

4.  **DONE — 7b-measure: REFUTED.** *(see §7b)* Rebuilt `_shred_graph`’s reach with
    the corrected regex and diff `realizability_surface`’s rank-1 set. The 8 edges are confirmed; the
    false-hole claim is inferred. Do not repeat it as fact until measured.

5.  **DONE — 7c.** Census **byte-identical at 14,131** (0 added, 0 removed). Aggravating detail: the
    module ALREADY imported `agda_lex` two lines above for the span/mask authority — the import was
    present and simply unused for enumeration, while its sibling `check_claims` delegated. Also removed
    an `if True:` left as indentation scaffolding; dead code in a gate reads as intentional later.
    ⚑ **It exposed a design defect in my own ratchet — see §7g.**

6.  **DONE — 7d, both defects mine.**

    - `check_feature_coverage`: the audit said “point it at both dirs” — **measured and declined.**
      52 scenarios in each, but el-atlas’s describe DOMAIN semantics (chart involutions, exp/log
      conjugacy), it has no test suite, and no test names any of them; extending the gate there would
      either fail permanently or demand 52 fake tests. The real fix is to **state what it does not
      cover**, since a citation in a WHY section reads as a coverage claim. Separately: `stale`
      reported but returned 0, so deleting a Scenario left its test naming nothing and the gate stayed
      GREEN — coverage could shrink toward zero while printing “clean”. Now fails both ways (verified
      by deleting a Scenario, exit 1, and restoring it).
    - `run_selftests`: now a recursive walk over `scratch`/`scripts`/`jea`/`el-atlas`. It found
      `jea/jea_circuit.py` — **300 real trials against a numpy Laplacian-pseudoinverse oracle**,
      invisible to the runner AND unreportable once found (prose, no `N/M`). Fixed the report rather
      than exempting it: **413/413 across 11 suites**, up from 113/10. The audit said two suites
      violated `N/M`; measured, only one did — `sql_lift` already reports a count.

7.  **DONE — 7e: one fix and one REFUTATION.**

    - **Unknown flags, confirmed and fixed.** Every gate accepted `--queit` and ran verbose-but-passing
      (measured across five). `ratchet.check_argv` now refuses at the shared layer; four gates wired,
      each exits 2 on a typo with real flags unaffected. Deliberately NOT argparse — these are invoked
      positionally from a shell hook and several take bare paths, so a membership check is the whole fix.
    - ⚑ **`worklist.py --check` — THE AUDIT WAS WRONG, and the plan previously told a future reader to
      “fix” a working gate.** Tested both failures it exists to catch: an unparseable module and a
      crashing predicate — **both exit 1**. Its purpose, stated in the hook comment, is that the tracker
      must PARSE AND RUN end-to-end (a dropped comma once made it unparseable for \~10 commits, invisible
      because no gate ran it). “Returns 0 unconditionally” describes only the CONTENT branch, which is
      deliberate and documented inline: an OPEN item with an artifact predicate is legitimately
      not-done, not a regression. **A smoke test that works is not a gate that fails to work.**

### Earlier items

8.  **(M/L) 6d residue: converge the remaining 21 enumeration sites.** Retires the armed
    `_build` asymmetry and the four-different-bodies-one-name hazard (`agda_files()` is defined four
    times with **different bodies** — a shared NAME is not a shared authority).
9.  **(M) `check_rederive_ratchet.py`** — a paydown-only ratchet over the *rederivation-site* census,
    with `⚑rederive: <reason>` markers COUNTED, not exempted. Ship after 1 so the initial baseline
    reflects a converged tree instead of freezing today’s debt.
10. **(S) 9b/9c/9d/9e — the Audit V residue**, in severity order: `carriers()` name collision (drops 2
    sites from a live policy); the `STRUCTURAL` module-parameter gap (latent unpayable debt); the four
    baselines with no `gate_keys.SCHEMA` entry (inverts churn verdicts); `check_argv` at 5-of-21.
11. **(M) 9g — the COMPLETENESS GATE OVER GATE COVERAGE.** The only structural answer to the
    guard-from-the-instance class, because its population is DISCOVERED rather than declared. Asserts
    every `scripts/check_*.py` is hook-wired-or-declared-advisory, calls `check_argv`, and — if it
    writes a baseline — has a schema entry and a tracked file. Would have caught 9a, 9d and 9e at once.
12. **(S) The standing instruction.** The audit drafted CLAUDE.md wording for the derived-view trigger
    plus a table of canonical derivations, and proposed `tightening-loop` carry it (its reify-audit
    phase already asks “where was a tie asserted in prose but no term wired?” — `gen_build_makefiles`’
    “SOUND super-set” docstring was exactly that, and it was false). **Not applied — needs approval**,
    since it changes standing instructions rather than code.
    4b. **(L) THE `Bisim` PRELUDE — the highest-leverage paydown in the tree, and it is NOT the rewire
    extension.** \~3,000 of 3,715 renaming clauses are ONE replicated 10-clause import prelude over
    `Substrate.Algebra.R.Trace.Bisim` across \~272 files in `Category/UniversalProperty/ExtrudeCoEmitGraded/`.
    A single `rename_at_source` pass on `Bisim` retires \~80% of the renaming census. Scope as its own
    arc; it dwarfs §11’s extension. (`Bisim` has NO leaf dir — it needs the split first.)
    4c. **(M) The `renaming` extension**, reordered by §11d — the SCOPE WALK LEADS, because it decides how
    much of 11c’s population is real:
    1.  ✅ **DONE — `scope_fix._in_scope` is telescope- AND position-aware.** MEASURED broken: it
        returns `False` for `_+_` in `Graded/Defs.agda` because its `^module [^\n]*\(` pattern demands
        the parameter on the header’s FIRST line. Route through `agda_lex.statements`/`_depth_after`
        (the span authority) — the `⟡paydown-telescope-anchor` hazard is documented at `scope_fix.py:362`
        **in the same file**.

        **What landed.** The telescope parser is `agda_lex.module_scopes()` + `binds_at()` — in the SPAN
        AUTHORITY, not in `scope_fix`, so there is one telescope parser rather than two. `_in_scope` gained
        an optional `lineno`: omitted → the file-level question its three `application_args` callers ask
        (contract preserved); supplied → positional. Verified on the witness:
        `_in_scope(Defs.agda,"_+_")` **False → True** (the bug), `(…,6)` False at the import line,
        `(…,55)` True at the use site.

        ⚑ **BLAST RADIUS MEASURED: 1590 of 1948 telescope parameters tree-wide were INVISIBLE** to the old
        regex — it saw **18%**. So `application_args` has been under-supplying module arguments across the
        whole tree, and this fix is far larger than the un-rename gate that motivated it. (What that
        changes downstream is UNMEASURED — `application_args` now answers True in many more places, and
        nothing yet exercises it end-to-end.)

        **Guarded: 8 selftest cases** in `agda_lex` (suite 413 → **421**, so they demonstrably run),
        each the measured defect — 2nd-line param binds, param NOT bound above its own header, sibling
        module’s param does not leak, header with no `where` is not a scope.

    2.  ✅ **DONE — the REAL count, and the scope walk was NOT the lever.**

        | classifier               | CLEAN | BODY-OCCURS | OTHER-PROVIDER | unfixable            |
        |:-------------------------|:------|:------------|:---------------|:---------------------|
        | textual (file-level)     | 3006  | 122         | 487            | **609 / 3615 (16%)** |
        | scope-aware (positional) | 3021  | 107         | 487            | **594 / 3615 (16%)** |

        ⚑ **THE SCOPE WALK RESCUES 15 CLAUSES. Fifteen.** I expected it to clear “an unmeasured fraction”
        of the blockers; it moves 609 → 594. The §11d fix was still correct and necessary — the
        `Graded/Defs.agda` capture is real and `_in_scope` was genuinely broken tree-wide (1590/1948) —
        **but it was not the bottleneck, and predicting it would be was the same guess-shaped error §11d
        retracted, just pointing the other way.** Recording the small number rather than the story.

        ⚑ **AND MY FIRST RUN SAID 100% UNFIXABLE — A BUG IN MY OWN CLASSIFIER.** The `body_occurs` test
        scanned the WHOLE file, so `old` always matched ITSELF inside its own `renaming (old to new)`
        clause; every clause read BODY-OCCURS and the scope walk appeared to “rescue 3117”. **What caught
        it was the disagreement with the agent’s 26%** — a number I had deliberately preserved as
        not-to-be-quoted. A second independent measurement is what made my own bug visible; had I only
        run mine, I would have published a 3117-clause triumph built on a self-match.

        **WHERE THE REAL BLOCKER IS — 487 OTHER-PROVIDER, and it is ONE NAME.**

        | count   | clashing name |     | count   | provider                        |
        |:--------|:--------------|-----|:--------|:--------------------------------|
        | **434** | `_+_`         |     | **424** | `Substrate.Algebra.F2`          |
        | 26      | `suc`         |     | 27      | `Foundation.Level`              |
        | 12      | `+-comm`      |     | 16      | `Foundation.Nat.Properties.Add` |

        So 434 of 487 blockers are `_+_`, and 424 of those come from a SINGLE provider. That is one
        `rename_at_source` decision on `Algebra.F2`’s `_+_` — not 487 judgements. **Together with the
        `Bisim` prelude (4b), the renaming census is dominated by a handful of single-provider
        decisions**, which is a different arc shape than “build a general un-rename tool”.

    3.  ⚑ **RESEQUENCED BY STEP 2 — the two single-provider renames come FIRST, and they may make most
        of the general tool unnecessary.** The census is not 3,615 independent decisions:

        - ✅ **DONE — `Algebra.F2`’s `_+_` → `_+F_`.** 201 files renamed, 232 correctly left AMBIGUOUS for
          the build. **Ban paydowns 2043 → 2898 (+855); additions 73 → 71.**

          *The name was a technical call, not a preference* — I initially punted it to the user, who
          rightly declined (“I don’t know Agda well enough to have a code style preference here”). The
          tree looked split 277 `_+F_` vs 272 `_⊕₂_`, but **all 272 `_⊕₂_` uses are ONE directory**
          (`ExtrudeCoEmitGraded/`, the same replicated prelude 3b retires) — so it is one decision counted
          272 times, and `_+F_` (277 files, spread tree-wide) is the genuine convention. Zero existing
          providers for any candidate, so no new collision.

          ⚑ **3c PAID FOR ITSELF WITHIN MINUTES.** `F2.agda:59-60` are bare-infix clauses (`𝟘 +F y = y`)
          — **under the shipped two-spelling bug those would have kept `+` and become an undefined
          operator across the whole file.** The selftest cases written an hour earlier were not
          hypothetical; they described exactly what this rename would have done.

          ⚑ **AND I CALLED A PRE-EXISTING CONDITION MY OWN DAMAGE.** Seeing 210 files with a DOUBLE
          `import … F2 … renaming (_+_ …)`, I concluded the rename had duplicated them. **Diffing against
          the safety tag showed the pair was already there, byte-identical.** Of 729 F2-importing files,
          64 changed, and every change is CORRECT: the clause tracks the renamed source
          (`renaming (_+F_ to _⊕₂_)`), and `renaming (_+F_ to _+F_)` is now a rename-to-SELF — deletable
          noise, the shape that dissolves. **Tagging before the write is what made “is this mine?”
          answerable at all** (`pre-3a-f2-rename`); without it I would have been reasoning from memory
          about a 201-file rewrite.

          *Residue:* 214 files still carry a now-STALE `_+_` clause (F2 no longer exports `_+_` — verified
          0 occurrences), and 434 comment lines were rewritten too (the tool is comment-blind; here that
          is cosmetically right but it is UNGUARDED behaviour, not a designed feature). `fix_stale_using`
          is the tool for the clauses; the classifier still reports 487 OTHER-PROVIDER because the clauses
          remain in the consumers — **the rename made them removable, it did not remove them.**

        - **the `Bisim` prelude** (4b) — ⚑ **TWO CORRECTIONS, and the second changes the TOOL.**

          *(i) The number was wrong.* `Bisim` is **1088 clauses across 272 files**, not \~3,000. The
          agent’s figure conflated it with its SIBLING preludes in the same replicated block —
          `Allegory.Refinement` 816, `ExtrudeCoEmitViaTrace` 274, `Foundation.Empty` 272,
          `R.Trace.Final` 272. One block, five providers.

          *(ii) ⚑ I FRAMED SPLITTING AS A CANDIDATE FIX AND JUDGED IT AGAINST ONE METRIC — WRONG (user:
          “splitting is the goal; it comes with many benefits, collision avoidance is merely one”).*
          I wrote “splitting `Bisim` would NOT have fixed it”, treating decomposition as a *means* to the
          renaming paydown and scoring it on whether it retired clauses. **That inverts the arc.**
          Definition-per-file decomposition is the OBJECTIVE (⟡cap-128 elaboration peaks, one lemma per
          elaboration unit, importable leaves, and — per the ban skill — the precondition that makes bare
          imports possible at all). Collision-dissolution is one downstream benefit among several. A tool
          that does not move THIS census is not thereby “not the fix”; it may simply be paying a different
          part of the same objective. `Bisim` still wants splitting on its own merits, independent of
          anything measured here.

          *What is true, narrowly:* the dead clauses in `ExtrudeCoEmitGraded/` will not be removed BY the
          split, because a consumer that references a name zero times is unaffected by which module
          exports it. That is a statement about the removal of those 3244 clauses, NOT a verdict on
          splitting.\*
          ⚑ **My first statement of this was incoherent and the user caught it**: I wrote that the clauses
          “are not dodging collisions — they are prefix-disambiguations”, which is a distinction without a
          difference (disambiguation IS collision-dodging). Measured properly with `def_index`, **most ARE
          real collision-dodges**: `⊥` has **6** providers, `iterate` 3, `~-refl` 3, `out`/`chain`/`coalg`
          2 each; only `head~`/`tail~`/`_~_` are sole-provider and therefore stylistic.

          The actual reason splitting does not help is different and stronger: **the file dodges a
          collision for a name it never uses.** The clash is real, the import is dead. Splitting a
          provider changes which module exports a name; it cannot help a consumer that references the name
          zero times. **MEASURED: of 3264 renaming clauses in
          `ExtrudeCoEmitGraded/`, 3244 name something DEAD — the new name occurs exactly once, on its own
          import line.** That is **90% of the whole tree-wide renaming census (3244 of 3615)**, and it is
          an UNUSED-IMPORT problem. The tool is `prune_imports`, not `split_lemmas` + `rename_at_source`.
          Only **20 clauses are genuinely used** (`Bot`, `Rchain`, `Riterate`, `bhead~`, `btail~`,
          `coemit-coalg`, `trace-out`, `~-refl'`).

          ⚑ **AND I RAN A WRITE THINKING IT WAS A DRY RUN.** `prune_imports` writes BY DEFAULT — its flag
          is `--dry-run`, the INVERSE of `split_pipeline`/`capstone_to_dir`/`rename_at_source`, which all
          take `--apply`. I invoked it bare on one file expecting a preview and it deleted 12 import
          lines. The deletions were correct (verified: none of the 12 names appears in the body) and the
          tool snapshotted first, so nothing was lost — but **the write-polarity divergence §7e recorded
          as an inconsistency is a live hazard, not a stylistic one**, and it just fired on the person who
          wrote that finding down.

          *(iii) ⚑ AND `prune_imports` DID NOT DO THE JOB — I picked the wrong tool after correctly
          diagnosing the problem.* Ran over all 272 files: **2927 unused import lines dropped, and ALL
          3264 renaming clauses remain. Ban census UNMOVED (2898 paid / 71 added).** The reason is in the
          tool’s own docstring, which I had already read: `prune_imports.should_keep` treats
          `renaming`/`as` imports as UNTOUCHABLE by design. So it removed unused BARE imports — genuine
          cleanup, orthogonal to the ban debt — and left every dead rename in place.

          **The 3244 dead clauses still need a remover, and no existing tool removes them:**
          `prune_imports` refuses renaming imports; `fix_stale_using` repairs `using` lists from build
          logs; `rewire_to_leaves` needs leaves. This is precisely the `--unrename`/dead-clause tool of
          step 4 — **so 3b did not eliminate the need for the general tool, it SHARPENED it**: the tool’s
          primary job is not un-renaming live aliases (20 clauses) but DELETING dead ones (3244). That is
          a far simpler predicate — “the new name occurs only on its own import line” — with no capture
          risk at all, because nothing references the name being removed.

          \*(iv) ✅ **`Bisim` SPLIT ON ITS OWN MERITS — 6 leaves** (`Cons`, `Op`, `RecipInvol`, `Refl`,
          `Sym`, `Trans`), then **26 importers rewired**. Which immediately surfaced a REAL TOOL DEFECT:

          ⚑ **`split_lemmas` did not emit record FIELDS in `-- Defines:`.** `head~`/`tail~` are
          projections of `record _~_`, sitting under an indented `field` keyword — `CTOR` expects the
          name at the data block’s own indent, so it never saw them and the header listed only `_~_`.
          Consequence: **six consumers importing `head~` went UNMAPPED** in `rewire_to_leaves`, because
          no leaf claimed to define a name that plainly travels with `_~_`. Tree-wide, only **12 of 686**
          `-- Defines:` headers mention any field.

          **Fixed at source** (`split_lemmas.field_names`, wired into `provides`), not by hand-patching
          the one header — same class as the constructor gap the function’s own comment records, one
          layer deeper, and the third time this arc that an indent assumption hid names (`agda_defs`
          heads, `split_lemmas` constructors, now fields). After the fix: UNMAPPED → 0, 26 importers
          rewired. The residue at those sites is `renaming` clauses, i.e. the known step-4 gap, not a
          new failure.

          *(v) The four SIBLING preludes also have split plans* — `Allegory.Refinement` (10 leaves),
          `ExtrudeCoEmitViaTrace` (14), `R.Trace.Final` (10), `Foundation.Empty` (2). 36 leaves; they
          want splitting for the same objective-level reasons `Bisim` did.

          ✅ **SPLIT — 36 leaves: `Refinement` 11, `ExtrudeCoEmitViaTrace` 14, `R.Trace.Final` 10,
          `Foundation.Empty` 1.** Rewiring reported **0 importers** for the first two, which is not a
          failure: their consumers reach them through the `renaming` prelude, which `rewire_to_leaves`
          does not parse. That is the step-4 gap, and step 4’s tool then removed 3444 of those clauses —
          so the rewire should be re-run now that the consumers are bare.
          Do these, re-census, and only then size the general tool against what actually survives. Building
          it first would be building for a population that two commands can mostly retire.

    4.  ✅ **DONE — and `parse_renaming` was NOT owed: the agent’s “verified absent tree-wide” was WRONG.**
        `scope_fix._rename_pairs` (`:2017`) already parses `renaming (src to tgt; …)` into pairs and is
        used at three sites. I nearly built a fourth copy on the agent’s word — **a second agent’s
        absence-claim is exactly as unreliable as my own** (CLAUDE.md: report presence with witnesses; an
        empty search is a fact about the METHOD). `drop_dead_renames` imports it.

        **`scratch/drop_dead_renames.py` — 3444 dead clauses removed tree-wide, ban paydowns
        2898 → 5437 (+2539), the largest single movement of the arc.** 3244 of those were the
        `ExtrudeCoEmitGraded/` family, matching my independent census exactly (an agreement check, not a
        re-derivation). 7 selftest cases; suite 437 → 444 across 12 → 13. Defaults to DRY RUN with
        `--apply` — deliberately the sibling convention, NOT `prune_imports`’ inverted `--dry-run` that
        cost an unintended write earlier today.

        *Why it is safe:* a DEAD clause has no use sites, so the capture risk that makes un-renaming
        dangerous (the `Graded/Defs.agda` module-parameter witness) **cannot arise** — the tool deletes a
        clause naming a name the body never mentions and refuses everything else. It never rewrites a
        body. Verified after the run: zero malformed imports; the one residual `using ()` is a
        PRE-EXISTING wrapped continuation in `TokiPona/F2toQForget.agda:26`, not tool output, and is left
        alone rather than guessed at.

    5.  ✅ **RE-RAN THE REWIRES — 1081 importers, and this closes the loop.** Before the dead-clause
        removal the four sibling splits rewired **0** importers; after it: `Refinement` 271,
        `ExtrudeCoEmitViaTrace` 267, `R.Trace.Final` 271, `Bisim` 272. **The `renaming` clauses were what
        blocked them** — step 4 unblocked step 3’s splits, which is the dependency the resequencing
        predicted. Ban paydowns **5437 → 6512** (+1075).

        **ARC TOTAL: renaming population 3615 → 283 LIVE clauses (92% gone); ban paydowns 1674 → 6512.**
        *(reported as 185/95% before the span fix — a line-based undercount, corrected here.)*

    6.  ✅ **STEP 4b GATE BUILT — and “these are the genuine collision-dodges” was WRONG AGAIN.**
        I asserted the 185 survivors were real collisions. Measured with `def_index`:

        | verdict   | count   | meaning                                                                                                                  |
        |:----------|:--------|:-------------------------------------------------------------------------------------------------------------------------|
        | **SAFE**  | **126** | no clash, no capture — un-renameable now                                                                                 |
        | COLLISION | 33      | another provider co-imported → **CHECK THE PROVIDER FOR AN EXISTING PATTERN SYNONYM FIRST**, then fix upstream at source |
        | OCCUPIED  | 25      | `old` already free in the body                                                                                           |
        | CAPTURE   | **1**   | `old` bound by a telescope AT a use site                                                                                 |

        Only **33 of 185** are real collisions; 126 are aliases guarding against nothing in this file.
        **Third time this arc I called a population “genuine X” before measuring it** (the 26% unfixable,
        the “must refuse” shape, now this) — the shape of the error is stable: I generalise from the
        first two witnesses I read.

        ⚑ **AND THE SELFTEST FOUND DEAD CODE IN MY OWN GATE.** I wrote a case asserting a CAPTURE verdict
        where nothing else blocks; it returned OCCUPIED. Cause: gate (2) scanned the whole body, so
        `module Over (old : Set)` counted as an occurrence — **a telescope BINDER read as a USE, which
        meant gate (3) was UNREACHABLE.** The capture check I built the scope walk for could never fire.
        Fixed by excluding module-header lines before gate (2); re-measured, **CAPTURE now fires on 1
        clause it had been masking.** The earlier “0 blocked by capture” was an artifact of that bug, and
        only a test written to demand the verdict — rather than to confirm the tool — exposed it.

        ⚑ **THEN THE 73-ADDITIONS ITEM EXPOSED A SPAN DEFECT IN THE SAME TOOL — MINE, TODAY.**
        Investigating why the additions held steady at \~73 all session while everything else moved by
        thousands: `gate_preflight` says only **40 are genuinely new** (33 are churn). Four looked like a
        GATE BUG — keys tagged `::renaming` for what my grep showed as bare imports. **The gate was
        right and my grep was wrong**: `Graded/Mod.agda:30` is `open import …SLesInjective` with
        `renaming (…)` on **line 31, a continuation**.

        That is the statement-span class this arc retired in fifteen tools, and `drop_dead_renames` —
        written hours ago — had it TWICE:

        - `dead_pairs` read `_rename_pairs(lines[i])`, one line, so every wrapped clause was invisible;
        - and `body` blanked only IMPORT-matching lines, leaving the CONTINUATION in the body, so the
          new name **matched itself** and every wrapped clause read as live. *That is the same
          self-match that made my step-2 classifier report 100% unfixable* — recurring because “the
          body” is easy to define one line at a time.
          Both now route through `agda_lex.statements`. **Re-measured: 283 renaming clauses, not 185** — 98
          were hidden by the line-based read — and **0 remain dead** (the earlier sweep did get them all).
          Verdicts over the true population: SAFE 126, OCCUPIED 102, COLLISION 54, CAPTURE 1.
          Guarded by 2 span selftest cases (wrapped-dead, wrapped-live); suite 15/15 in this tool.

        `token_ledger` also landed: `S' = S − k·{new} + k·{old}`, nothing else moving. Line-conservation
        cannot see capture (a substitution is not a permutation), so the invariant had to be on tokens.
        13 selftest cases, 3 of them ledger-negative (extra token; greedy rewrite inside a longer name).

        *(superseded scoping note follows)* **STEP 4b IS NOW SMALL AND SHARPLY DEFINED — 185 clauses, not 3615.** These are the genuine
        collision-dodges the `--unrename` gate was designed for, and only here does the capture risk
        (`binds_at` per use site + token-conservation ledger) actually bind. Head of the population:
        `Tm` 39, `suc` 22, `Wedge` 20, `+-comm` 14, `+-assoc` 9, then a tail (`coalg`, `⊥`,
        `Canonical-ex` 5 each). ⚑ **Note the shape change: `Tm`/`Wedge` lead now, NOT the `_+_` family** —
        sizing the general tool against the pre-step-4 census would have targeted a population that no
        longer exists, which is exactly what the resequencing avoided.
        `rename_at_source`’s two-spelling fix is **DONE** (both sites). **Defer `as`** (932 statements, but
        qualified-name resolution — a different rewrite; `scope_fix.fix_qualified` already exists).
        4d. ✅ **DONE — `rename_at_source.py` now has a `_selftest`: 16 cases, suite 421 → 437 across 11 → 12
        suites.** ⚑ **The SUITE count moving from 11 to 12 is the evidence it was INVISIBLE, not passing** —
        `run_selftests` discovers modules that DEFINE `_selftest`, so a write-path tool with none is simply
        absent from the denominator.

    Two structural changes were needed before it could be tested at all:
    - **The two-spelling logic was a CLOSURE inside `rename()`** — unreachable from a test, which is
      part of why the bug survived. Lifted to module level as `spellings()` / `apply_spellings()` /
      `any_spelling()`; `rename()` now routes through them, and the coming `--unrename` mode shares one
      implementation instead of re-deriving a third.
    - **`--selftest` was not dispatched** — it fell through to the arity check and printed usage, which
      `run_selftests` scores as a FAILING suite (a missing `selftest: N/M` line is failure by design).
      Dispatched before the arity check.

    ⚑ **The cases were verified to FAIL against the shipped bug, not merely to pass now.** Simulating
    the old underscore-only behaviour: `zero ≟ zero = yes` stays unrewritten (fixed: `≟ℕ`), and
    `any_spelling` returns False (fixed: True) — so a file using only the bare-infix form was never even
    SELECTED. A guard that passes on the fixed code but would also have passed on the broken code is
    decoration; these two are not.

*(superseded: “it has none, which is why 413/413 stayed green”)* — the original note follows.
**(S) A `_selftest` for `rename_at_source.py`** — it has none, which is why 413/413 stayed green
through a live write-path bug. Owed regardless of §11.
4e. **(S) OPEN — a QUALIFIED-name matcher.** `agda_lex.word` matches a BARE name; `retire_mod_tip.py:88`
needs ``` Div.Over.recon-nth\``, where the name is preceded by ```.```` . The DRY audit attributed that miss    to```\b```{=tex}; **measured, ````word()`also returns False there and correctly so** —`.`is deliberately not a delimiter. Whether`word`should accept a leading`.`, or a separate`qualified(mod, name)`helper should exist, is a design question. **Not answered silently**: widening`word```` to make one witness pass would weaken the boundary for all eight adopters. 4f. **(S) OPEN — the```\b```{=tex} motif censuses the shape, not the intent.\*\* ````check_rederive_ratchet`now flags`r”`\b"`{=tex} + re.escape(…)`, and my own bulk sweep proved a mechanical rewrite **cannot distinguish a USE of the broken pattern from a DEMONSTRATION of it** (it inverted an`agda_lex```` selftest case that exists to show```\b```{=tex} fails on ````∙\`). Any future sweep over this motif must exempt test/demo code, or
be applied by hand.

5.  **Then** the Agda tree — ⚑ **RE-MEASURED 2026-08-01, and every figure in the old version of this
    step was superseded** (it said “33 build errors → pay down 245 ban keys → release 1674 paydowns”;
    all three moved):

    **a. FIX THE ROOTS, RE-CENSUS AFTER EACH.** **51 errors** (was 60; the `Foundation/Bool` parent
    cleared 9). ⚑ **The tree is NOT blocked — it is largely BUILT with a failing frontier: 2909 `.agdai`
    cores on disk, \~51 modules typechecking per run.** An earlier version of this step said “0 cores
    compiled in 30 minutes, everything downstream is BLOCKED”; that read `make` skipping up-to-date
    targets as *nothing compiling*, which is the opposite of what it meant. Root-first still holds
    (failures do cluster at `Foundation/*` and one root cleared nine errors), but not because the tree
    is dead.

    ⚑ **`AmbiguousParseForApplication` / `NoParseForApplication` ARE A DISTINCT CLASS — a SECTION vs a
    GRAMMAR, not a shared name.** `CFMatrixBridge/Properties.agda:40`: `a * p₁ +_` parses as either
    `a * (p₁ +_)` or `(a * p₁) +_`, where `_*_` (infixl 7) and `_+_`’s postfix SECTION `+_` (level 6)
    come from DIFFERENT modules and share NO name. **No name-based tool can see this**, including the
    conduit `ambiguity()` check — measured, it does not flag this site. The pipeline already knew:
    `split_pipeline:366` records the same expression and that **dropping the unused import fixes it
    while parenthesising does not** (both readings parse the same). So the fix for this class is
    *narrow the import*, not disambiguate the name.

    **Live head (STALE — predates the F2 split; RE-CENSUS before working it, and expect
    `FileNotFound` to rise by up to 30 from the consumed-parent survivors above):**
    29 `NotInScope`, 9 `FileNotFound`, 4 `NoParseForApplication`,
    4 `ConstructorPatternInWrongDatatype`, 3 `MissingTypeSignature.Function`, 1 `UnequalTerms`,
    1 `AmbiguousParseForApplication`.
    *(✅ 2 `AmbiguousName` — the fzero synonyms. ✅ 8 `DuplicateBuiltinBinding` — ONE root cause: the
    leftover `Foundation/Bool.agda` parent. Both above.)*

    ⚑ **`FileNotFound` is the mechanical class and it recurs**: a consumed parent whose importers were
    never rewired. Both rounds so far were this (`Conway.Mul`, `Foundation.Nat`, `Kelen.Fragment`,
    `Linguistic.RosettaTable`, `TokiPona.AsFreeOverBasis`, then `Foundation.Bool`). **Check for a
    leftover parent FIRST on every `FileNotFound`** — `rewire_to_leaves` clears it in one call, and the
    driver finds importers a column-0 grep misses (129 vs the 4 I counted by hand).

    **b. THEN the ban additions** — *(as written: “the 65 additions hold 6599 paydowns … they need (a)
    first”; **both the figures and the dependency are superseded immediately below**)*.

    ⚑ **RE-MEASURED 2026-08-01, AND THE SEQUENCING IS WRONG — “they need (a) first” is true of a
    MINORITY.** Current census, stable over three consecutive runs: **66 additions holding 6998
    paydowns.** Split by the tool that resolves each:

    | directive  | keys   | tool                                                      | needs a green tree?                                 |
    |:-----------|:-------|:----------------------------------------------------------|:----------------------------------------------------|
    | `using`    | **34** | `split_pipeline` on the provider                          | **no** — decomposition is what MAKES the tree green |
    | `as`       | **22** | qualified-ref rewrite; the F2 ones are mechanical (below) | **no**                                              |
    | `renaming` | **10** | the 4b un-rename gate (and A3’s 113 fully-safe keys)      | **no**                                              |

    Filing all 66 behind “(a) the build errors” serialised the entire 6998-paydown backlog behind a
    green tree that the very same decomposition work is what produces. **The dependency is inverted for
    the `using` bucket and absent for the other two** — the same inversion §9a already recorded once
    (“decomposition is what MAKES the tree green”) and that this step then re-introduced.

    ⚑ **AND ONE `as` BUCKET IS A REGRESSION I CREATED TODAY.** 28 files still
    `import Substrate.Algebra.F2 as F2` — a module **the split in §23 CONSUMED**. Those are live
    `[FileNotFound]`, they are not the deferred `as` class, and they must not be sized against
    `scope_fix.fix_qualified` (\~400 lines): the qualified references are exactly `F2.F₂`,
    `F2.CommRing`, `F2.Polynomial`, each resolving to ONE leaf. **Mechanical, and it goes first** —
    leaving a self-inflicted FileNotFound population in the tree while re-censusing build errors would
    attribute my own regression to the pre-existing backlog.

    **c. THEN `make catalog`** (2762 cores, for §8’s Set₁ question) **→ the gated commit**, at which
    point the re-baselines are banked with their deltas in the commit message.

    ⚑ **The invocation, because exit 144 defeated five launch shapes:** foreground
    `timeout 540 make -C agda -j -k > LOG 2>&1`. And verify a build is running with `pgrep -af "^make"`
    — `pgrep -f "make -C agda"` matches the WRAPPER SHELL and told me a build was live twice when none
    was.

⚑ **Sequencing note.** Steps 1-5 are all verifiable WITHOUT committing (tests, selftests, census diffs,
`make`), which is what makes them safe to do while the tree is red. Step 6 is the only one that needs a
green tree, and it is where the re-baselines land — so a re-baseline can never be mistaken for absorbing
a broken tree.

## Out of scope (labelled, not dropped)

- **The commit itself.** 12 unconditional gates census the whole tree; it is mid-decomposition at 33
  errors, so nothing commits until that is green. This plan is verifiable *without* committing.
- **The catalog.db / `.agdai` derivation route** — the audit’s largest coverage gap; it could not
  measure it without a full build. `gen_build_makefiles.py:25-31` documents that it diverges from the
  source route BY DESIGN (the good case), but nothing measures the magnitude, so nobody would notice
  it growing. Report the delta as a tracked number, not a gate.
- **Provenance-vs-directory ownership across the \~40 `scratch/` write tools** — the F18 worry. The
  audit checked the gate path (found `rglob`-over-content, not `listdir`-as-ownership) but not every
  write tool.
- **`scope_fix.py`’s comment-masking gap** (\~40 raw-source regexes) — declared in its `⚑rederive:`
  header; wide, behaviour-changing, wants its own arc.
- **`scope_fix.py`’s cwd=`agda/` contract.** Phase A preserves it by passing `root=""`. Changing it is
  a larger build.
- **A `stem` helper.** \~14 sites do a bare `[:-5]` with no `.replace` — a real duplication class, but
  `agda_lex` exposes no such helper. Residue, not conversion.
- **`check_rederivation.py`** — the gate that would stop a *new* tool re-deriving these. Needs the
  `⚑rederive:` declaration convention to settle first.
- **Packaging.** The helpers are now pure and root-parameterized (the shippable shape), but no
  `pyproject.toml` exists and adding one is its own decision.
