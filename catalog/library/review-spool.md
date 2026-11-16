# External review — `scratch/spool.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured. Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24).

---

This is a highly defensive, incredibly well-reasoned piece of infrastructure. The architectural clarity—specifically the explicit documentation of *why* choices were made, rather than just *what* the code does—makes this exceptional.

Here is a breakdown of thoughts on the design, alongside a few structural concerns to address before this hits production.

## The Good: Architectural Strengths

* **Daemon-Free by Design:** You correctly identified that requiring a high-availability broker to protect against a store outage is a false economy. Piggybacking on SQLite via `persist-queue` to handle state is exactly the right structural correspondence for a client-arbitrated system.
* **Decoupled Delivery (`deliver` callback):** Passing the delivery mechanism as a parameter to `drain` is excellent. The queue remains completely agnostic to OTLP, Cassian, or the shape of the data.
* **Graceful Degradation:** The fact that `_queue()` returns `None` when the library is missing, and the rest of the module handles that `None` silently, perfectly honors the rule that telemetry is an observation, not a load-bearing pillar of the suite run.
* **Drop-Oldest Strategy:** For monitoring and TSDBs, recency is paramount. Purging the oldest records when hitting `MAX_DEPTH` guarantees the system recovers from a long outage with the most immediately actionable data.

---

## The Concerns: Edge Cases and Potential Traps

### 1. `enqueue` Can Still Crash the Suite Run

You explicitly stated: *"A suite must not fail because a buffer is unavailable."*
While you catch exceptions during the drop-oldest phase, the actual enqueueing is unprotected:

```python
    while q.size >= MAX_DEPTH:
        # ... try/except catches exceptions here
    q.put(sample) # <-- UNPROTECTED
```

Under concurrent load, SQLite can raise `sqlite3.OperationalError: database is locked`. If that bubbles up from `q.put()`, it will crash the suite run. **Wrap `q.put()` in a broad `try/except` block** to guarantee telemetry failures never poison the producer.

### 2. Multi-User Permission Conflicts

Because `SPOOL_DIR` is relative to the codebase (`ROOT/.spool`), you may encounter permission errors in a shared environment.
If User A runs the suite, the `.spool` directory and the SQLite files are created under User A's ownership. If User B later runs a suite from the same checkout, `SQLiteAckQueue` will likely throw a `PermissionError` when trying to open or lock the database, breaking the script.

* **Mitigation:** If this runs in a shared environment, consider placing the spool in a user-specific path (e.g., `~/.cache/your_tool/spool`) or strictly wrapping the initialization and queue operations to swallow `PermissionError`.

### 3. Infinite Blocking in `deliver`

Because `drain` iterates through the queue and synchronously calls `deliver(item)`, the resilience of this script entirely depends on the `deliver` callback honoring strict timeouts. If `deliver` hangs on a dead socket without timing out, the entire `drain` process (and thus the suite run) hangs. The module correctly separates concerns, but the caller must be ruthless about network timeouts.

### 4. Too Silent on Missing Dependencies?

While graceful degradation is good, a silently missing `persist-queue` means telemetry could be dropped for months without anyone noticing. You might want to emit a single, non-fatal `logging.warning()` when `_queue()` catches the `ImportError`, ensuring the degradation is at least visible in the suite's execution logs.

---

## Reading, for the unification planning

### ⚑ CONCERN 1 IS THE FILE'S OWN STATED RULE, VIOLATED ONE LINE BELOW WHERE IT IS GUARDED

The docstring says *"a suite must not fail because a buffer is unavailable."* The
drop-oldest loop is wrapped; `q.put(sample)` — the operation the rule is ABOUT — is
not. If it holds, this is the **guard-from-the-instance** class in its purest form
(§7b-bis, three occurrences in one day, all mine): *a guard written from the instance
passes on everything except the instance.* I wrapped the branch I was thinking about
and left the primary path bare.

