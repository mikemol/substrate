#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The catalog RENDER TARGETS as a named vocabulary, and the refusal for an unknown one.

⚑⚑⚑ THIS IS DRAINED OUT OF `scripts/reuse_catalog.py`, AND THE FILE IT LEAVES IS UNIMPORTABLE
TODAY. That module's line 58 reads `sys.path.insert(...)` while the only binding in scope is
`sys as _sys` — a bare `sys` that was never imported — so importing it raises `NameError` at
module scope. The three consumers (`gen_catalog`, `gen_reuse_index`, `gen_reuse_graph`) are
each reported by the adopter probe as the FAILING module, and none of them contains the defect:
all three spell `import os, sys` correctly. The error is attributed to the importer and lives in
the imported, which is the same displacement a `sys.path` mutation makes one layer up.

⚑⚑ SO THE TARGET NAMES COULD NOT BE READ WITHOUT RUNNING THE WALK, AND THAT IS THE REAL COST.
`_RENDERERS` is a dict literal in that module, so the question *"what can this tool render"* was
answerable only by importing a module that raises, or by reading the source by eye. The names are
a VOCABULARY — closed, ordered, and independent of any store — and nothing about them needs the
`.agdai` cores, postgres, or the SPPF projection. Keeping them beside the renderer bodies made a
pure fact hostage to an impure module.

⚑ AN UNKNOWN TARGET RAISES INSTEAD OF `KeyError`, WHICH IS THE DEFECT THIS CLOSES. The superseded
driver indexes `_RENDERERS[t]` directly, so a mistyped target surfaces as a bare `KeyError:
'sitmap'` from inside a loop, naming neither the tool, the valid set, nor which of several
requested targets was wrong. A caller cannot act on that and a case cannot assert it precisely.

⚑ THE ORDER IS DECLARED, NOT INCIDENTAL. `DEFAULT` is the full sequence the gate path renders,
and it is a tuple rather than a set because two renders write sibling files a reader diffs
together; an order that varied per run would churn the diff for no reason. Callers asking for a
subset get it in THIS order, never in argv order, so the same request always renders the same way.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND THAT IS LOAD-BEARING. The module
this was cut from reaches for `store`, `jea_agdai`, `query_builders` and `_content_addr` through
four separate `sys.path` inserts. A vocabulary that named any of them would inherit the whole
untyped hub and could not be made clean under this tree's per-file gate.
"""

from __future__ import annotations

#: The name/home index: name -> canonical home plus cross-name shape-parallels.
INDEX = "index"
#: The struct refinement graph: X -> Y iff X's core is built on Y.
GRAPH = "graph"
#: The flat discovery manifest, priority = in-degree.
SITEMAP = "sitemap"
#: The reuse distribution — real primitives against structurally-isolated structures.
USAGE = "usage"
#: The module semantic-dependency graph, over the cores rather than source import lines.
IMPORT = "import"

#: Every target, in the order the full path renders them. ⚑ A TUPLE, NOT A SET: two of these
#: write sibling files that get diffed together, so a varying order would churn the diff.
DEFAULT: tuple[str, ...] = (INDEX, GRAPH, SITEMAP, USAGE, IMPORT)

#: The same names as a membership set, derived rather than retyped. ⚑ DERIVED SO THE TWO CANNOT
#: DISAGREE — a hand-written second listing is exactly how a vocabulary comes to admit a name its
#: own sequence does not render.
KNOWN: frozenset[str] = frozenset(DEFAULT)


def unknown(targets: tuple[str, ...]) -> tuple[str, ...]:
    """Return the requested targets this vocabulary does not know, in the order requested.

    ⚑ IT REPORTS EVERY UNKNOWN NAME RATHER THAN THE FIRST. A caller that mistyped two targets
    should learn both in one refusal; stopping at the first turns one wrong invocation into two
    round-trips, and the second mistake is discovered only after the first is fixed.

    ⚑ REQUEST ORDER IS PRESERVED HERE EVEN THOUGH `plan` IMPOSES `DEFAULT` ORDER. This is the
    diagnostic, and a reader matching the message against what they typed needs their own
    spelling back; normalising it would make the refusal harder to read than the mistake.
    """
    return tuple(t for t in targets if t not in KNOWN)


def plan(targets: tuple[str, ...]) -> tuple[str, ...]:
    """Order and de-duplicate a known-target request into the sequence to render.

    ⚑ IT RAISES ON AN UNKNOWN TARGET rather than dropping it. Silently rendering the subset it
    recognised would report success for a request it did not satisfy — the shape where a tool
    answers a question nobody asked and nobody can tell.

    ⚑ A REPEATED TARGET RENDERS ONCE. Asking for the same catalog twice is redundant rather than
    contradictory, and rendering it twice would write the same file twice and double the walk's
    only cheap half for no gain.
    """
    bad = unknown(targets)
    if bad:
        msg = (
            f"unknown catalog target(s): {', '.join(repr(t) for t in bad)} — "
            f"known targets are {', '.join(DEFAULT)}"
        )
        raise ValueError(msg)
    return tuple(t for t in DEFAULT if t in set(targets))
