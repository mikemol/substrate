# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The facts behind `gate_status`: the hook's gate list, a verdict line, the write-default probe.

⚑⚑⚑ DRAINED FROM `scripts/gate_status.py` (W330). That file carried 351 findings, so the per-file
gate refused every edit; each concern moved into a clean `substrate/` module, held value-for-value
against the origin before the swap. This module is the READING half: it runs nothing itself, and
the one command it needs (`bash -n`) goes through an injected `Runner`.

⚑ THE GATE LIST IS PARSED FROM THE HOOK, NEVER RESTATED. A hand-maintained copy is a derived view
that silently diverges. If a gate is added to `.githooks/pre-commit` it appears on the next run
with no edit; if one is removed it disappears. That also makes the COVERAGE question answerable:
this reader cannot report a gate the hook does not actually run.

⚑ A HOOK THAT DOES NOT PARSE AS SHELL YIELDS A SHORT GATE LIST, NOT AN ERROR — so `gates` asks
`bash -n` first and REFUSES. The hook is the authority on which gates exist; a broken hook is the
one condition under which this reader must refuse rather than report.

⚑ THE TREE IS A PARAMETER. Nothing here derives a path from `__file__`; the CLI shim resolves the
root at call time and hands it down.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple, cast

from substrate import sibling_finder
from substrate.gate_status_exec import run_process

if TYPE_CHECKING:
    from collections.abc import Sequence

    from substrate.gate_status_exec import Runner

#: `run "<name>" <argv…>` — the hook's own spelling of a gate; indentation marks a conditional one.
RUN = re.compile(r'^(\s*)run\s+"([^"]+)"\s+(.*)$')

#: ⚑ `--queit` IS A DELIBERATE TYPO AND THE MOST IMPORTANT ENTRY. Every other mode asks *does this
#: flag work*; this one asks *does the gate REFUSE what it does not know* — a typo'd flag that
#: silently degrades a gate to verbose-but-passing still looks like it ran.
MODES = ("", "--quiet", "--list", "--check", "--dry-run", "--queit")

#: ⚑ `--check` IS THE MODE GATES ARE WIRED WITH; a sweep that omitted it checked every mode EXCEPT
#: the one the gated commit depends on.
CHECK_MODE = "--check"

#: ⚑ A SWEEP MUST NOT WRITE: a write-default tool regenerates its artifact on any invocation that is
#: not `--check`, so a sweep would multiply one accidental write by the number of modes.
WRITE_DEFAULT_HINT = (
    "   ⚑ WRITE-DEFAULT — a bare run REGENERATES its artifact, so a mode sweep\n"
    "     would write once per mode.  Swept in --check mode only; pass\n"
    "     --allow-writes to sweep every mode anyway."
)

#: ⚑ THE RATCHET FAMILY PRINTS ITS `refuse_hint` LAST, SO THE TAIL LINE IS ADVICE, NOT A VERDICT.
#: The verdict is the line naming the LABEL (`<label>: N <noun> …`), which every gate in the family
#: emits. Prefer it; fall back to the last line for gates outside the family.
VERDICT = re.compile(r"^[\w.-]+(?:-ratchet)?:\s")

#: How long the shell-syntax check may take before the hook is declared unreadable.
SYNTAX_TIMEOUT_S = 60

_SCRATCH = "scratch"
_PYCODEMOD = "pycodemod"
_PROBE = "writes_by_default"


class Gate(NamedTuple):
    """One hook-wired gate: its name, its shell fragment, and whether it is conditional."""

    name: str
    argv: str
    conditional: bool


class Tree(NamedTuple):
    """The tree a sweep reads: its root, its hook, and the membudget client it leases through."""

    root: Path
    hook: Path
    membudget: Path


def expand(argv: str, root: Path) -> str:
    """Return the hook fragment with its `$ROOT` spellings resolved to `root`."""
    return argv.replace('"$ROOT"', str(root)).replace("$ROOT", str(root))


def gates(hook: Path, runner: Runner = run_process) -> list[Gate]:
    """Return the gates parsed from the hook's own `run` lines.

    `conditional` is True when the line is indented, i.e. nested inside an `if` in the hook —
    those gates do not fire on every commit, and reporting them as unconditional would overstate
    what the gated commit must satisfy. A trailing backslash continues a `run` line.
    """
    checked = runner(["bash", "-n", str(hook)], Path.cwd(), os.environ, SYNTAX_TIMEOUT_S)
    if checked.rc != 0:
        msg = (
            f"{os.path.relpath(hook)} is not valid shell — the gate census would be "
            f"silently truncated:\n{(checked.stderr or '').strip()}"
        )
        raise SyntaxError(msg)
    out: list[Gate] = []
    text = hook.read_text(encoding="utf-8").split("\n")
    i = 0
    while i < len(text):
        m = RUN.match(text[i])
        if not m:
            i += 1
            continue
        indent = cast("str", m.group(1))
        name = cast("str", m.group(2))
        rest = cast("str", m.group(3))
        while rest.rstrip().endswith("\\") and i + 1 < len(text):
            i += 1
            rest = rest.rstrip()[:-1] + " " + text[i].strip()
        out.append(Gate(name, rest.strip(), bool(indent)))
        i += 1
    return out


def verdict_line(lines: Sequence[str]) -> str:
    """Return the line that states the census verdict, not the remediation advice."""
    for line in reversed(lines):
        if VERDICT.match(line.strip()):
            return line.strip()
    return lines[-1].strip() if lines else ""


def _load_pycodemod(scratch: Path) -> object:
    """Load `pycodemod` from `scratch` by location; its bare-named siblings resolve beside it."""
    cached = sys.modules.get(_PYCODEMOD)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(_PYCODEMOD, str(scratch / f"{_PYCODEMOD}.py"))
    if spec is None or spec.loader is None:
        msg = f"{_PYCODEMOD} is not loadable from {scratch}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[_PYCODEMOD] = module
    try:
        with sibling_finder.siblings_of(scratch):
            spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(_PYCODEMOD, None)
        raise
    return module


def script_path(script: str, root: Path) -> str:
    """Return `script` as an absolute path, resolving a relative one against `root`."""
    return script if Path(script).is_absolute() else str(root / script)


def write_default(script: str, root: Path) -> tuple[bool, str]:
    """Return `(bool, why)` — whether a bare run of `script` writes; `pycodemod` owns the answer.

    ⚑ A FAILURE TO ASK IS A "YES". Any error reaching the probe reads as write-default, so the
    guard's own failure can never authorise a write.
    """
    path = script_path(script, root)
    try:
        module = _load_pycodemod(root / _SCRATCH)
        probe = cast("Sequence[object]", getattr(module, _PROBE)(path))
    except (ImportError, OSError, AttributeError, SyntaxError, TypeError, ValueError) as e:
        return True, f"undetermined ({e})"
    return cast("bool", probe[0]), cast("str", probe[1])
