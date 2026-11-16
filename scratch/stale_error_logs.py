#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⚑ SCAFFOLD — do stale build logs produce a WRONG ANSWER, or are they inert?

MEASURED 2026-08-03: 152 `.agdai.log` carry `error:` — 103 fresh, 46 stale,
3 ORPHAN (source deleted).  The census is right (`--verify --from-build` gates on
`log_is_fresh`), so the question is whether anything reads a log WITHOUT that
gate and therefore classifies a module on fiction.

`figures._failures_by_kind` filters rows to `build-failed` from the ledger, then
calls `_classify` on the log.  That is a ROW filter, not a FRESHNESS check: it
assumes a build-failed module has a current log.  This asks whether the
assumption holds — for each build-failed row, is its log actually fresh?

An `?` freshness reason means `log_is_fresh` withheld its verdict, which is
itself worth separating from a measured stale.

Delete once the reading lives in a tool mode.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scratch"))
sys.path.insert(0, os.path.join(ROOT, "catalog", "library"))

import split_pipeline as SP  # noqa: E402
import figures as F  # noqa: E402

txt = F._read(F.LEDGER)
rows = []
for line in txt.splitlines():
    if line.startswith("#"):
        continue
    p = line.split("\t")
    if len(p) >= 2 and p[1] == "build-failed":
        rows.append(p[0])

print("%d build-failed row(s) in the ledger" % len(rows))

fresh, stale, missing = [], [], []
for rel in rows:
    log = F.build_log(rel)
    if not os.path.exists(log):
        missing.append(rel)
        continue
    ok, _lg, why = SP.log_is_fresh(rel)
    (fresh if ok else stale).append((rel, (why or {}).get("why", "?")))

print("  log FRESH   %d — `_classify` reads a current error" % len(fresh))
print("  log STALE   %d — ⚠ `_classify` reads an error that no longer applies"
      % len(stale))
print("  log MISSING %d — `_classify` receives '' and classifies as clean"
      % len(missing))
print()
for rel, why in sorted(stale):
    print("  STALE  %-64s %s" % (rel, why))
for rel in sorted(missing):
    print("  MISSING %s" % rel)
