#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which file an Agda compile failure CITES - the reading every consumer was re-deriving.

THE FIRST CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_pipeline.py:255-278, 326-331`, W4
tick 39). A compile failure names a FILE, and that file is USUALLY NOT THE ONE UNDER TEST.
The origin records the measurement that made this a reader rather than a regex at every call
site: verifying R9, 12 of 25 sampled leaves "failed" - but 9 of the 12 cited an error in a
DEPENDENCY (`F2/Vector.agda:167`, the section-vs-grammar case; `Permutation.agda:16`, a
telescope-import case). Read as a 48% failure rate that is a regression worth reverting; read
correctly it is a ~12% defect rate plus the pre-existing broken frontier the build census
already tracks. Attributing a failure to the thing you just changed WITHOUT reading which file
the error cites is how a working change gets rolled back.

THE VERDICT IS THREE-VALUED AND THE THIRD VALUE CARRIES A FILE. `clean` is empty output, or
output with no cited file and no `error` in it; `own` is a citation ending in the leaf under
test, or an `error` line that cites nothing (attributed to the leaf, the conservative reading);
`dependency` is a citation of some OTHER file, which is returned so the caller can chase it.

`parse_clash` reads the one error shape the collision cure acts on - `[ClashingDefinition]`,
with the consumer file, the clashing name, and the file of the previous definition - and
returns None for every other error. Both readers are pure over text; nothing here runs agda.
"""

from __future__ import annotations

import re

Verdict = tuple[str, str | None]
Clash = tuple[str, str, str]

# A cited file: an absolute `.agda` path at the head of a line, followed by a line number.
_CITED = re.compile(r"^(/\S+\.agda):\d+", re.MULTILINE)
_CLASH = re.compile(
    r"^(\S+\.agda):\d+[\d.,-]*: error: \[ClashingDefinition\]\s*\n"
    r"\s*Multiple definitions of (\S+)\. Previous definition at\s*\n"
    r"\s*(\S+\.agda):",
    re.MULTILINE,
)


def blame(leaf_path: str, out: str) -> Verdict:
    """Return ('clean' | 'own' | 'dependency', cited_file) for one compile's output."""
    if not out:
        return ("clean", None)
    m = _CITED.search(out)
    if not m:
        return ("clean", None) if "error" not in out.lower() else ("own", leaf_path)
    cited = str(m.group(1))
    return ("own" if cited.endswith(leaf_path.lstrip("./")) else "dependency", cited)


def parse_clash(out: str) -> Clash | None:
    """Return (consumer_file, name, previous_def_file) for a ClashingDefinition, else None."""
    m = _CLASH.search(out)
    return (str(m.group(1)), str(m.group(2)), str(m.group(3))) if m else None
