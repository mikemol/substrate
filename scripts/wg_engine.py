#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""wg_engine.py — locating the paperkit engine, and running one of its entry points.

⚑ THIS IS A SEAM, NOT A NEW LAYER.  Split out of `worklist_gate.py` (1,458 code
lines, over the 1200 threshold) on 2026-08-11.  The seam is chosen by WHAT STATE
THE GROUP TOUCHES: everything here is about the SUBPROCESS BOUNDARY — where the
engine lives, what environment its child gets, where its scratch goes, and how
its transcript is summarised.  Nothing here imports `items` or `figures`, and
nothing here knows what a worklist ITEM is.  That is what makes it separable:
the DAG side (`wg_order`) and the report side (`wg_report`) both drive the
worklist's own data, while this drives another program.

⚑ `worklist_gate.py` RE-EXPORTS EVERY NAME HERE.  The public surface did not
move — a caller still writes `worklist_gate.engine()` — because a decomposition
that relocates an API is a rename wearing a refactor's clothes.
"""

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT = os.path.join(ROOT, "catalog", "worklist")
LIBRARY = os.path.join(ROOT, "catalog", "library")

# Conventional checkout locations, in order.  ⚑ The env var wins so a different
# engine version can be pinned without editing this file.
CANDIDATES = [
    os.environ.get("PAPERKIT"),
    os.path.expanduser("~/github/paperkit"),
]


def engine():
    """(path, reason).  The paperkit checkout, or None with a stated reason."""
    tried = []
    for c in CANDIDATES:
        if not c:
            continue
        tried.append(c)
        if os.path.isfile(os.path.join(c, "paperkit", "gate.py")):
            return c, None
    return None, (
        "no paperkit engine found (looked in: %s). Paperkit is an "
        "engine you point at a project; set PAPERKIT=<checkout> or "
        "clone it to ~/github/paperkit." % ", ".join(tried or ["<nothing>"])
    )


# ⚑ THE ENGINE NEEDS SCRATCH SPACE, AND THE DEFAULT ONE IS TOO SMALL.
# `discriminate.py` grades a check by COPYING the project to a sandbox and
# mutating one file at a time — so Delta's disk cost scales with project size x
# input count, while `gate` and `project` need almost none.  On this box /tmp is
# a 4 GiB tmpfs shared with the editor and the agent harness; Delta filled it and
# every child process then failed at spawn with ENOSPC, which reads as "the tool
# is broken" rather than "the volume is full".
#
# So the scratch directory is CHOSEN here rather than inherited.  Same shape as
# `membudget` owning the memory ceiling: the resource a tool needs is part of
# knowing how to invoke it, and leaving it to a shared default means the failure
# lands somewhere with no idea what asked for it.
# ⚑ AND IT IS A FLAG, NOT ONLY A DEFAULT.  `--scratch=<dir>` overrides it, in
# the same spirit as `AGDA_MB` pinning a membudget lease: placement is something
# the caller may need to control, and a tool whose only answer is "wherever the
# environment happened to point" cannot be aimed.
SCRATCH = os.environ.get("PAPERKIT_TMPDIR") or os.path.join(ROOT, ".paperkit-tmp")

# ⚑ ONLY Delta NEEDS A SANDBOX.  My first cut redirected TMPDIR for EVERY entry
# point and created the directory eagerly, so `--figures` and `--items` — which
# spawn nothing and mutate nothing — still minted a scratch dir.  Redirecting a
# resource that a mode does not use is how a scratch dir becomes permanent
# without anyone deciding it should.
NEEDS_SANDBOX = {"discriminate.py"}


@contextlib.contextmanager
def _sandbox(entry, scratch=None):
    """Yield the child's environment; REMOVE the scratch tree afterwards.

    ⚑ I FILLED THE VOLUME TWICE WRITING THIS, AND BOTH TIMES THE DEFECT WAS THE
    SAME SHAPE: a temp directory created as a side effect and owned by nobody.
    Delta copies the project once per mutated input, so its scratch grows with
    (project size x input count) and NOTHING was deleting it between runs.

    So the scratch is a CONTEXT, not a location: created only for the entry that
    needs it, and torn down on the way out even when the child crashes.  That is
    the same discipline as `membudget` releasing a lease on exit — a resource
    acquired by a tool is released by that tool, never left for a human to
    notice when the volume fills.  `--keep-scratch` overrides it for debugging,
    which is the only case where the tree is worth more than the space."""
    env = dict(os.environ)
    if entry not in NEEDS_SANDBOX:
        yield env
        return
    d = scratch or SCRATCH
    os.makedirs(d, exist_ok=True)
    made = tempfile.mkdtemp(prefix="run-", dir=d)
    for var in ("TMPDIR", "TEMP", "TMP"):
        env[var] = made
    try:
        yield env
    finally:
        if os.environ.get("PAPERKIT_KEEP_SCRATCH"):
            print("worklist-gate: kept scratch %s" % made)
        else:
            shutil.rmtree(made, ignore_errors=True)


def scratch_size(path=None):
    """Bytes currently held by the scratch tree — 0 when it does not exist.

    ⚑ EXISTS SO THE QUESTION IS ASKABLE.  "Is something filling the disk" was
    answered by the volume filling, twice.  A tool that acquires space should be
    able to report how much it is holding."""
    d = path or SCRATCH
    total = 0
    for dp, _, fns in os.walk(d):
        for fn in fns:
            try:
                total += os.path.getsize(os.path.join(dp, fn))
            except OSError:
                pass
    return total


def _emit(text, out=None):
    """Write a report to `out`, or to stdout when no destination is named.

    ⚑ `--out=<file>` EXISTS BECAUSE A CALLER'S STDOUT IS NOT ALWAYS A PLACE THE
    RESULT CAN GO.  Delta's report is long, and it was being produced correctly
    while the surrounding spool could not hold it — so the tool looked broken
    when the volume was.  Naming the destination is the same move as
    `.leaf-verify.tsv` persisting the census instead of printing it: a result
    worth computing is worth putting somewhere the next command can read."""
    if not out:
        print(text, end="" if text.endswith("\n") else "\n")
        return
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text if text.endswith("\n") else text + "\n")
    print("worklist-gate: wrote %s (%d lines)" % (out, len(text.splitlines())))


def run(entry, extra=(), quiet=False, out=None, scratch=None):
    """Invoke one paperkit entry point against catalog/worklist/.

    ⚑ SUMMARISES ITS OWN OUTPUT.  The engine is verbose and its verdict is not
    reliably its last line — the exact defect §60 found in `gate_status.run_gate`
    keeping `tail[-1]` while the ratchet family printed its hint last.  A caller
    reaching for `| tail` is applying reasoning the tool should carry, so the
    verdict lines are SELECTED here, by prefix, and the full transcript is one
    flag away."""
    root, why = engine()
    if root is None:
        print("worklist-gate: CANNOT MEASURE -- %s" % why, file=sys.stderr)
        print("worklist-gate: refusing rather than reporting clean.", file=sys.stderr)
        return 2
    cmd = [sys.executable, os.path.join(root, "paperkit", entry), PROJECT]
    cmd.extend(extra)
    with _sandbox(entry, scratch) as env:
        p = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, env=env)
    text = (p.stdout or "") + (p.stderr or "")
    if quiet:
        # ⚑ the verdict lines, not the tail: every line the engine tags with its
        # own name is a verdict; anything else is working detail.
        text = "\n".join(l for l in text.splitlines() if l.startswith("paperkit-"))
    _emit(text, out)
    return p.returncode