⚑ **AND IT IS ALSO THE INERT-GUARD CLASS `--discards` EXISTS TO FIND** — a protection
that is present, greppable, and not covering the operation it names. Worth checking
whether `pycodemod --discards` or `--discriminates` can SEE this shape; if not, that
absence is itself a finding, because this is precisely the defect those modes are for.

`sqlite3.OperationalError: database is locked` is a real concurrent-writer failure and
`make -j` is this repo's normal invocation — so the trigger condition is the standard
build path, not an exotic one.

### Concern 2 is a SCOPE decision the dispatcher must make, not a spool defect

`SPOOL_DIR = ROOT/.spool` is *"state stored beside the code."* The reviewer's
multi-user case may not bind here (single-user box), but the same choice binds a
question the unification MUST answer: **where does per-tool state live?**

Live instances of the identical decision, all currently ad-hoc:
  * `agda/.leaf-verify.tsv` — census ledger beside the corpus
  * `DISCARD_LEDGER` — beside the tool
  * `scratch/.edit-snapshots/` — beside the tool, and it ALREADY caused a defect:
    the rederivation ratchet began censusing it, because byte copies of censused
    sources sat inside the censused tree (§7g)
  * `.spool/` — beside the code

**A dispatcher that supplies a state directory retires the whole class**, including
the §7g self-census hazard: state that lives outside the corpus cannot be enumerated
as part of it. That is a predicate, not an exclusion list, which is the form this repo
prefers. ⚑ *Recorded as a design input, NOT as a filed defect — no multi-user failure
has been observed here.*

### Concern 3 is CORRECT AND ALREADY HONOURED — record it so nobody "fixes" it

The reviewer identifies that `drain`'s resilience depends entirely on `deliver`
honouring timeouts, and states the module correctly separates concerns. It does, and
the caller IS ruthless: `tsdbprobe._get` takes `timeout=8.0`, and
`membudget_otlp`/`run_selftests` are the delivery paths. **The right reading is that
this is a CONTRACT the dispatcher should make explicit** (a plugin supplying a
`deliver` declares its timeout), not a defect to patch inside `spool`.

⚑ Note the tension with [review-tsdbprobe.md](review-tsdbprobe.md) concern 2, which
observes the same 8s timeout STACKS against a 45s verify deadline (≈5 retries, not 30).
**Both reviewers are right and they pull opposite ways**: the timeout must be short
enough that a hung socket cannot stall a drain, and long enough that a slow store is
not read as absent. That trade-off is a fact about the pair, and it is invisible from
inside either tool — which is an argument for the contract living at the dispatcher.

### Concern 4 — GRACEFUL DEGRADATION vs. AN UNMEASURED TREE, and this repo has a rule

The reviewer's worry is that a silently-missing `persist-queue` drops telemetry for
months unnoticed. This repo has already ruled on the general form, TWICE, and both
times against silence:

  * `jea_circuit.py:197` returned `True` on `SKIP (numpy absent)` — **an absent
    dependency silently scoring as a pass**, recorded as a defect;
  * `mdstruct` reported `selftest: 0/0` and returned `True` when pandoc was missing —
    the SAME defect, reproduced in a tool written AFTER the first was recorded. Fixed
    so an unmeasured case is announced UNRUN, never counted as passing (Guard (2): *an
    incomplete census is not a low count*).

So the reviewer is right in direction, and `pycodemod --available` already exists as
the family's answer to *"is this library importable HERE"*. ⚑ **But note the
asymmetry the reviewer did not have**: a missing selftest dependency corrupts a
VERDICT (the suite claims coverage it does not have), whereas a missing spool
dependency degrades an OBSERVATION (telemetry is explicitly not load-bearing). The
rule to apply is *say the degradation out loud*, not *fail the run* — a `logging.warning`
is right; raising is not.

### What this review does NOT cover

The reviewer did not exercise the ACK semantics (`SQLiteAckQueue(auto_resume=True)`
calling `resume_unack_tasks()` in `__init__` — the crash-mid-drain recovery that was
the whole reason for taking the dependency), nor the NACK-not-`ack_failed` choice on
delivery failure. Silence there is scope, not a pass.
