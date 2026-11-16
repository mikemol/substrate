#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Stage post-edit content where the checkers can see it, and collect their verdicts.

⚑ STAGING IS ITS OWN RESPONSIBILITY: it changes when the way content reaches a
checker changes (tempfile placement, stdin, a shadow file), and that is independent
of which checkers exist, what a verdict means, or how a refusal reads.

⚑⚑ AND COMPOSING THE VERDICTS IS A SECOND ONE, SPLIT OUT AS OF ⟡the-first-none-wins.
This file COLLECTS outcomes; `pycheck_compose` decides what a set of them means. They
changed for different reasons the moment the composite stopped being "return on the
first `None`", and keeping the rule here would have hidden an ordering accident inside
a staging loop — which is exactly where it hid before.

⚑⚑ THE ROOT PRELUDE IS REQUIRED, NOT INCIDENTAL, AND DROPPING IT WAS A MEASURED
MISTAKE ON THIS FILE. `check_hook_set.py` arm 2 asserts that every file importing a
sibling carries it, because `scripts/` is a package HERE and a bare directory in an
adopting repo — where the honest spelling raises `ModuleNotFoundError` AT MODULE
LOAD, the harness reads empty stdout as ALLOW, and the gate denies nothing while
reading as armed. That is the exact failure `hook_pycheck.py` shipped by being the
missed member of the set, found by an adopter rather than by review.

⚑ AND THE `try:` IS WHAT MAKES THE PRELUDE AND THE LINTER AGREE. An import inside a
`try` is not a module-level import statement, so `E402` does not fire on the sibling
imports that must follow the `sys.path` repair — while the `except` arm is the
fail-loud path. One construct, both jobs; this is the sibling hooks' shape, matched
rather than reinvented.

⚑⚑⚑ `absolute()`, NEVER `resolve()`, AND RUFF WILL TELL YOU OTHERWISE. `PTH100`
offers `Path.resolve()` as the counterpart of `os.path.abspath`, and it is NOT one:
`resolve()` FOLLOWS SYMLINKS. While these hooks were symlinked into other checkouts,
a resolved `__file__` derived SUBSTRATE's root and a hook read substrate's data
instead of the adopting repo's.

