#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⚑ SCAFFOLD — does `PARTS` cover what `SIZES` claims?

`size` is the pre-`PARTS` collapse: one scalar beside the rows that ARE the
population (user, 2026-08-03: *"`size` shouldn't be a thing. That's obsoleted by
the omitted rows."*).  Before removing it from the sort key, measure the
disagreement — an item with a size and NO parts would lose its magnitude
entirely, which is a different change from replacing a scalar with a count.

Delete once the reading lives in a witness.
"""
import io
import os
import sys
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "catalog", "library"))

import items as I  # noqa: E402

for key, fn in sorted(I.ITEMS.items()):
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            fn()
        except BaseException:
            pass

both, size_only, parts_only, neither = [], [], [], []
for key in sorted(I.ITEMS):
    s = I.SIZES.get(key)
    p = I.PARTS.get(key)
    if s is not None and p:
        both.append((key, s, len(p)))
    elif s is not None:
        size_only.append((key, s))
    elif p:
        parts_only.append((key, len(p)))
    else:
        neither.append(key)

print("BOTH (size and parts) — does the scalar equal the row count?")
for k, s, n in both:
    print("   %-38s size=%-6s parts=%-5d %s"
          % (k, s, n, "agree" if s == n else "DISAGREE"))
print()
print("SIZE ONLY — removing `size` LOSES their magnitude (%d)" % len(size_only))
for k, s in size_only:
    print("   %-38s size=%s" % (k, s))
print()
print("PARTS ONLY — already row-shaped (%d)" % len(parts_only))
for k, n in parts_only:
    print("   %-38s parts=%d" % (k, n))
print()
print("NEITHER — no magnitude at all (%d): %s"
      % (len(neither), ", ".join(neither)))
