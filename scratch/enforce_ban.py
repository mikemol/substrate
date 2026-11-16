#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Enforce() — the ban-ratchet paydown as an unattended, resumable QUEUE.

This is the one procedure in `.claude/skills/agda-ban-decompose/one-lemma-per-file.md`
that was never mechanized.  Every existing tool is PER-MODULE (`split_pipeline.py`
takes one file; `rewire_to_leaves.py` takes one parent); nothing decided WHICH
module to split next, so "order/scope" read like a judgement call.  It is not —
it is a sort, and the input already exists.

THE QUEUE IS THE BAN CENSUS, INVERTED.
`check_ban_ratchet.census()` emits `<consumer>::<upstream module>::<directive>`,
i.e. literally "this consumer imports a module holding more than it needs".
Group by the MODULE column and the split order falls out, highest first; the
count is CONSUMERS FREED, and one split discharges all of them at once.  That
is why the unit of work is the module, never the key: 12,090 `using` keys sit
over 1,164 modules, and the top 12 modules carry 46% of the debt.

    python3 scratch/enforce_ban.py                 # show the queue, touch nothing
    python3 scratch/enforce_ban.py --apply         # run it, unattended
    python3 scratch/enforce_ban.py --apply --max=1 # ONE module (see below)
    python3 scratch/enforce_ban.py --status        # journal summary
    python3 scratch/enforce_ban.py --stop-on-fail  # HALT on the first parked module instead of
                                                   # journalling it and moving on
    python3 scratch/enforce_ban.py --include-renaming
                                                   # COUNT `renaming`/`as` toward the split signal.
                                                   # ⚑ OFF BY DEFAULT AND THAT IS THE CORRECT
                                                   # DEFAULT, not a conservative one: they are a
                                                   # DIFFERENT debt with a different repair (rename
                                                   # at source), and a split does not discharge
                                                   # them — so counting them inflates the "consumers
                                                   # freed" figure with work this queue will not do.
                                                   # They are reported either way, so nothing is
                                                   # silently dropped from the picture; the flag
                                                   # only changes what the ORDER is computed on.

⚑ `--max=N` AND `--mb=N` TAKE THEIR VALUE WITH AN `=`, and the divergence census reads `--max`
as UNBACKED because of it: it extracts the bare `--max` from the usage line above and finds no
matching literal, since the code tests `a.startswith("--max=")`. Both halves are correct and the
spelling is deliberate — recorded here so the next reader does not "fix" a working flag.

⚑ HOLD `--max=1` UNTIL A CLEAN END-TO-END (user decision, 2026-07-31).
Batch size is a DEFECT-RATE instrument, not a throughput knob.  While the
per-module rate of tool defects or hand edits is above zero, N>1 batches
several modules' worth of unknown breakage into one build, so the failure
you read is a SUM and you cannot attribute it.  N=1 keeps signal attributable
and each defect fixable at source.  Raise N only after one module completes
end-to-end with ZERO tool defects and ZERO manual edits — that observation,
not a count of past attempts, is what licenses the increase.

RECOVERABILITY IS THE POINT (and why this is unattended-safe).
State lives in `scratch/enforce_ban.journal.tsv`, appended after EVERY module,
never held in memory across a step.  So a crash, a timeout, a compaction, or a
`^C` costs exactly the module in flight — re-running resumes at the next unsplit
module with no argument and no recollection required.  The journal is the
authority, not this process and not a context window.

WHAT IT DOES NOT DO — deliberate, per repo policy:
  * never reverts.  `split_pipeline` leaves a failed split ON DISK (stash, don't
    revert); this tool PARKS that module in the journal and moves on, so one
    hard module cannot stall the queue.  `--stop-on-fail` opts into halting.
  * never commits and never pushes.  The user pushes.
  * never edits a baseline or adds an exemption.  A ratchet is paid down by
    splitting, not by moving the goalposts.

