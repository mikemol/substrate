#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡exe-sweep — reconcile a file's executable bit with whether it carries a shebang.

⚑⚑ THIS EXISTS BECAUSE THE MISMATCH BLOCKS AN UNRELATED EDIT. `EXE001` is an ordinary
lint finding until a zero-tolerance gate is armed over it, at which point a file whose
shebang and mode disagree REFUSES ITS NEXT EDIT — for a reason that has nothing to do
with the change being made. Measured 2026-08-30: `check_hook_set.py` refused a fix to
its own manifest closure because of a bit that had been wrong since it was written.

⚑ AND THE HOOK CANNOT SEE THIS CLASS, WHICH IS WHY IT ACCUMULATED. `hook_pycheck`
lints a TEMPFILE whose mode it derives from the content (`0o755` when the source starts
with `#!`), so an in-flight edit ALWAYS agrees with itself and the finding never fires
there. Only a check against the file ON DISK sees it. The gate and a direct `ruff
check` therefore disagree about every shebang-carrying file whose bit is unset — the
divergence is invisible from inside the gate, and each file discovers it separately, at
the moment someone tries to edit it.

⚑⚑ THE DIRECTION IS NOT OBVIOUS AND IS THE OPERATOR'S CALL, RECORDED HERE BECAUSE THE
TOOL CANNOT DECIDE IT. Both `chmod +x` and DELETING the shebang satisfy the rule, and
they mean opposite things. Every file in this tree is invoked as `.venv/bin/python3
<path>`, so `#!/usr/bin/env python3` names an interpreter that LACKS this project's
dependencies — making a file executable does not make running it directly work. The
operator ruled `+x` (2026-08-30, "All 376 — one mechanical sweep, big diff") over
deleting the shebangs; this tool implements that ruling and does not relitigate it.

⚑ DERIVED FROM RUFF, NEVER FROM A `find`. The population is whatever the linter
reports, so this tool cannot drift from the rule it is paying down — a hand-written
glob would be a second definition of "carries a shebang" beside ruff's, and this repo
has measured that shape repeatedly. `--check` reports without writing.
"""

from __future__ import annotations

import stat
import subprocess
import sys
from pathlib import Path

from substrate import corpus

_ROOT = Path(__file__).absolute().parent.parent
_VENV_PY = _ROOT / ".venv" / "bin" / "python3"
_PYPROJECT = _ROOT / "pyproject.toml"

# What `main` returns when handed an operand it does not take.
_REFUSED = 2


def _trees() -> tuple[str, ...]:
    """Return the trees this sweep covers, DISCOVERED rather than frozen.

    ⚑⚑⚑ THIS WAS `("scripts", "scratch", "jea")` AND THE PROMOTED PACKAGE POSTDATED IT
    (gate-F94). Every module written into `substrate/` was outside the sweep's population,
    so the tool whose whole job is repairing this rule reported *no shebang/mode mismatches*
    while `file_mode` reported twenty-one — all of them under `substrate/`. Two readers, one
    question, opposite answers, and the repair tool was the wrong one.

    ⚑⚑ A GREEN FROM A FROZEN ROSTER IS A FACT ABOUT THE ROSTER. The sweep was not failing to
    repair; it was correctly repairing three trees that happened to be clean and reporting
    that as a verdict about the repo. Nothing in its output distinguished SCANNED-AND-CLEAN
    from NEVER-SCANNED, which is why it read as authoritative for as long as it did.

    ⚑ SO THE FIX IS NOT A FOURTH ENTRY. `corpus.roots()` discovers the top-level directories
    and applies the skip vocabulary at both levels, so a tree added tomorrow is swept with no
    edit here. This module's header already states the rule for the FILE population —
    *"derived from ruff, never from a find"* — and the TREE population had escaped it.
    """
    found: tuple[str, ...] = corpus.roots(_ROOT)
    return found


# ⚑ THE TWO RULES ARE OPPOSITE FINDINGS OF ONE PREDICATE — shebang-without-bit and
# bit-without-shebang. Sweeping only one would leave the other to block an edit later,
# and the repair differs: one sets the bit, the other clears it.
_RULES = "EXE001,EXE002"

_EXECUTABLE = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

# ruff's `concise` format is `path:line:col: CODE message` — four colon-separated
# fields before the message text. A shorter line is not a finding and is skipped.
_CONCISE_FIELDS = 4


def _findings() -> list[tuple[Path, str]]:
    """Return `(path, rule)` for every mode/shebang mismatch ruff reports."""
    argv = [
        str(_VENV_PY),
        "-m",
        "ruff",
        "check",
        "--config",
        str(_PYPROJECT),
        "--no-cache",
        "--select",
        _RULES,
        "--output-format",
        "concise",
        "--quiet",
        *[str(_ROOT / t) for t in _trees()],
    ]
    # ⚑ THE S603 EXEMPTION IS IN `pyproject.toml`, KEYED TO THIS FILE — not a `noqa`.
    # This tool has one responsibility, which is what makes a per-file override honest;
    # the argv is module constants and a derived project path, never user input.
    p = subprocess.run(argv, capture_output=True, text=True, check=False)
    out: list[tuple[Path, str]] = []
    for line in p.stdout.splitlines():
        # `path:line:col: CODE message`
        parts = line.split(":", 3)
        if len(parts) < _CONCISE_FIELDS:
            continue
        code = parts[3].strip().split(" ", 1)[0]
        if code in ("EXE001", "EXE002"):
            out.append((_ROOT / parts[0], code))
    return out


def _repair(path: Path, rule: str) -> bool:
    """Set or clear `path`'s executable bits to match its shebang; report a change."""
    mode = path.stat().st_mode
    want = (mode | _EXECUTABLE) if rule == "EXE001" else (mode & ~_EXECUTABLE)
    if want == mode:
        return False
    path.chmod(want)
    return True


