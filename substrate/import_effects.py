#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What importing a module DOES to the process and the filesystem, not merely whether it succeeded.

⚑⚑⚑ THIS EXISTS BECAUSE A BROAD IMPORT PROBE REPORTED A CORRUPTED RESULT AND NOTHING COULD SAY
WHY. `adopter_import` answers ONE question — did `import_module` raise — and a module that
imports cleanly while writing a file, prepending to `sys.path`, or leaving a foreign name in
`sys.modules` is recorded by it as `OK`. So an observer who sees a later probe return a wrong
answer has no instrument that can name the cause, and the vacuum is filled by a mechanism the
observer INFERS. That is exactly what happened here: an import-time write was reported and the
reported write does not exist, while the real cause went unmeasured because nothing measured it.

⚑⚑ AN UNREPRODUCIBLE CORRUPTION IS A WORSE RESIDUE THAN A FOUND ONE, so this reader is built to
make the NEXT one attributable rather than to vindicate a verdict about the last. It reports what
an import DID, per module, whether or not anything went wrong — a positive record, so a future
anomaly is checked against a baseline instead of against a memory.

⚑⚑⚑ THE FOUR EFFECTS ARE MEASURED SEPARATELY BECAUSE THEY HAVE FOUR DIFFERENT REMEDIES, and
collapsing them to one "clean/dirty" bit is the scalar collapse this repo retires on sight.
A filesystem WRITE is a defect in the imported module. A `sys.path` mutation is a shadowing
hazard that corrupts every LATER import in the same process rather than the one that did it — the
mechanism originally alleged, and the one an exception-typed probe is blindest to. A stray
`sys.modules` entry is how a half-initialised corpse reaches the next importer. A SUBPROCESS is an
unbounded effect no static reader can follow. Only the first was what the original report named;
the other three are the hypotheses that report displaced.

⚑⚑ EACH MODULE IS MEASURED IN ITS OWN SUBPROCESS, for the reason `adopter_import` probes that way
and one more: the `sys.path` and `sys.modules` arms are BEFORE/AFTER DIFFERENCES over interpreter
state, and state left behind by a previous import would be attributed to this one. A
single-process sweep cannot tell "this module mutated sys.path" from "something earlier did".

⚑⚑⚑ THE FILESYSTEM AND SUBPROCESS ARMS USE `sys.addaudithook`, NOT A DIRECTORY DIFF, and the
choice is load-bearing. A diff over the cwd sees only writes that land in ONE directory, so a
module writing to the repo, to a cache, or to a temp path reads as inert — an instrument whose
blind spot is most of the filesystem. The audit hook observes the CALL, so it names the write
wherever it goes. `check_scratch_runtime._PREAMBLE` established this mechanism here; that gate
narrows its hits to `scratch/` because it is asking a coupling question, and this reader keeps
the whole surface because it is asking an attribution one.

⚑⚑ THE `open` EVENT IS FILTERED BY MODE, WHICH THE ESTABLISHED PREAMBLE DOES NOT DO. Its third
audit argument is the flag set, and a read is not a side effect — reporting every file an import
READS would bury the writes under the stdlib's own traffic and make the reader unusable, which is
the false-positive twin of the false zero. Only a write-intent open is recorded.

⚑ BYTECODE WRITING IS DISABLED IN THE CHILD RATHER THAN FILTERED FROM THE RESULT. A `__pycache__`
entry is then never created to be explained away, so no reader has to decide case-by-case which
writes count — the judgement stays in the program.

⚑ THE STATIC AUTHORITY IS NOT DUPLICATED. `import_writes.why_not_import` already answers "would
importing this write" from the SOURCE, delegating to `_pycodemod_census.writes_by_default` — a
whole-file regex with no import-time scope and no path/modules/subprocess axis at all. This
answers the RUNTIME twin, and the two are worth having separately: the static one can be asked
without running anything, this one can see an effect no source read predicts, and DISAGREEMENT
between them is itself a finding rather than an error in either.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from substrate import adopter_import