⚠ It runs a FULL BUILD per module (via `split_pipeline`'s own hard-gate stages),
so a queue of N modules is N builds.  That is the cost of green-at-every-step,
which is what makes it abandonable at any point.
"""
import os
import re
import sys
import time
import collections
import importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scratch"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import split_pipeline as SP  # noqa: E402
import split_lemmas as SL    # noqa: E402

AG = "agda"
JOURNAL = os.path.join(ROOT, "scratch", "enforce_ban.journal.tsv")


def _census():
    """check_ban_ratchet.census() — loaded by path (the script is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "_cbr", os.path.join(ROOT, "scripts", "check_ban_ratchet.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.census()


def path_of(mod):
    """Substrate.Foundation.Eq -> agda/Substrate/Foundation/Eq.agda"""
    return os.path.join(AG, mod.replace(".", os.sep) + ".agda")


def queue(include_renaming=False):
    """[(module, consumers_freed, directives)] — the split order, richest first.

    Only `using` counts toward the split signal by default: `renaming`/`as` are
    a DIFFERENT debt with a different repair (rename at source — see the
    ban-gate's own header), and a split does not discharge them.  They are
    reported so they are not silently dropped from the picture.
    """
    per = collections.defaultdict(collections.Counter)
    for k in _census():
        _consumer, mod, dirv = k.split("::")
        per[mod][dirv] += 1
    out = []
    for mod, d in per.items():
        n = d["using"] + (d["renaming"] + d["as"] if include_renaming else 0)
        if n:
            out.append((mod, n, dict(d)))
    # GAP-1 LAST.  `rewire_to_leaves` cannot rewrite the combined
    # `using (...) renaming (...)` form (known gap 1), so a module whose
    # consumers use it CANNOT complete — the post-rewire sweep stops the
    # pipeline after the split is already on disk.  Ordering purely by size
    # therefore spends a full build to park the biggest modules first:
    # MEASURED on Foundation.Eq — 1740 importers rewired, then 545 combined-form
    # survivors halted it.  1068 of 1162 modules are gap-1-free, so deferring
    # the blocked ones keeps the queue on work it can finish.  They are NOT
    # dropped: they sort last and are listed, so the debt stays visible.
    #   within each band: descending by consumers freed (biggest paydown first),
    #   module name breaking ties so the order is STABLE across runs — a queue
    #   you cannot reproduce is not recoverable.
    out.sort(key=lambda t: (t[2].get("renaming", 0) + t[2].get("as", 0) > 0,
                            -t[1], t[0]))
    return out


def read_journal():
    """module -> (status, detail). Last line for a module wins (append-only)."""
    seen = {}
    if os.path.exists(JOURNAL):
        for line in open(JOURNAL, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3 and not line.startswith("#"):
                _ts, mod, status = parts[0], parts[1], parts[2]
                seen[mod] = (status, parts[3] if len(parts) > 3 else "")
    return seen


def journal(mod, status, detail=""):
    new = not os.path.exists(JOURNAL)
    with open(JOURNAL, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# ts\tmodule\tstatus\tdetail\n")
        detail = re.sub(r"\s+", " ", detail)[:400]
        fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{mod}\t{status}\t{detail}\n")


def split_one(mod, mb):
    """Run the full per-module pipeline. Returns (status, detail).

    `split_pipeline.die()` raises SystemExit — catch it so ONE hard module parks
    itself rather than killing the queue.  That containment is what makes the
    run unattended-safe.
    """
    path = path_of(mod)
    if not os.path.exists(path):
        return "skip", "no such file (already split, or a directory module)"
    try:
        files, _named = SL.split(path, apply=False)
    except Exception as e:                                    # noqa: BLE001
        return "fail", f"plan error: {type(e).__name__}: {e}"
    if len(files) <= 1:
        return "atomic", "already one declaration — nothing to split"

    try:
        rc = SP.main(["split_pipeline.py", path, "--apply", f"--mb={mb}"])
    except SystemExit as e:                                   # die() inside a stage
        return "fail", f"pipeline stopped (exit {e.code}); split may be ON DISK — stash, do not revert"
    except Exception as e:                                    # noqa: BLE001
        return "fail", f"{type(e).__name__}: {e}"
    return ("done", f"{len(files)} leaves") if rc == 0 else ("fail", f"pipeline rc={rc}")


def main(argv):
    apply = "--apply" in argv
    status_only = "--status" in argv
    stop_on_fail = "--stop-on-fail" in argv
    include_ren = "--include-renaming" in argv
    mb = SP.DEFAULT_MB
    limit = None
    for a in argv:
        if a.startswith("--max="):
            limit = int(a.split("=", 1)[1])
        if a.startswith("--mb="):
            mb = int(a.split("=", 1)[1])

    done = read_journal()

    if status_only:
        by = collections.Counter(s for s, _ in done.values())
        print(f"journal: {JOURNAL}")
        for k, v in by.most_common():
            print(f"  {v:5d}  {k}")
        for mod, (st, detail) in sorted(done.items()):
            if st == "fail":
                print(f"  PARKED  {mod}\n          {detail}")
        return 0

    q = queue(include_ren)
    total = sum(n for _, n, _ in q)
    pending = [(m, n, d) for m, n, d in q if done.get(m, ("", ""))[0] not in ("done", "atomic", "skip")]

    print(f"ban-ratchet paydown queue — {len(q)} upstream module(s), "
          f"{total} consumer-import(s) to free")
    print(f"journal {JOURNAL}: {len(done)} module(s) already recorded; "
          f"{len(pending)} pending\n")
    for i, (mod, n, d) in enumerate(pending[:20]):
        mark = "PARKED " if done.get(mod, ("", ""))[0] == "fail" else "       "
        extra = " ".join(f"{k}={v}" for k, v in sorted(d.items()) if k != "using")
        print(f"  {mark}{n:5d}  {mod}  {extra}")
    if len(pending) > 20:
        print(f"  … {len(pending) - 20} more")

    if not apply:
        print("\nDry run — pass --apply to execute. Each module is a full "
              "split+rewire+build cycle;\nstate is journalled after every one, so "
              "this is resumable at any point.")
        return 0

    ran = 0
    for mod, n, _d in pending:
        if limit is not None and ran >= limit:
            print(f"\n--max={limit} reached; {len(pending) - ran} module(s) still pending.")
            break
        if done.get(mod, ("", ""))[0] == "fail":
            print(f"\n=== SKIP (parked earlier) {mod} — clear it from the journal to retry")
            continue
        print(f"\n{'=' * 70}\n=== {mod}  ({n} consumer-import(s) to free)\n{'=' * 70}")
        status, detail = split_one(mod, mb)
        journal(mod, status, detail)          # AFTER every module, before the next
        print(f"--- {mod}: {status.upper()} — {detail}")
        ran += 1
        if status == "fail" and stop_on_fail:
            print("\n✗ --stop-on-fail: halting. The tree may hold a partial split; "
                  "stash, do not revert.")
            return 1

    print(f"\nqueue: {ran} module(s) attempted this run. "
          f"Re-run to continue; `--status` for the journal.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
