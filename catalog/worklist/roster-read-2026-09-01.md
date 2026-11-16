# Ⓝ24a-1 ⟡roster-read — the full selftest roster, read

Run: `make -f Selftest.mk -j20 --output-sync=target -k`, cold (`_build/selftest` cleared),
2026-09-01, after ⟡ledger-parametric and ⟡membudget-wire landed.

⚑ **RE-RUN RATHER THAN READ FROM THE OLD LOG.** Run 2's output was truncated by kills that the
autobudget wire was expected to fix, so reading it would have measured a run whose halting
condition no longer applies. The re-run is the honest instrument; what follows is entirely from
it.

## The headline: 21 failed targets, and they are FOUR different kinds

`make` knows two states. `suite_outcome` names seven, and the split is what makes this
actionable — three of the four kinds below are not "the suite is broken".

| kind | n | what it means | where to look |
|---|---|---|---|
| `unread` | **3** | ⚑ **A READER DEFECT, NOT A SUITE DEFECT — FIXED** | `suite_record.py` |
| `unfit` (rc 143) | 3 | killed by the memory lease | the lease, not the code |
| `silent` (0/0) | 9 | ran and asserted **nothing** | the suite |
| `cases` | 5 | genuine assertion failures | the suite |
| `vacuous` (0/0) | 1 | reported 0/0 explicitly | the suite |

## ⚑⚑⚑ THE `unread` THREE WERE THE READER, AND THEY WERE PASSING

`scratch/tmi_index.py` (33/33), `tmi_status.py` (51/51), `tmi_subject.py` (15/15) each printed a
complete typed record and `state: "ok"` — and each failed its target with Error 1.

**Cause: a two-spelling defect across the row contract.** `scratch/rungs.py` OWNS it and declares
`ROW_PREFIX = "#row\t"` (a TAB). `substrate/suite_record.py` restated it as `"#row "` (a SPACE).
So `line.startswith(RECORD_PREFIX)` was FALSE for every real record, the structural arm never
fired, the prose arm found no `N/M` in `0 of 15 check(s) failed`, and the verdict was
`unread (0/0)`.

⚑⚑ **THE FAILURE POINTED AT THE WRONG FILE.** A reader seeing `unread` goes to the suite's code —
which is correct — rather than to the reader that cannot parse it. The emitter was right the
whole time. This is `census-keyed-on-one-spelling` at its most expensive: the two halves disagree
SILENTLY and the blame lands on the innocent half.

⚑ **AND NOTHING CAUGHT IT BECAUSE `suite_record.py` HAD NO SUITE.** `suite_outcome_selftest`
covers the CLASSIFIER thoroughly — it even pins that a parsed count is never reported unread —
but the classifier was never reached: the failure was upstream, in the parse. **A case over the
verdict logic cannot see a reader that hands it nothing.**

**Repaired:** prefix corrected and the authority NAMED rather than silently re-copied (the
constant is still restated, because `scratch/` is unpackaged, `rungs.py` executes at import, and
`check_scratch_independence` gates `substrate/` against depending on `scratch/` — so the honest
form is debt with a citation, not a load). New suite `substrate/suite_record_selftest.py`, 12/12,
whose first arm reads the declaration out of `scratch/rungs.py` so the two cannot drift again.
Verified: all three targets now green through the real make path.

## ⚑⚑ THE THREE KILLS ARE NOT WHAT I PREDICTED, AND THE PREDICTION WAS THE ERROR

`catalog/library/figures.py`, `scripts/promote_frontier.py`, `scripts/worklist_gate.py` — all
rc **143**. Per `membudget`'s own note that is a real OOM kill on this systemd (SIGTERM from
scope-OOM handling; 137 is the kernel killer, and which fires is version-dependent).

⚑ **I EXPECTED `worklist_gate` TO BE FIXED BY THE WIRE AND IT WAS NOT — because I sized against
the wrong key.** Its recipe label is **`claim:roster`**, not `selftest:worklist_gate.py`. The
166-run/188MB history I measured belongs to a DIFFERENT invocation path. `membudget peaks
claim:roster` → **no rows**. So `label_lease` correctly returned the default, and the wire did
exactly what it should.