⚑⚑⚑ AND THE CONFIG NOW FOLLOWS THE EDITED FILE RATHER THAN THIS HOOK (⟡pycheck-config-per-file).
Until 2026-08-31 the project was derived from the HOOK's location, so every file got THIS repo's
bar regardless of which repo the file lived in — invisible inside substrate, wrong in both
directions the moment a second repo is edited in the same session. MEASURED: creating a PEP 420
namespace package in a sibling repo was refused with `INP001: add an __init__.py`, correct under
substrate's config and exactly backwards for a namespace distribution, where the absent
`__init__.py` is the property the package rests on. **The hook was demanding the destruction of
the thing being built.**
"""

from __future__ import annotations

import contextlib
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from scripts import checker_context, project_root
    from scripts.pycheck_checkers import checker_argv
    from scripts.pycheck_compose import Outcome, compose
    from scripts.pycheck_syntax import syntax_error
    from scripts.pycheck_verdict import Verdict, run_checker
except ImportError as _e:  # pragma: no cover - adoption-shaped, not reachable in-repo
    # ⚑ FAIL LOUD, NEVER SILENT-ALLOW. Emitting nothing is what the harness reads as
    # permission granted; a module that cannot load must SAY so and exit non-blocking
    # rather than vanish. `check_hook_set.py --manifest` names the files a working
    # adoption requires — this module is one of six.
    sys.stderr.write(
        f"pycheck_analyze: cannot import a sibling ({_e}). The pycheck hook is "
        f"checking NOTHING. Fix: make the adopting repo's `scripts/` importable "
        f"(an `__init__.py`), or unarm the hook so it does not read as a guard it "
        f"is not.\n"
    )
    sys.exit(0)

PROJECT = _ROOT
VENV_PY = PROJECT / ".venv" / "bin" / "python3"
PYPROJECT = PROJECT / "pyproject.toml"


def project_for(path: str) -> tuple[Path, Path, Path]:
    """Return `(project, venv_python, pyproject)` governing the EDITED FILE.

    ⚑⚑ CONFIG, STAGING AND INTERPRETER ARE ONE DECISION, which is why this returns all three.
    ruff and mypy discover configuration by walking UP from the file they are handed, so a
    tempfile staged in the wrong project inherits the wrong `pyproject.toml` even when one is
    named explicitly — and the editable install that resolves a half-migrated module's sibling
    imports is the one in THAT project's venv.

    ⚑ THE FALLBACK IS THIS REPO, AND IT IS THE HONEST ONE. A file under no project at all — a
    scratch path, content with no path — still deserves a verdict, and the hook's own project is
    the only bar available. What changed is that a file WITH a project now gets ITS bar.

    ⚑ A FOREIGN PROJECT WITHOUT A VENV KEEPS THIS ONE'S INTERPRETER: its config is still the
    right bar, and this interpreter can apply it. The reverse — a foreign venv with this repo's
    config — is what must not happen, and cannot, because the three are chosen together.
    """
    root = project_root.project_for(path) if path else None
    if root is None:
        return PROJECT, VENV_PY, PYPROJECT
    venv = project_root.venv_python_for(path)
    return root, (venv if venv is not None else VENV_PY), root / project_root.MARKER


def tools_available() -> bool:
    """Report whether a verdict can be rendered at all (venv + house config present)."""
    return VENV_PY.exists() and PYPROJECT.exists()


def analyze_python(content: str, path: str = "") -> Verdict:
    """Return the verdict for the .py source `content`.

    ⚑⚑ THE TEMPFILE LIVES INSIDE THE GOVERNING PROJECT, AND THAT PLACEMENT IS LOAD-BEARING.
    ruff and mypy discover configuration by walking UP from the file they are given, so a
    tempfile outside that project gets neither its `pyproject.toml` nor its editable installs.
    Both failures are silent and both bias toward CLEAN: a weaker config finds less, and
    unresolvable sibling imports become `ignore-missing-imports` rather than errors. **A checker
    pointed at the wrong config is a checker that agrees with you.**

    ⚑ AND IT IS WHAT MAKES A HALF-MIGRATED MODULE CHECKABLE AT ALL. A module being promoted into
    a package imports siblings by package name; only a tempfile inside that project resolves
    those against the real editable install.

    ⚑⚑ THE TEMPFILE IS STILL WRITTEN EVEN FOR THE STDIN CHECKER, because mypy reads a PATH. Only
    ruff is fed on stdin (with `--stdin-filename`), so the staging cost is paid once and serves
    both.

    ⚑⚑⚑ UNPARSEABLE IS ANSWERED BEFORE A CHECKER RUNS, AND AS `False` RATHER THAN `None`.
    `pycheck_syntax` carries why it is a state of its own and why the fail-open rationale
    INVERTS on it. It is answered here rather than left to the roster because the checkers
    DISAGREE about a syntax error — ruff reports a finding and exits 1, mypy exits 2 — and a
    single authoritative answer beats reconciling two.

    ⚑⚑⚑ EVERY CHECKER NOW RUNS, AND THE COMPOSITE IS A FOLD (⟡the-first-none-wins). This loop
    used to RETURN on the first `None`, discarding findings an earlier checker had already
    collected — so a real refusal was overwritten by a later checker's inability to run, decided
    by roster ORDER rather than by evidence. `pycheck_compose.compose` carries the three arms
    and why each is not the other two; what belongs HERE is only that nothing short-circuits:
    an outcome cannot pre-empt another by arriving first if all of them are collected.
    """
    if not tools_available():
        return None, f"the project venv or pyproject.toml is absent at {PROJECT}"

    project, venv_py, pyproject = project_for(path)
    if not pyproject.exists():
        return None, f"no pyproject.toml governs {path or '<the edited file>'}"

    # ⚑⚑ THE FOURTH STATE, RESOLVED INTO THE THREE RATHER THAN ADDED BESIDE THEM. A file
    # that does not parse is not UNKNOWN — the checkers are fine and the CONTENT is broken —
    # so it belongs on the FINDINGS side, which already owns a refusal path, a bounded
    # message and a deny exit. A truncated write under ENOSPC produces exactly this shape,
    # which is the reason it must never read as clean.
    broken = syntax_error(content, path)
    if broken:
        real = path or "<the edited file>"
        return False, f"--- syntax ---\n{real}: error: {broken}  [syntax]"

    fd, tmp_name = tempfile.mkstemp(suffix=".py", dir=project)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        # ⚑ MODE FROM CONTENT, so EXE001/EXE002 (shebang-without-+x, and its
        # inverse) read TRUE rather than reporting on the tempfile's default mode.
        tmp.chmod(0o755 if content.startswith("#!") else 0o644)
        outcomes: list[tuple[str, Outcome]] = []
        # ⚑⚑ THE CHECKER RUNS **IN** THE GOVERNING PROJECT, not merely with its config, and the
        # binding is AMBIENT rather than threaded (operator: *"Contextvars; don't thread."*).
        # Relative paths inside a config — `namespace-packages`, `exclude`, `src` — resolve
        # against the working directory, so naming the config while standing elsewhere reads the
        # right rules against the wrong root. Measured on a sibling repo whose declared namespace
        # was honoured from its own directory and ignored from this one.
        for name, argv, reads_stdin in checker_argv(tmp, path, venv_py, pyproject):
            with checker_context.in_project(project):
                ok, report = run_checker(name, argv, content if reads_stdin else None)
            if ok is False:
                # ⚑ THE TEMPFILE PATH IS REWRITTEN TO THE REAL ONE. A deny message
                # naming a `tmpab12cd.py` tells the author nothing about their own
                # file, and the path is the first thing a reader looks at.
                #
                # ⚑⚑ BOTH SPELLINGS, BECAUSE REPLACING ONLY THE ABSOLUTE PATH LEFT THE
                # STEM IN EVERY FINDING FROM A CHECKER THAT RENDERS THE BARE NAME. A
                # rewrite keyed on `str(tmp)` alone fixed one checker's half and
                # silently missed the other's. Found by a selftest arm asserting the
                # author's path appears; the arm was right and the hook was wrong.
                #
                # ⚑ RUFF NO LONGER NEEDS THIS — `--stdin-filename` makes it render the
                # author's path itself. The rewrite stays for mypy, which is still
                # pointed at the tempfile until ⟡pycheck-shadow lands, and is harmless
                # where it finds nothing to replace.
                real = path or "<the edited file>"
                report = report.replace(str(tmp), real).replace(tmp.name, real)
            outcomes.append((name, (ok, report)))
        return compose(outcomes)
    finally:
        # ⚑ SUPPRESS, NOT try/except/pass — the checker asked for it (SIM105) and it
        # is the honest spelling: an unlinkable tempfile is a cleanup failure, not a
        # verdict, and must not disturb the one being returned.
        with contextlib.suppress(OSError):
            tmp.unlink()