# The probe body the child runs. It arms an audit hook, snapshots interpreter state, imports, and
# emits the DIFFERENCE as one JSON object on stderr behind a marker.
#
# ⚑ THE HOOK IS ARMED FIRST AND THE SNAPSHOT TAKEN AFTER THE CHILD'S OWN IMPORTS, so this reader's
# machinery never appears in the measured module's ledger. ⚑ The hook body does only string work:
# an audited call inside an audit hook would recurse.
CHILD = r"""
import json, os, sys
_W, _X = [], []
def _hook(ev, a):
    if ev == "open" and len(a) > 2 and isinstance(a[0], str):
        try:
            if a[2] is not None and int(a[2]) & 3:
                _W.append(a[0])
        except (TypeError, ValueError):
            pass
    elif ev in ("subprocess.Popen", "os.exec", "os.posix_spawn") and a:
        _X.append(str(a[0]))
sys.addaudithook(_hook)
_p0, _m0 = list(sys.path), set(sys.modules)
_err = ""
try:
    import importlib
    importlib.import_module(sys.argv[1])
except BaseException as exc:
    _err = type(exc).__name__
_out = {
    "error": _err,
    "wrote": sorted(set(_W)),
    "spawned": sorted(set(_X)),
    "path": [q for q in sys.path if q not in _p0],
    "modules": sorted(n for n in set(sys.modules) - _m0
                      if "." not in n and n not in sys.stdlib_module_names),
}
sys.stderr.write("__EFFECTS__" + json.dumps(_out))
"""

# The marker the child writes its ledger behind, so an imported module's own chatter on stdout or
# stderr can never be mistaken for the measurement.
MARK = "__EFFECTS__"

# How long one probed import may run. An import exceeding this is doing work no import should do.
TIMEOUT_S = 120

# What a clean import may leave in `sys.modules`: the child's own machinery. The module under test
# and its own package are filtered per-probe rather than named here.
#
# ⚑⚑ THE STDLIB IS EXCLUDED IN THE CHILD, AND THE FIRST CUT DID NOT DO IT — which made this axis
# useless in exactly the way the read-vs-write filter exists to prevent on the write axis. Every
# module transitively imports `ast`, `typing`, `subprocess` and thirty more; reporting those made
# 363 of 396 modules read as having "left names in sys.modules", burying the one finding that
# would matter under the ordinary cost of importing anything. A stray entry is a NON-STDLIB name
# the module put there, and `sys.stdlib_module_names` is the authority rather than a list here.
EXPECTED = frozenset({"json", "os", "sys", "importlib"})

# The verdict recorded when the child produced no ledger at all.
UNMEASURED = "Unmeasured"


@dataclass(frozen=True, slots=True)
class Effects:
    """What one module's import did, beyond raising or not.

    ⚑ EVERY FIELD IS A WITNESS LIST, NEVER A COUNT. "3 writes" tells an operator nothing they can
    act on; the filenames name the culprit and the remedy at once.
    """

    module: str
    error: str
    wrote: tuple[str, ...]
    spawned: tuple[str, ...]
    path_added: tuple[str, ...]
    modules_added: tuple[str, ...]

    @property
    def measured(self) -> bool:
        """Whether the child returned a ledger at all.

        ⚑ UNMEASURED AND INERT ARE OPPOSITE READINGS, and only this property separates them. A
        probe that could not report is not a probe that found nothing.
        """
        return self.error != UNMEASURED

    @property
    def inert(self) -> bool:
        """Whether the import left the process and the filesystem exactly as it found them.

        ⚑ AN IMPORT THAT RAISED IS NOT THEREBY INERT, and reading it that way inverts the risk. A
        module that writes a file and THEN dies has done the damage; the exception says only that
        the import did not finish, never that it did nothing.
        """
        return self.measured and not (
            self.wrote or self.spawned or self.path_added or self.modules_added
        )

    def render(self) -> str:
        """Render this module's effects, naming each one, or state that there were none."""
        if not self.measured:
            return f"{self.module}: UNMEASURED — the probe returned no ledger"
        if self.inert:
            return f"{self.module}: inert"
        parts = [f"{self.module}:"]
        for label, items in (
            ("wrote", self.wrote),
            ("spawned", self.spawned),
            ("added to sys.path", self.path_added),
            ("left in sys.modules", self.modules_added),
        ):
            if items:
                parts.append(f"  {label:<20}: {', '.join(items)}")
        if self.error:
            parts.append(f"  (the import also raised {self.error})")
        return "\n".join(parts)