⚑⚑ **A CLAIM LABEL IS NOT A WORKLOAD IDENTITY, which is the same defect one level up.** Every
suite claiming an artefact shares one label (`claim:roster`, `claim:pg`), so they collapse onto
one ledger row — precisely the *"per-label is the right key for a gate that runs once; per-module
is the right key for work that runs per core"* failure `_auto_mb`'s own comment warns about. The
autobudget cannot size these, and it is not a bug in the autobudget.

⚑ **AND THE LEDGER CANNOT CONVERGE ON A WORKLOAD THAT ALWAYS DIES.** `_record_time` records only
SUCCESSFUL runs (correctly — a killed run's peak is the CAP, not the need), and
`MEMBUDGET_RETRY_OOM` is set by the agda shim but NOT by `Selftest.mk`, so a suite whose default
lease is too small dies with no retry and no peak recorded. `figures.py` has 227 runs at max
79MB, sized to 128MB, and **still died at 128** — its footprint under the roster differs from its
footprint solo, and nothing in the ledger can learn that.

**Filed, not fixed here:** ⟡claim-label-identity (a claim label needs a per-suite sub-key) and
⟡retry-in-selftest-mk (the roster should set `MEMBUDGET_RETRY_OOM`, since a suite re-run is
idempotent).

### ⚑⚑⚑ CORRECTION (operator, 2026-09-01): `unfit` REACHING A READER IS ITSELF THE BUG

I described `unfit` as a verdict kind that "sends you to the lease, not the code" — as though a
kill were a terminal state to be classified. Operator: *"we're supposed to have our memory lease
GROW and the test retried."* Correct, and the machinery exists: `membudget` retries on 137/143,
releases, and re-enters at the next power-of-two bucket until it fits or hits the ceiling, and
its comment records deliberately extending that to NESTED leases so a child can correct its own
too-tight guess.

⚑⚑ **THE LADDER IS ARMED ONLY FOR THE AGDA SHIM AND IS INERT FOR EVERY SUITE.** The guard is
`[ -n "${MEMBUDGET_RETRY_OOM:-}" ]`; the shim sets it, `Selftest.mk` does not. So all three of
this run's kills were **un-fired retries**, not memory verdicts — and because `_record_time`
records only SUCCESSFUL runs, each also left no peak, so history cannot converge on exactly the
workloads that need it.

⚑ **SO `unfit` SHOULD BE VERY NEARLY UNOBSERVABLE**, and its appearing as a populated category
is a fact about the omission rather than about the suites. That also sharpens what a pytest
migration must carry: not a verdict NAME but the **retry-and-learn loop** — grow the lease,
re-run, record the real peak. `pytest-xdist` has no equivalent and nowhere to put one.

### ⚑⚑ AND `vacuous` IS A DISCRIMINATION PROPERTY, NOT A COUNT (operator, same)

I defined it as "reported 0/0 and asserted nothing." Operator: *"a vacuous test is a test that
fails to be a discriminator."* That is the better definition and it is ALREADY THIS REPO'S, one
silo over: `pack_discrimination` exists precisely to report *"whether that gate could even have
failed at the level it ran on"*, and the standing rule is that a PASS is never banked on a level
that cannot fail.

⚑ **WHICH MEANS `vacuous` IS UNDER-DETECTED, NOT MERELY HARD TO PORT.** 0/0 is the degenerate
case; a suite with fifteen arms that would pass against ANY input is equally non-discriminating
and currently reads `ok`. The real predicate is the mutation-shaped one — *would this suite
notice if the thing under test broke?* — and `mutation_intent` sits in the baseline roster
reading **ABSENT**. New symbol: **⟡vacuous-is-nondiscrimination**.

## Ⓝ24a-5 ⟡silent-nine — RESOLVED. The class was FOUR causes, and only one is a suite defect

Every one opened individually (⚑ the `unread` three had already proved a reader defect can wear
a suite defect's clothes, so none was classified without running it).

| suite | cause | kind |
|---|---|---|
| `scripts/ddl_lifecycle.py` | `sandbox_fixture` → `OperationalError` | ENVIRONMENT |
| `jea/metalanguage/reconstruct.py` | same, ⚑ *after* correctly SKIPping an empty-SPPF case | ENVIRONMENT |
| `jea/metalanguage/schema.py` | same (`schema_selftest.py:202`) | ENVIRONMENT |
| `jea/metalanguage/catalog_db.py` | same (`:398`) | ENVIRONMENT |
| `scripts/sppf_db.py` | same, via `sppf_decode.py:1371` | ENVIRONMENT |
| `scratch/mitigation-index/items.py` | ⚑ **PASSES 105 CHECKS** — output matches neither reader | READER |
| `substrate/mode_coverage.py` | honestly reports UNMEASURED, exits 0, emits no record | READER |
| `substrate/selftest_mk.py` | ⚑ `--selftest` → bare `0`; **has no cases at all** | NO SUITE |
| `scripts/run_selftests.py` | ⚑ `TypeError: may_write() takes 0 positional arguments but 1 was given` | **CODE DEFECT** |
| `scratch/bibstruct.py` | exits 1 on a real `--add` refusal; no record emitted | READER |

### ⚑⚑⚑ FIVE ARE ONE ENVIRONMENT FACT, AND IT IS A TENANT SPLIT — NOT "postgres is down"

MEASURED: `schema.py --live --relations` → **31 relations, connects fine**.
`schema.py --sandbox --relations` → `Connection refused`, same host, same port.

`PG_SANDBOX_DB` (`store.py:124`) is a SEPARATE DATABASE WITH A SEPARATE ROLE — deliberately, so
that *"the only thing harmed is a database that exists to be harmed"* rests on a CREDENTIAL
rather than on a `dbname` field. The sandbox role is absent or unauthorised here; live is
healthy. **Reading this as "the store is down" would have been the wrong-tenant error the
sql-relalg skill calls SILENT, committed while diagnosing.**

⚑ **AND THESE SUITES CRASH WHERE THEY COULD SKIP.** `reconstruct.py` prints
`SKIP store cases — the SPPF is empty` one line before dying on the sandbox connect: it already
knows how to declare a dependency UNMEASURED and simply does not guard this call. A declared SKIP
is a different fact from a traceback — `suite_outcome` models it, and the difference is whether a
reader goes to the code or to the environment.

### ⚑⚑ THREE MORE ARE THE READER AGAIN, AND ONE OF THEM IS PASSING 105 CHECKS

`scratch/mitigation-index/items.py` prints `105 check(s), 0 failure(s)` — which matches neither
`#row\t` nor the `N/M` prose regex, so it reads as `silent (0/0)` while asserting 105 things. That
is the SAME family as the `#row` separator bug fixed this turn: **a suite whose output shape no
reader knows is indistinguishable from one that says nothing.**

`mode_coverage` is the honest inverse — it deliberately reports *"no advertised mode read —
UNMEASURED, not clean"* and exits 0. Correct behaviour, unreadable verdict: a suite CORRECTLY
declaring it measured nothing renders identically to one that measured nothing by accident.

### ⚑ ONE IS A REAL CODE DEFECT

`scripts/run_selftests.py:724` — `ratchet.may_write(write)` against a `may_write()` taking zero
positional arguments. Signature drift: the callee changed and this call site did not. Unrelated
to tenancy, unrelated to the readers.

### ⚑ AND ONE HAS NO SUITE

`substrate/selftest_mk.py:54` — `sys.exit(main(sys.argv) if "--selftest" not in sys.argv else 0)`.
The flag exists ONLY so `suite_discovery` sees the module; it asserts nothing. That is precisely
the defect `suite_run`'s own docstring records catching in ITSELF on its first run, and the fix
it prescribes is delegation to a sibling suite rather than a bare `0`.

**So the honest verdict on ⟡silent-nine: 1 code defect, 1 missing suite, 3 reader gaps, 5
environment. NOT nine broken suites** — which is what the count alone said.

## The 9 `silent` — as first read (superseded by the census above)

A suite that runs and reports nothing. `make` would have marked every one of these DONE under a
bare `touch` stamp; the record-carrying stamp is what makes them visible.

`scratch/bibstruct.py` · `scratch/mitigation-index/items.py` · `scripts/ddl_lifecycle.py` ·
`scripts/run_selftests.py` · `substrate/mode_coverage.py` · `substrate/selftest_mk.py` ·
`jea/metalanguage/schema.py` · `jea/metalanguage/reconstruct.py` · `scripts/sppf_db.py` ·
`jea/metalanguage/catalog_db.py`

⚑ `bibstruct` is READ and is genuinely silent — it prints diagnostics and no record. It also
surfaces the SAME `consumer_fields` gap already repaired in `substrate/warrant_bib.py`: *"field
'enables' is not a paperkit field and was DROPPED"*. `warrant_bib` now passes the project's
declared consumer fields; `bibstruct` does not route through it. **One capability, two readers,
one of them repaired** — the shape this file keeps recording.

⚑ **NOT ESTABLISHED for the other eight:** whether each is silent because it has no cases, or
because its output is unreadable by some further reader defect. The `unread` three prove that
class exists and that it is invisible without opening the output. Each needs its log read
individually before any is called a suite defect.

## The 5 `cases` — genuine failures, counted

| suite | reported |
|---|---|
| `jea/metalanguage/sql_lift.py` | 30/33 |
| `scratch/split_pipeline.py` | 53/55 |
| `jea/metalanguage/query_registry.py` | **26/29** — the known Ⓝ24a-4, diagnosed below |
| `scripts/catalog_query.py` | 7/8 |

### Ⓝ24a-6 ⟡catalog-query-store — DIAGNOSED, deliberately NOT repaired here

`catalog_query` 7/8. The failing case is *"the relations this tool's commands name exist in the
store it connects to: got ['edges', 'in_degree', 'module_edges', 'structs'], want []"*.

⚑ **THE CASE IS CORRECT AND IS DOING EXACTLY ITS JOB.** It is a REACHABILITY check
(`catalog_query.py:368-384`) — it asserts the relations are PRESENT, never what they contain, so
it stays honest on an empty store and fails precisely when a reader has outlived its data. Its
own comment records this module having been read GREEN once before while every parameterised
query was broken. Do not weaken it.

⚑⚑ **AND `--relname structs` SHOWS THE MIGRATION CAUGHT MID-FLIGHT: TWO PARAMSTYLES IN ONE
FILE.** `:133` is `WHERE name LIKE ?` (sqlite) while `:156` and `:213` are `WHERE name = %s`
(postgres). So `_con()` was pointed at postgres — correctly, per its docstring about avoiding a
stale-store read — and the command bodies were only partly converted.

⚑ **WHY THIS IS NOT A ROSTER FIX.** The four relations are not merely missing from one tenant:
per ⟡sppf-rederived they are **re-derived from the SPPF rather than stored**, in EITHER postgres
tenant — `catalog/catalog.db` is the OLD sppf. So the repair is "re-express four commands against
the SPPF", which is sql-arc work with a real design question in it, not a roster item. **Filed
with its diagnosis rather than started**; the 7/8 stands as an honest red.

## What the roster itself says

`gen_selftest_mk.py --check` → **clean**. So ⟡suite-roster-stale's premise is measured FALSE as
of this run: the generated roster matches discovery. The staleness this item was opened for is
not present; what IS present is the four-way failure split above.

## Ⓝ24a-4 ⟡query-registry-cases — DIAGNOSED. All three failures are ENVIRONMENT, not the tool

    FAIL ...and it is a cardinality readout, not a 'not probed' excuse     (:739)
    FAIL edge.clid is reported as too big to probe, not estimated          (:743)
    FAIL ...to its own builder's derived table                             (:766)

⚑⚑⚑ **THE STORE IS EMPTY, AND THAT IS AN EXACT MEASUREMENT, NOT AN ESTIMATE.** `--index-report`
labels `obs_node.local_id` and `edge.clid` **`0-row table (index moot)`**. `--census` reads
`n_live_tup` estimates, which the tool itself warns "read 0 after a stats reset" — so the count
alone could not settle it. `--nullity` is the exact reader: **`edge is empty`**, **`obs_node is
empty`**. The registry is reporting a TRUE fact.

So cases `:739` and `:743` assert against a POPULATED store — a cardinality readout and a
"too big to probe" refusal both presuppose rows. Against an empty store the honest output is
exactly what the tool produces, and the cases are the things that are wrong.

⚑⚑ **AND THE THIRD IS A STALE WITNESS — THE SAME CLASS THE FILE ALREADY HANDLED ONCE.**
`n.kids` appears in NEITHER `--index-report` NOR `--candidates`: the column left the corpus when
the builders changed, so `_note.get("n.kids")` is empty and `"DERIVED table" in ""` is False. The
comment at `:730-736` records precisely this happening to `node_child.node_id` when
⟡index-coverage-wrong-store landed, and prescribes the repair: **re-pin the PROPERTY to a column
that still exhibits it, never re-pin the old witness** (which would assert a false positive).

⚑ **THE STORE MOVED OUT FROM UNDER THE PLAN'S FIGURES TOO.** `~/.claude/plans/…` records
`obs` 105,389,332 · `edge` 105,376,801 · `obs_node` 956,336. Live today: **2,477 rows total,
`obs`/`edge`/`event`/`obs_node` all exactly 0**, only `core_decoded` populated. Every figure in
that plan is now historical. **Not established:** whether this was a deliberate drain, the
⟡prune-incremental gate-as-corpus-writer incident recurring, or a restore — three causes, no
predicate here distinguishes them, and naming one would be the unestablished-cause error.

**NOT REPAIRED HERE, deliberately.** Two of the three cases need re-expressing so they state
their precondition (a populated store) and SKIP rather than FAIL when it does not hold — the
`declared SKIP` shape `suite_outcome` already models and `reconstruct.py` already uses one line
before it crashes. The third needs a live witness column. Both are edits to CASES, and making a
red case green while the underlying store question is unresolved is the wrong order.

## ⚑⚑ CORRECTION TO ⟡silent-nine's ENVIRONMENT DIAGNOSIS — IT IS A PORT, AND I HAD IT WRONG

I recorded the five sandbox failures as "the sandbox role is absent or unauthorised". **MEASURED
while diagnosing Ⓝ24a-4:** live connects on `{'host': '127.0.0.1', 'port': 30432, 'dbname':
'substrate'}` — **port 30432**. `sandbox_connect` (`store.py:492`) dials `PG_HOST` on the default
**5432**, which is what refuses.

⚑ So the two connect paths disagree about the PORT, and the sandbox's separate-role design —
which is sound and deliberate — is not what is failing. **A plausible cause fitted to a real
symptom, stated before the second reading that would have falsified it.** The refusal text
(`Connection refused` on 5432) was consistent with both stories; only reading the live DSN
separated them.

## Residue — carried, not resolved

* **⟡claim-label-identity** — `claim:*` labels collapse many suites onto one ledger row, so the
  autobudget cannot size any of them.
* **⟡retry-in-selftest-mk** — the roster does not set `MEMBUDGET_RETRY_OOM`, so a too-small
  default lease is fatal rather than self-correcting.
* **⟡silent-nine** — eight of the nine silent suites are unread-by-me; each needs its output
  opened before it is classified.
* **⟡bibstruct-consumer-fields** — the second reader of the warrant grammar still drops
  `enables`.
* **Ⓝ24a-4 ⟡query-registry-cases** — 26/29, unchanged.