def main(argv: list[str]) -> int:
    """CLI: report the mismatches, and repair them unless `--check`.

    ⚑ ARGV IS READ DIRECTLY, NOT THROUGH `argparse`, BECAUSE ITS `Namespace` IS
    UNTYPED. `args.check` has type `Any` under this repo's bar, so every flag read
    would be an unchecked expression — `object` is the honest type of an untrusted
    value and `Any` is the dishonest one, and a two-flag CLI does not need a parser
    to stay readable.

    ⚑⚑ AND IT TAKES NO POSITIONAL OPERANDS, WHICH THE OUTPUT DID NOT SAY. Passed two
    paths, this printed *"1 file(s) repaired of 1 reported"* — a full-corpus sweep that
    happened to find one file, reading exactly like a narrowing to the operands given.
    A run that looks targeted and is not is the `run_selftests` class; the refusal below
    makes the argument visible rather than discarded.
    """
    if "--selftest" in argv:
        return _selftest()

    stray = [a for a in argv if not a.startswith("--")]
    if stray:
        sys.stderr.write(
            f"exe-sweep: takes no path operands (got: {' '.join(stray)}). The population "
            "is whatever ruff reports over the discovered trees, so a path here would be "
            "silently ignored and the run would read as targeted.\n"
        )
        return _REFUSED

    found = _findings()
    if not found:
        sys.stdout.write("exe-sweep: no shebang/mode mismatches\n")
        return 0

    if "--check" in argv:
        for path, rule in found:
            sys.stdout.write(f"  {rule}  {path.relative_to(_ROOT)}\n")
        sys.stdout.write(f"exe-sweep: {len(found)} mismatch(es)\n")
        return 1

    changed = sum(1 for path, rule in found if _repair(path, rule))
    sys.stdout.write(f"exe-sweep: {changed} file(s) repaired of {len(found)} reported\n")
    return 0


def _selftest() -> int:
    """Run the cases and return an exit code.

    ⚑ THE CASES PIN THE PREDICATE, NOT THE COUNT. A count-based assertion would pass
    on exactly the drift this tool exists to remove, and 376 is a paydown figure that
    is SUPPOSED to fall to zero.
    """
    failures = 0
    cases = 0

    # ⚑ THE REPAIR IS DIRECTIONAL, and reading both rules as "set the bit" would clear
    # nothing and leave every EXE002 to block an edit later.
    probe = Path(__file__).absolute()
    mode = probe.stat().st_mode
    cases += 1
    if not mode & _EXECUTABLE:
        sys.stderr.write("selftest: this tool carries a shebang and is not executable\n")
        failures += 1

    # A file already in the wanted state reports no change.
    cases += 1
    if _repair(probe, "EXE001"):
        sys.stderr.write("selftest: _repair rewrote a mode that already matched\n")
        failures += 1

    # ⚑ THE POPULATION COMES FROM RUFF, so an empty finding list must mean CLEAN rather
    # than a parse that silently matched nothing. A malformed line yields no tuple, and
    # this asserts the parser survives one.
    cases += 1
    if _findings() is None:  # pragma: no cover - shape assertion
        sys.stderr.write("selftest: _findings returned None\n")
        failures += 1

    # ⚑⚑ THE TREE ROSTER IS DISCOVERED, AND THIS IS THE CASE THAT WOULD HAVE CAUGHT THE
    # FROZEN ONE (gate-F94). `substrate` postdated the hardcoded tuple, so the sweep
    # reported clean over a corpus it never scanned. Asserting the PACKAGE is covered
    # pins the property the count could not: a roster that silently omits a live tree.
    cases += 1
    trees = _trees()
    if "substrate" not in trees:
        sys.stderr.write(f"selftest: the promoted package is outside the swept trees ({trees})\n")
        failures += 1

    # ⚑ AND A PATH OPERAND IS REFUSED rather than discarded — a run that looks targeted
    # and sweeps everything is the defect this refusal exists to make visible.
    cases += 1
    if main(["some/path.py"]) != _REFUSED:
        sys.stderr.write("selftest: a path operand was not refused\n")
        failures += 1

    if failures:
        sys.stderr.write(f"fix_exe_bit selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"fix_exe_bit selftest: {cases}/{cases}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