def _strings(got: dict[str, object], field: str) -> tuple[str, ...]:
    """Read one list-of-strings field back across the untyped JSON boundary."""
    value = got.get(field)
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in cast("list[object]", value))


def _ledger(text: str) -> dict[str, object] | None:
    """Return the child's ledger from its stderr, or None when it emitted none."""
    at = text.rfind(MARK)
    if at < 0:
        return None
    try:
        got: object = json.loads(text[at + len(MARK) :])
    except ValueError:
        return None
    if not isinstance(got, dict):
        return None
    return {str(k): v for k, v in cast("dict[object, object]", got).items()}


def effects(module: str, where: Path) -> Effects:
    """Import `module` in a fresh interpreter whose cwd is `where`, and report what it did.

    ⚑ `where` IS THE ALLEGED TARGET, which is why the sweep runs in an empty private directory:
    the original report named a write into "the adopter's cwd", so the probe must run somewhere a
    write would be unambiguous rather than lost among a working tree's existing churn.
    """
    try:
        done = subprocess.run(  # noqa: S603 - fixed argv built in this file, never a shell
            [sys.executable, "-B", "-c", CHILD, module],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
            cwd=str(where),
        )
    except subprocess.TimeoutExpired:
        return Effects(module, "Timeout", (), (), (), ())
    got = _ledger(done.stderr)
    if got is None:
        return Effects(module, UNMEASURED, (), (), (), ())
    root = module.split(".", 1)[0]
    left = tuple(n for n in _strings(got, "modules") if n not in EXPECTED and n != root)
    return Effects(
        module,
        str(got.get("error") or ""),
        _strings(got, "wrote"),
        _strings(got, "spawned"),
        _strings(got, "path"),
        left,
    )


def sweep(package: str, where: Path) -> list[Effects]:
    """Measure every module of the installed `package` for import-time effects."""
    return [effects(name, where) for name in adopter_import.population(package)]


def render(package: str, found: list[Effects]) -> str:
    """Render the sweep, keeping every effect NAMED beside the ratio.

    ⚑ THE INERT AND UNMEASURED COUNTS ARE BOTH REPORTED, because "no module had an effect" and "no
    module could be measured" are opposite readings that a list of findings cannot distinguish.
    """
    if not found:
        return f"{package}: not installed, or the distribution contains no modules"
    loud = [item for item in found if item.measured and not item.inert]
    dark = [item for item in found if not item.measured]
    head = (
        f"{package}: {len(found) - len(loud) - len(dark)} of {len(found)} module(s) "
        f"import with no side effect; {len(loud)} with, {len(dark)} unmeasured"
    )
    if not (loud or dark):
        return head
    return "\n".join([head, *(item.render() for item in [*loud, *dark])])


def main(argv: list[str]) -> int:
    """Run the sweep against a private empty directory and print what each import did.

    ⚑ `argparse.Namespace` attributes are `Any`, which this project's settings forbid from being
    spelled OR propagated, so the cast is the wall — every expression downstream is concrete.
    """
    parser = argparse.ArgumentParser(description="report what importing each installed module DOES")
    parser.add_argument("packages", nargs="*", help="installed packages to measure")
    namespace = parser.parse_args(argv)
    names = tuple(cast("list[str]", namespace.packages))
    with tempfile.TemporaryDirectory() as tmp:
        where = Path(tmp)
        for package in names or adopter_import.DEFAULT_PACKAGES:
            sys.stdout.write(render(package, sweep(package, where)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
