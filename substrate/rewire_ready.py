#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Is an emitted rewire remedy SAFE TO RUN - the verdict, with every input a parameter.

THE SECOND CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_pipeline.py:403-497`, W4 tick 40).
The origin's `ready_verdict` prints a remedy's precondition, which was once printed unchecked:
the batch path emitted the same runnable command for every file-not-found module with nothing
testing whether it applied. MEASURED 2026-08-17, four targets, four DIFFERENT correct actions
behind one remedy string - `Vec.Properties` rewired 42 importers cleanly; `Foundation.Nat` 3
with one UNMAPPED name; `GUnit.Base` 0 with two UNMAPPED; and `Algebra.F2` 0 of 0, a NO-OP that
`--apply` would have reported as success. Those four are this module's fixture.

THE ORIGIN ORCHESTRATES THREE EXTERNALS AROUND A PURE CORE, and only the core is here. It runs
`rewire_to_leaves --manifest --dry-run` and regexes the text; it asks `agda_defs.reexport_index`
which `public` re-exports target the module; it isolate-compiles the leaves through
`leaves_ready`. Each is a parameter: `parse_manifest` reads the subprocess text, `Inputs`
carries the leaf count, the re-exports and the compile result, and `verdict` renders. The shim
supplies the three readers; nothing below runs a process or a compile.

TWO ORDERINGS ARE LOAD-BEARING AND KEPT. The ARITY test (how many importers the rewire would
touch, counted from its own manifest) comes before the COMPILE test, because `leaves_ready`
isolate-compiles every module under the prefix - for `Substrate.Algebra.F2` that is 369
modules to answer a question the count settles - and `compile_cap` bounds what is left as a
TERMINATION bound, not a capability bound: over it the verdict says so rather than truncating.
And a surviving `public` re-export is reported BEFORE the compile result, because stage 6
refuses on one and a classifier that cannot see the thing that halts the run is not
classifying the run (measured: `--ready` called `SimplicialBoundary` clean, `--apply` rewired
10 importers and stopped at a `public using` line).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A `public` re-export as `agda_defs.reexport_index` yields it: (module, line, target, tail, kind).
Reexport = tuple[str, int, str, str, str]
# One isolate-compiled leaf: (path, verdict, cited) - the `leaves_ready` row shape.
LeafRow = tuple[str, str, str | None]

_REACH = re.compile(
    r"(\d+)\s+names?\s*/\s*(\d+)\s+leaves?\s*->\s*(?:WOULD rewire\s+)?(\d+)\s+importer"
)
_UNMAPPED = re.compile(r"⚠ UNMAPPED in (\S+): (\[[^\]]*\])")
# How many UNMAPPED sites, re-exports and bad leaves a verdict lists before eliding.
LIST_CAP = 5
DEFAULT_COMPILE_CAP = 24


@dataclass(frozen=True)
class Manifest:
    """What the rewire's own dry-run manifest says about its reach."""

    importers: int | None
    unmapped: tuple[tuple[str, str], ...] = ()


def parse_manifest(txt: str) -> Manifest:
    """Read the importer count and the UNMAPPED sites off a `--manifest --dry-run` text."""
    m = _REACH.search(txt)
    importers = int(m.group(3)) if m else None
    # `finditer` yields typed matches where `findall` yields `Any`.
    unmapped = tuple((str(u.group(1)), str(u.group(2))) for u in _UNMAPPED.finditer(txt))
    return Manifest(importers, unmapped)


@dataclass(frozen=True)
class Inputs:
    """Everything the verdict reads, supplied by the caller rather than fetched."""

    leaf_count: int
    manifest: Manifest
    reexports: tuple[Reexport, ...] = ()
    # None means the compile was NOT run; the verdict decides whether to ask for it.
    compiled: tuple[bool, tuple[LeafRow, ...]] | None = None
    compile_cap: int = DEFAULT_COMPILE_CAP
    root: str = ""


def needs_compile(inp: Inputs) -> bool:
    """Return whether the verdict would consult the compile - the caller runs it only then."""
    m = inp.manifest
    return (
        inp.leaf_count > 0
        and m.importers is not None
        and m.importers > 0
        and inp.leaf_count <= inp.compile_cap
    )


def _reach_lines(inp: Inputs) -> list[str]:
    """Render the arity verdict and the UNMAPPED sites."""
    m = inp.manifest
    if m.importers == 0:
        head = (
            f"ready: ✗ NO-OP — resolves {inp.leaf_count} module(s) under this prefix but "
            f"rewires 0 importer(s); --apply changes nothing"
        )
    elif m.importers is None:
        head = "ready: ? could not read the rewire's reach from its own output"
    else:
        head = f"ready: → would rewire {m.importers} importer(s)"
    out = [head]
    out.extend(f"    UNMAPPED {names} in {site}" for site, names in m.unmapped[:LIST_CAP])
    if m.unmapped:
        out.append(
            f"    ⚑ {len(m.unmapped)} site(s) name what no leaf provides — those "
            f"importers are left UNTOUCHED by --apply"
        )
    return out


def _reexport_lines(inp: Inputs) -> list[str]:
    """Render the surviving `public` re-exports stage 6 will refuse on."""
    if not inp.reexports:
        return []
    head = (
        f"    ⚑ {len(inp.reexports)} `public` re-export(s) TARGET this module — stage 6 "
        f"will refuse until they are retired (re-exports are banned)"
    )
    out = [head]
    out.extend(
        f"        {mod}:{ln}  [{kind}]  {tail}"
        for mod, ln, _t, tail, kind in inp.reexports[:LIST_CAP]
    )
    return out


def _relative(path: str, root: str) -> str:
    """Render a leaf path relative to the root when it is absolute under it."""
    prefix = root.rstrip("/") + "/"
    return path[len(prefix) :] if root and path.startswith(prefix) else path


def _compile_lines(inp: Inputs) -> list[str]:
    """Render the compile result, the cap refusal, or nothing when the compile was not run."""
    if inp.leaf_count > inp.compile_cap:
        capped = (
            f"    leaves: {inp.leaf_count} > cap {inp.compile_cap} — NOT compile-checked "
            f"(raise the cap to check)"
        )
        return [capped]
    if inp.compiled is None:
        return []
    ok, rows = inp.compiled
    if ok:
        return [f"    leaves: ✓ {len(rows)} compile"]
    bad = [(q, v) for q, v, _c in rows if v != "clean"]
    out = [f"    leaves: ✗ {len(bad)} of {len(rows)} NOT clean — clear these FIRST"]
    out.extend(f"        {v:<12} {_relative(q, inp.root)}" for q, v in bad[:LIST_CAP])
    return out


def verdict(inp: Inputs) -> list[str]:
    """Render the readiness lines: arity first, re-exports next, compile last and only if due."""
    if inp.leaf_count == 0:
        return ["ready: ✗ NO LEAF SET — not a consumed parent; this remedy does not apply"]
    out = _reach_lines(inp) + _reexport_lines(inp)
    if inp.manifest.importers == 0:
        return out
    return out + _compile_lines(inp)
