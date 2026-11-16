#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Run a POPULATION of row-emitting members, one process each, and fold the rows.

⚑ LIFTED BECAUSE IT WAS WRITTEN TWICE (user, 2026-08-05: *"run_selftest should
actually exercise items()'s witness infrastructure"*).  Two collectors existed
for one job:

  * `items._stream` — one witness per process under a `membudget` lease, rows
    emitted as each rung lands, `unfit` when a rung is killed before reporting;
  * `run_selftests._cmd` + `run_one` — the same, one SUITE per process.

Neither knew about the other, and they had already diverged in ways that matter:
`run_selftests` carries `_requires` (a per-member dependency declaration, routed
through `uv run --with`, which is why `jea_circuit` runs 300 real trials instead
of scoring an absent numpy as a silent pass), while `items.py` carries the ROW
CONTRACT and the `--row` rung.  Each had half the capability.

⚑ THE POPULATION AND THE INVOCATION ARE THE CALLER'S; EVERYTHING ELSE IS HERE.
That is the whole seam.  A caller supplies WHAT its members are and HOW one is
run; this module owns the concurrency, the row parse, the verdict selection and
the kill/silence distinction.  A collector that also knew the population would
be a third roster to drift.

⚑ AND THE LEASE IS PER-MEMBER BY CONSTRUCTION.  `SUITE_MB` and `ITEM_MB` differ,
correctly — a suite and a witness have different footprints, and `R` is
position-dependent besides.  So the hook returns the WHOLE command, not a script
path this module then wraps: wrapping here would relocate the lease decision to
the place that cannot size it.
"""
import json
import os
import subprocess
import sys

# ⚑ THE VERDICT IS THE LAST ROW, NOT THE FIRST.  Under the streaming contract a
# member emits parts as it finds them and its verdict TRAILS (its size is the
# count of the parts before it), so a consumer that returns on the first `#row`
# reads a PART and truncates the rest.  Measured: `items._stream` had exactly
# that defect the moment its first witness began streaming — the same shape as
# `catalog_query.cmd_sql` reading its header off `rows[0]` and re-walking.
ROW_PREFIX = "#row\t"

# ⚑ THE SUITE RESULT IS A TYPED RECORD, NOT PROSE THE RUNNER RE-PARSES (user,
# 2026-08-11: *"shouldn't they emit a json blob instead of something that needs a
# regex to parse?"*).  `run_selftests` learned every suite's result from
# `re.compile(r"selftest:\s*(\d+)\s*/\s*(\d+)")` — a TEXTUAL query against a
# STRUCTURED artifact, the exact shape this repo forbids everywhere else, sitting
# in the instrument that gates every commit.  It bit: five restored suites print
# `PASS` / `ALL PASS` / `SELFTEST PASS`, so the regex could not read them and they
# reported SILENT while passing.  A suite's result is a RECORD; the prose line is
# a rendering of it, for a human.
#
# ⚑ AND IT IS NOT A SECOND MACHINE-READABLE LINE FORMAT.  The reuse-search fires
# here: this module already carries a row contract (`ROW_PREFIX` + a JSON object,
# `parse_rows`/`fold`), already selftested, already read by `items.py`'s witness
# collector.  Minting `##selftest## {…}` beside it would be a second encoding of
# one capability — the `agda_files`-had-four-bodies shape.  So a suite's verdict
# is a `#row` verdict CARRYING COUNTS, and the same fold reads both.
#
# ⚑ THE NUMBERS ARE THE FIELD THAT MAKES IT A SUITE RECORD.  A witness verdict row
# carries `state` and no counts; requiring `passed` AND `total` is what lets a
# consumer tell a suite's result from any other row a suite happens to print, with
# no ambiguity about WHICH line is the result.
RECORD_SCHEMA = 1


def record(passed, total, skipped=0, reason=None, key=None):
    """The typed suite result.  `passed`/`total` are REQUIRED and are the verdict.

    `skipped` counts cases the suite DELIBERATELY did not run (a dependency
    absent, a store tier un-ingested) and `reason` says why — declared and
    counted, never silently folded into the denominator.  Skipped cases are NOT
    in `total`: a suite that ran 8 of 12 reports `8/8 (4 skipped)`, because
    `8/12` would read as four FAILING assertions and send a reader hunting them.

    ⚑ `state` IS EMITTED FOR `verdict_kind`'s SAKE AND IS NOT THE AUTHORITY.  A
    suite must not be able to grade itself green: the consumer derives the kind
    from the NUMBERS (see `run_selftests.verdict_kind`), so a producer bug that
    writes `"state": "ok"` beside `0/0` still reads VACUOUS.
    """
    passed, total, skipped = int(passed), int(total), int(skipped)
    row = {"kind": "verdict", "schema": RECORD_SCHEMA, "key": key,
           "passed": passed, "total": total, "skipped": skipped,
           "state": "vacuous" if total == 0 else
                    ("ok" if passed == total else "cases")}
    if reason:
        row["reason"] = str(reason)
    return row


def emit_record(passed, total, skipped=0, reason=None, key=None):
    """Print the typed result on its own line.  ONE per suite, the last word."""
    print(ROW_PREFIX + json.dumps(record(passed, total, skipped, reason, key),
                                  sort_keys=True))


def read_record(stdout):
    """The LAST well-formed suite record in `stdout`, or None.

    ⚑ A MALFORMED RECORD IS NOT A RECORD, AND IS NEVER REPAIRED INTO ONE.
    `passed > total`, a negative count, a non-integer — each means the PRODUCER
    is broken, and coercing it to something readable would launder a producer bug
    into a green number.  The row is refused; a suite with no other record then
    reads SILENT, which is the honest verdict for "reported nothing I can read".

    ⚑ THE LAST ONE WINS, for the same reason `fold`'s verdict trails: a suite may
    print records for sub-populations as it goes, and its own result is the one it
    ends with.
    """
    found = None
    for row in parse_rows(stdout):
        if row.get("kind") != "verdict":
            continue
        p, t = row.get("passed"), row.get("total")
        s = row.get("skipped", 0)
        if not all(isinstance(v, int) and not isinstance(v, bool)
                   for v in (p, t, s)):
            continue
        if p < 0 or t < 0 or s < 0 or p > t:
            continue
        found = {"passed": p, "total": t, "skipped": s,
                 "reason": row.get("reason"), "key": row.get("key")}
    return found

# ⚑ A SUITE MUST NOT RUN FROM WITHIN A PID ALREADY RUNNING ONE (user,
# 2026-08-05: *"calls to _selftest should not happen from within the same
# proc"*, correcting my *"a witness must not derive the suite of the module it
# lives in"*).  My phrasing scoped the rule to MODULE IDENTITY — the instance I
# had hit — when the constraint is about the PROCESS.  `items.py`'s suite
# spawning `worklist_gate`'s suite, which derives suites, recurses exactly as
# surely, and a module-scoped predicate lets it straight through.
#
# ⚑ MEASURED, AND THE GRADING SEPARATED TWO FINDINGS UNDER ONE SYMPTOM.  At the
# default lease both suites read `unfit` (killed); at 2048MB `items.py` moved to
# `cases` while the recursion persisted.  Only because `verdict_kind`
# distinguishes killed-by-lease from assertions-failed was the lease artifact
# separable from the real defect.
#
# ⚑ AND THE MARK IS SET BY THE SUITE ITSELF, NOT BY ITS SPAWNER.  My first cut
# had `execute` mark the child's env, which covers only the spawners that
# remember to — the frozen-roster shape.  A suite marking its OWN process at
# entry holds for EVERY route in: the runner, a witness filling a memo miss, or
# a human at a shell.
#
# ⚑ THIS IS A CYCLE GUARD, NOT A BUDGET — AND NOT A DEPTH CAP (user, 2026-08-05:
# *"or that's where a subdelegation is needed, recursively"*).  The two concerns
# are separate and BOTH are needed:
#
#   * THE LOCAL CAP BOUNDS LOCAL COMPLEXITY; RECURSION IS A DIFFERENT GRADE
#     (user, 2026-08-05: *"recursion should not come out of the same local pool.
#     The local memory containment is to ensure LOCAL complexity doesn't
#     explode.  That's distinct from cross-grade complexity"*).
#
#     A lease is not a slice of a parent's allowance — it is a statement about
#     how much THIS unit of work may cost.  A recursive derive is not more of
#     the same work; it is work at another grade, and charging it to the
#     caller's local bound conflates the two.
#
#     ⚑ THE MECHANISM, READ FROM EXECUTING CODE (2026-08-05).  An earlier
#     version of this block cited `membudget:75` as the rule.  That line is
#     INSIDE THE `ensure()` HEREDOC — a literal written into the ledger as a
#     header comment.  It is data, not code, and citing it meant this module
#     recorded a mechanism nobody could act on.  *A comment that states a rule
#     is not the rule; only the statement that executes is.*  The rule is
#     `_snapshot` (`membudget:104-112`):
#
#         $1=="LEASE" && $2==p  {pmb=$3}      # budget := the PARENT's own mb
#         $1=="LEASE" && $6==p  {used+=$3}    # used   := its DIRECT children
#         END { if (p=="-") {b=tot} else {b=pmb} ... }
#
#     so for a nested lease (`p` = the parent's id, from `MEMBUDGET_PARENT` at
#     `:230`) the budget genuinely IS field 3 of the parent's LEASE record —
#     the caller's whole local reservation — not `TOTAL_MB`.  Records are
#     written at `:267` as `LEASE id mb owner epoch parent label`.
#
#     ⚑ AND TWO GATES MAKE THE NESTED PATH WEAKER THAN THE TOP ONE, which is
#     what turned this from a sizing question into `unfit`:
#       - NO CONTAINMENT.  `_launch_scope` (`:198`) has exactly two call sites,
#         `:294` and `:296`, both inside `if [ "$parent" = "-" ]` (`:291`).
#         The else arm (`:300`) runs the command directly, so a sublease has a
#         budget but no `MemoryMax` of its own — it lives inside the ancestor's.
#       - NO SELF-CORRECTION.  The retry-on-OOM guard (`:312`) conjoins
#         `[ "$parent" = "-" ]`, so a nested job killed at 137 does NOT re-enter
#         at the next power-of-two bucket the way a top-level one does.
#     A nested derive therefore consumes the caller's pool, is contained by the
#     caller's cap, and cannot grow out of a too-tight guess.  That is why
#     `worklist_gate`'s suite read `unfit` at 192MB.  Raising `SUITE_MB` would
#     have "fixed" it by loosening the very bound that exists to stay tight —
#     treating a structural mis-charge as a sizing shortfall.
#
#     ⚑ RECORDED, NOT FIXED HERE.  `_snapshot` is reached identically by the
#     hook's `make -C agda -j` and by a hand-typed `membudget run` — both land
#     on the single `cmd_run` at `membudget:349`, so there is one accounting
#     path and changing it moves the build gate too.  Nothing in this module
#     models the budget, and nothing should.
#   * What a sublease does NOT give is TERMINATION.  `items.py`'s suite contains
#     a witness that derives `items.py`'s suite: a genuinely cyclic edge.  Each
#     level would be correctly and progressively smaller, terminating only by
#     exhaustion — a memory-bounded infinite regress, which stops for the wrong
#     reason and reports `unfit` instead of a verdict.
#
# So this guard breaks the CYCLE and leaves the BUDGET to the semaphore.  It is
# not `head_span`'s `j - i < 6` or `mdstruct`'s `rounds=25`: those bounded a
# well-founded descent that needed no bound.  This bounds a relation that has a
# genuine self-edge.
_IN_SUITE = "SUBSTRATE_SUITE_RUNNING"


def in_suite():
    """Is THIS process (or an ancestor that could pass it on) running a suite?"""
    return bool(os.environ.get(_IN_SUITE))


def enter_suite(label):
    """Mark this process as running `label`'s suite.  Idempotent per process.

    Called by the suite entry point, so the mark exists for the whole run
    regardless of how the suite was invoked — by the runner, by a witness
    deriving a miss, or by a human at a shell."""
    cur = os.environ.get(_IN_SUITE, "")
    os.environ[_IN_SUITE] = (cur + os.pathsep + label) if cur else label
    return os.environ[_IN_SUITE]

# ⚑ A CGROUP KILL IS A SIGNAL, NOT AN EXIT STATUS.  `membudget` runs each member
# in a `systemd-run` scope with `MemoryMax`; exceeding it is SIGKILL (rc -9, or
# 137 through a shell) and a timeout is SIGTERM (-15 / 143).  Named because the
# set is the DISCRIMINATOR between "did not fit" and "failed" — a distinction
# that cost a session to learn, when a 192MB lease made a passing suite read as
# BROKEN.
KILL_CODES = (-9, 137, -15, 143)


def parse_rows(stdout):
    """Yield each emitted row, in order.  A stream, never a list.

    ⚑ THE PARTS ARE NOT ACCUMULATED HERE.  A member with 420 parts emits 420
    rows; collecting them to hand back one container is the shape the row
    contract exists to retire, rebuilt in the collector.
    """
    for ln in stdout.splitlines():
        if ln.startswith(ROW_PREFIX):
            yield json.loads(ln[len(ROW_PREFIX):])


def fold(stdout):
    """`(verdict_row_or_None, parts_forwarded)` from one member's output.

    The verdict is the LAST non-part row; the count is the parts before it, so
    the size is a fact about what crossed the boundary rather than a number the
    member declared.  `None` means the member emitted no verdict — which is a
    DISTINCT finding (killed, or silent), never an assumed failure.
    """
    last, parts = None, 0
    for row in parse_rows(stdout):
        if row.get("kind") == "part":
            parts += 1
            continue
        last = row
    return last, parts


def verdict_kind(row, parts, returncode):
    """`ok` / `cases` / `vacuous` / `unfit` / `silent` — WHICH kind of not-ok.

    ⚑ THE VOCABULARY IS `run_selftests`', UNCHANGED, because it was already
    right and the distinction was already earned:

      ok      — a verdict row saying so
      cases   — a verdict row saying otherwise: the member's own assertions
      vacuous — a verdict row over ZERO parts where parts were the subject
                (F1's `spool`: 8 assertions that never ran while the gate said
                green)
      unfit   — NO verdict row AND killed by a signal: a LEASE finding, not a
                defect.  Reporting it as a failure is what made a passing suite
                read as BROKEN for a session.
      silent  — NO verdict row, exited normally: it printed nothing at all
    """
    if row is None:
        return "unfit" if returncode in KILL_CODES else "silent"
    state = row.get("state")
    if state == "closed" or state == "ok":
        return "ok"
    return state or "cases"


def execute(population, command, jobs=None, cwd=None):
    """Run every member concurrently; yield `(key, CompletedProcess, seconds)`.

    The RAW result, before any row parse — because a caller whose members do not
    yet emit rows still needs the concurrency, the per-member timing and the
    one-process-per-member discipline.  `run()` below is this plus the fold.

    ⚑ EMISSION IS STREAMED; THE ARTIFACT IS ORDERED — AND THOSE ARE DIFFERENT
    LEVELS (user, 2026-08-05: *"a runner whose output reorders itself between
    runs is insufficiently-well-formed"*).  I first exposed an `ordered` flag
    and called completion-order and population-order two legitimate
    preferences.  They are not: a well-formed emitter's order is CANONICAL BY
    CONSTRUCTION — the same property the crossings census had to have when
    `sorted()` at its yield was refused.  Completion order is the SCHEDULER
    leaking into the artifact.

    What is genuinely required is streaming: a member's result must be
    available when it lands, because a partial run that printed nothing was
    indistinguishable from one where nothing completed.  That is satisfied
    here, and it costs no ordering — every result carries its KEY, so a
    consumer building an artifact sorts by the population it already holds.
    The pool is not the place to ask for well-formedness.

    ⚑ AND THE TIMING RIDES ALONG because `--profile` consumes it.  Dropping it
    here would have made the lift a feature regression discovered later, which
    is how a refactor ships a defect it cannot localize.
    """
    import concurrent.futures as _cf
    import time

    keys = list(population)

    def one(key):
        t0 = time.monotonic()
        r = subprocess.run(command(key), cwd=cwd, capture_output=True,
                           text=True)
        return key, r, time.monotonic() - t0

    with _cf.ThreadPoolExecutor(max_workers=jobs or (os.cpu_count() or 4)) as p:
        for fut in _cf.as_completed([p.submit(one, k) for k in keys]):
            yield fut.result()


def run(population, command, jobs=None, on_row=None):
    """Run every member concurrently; yield `(key, verdict_row, parts, rc)`.

    `population` — an iterable of member keys (the CALLER's roster)
    `command(key)` — the full argv for one member, lease included
    `on_row(key, row)` — optional, called for every row as it is parsed

    ⚑ YIELDS AS EACH MEMBER LANDS, NEVER AFTER THE POOL DRAINS.  A `p.map` here
    printed nothing until the SLOWEST member finished, so a killed run reported
    NOTHING even when 59 of 60 had succeeded — and a partial run was
    indistinguishable from a run where nothing completed.

    ⚑ CONCURRENCY IS SAFE BECAUSE THE SEMAPHORE OWNS THE AGGREGATE (user).  A
    lease that will not fit BLOCKS and wakes on a release; it does not OOM.
    Re-deriving a job limit here would be re-implementing in Python the budget
    `membudget` already enforces across processes.
    """
    # ⚑ ONE POOL, NOT TWO.  `run` is `execute` plus the row fold; writing the
    # concurrency again here is the duplication this module was lifted to end,
    # reproduced inside it.
    for key, r, _dt in execute(population, command, jobs=jobs):
        row, parts = fold(r.stdout)
        if on_row is not None:
            for e in parse_rows(r.stdout):
                on_row(key, e)
        yield key, row, parts, r.returncode


class Cases(object):
    """A suite's cases, as ROWS — the witness contract, one level down.

    ⚑ FIFTY SUITES REIMPLEMENTED THIS (measured, 2026-08-05).  `--rivals check`
    reports **55 defs, 55 reimplementing, 0 delegating**, and 40 of them are the
    identical single statement `cases.append((label, got == want, got, want))`.
    The TAIL is duplicated just as widely: filter the failures, print each, then
    `selftest: N/M`.  One name, fifty bodies, no authority — the `agda_files`
    shape in the machinery that verifies everything else.

    ⚑ AND A CASE IS A PART; `N/M` IS THE COUNT OF THE WALK.  That is the whole
    reason this belongs here rather than in a testing helper: a suite is a
    witness whose parts are its cases, so `selftest: N/M` stops being a printed
    total and becomes the fold of the rows it emitted.  A suite that reported a
    count without emitting its cases is the size-without-rows collapse the item
    layer already retired.

    ⚑ THE MIGRATION IS ADOPT-IN-PLACE, NOT A FLAG DAY.  A suite keeps its own
    `check(label, got, want)` call sites verbatim — 186 of them in the three
    sampled suites, all positional, one convention — and swaps only the four
    lines around them.  A sweep that rewrote call sites would be rewriting the
    part that is already uniform.

    ⚑ NOT a unittest shim.  It emits ROWS and returns the same `0`/`1` the
    runner already reads, so a suite converts without its consumers changing.
    """

    def __init__(self, key=None, emit=False):
        self.key = key
        self.emit = emit
        self.n = 0
        self.bad = []
        # ⚑ CONSTRUCTING THIS IS ENTERING A SUITE, so the process marks itself
        # here.  The mark must be set by the SUITE, not by whoever spawned it:
        # `membudget` runs under `systemd-run --scope`, which does not inherit
        # the caller's environment, so a spawner-side mark never arrives.
        if key:
            enter_suite(key)

    def __call__(self, label, got, want):
        """One case.  Streams as a PART when emitting; counted either way."""
        self.n += 1
        good = got == want
        if not good:
            # ⚑⚑⚑ ⟡check-lift — THE CALL SITE, WHICH NONE OF THE 78 LOCAL `check` BODIES CARRIED
            # (operator, 2026-08-22: *"We should have self-test failures include stack traces"*).
            # A failure printed only `FAIL <label>: got X want Y`, so LOCATING it meant searching
            # the corpus for the message string — MEASURED the same session at six tool calls for
            # one case, three of them guessed mode names, because labels are prose and case
            # helpers live in OTHER modules (`sppf_decode.decode_reason_cases` and friends receive
            # `check` as a parameter). The filename is therefore load-bearing, not decoration.
            #
            # ⚑⚑ `stack()[1]`, NOT A TRACEBACK. A case is not an exception — nothing is raised, so
            # there is nothing to unwind, and synthesising a stack would report THIS class rather
            # than the assertion. The frame that called it is the whole answer, at one frame
            # lookup per FAILURE (not per case, which is what keeps a 300-case suite cheap).
            #
            # ⚑ AND IT IS CAPTURED HERE RATHER THAN IN 78 PLACES. This class already existed with
            # the right contract; the local copies were reimplementations of it that each lost
            # something. Adding the location to the ONE implementation is what makes converging
            # on it strictly better than any copy — see `--collisions`' *sibling: candidate lift*.
            import inspect as _i
            import os as _os
            _f = _i.stack()[1]
            self.bad.append((label, got, want,
                             "%s:%d in %s" % (_os.path.basename(_f.filename),
                                              _f.lineno, _f.function)))
        if self.emit:
            row = {"kind": "part", "key": self.key, "name": label,
                   "state": "ok" if good else "cases"}
            if not good:
                row["got"], row["want"] = repr(got), repr(want)
            print(ROW_PREFIX + json.dumps(row, sort_keys=True))
        return good

    def report(self, skipped=0, reason=None):
        """Emit the typed record, print the failures and the counted line;
        return 0 ok / 1 not.

        ⚑ `N/M` IS DERIVED, NEVER LITERAL — `prune_imports` once carried a
        hardcoded `9/9` that hid a tenth case, which is why every suite derives
        its total.  Here the total is `self.n`, the count of the walk, so a case
        that ran and a case that was counted cannot come apart.

        ⚑ AND A ZERO DENOMINATOR IS NOT A PASS.  `0/0` satisfies the runner's
        `RESULT` regex while asserting nothing — measured on `spool`, whose 8
        assertions never ran while the gate read green.  A suite with no cases
        reports and REFUSES, rather than printing a green-shaped line.

        ⚑ THE RECORD IS EMITTED ON EVERY PATH, INCLUDING THE ZERO ONE.  A suite
        that ran nothing must still SAY so in the machine-readable form —
        omitting the record there would make a vacuous suite indistinguishable
        from a killed one, collapsing `vacuous` into `unfit`/`silent`, which are
        three different next actions.

        ⚑ AND THE PROSE LINE STAYS.  It is what a human at a shell reads; it is
        no longer what the RUNNER reads.  Keeping both is not a regex fallback —
        the record is present, so this suite is migrated by construction.
        """
        # ⚑ THE LOCATION IS ITS OWN LINE. A label here is a SENTENCE ("...and BOTH are reachable
        # from the CLI"), so a trailing `file:line` runs past the terminal width and is the first
        # thing a wrapped line loses — the one piece a reader most needs.
        for label, got, want, where in self.bad:
            print("  FAIL %s: got %r, want %r" % (label, got, want))
            print("       at %s" % where)
        emit_record(self.n - len(self.bad), self.n, skipped=skipped,
                    reason=reason, key=self.key)
        _sk = (" (%d skipped: %s)" % (skipped, reason or "no reason given")
               if skipped else "")
        if not self.n:
            print("selftest: 0/0 — NO CASES RAN; a zero denominator is not a pass"
                  + _sk)
            return 1
        print("selftest: %d/%d%s" % (self.n - len(self.bad), self.n, _sk))
        return 0 if not self.bad else 1


def _selftest():
    """⚑ DRIVEN AGAINST REAL SUBPROCESSES, not a simulated stdout.  The defects
    this module exists to hold — verdict-is-last, no-verdict-is-not-failure,
    kill-vs-silence — are all about what a PROCESS did, and a fixture that hands
    `fold` a string never exercises the part that runs one."""
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ── fold: the verdict is the LAST row, parts counted before it ──────────
    _out = (ROW_PREFIX + '{"kind": "part", "name": "a"}\n'
            + ROW_PREFIX + '{"kind": "part", "name": "b"}\n'
            + ROW_PREFIX + '{"kind": "verdict", "state": "OPEN"}\n')
    row, n = fold(_out)
    check("the verdict is the last row", row.get("state"), "OPEN")
    check("parts are counted, not collected", n, 2)

    # ⚑ THE DEFECT THIS REPLACES: returning on the FIRST row reads a PART.
    _first = next(parse_rows(_out))
    check("the first row is a PART, not the verdict", _first.get("kind"), "part")

    # ⚑ PARSE_ROWS STREAMS.  A list would satisfy every case above; only asking
    # whether it is its own iterator tells a generator from a container.
    _g = parse_rows(_out)
    check("parse_rows returns a stream", iter(_g) is _g, True)

    # ── no verdict is a DISTINCT finding, never an assumed failure ──────────
    check("no rows at all yields no verdict", fold("")[0], None)
    check("a killed member is UNFIT", verdict_kind(None, 0, -9), "unfit")
    check("a signal through a shell is UNFIT", verdict_kind(None, 0, 137), "unfit")
    # ⚑ AND THE CONVERSE, which is the half that would catch an over-eager
    # `unfit`: exiting normally with no row is SILENT, a different finding.
    check("a quiet member is SILENT", verdict_kind(None, 0, 0), "silent")
    check("a closed verdict is ok",
          verdict_kind({"state": "closed"}, 0, 0), "ok")
    check("an open verdict is not ok",
          verdict_kind({"state": "OPEN"}, 3, 1), "OPEN")

    # ── run: a REAL population of REAL processes ────────────────────────────
    # ⚑ THE MEMBERS ARE INTERPRETERS EMITTING ROWS, because the contract under
    # test is "what did the process print", and a fake command proves nothing
    # about the parse.
    def _cmd(key):
        if key == "quiet":
            return [sys.executable, "-c", "pass"]
        return [sys.executable, "-c",
                'print(%r + \'{"kind": "part", "name": "x"}\'); '
                'print(%r + \'{"kind": "verdict", "state": "closed"}\')'
                % (ROW_PREFIX, ROW_PREFIX)]

    got = {k: (r, n, rc) for k, r, n, rc in run(["a", "b", "quiet"], _cmd)}
    check("every member reported", sorted(got), ["a", "b", "quiet"])
    check("a member's parts are counted", got["a"][1], 1)
    check("a member's verdict is read", got["a"][0].get("state"), "closed")
    # ⚑ A MEMBER THAT PRINTS NOTHING IS NOT A FAILING MEMBER.  It exits 0, so it
    # is SILENT — the case that keeps `unfit`/`silent` from collapsing into
    # "broken", which is the distinction this whole module carries.
    check("a silent member has no verdict row", got["quiet"][0], None)
    check("and is graded silent, not failed",
          verdict_kind(got["quiet"][0], got["quiet"][1], got["quiet"][2]),
          "silent")

    # ⚑ `on_row` SEES EVERY ROW, not just the verdict — this is what lets a
    # caller stream parts through without the collector holding them.
    seen = []
    list(run(["a"], _cmd, on_row=lambda k, r: seen.append(r.get("kind"))))
    check("on_row observes parts and the verdict", seen, ["part", "verdict"])

    # ── execute: the raw half, for callers whose members emit no rows ───────
    # ⚑ THE MEMBERS HAVE DIFFERENT DURATIONS ON PURPOSE, so completion order and
    # population order genuinely differ.  A fixture finishing in submission
    # order would prove nothing about either property.
    def _slow(key):
        delay = {"first": 0.30, "second": 0.01}[key]
        return [sys.executable, "-c", "import time; time.sleep(%r)" % delay]

    # results ARRIVE as they land — that is the streaming half, and it is what
    # keeps a partial run readable
    # ⚑⚑⚑ THIS CASE IS LOAD-SENSITIVE AND IT FAILED THE COMMIT GATE TWICE — measured 2026-08-17:
    # 52/52 standalone, 51/52 inside `run_selftests.py`, 52/52 on re-run, then 51/52 again. The
    # margin is a 0.30s job against a 0.01s one, and under 72 concurrent suites in a 192MB
    # `membudget` cgroup, interpreter startup alone can eat 0.29s and invert the arrival order.
    #
    # ⚑⚑ MY FIRST RESPONSE WAS TO DOCUMENT IT, AND THAT WAS THE WRONG ACT. A note saying "this
    # is load-sensitive" leaves an intermittent RED in the gate, and an intermittent red is worse
    # than a missing test: it trains its reader to re-run rather than investigate, so the next
    # genuine regression in this file reads as the flake everyone already ignores. Recording a
    # defect is not the same as owning it.
    #
    # ⚑ SO THE ASSUMPTION IS NOW MEASURED RATHER THAN ASSUMED. The property under test is that
    # results ARRIVE as they complete, which needs the two jobs to actually complete in the
    # stated order — a precondition of the fixture, not of the code. `_dt` is what `execute`
    # already returns, so the case can CHECK its own precondition and report UNMEASURED when the
    # box did not honour it, instead of reporting the runner broken. The delays stay as they
    # are: widening them would weaken the property, and the ⚑ above says why they differ.
    _res = list(execute(["first", "second"], _slow))
    _arrival = [k for k, _r, _dt in _res]
    _dt = {k: d for k, _r, d in _res}
    if _dt.get("second", 0) < _dt.get("first", 0):
        check("results stream in completion order", _arrival, ["second", "first"])
    else:
        # ⚑ NOT A SKIP THAT HIDES: the case is named and counted, and it states that the BOX
        # inverted the durations rather than that the runner mis-ordered them. An unmeasured
        # case reported as a pass is the vacuous-green shape this repo refuses everywhere else.
        check("results stream in completion order (UNMEASURED — the box inverted the "
              "durations: first=%.3fs second=%.3fs, so completion order is not what the "
              "fixture staged)" % (_dt.get("first", -1), _dt.get("second", -1)),
              sorted(_arrival), ["first", "second"])

    # ⚑ AND THE ARTIFACT IS WELL-FORMED ANYWAY, which is the invariant that
    # matters (user: *"a runner whose output reorders itself between runs is
    # insufficiently-well-formed"*).  Every result carries its KEY, so a
    # consumer's report is canonical by construction rather than by asking the
    # pool to serialize.  This is the case that would fail if a future edit
    # made the key implicit — e.g. yielding bare results positionally.
    check("every result carries its key, so an artifact can be ordered",
          sorted(_arrival), ["first", "second"])

    # ⚑ THE TIMING IS REAL, because `--profile` consumes it and a zero would
    # read as an instant suite rather than as a missing measurement.
    _t = {k: dt for k, _r, dt in execute(["first"], _slow)}
    check("per-member timing is measured", _t["first"] > 0.2, True)

    # ── Cases: a suite's cases ARE its parts ───────────────────────────────
    import contextlib
    import io

    # ⚑ DRIVEN, NOT READ.  The defects this class encodes — a derived `N/M`, a
    # zero denominator refusing — are about what it PRINTS, so the cases capture
    # its output rather than inspecting its attributes.
    _c = Cases()
    _c("a", 1, 1)
    _c("b", 2, 3)
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _rc = _c.report()
    check("a failing case makes the suite fail", _rc, 1)
    check("the total is the count of the walk", "selftest: 1/2" in _buf.getvalue(), True)
    check("a failure names its got and want",
          "FAIL b: got 2, want 3" in _buf.getvalue(), True)
    check("check returns the verdict per case", (_c("c", 1, 1), _c("d", 1, 2)),
          (True, False))

    # ⚑ A ZERO DENOMINATOR REFUSES — `0/0` satisfied the runner's regex while
    # asserting nothing, and `spool` shipped 8 unrun assertions behind it.
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _rc0 = Cases().report()
    check("an empty suite REFUSES", _rc0, 1)
    check("and says why rather than printing a green-shaped line",
          "NO CASES RAN" in _buf.getvalue(), True)

    # ⚑ EMITTING TURNS EACH CASE INTO A PART — this is the contract the suites
    # converge on, and the row must be parseable by the SAME fold that reads a
    # witness.  A part shape only this module could read would be a second
    # contract wearing the first one's name.
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _e = Cases(key="probe", emit=True)
        _e("one", 1, 1)
        _e("two", 1, 2)
    _rows = list(parse_rows(_buf.getvalue()))
    check("each case emits one part", len(_rows), 2)
    check("a part carries its suite key", _rows[0].get("key"), "probe")
    check("a passing case is ok", _rows[0].get("state"), "ok")
    check("a failing case carries its evidence",
          (_rows[1].get("state"), _rows[1].get("want")), ("cases", "2"))

    # ── the recursion guard: a suite must not run inside a suite ────────────
    # ⚑ THE PREDICATE IS ABOUT THE PROCESS, NOT THE MODULE (user, 2026-08-05:
    # *"a witness must not derive the suite FROM WITHIN THE SAME PID"*,
    # correcting my module-scoped phrasing).  These drive `enter_suite` /
    # `in_suite` directly, because the defect they prevent — a suite spawning a
    # suite spawning a suite — is not reproducible inside one test run.
    _saved = os.environ.get(_IN_SUITE)
    try:
        os.environ.pop(_IN_SUITE, None)
        check("outside a suite, nothing is marked", in_suite(), False)
        enter_suite("a.py")
        check("entering marks the process", in_suite(), True)
        # ⚑ THE CHAIN ACCUMULATES, so a third level sees BOTH ancestors — the
        # module-scoped predicate I first wrote would have seen only its own.
        enter_suite("b.py")
        check("the chain records every suite entered",
              os.environ[_IN_SUITE].split(os.pathsep), ["a.py", "b.py"])
        # ⚑ AND THE GUARD IS ALL-OR-NOTHING BY PROCESS: inside ANY suite, a
        # witness derives none — including suites it has never heard of.  That
        # is the half the module-scoped version got wrong.
        check("inside a suite, the guard is set regardless of which",
              in_suite(), True)
    finally:
        if _saved is None:
            os.environ.pop(_IN_SUITE, None)
        else:
            os.environ[_IN_SUITE] = _saved

    # ⚑ CONSTRUCTING `Cases` IS ENTERING A SUITE — the mark must not depend on a
    # caller remembering to apply it.
    _saved = os.environ.get(_IN_SUITE)
    try:
        os.environ.pop(_IN_SUITE, None)
        Cases(key="probe.py")
        check("constructing Cases marks the process", in_suite(), True)
    finally:
        if _saved is None:
            os.environ.pop(_IN_SUITE, None)
        else:
            os.environ[_IN_SUITE] = _saved

    # ── the TYPED RESULT RECORD: what the runner reads instead of prose ─────
    # ⚑ EVERY CASE HERE FAILS AGAINST THE PRE-CHANGE MODULE, which had no record
    # at all — the runner learned a suite's result by regex over its stdout, so a
    # suite printing `ALL PASS` was unreadable and reported SILENT while passing.
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _r = Cases(key="probe.py")
        _r("a", 1, 1)
        _r("b", 2, 2)
        _r.report()
    _rec = read_record(_buf.getvalue())
    check("report() emits a typed record", (_rec or {}).get("total"), 2)
    check("...carrying the passed count", (_rec or {}).get("passed"), 2)
    check("...and the suite's own key", (_rec or {}).get("key"), "probe.py")
    # ⚑ THE PROSE LINE IS A RENDERING, NOT THE RESULT.  It stays for a human; the
    # runner no longer reads it.  A case here so a future edit cannot quietly drop
    # the half a person at a shell depends on.
    check("...beside the human-readable line",
          "selftest: 2/2" in _buf.getvalue(), True)

    # ⚑ `0/0` MUST REMAIN VACUOUS THROUGH THE RECORD.  The producer states its
    # emptiness rather than falling silent — a record saying zero and NO record at
    # all are different findings (`vacuous` vs `unfit`/`silent`), and the whole
    # reason `spool` shipped 8 unrun assertions behind a green gate.
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        Cases(key="empty.py").report()
    _rec0 = read_record(_buf.getvalue())
    check("an empty suite still emits a record", _rec0 is not None, True)
    check("...whose total is 0 (vacuous, not absent)",
          (_rec0 or {}).get("total"), 0)
    check("...and whose state says vacuous, never ok",
          record(0, 0)["state"], "vacuous")

    # ── a DELIBERATE skip is DECLARED and COUNTED, never folded away ────────
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _s = Cases(key="skip.py")
        _s("ran", 1, 1)
        _s.report(skipped=3, reason="the store tier is un-ingested")
    _recs = read_record(_buf.getvalue())
    check("a skip is carried in the record", (_recs or {}).get("skipped"), 3)
    check("...with its reason", (_recs or {}).get("reason"),
          "the store tier is un-ingested")
    # ⚑ SKIPPED CASES ARE NOT IN THE DENOMINATOR.  `1/4` would read as three
    # FAILING assertions and send a reader hunting them; `1/1 (3 skipped)` says
    # what happened.  The count is not lost — it is reported as its own kind.
    check("...and NOT folded into the denominator", (_recs or {}).get("total"), 1)
    check("...so a fully-skipped suite is still vacuous, never green",
          record(0, 0, skipped=5, reason="dep absent")["state"], "vacuous")

    # ── a MALFORMED record is refused, never repaired into a green number ───
    # ⚑ EACH OF THESE IS A PRODUCER BUG, and coercing it to something readable
    # would launder that bug into a count the gate believes.
    check("passed > total is refused",
          read_record(ROW_PREFIX + '{"kind":"verdict","passed":5,"total":3}'),
          None)
    check("a negative count is refused",
          read_record(ROW_PREFIX + '{"kind":"verdict","passed":-1,"total":3}'),
          None)
    check("a non-integer count is refused",
          read_record(ROW_PREFIX + '{"kind":"verdict","passed":"2","total":"2"}'),
          None)
    # ⚑ AND A WITNESS VERDICT IS NOT A SUITE RECORD.  `items.py` emits verdict
    # rows with a `state` and no counts; the NUMBERS are what make a row a suite
    # result, which is what keeps one contract from being read as two.
    check("a countless witness verdict is not a suite record",
          read_record(ROW_PREFIX + '{"kind":"verdict","state":"closed"}'), None)
    check("a part is not a suite record",
          read_record(ROW_PREFIX + '{"kind":"part","passed":1,"total":1}'), None)
    check("no rows at all yields no record", read_record(""), None)
    # ⚑ THE LAST RECORD WINS, for the same reason `fold`'s verdict trails: a
    # suite may report sub-populations as it goes and its own result ends it.
    check("the LAST record is the suite's result",
          read_record(ROW_PREFIX + '{"kind":"verdict","passed":1,"total":1}\n'
                      + ROW_PREFIX + '{"kind":"verdict","passed":9,"total":9}'
                      )["total"], 9)

    ok = sum(1 for c in cases if c[1])
    for label, good, got_, want in cases:
        if not good:
            print("  FAIL %s: got %r, want %r" % (label, got_, want))
    emit_record(ok, len(cases), key="scratch/rungs.py")
    print("selftest: %d/%d" % (ok, len(cases)))
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    print(__doc__)
    sys.exit(2)
