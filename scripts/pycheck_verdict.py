#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run one checker process and return a three-valued verdict.

⚑⚑ THIS MODULE EXISTS TO BE THE PYCHECK HOOK'S SOLE SUBPROCESS CALLER, AND THAT IS
ITS WHOLE RESPONSIBILITY. The operator's ruling is *"we don't do line-scoped
overrides; we have ecosystem-wide standards, and, if necessary, SRP per-file
overrides."* A per-file override is only honest when the file has ONE responsibility,
so the override and the decomposition are the same act: exempting `hook_pycheck.py`
as a monolith would have granted the exemption to six responsibilities to cover one.

⚑ THAT IS THE IMPORT BAN'S ARGUMENT IN ANOTHER LANGUAGE. A `per-file-ignores` entry
is a `using` list: it does not narrow what is exempted, it narrows what is VISIBLE
as a finding while the whole file stays covered. Decomposition is what makes the
override honest, exactly as it is what makes a bare import possible.

⚑⚑ AND THE `noqa` IS GONE — THAT WAS THE POINT. The S603 suppression that sat on the
monolith's call site for a day now lives in `pyproject.toml`, keyed to this path, and
is reachable because the checkers are told the author's real filename
(`pycheck_checkers`'s `--stdin-filename`). Ecosystem standard, per-responsibility
scope, no line-scoped override anywhere.

⚑⚑⚑ TWO INDIRECTIONS WERE TRIED TO MAKE S603 NOT FIRE SYNTACTICALLY, AND BOTH COST
MORE THAN THEY BOUGHT — recorded so the next reader does not retry them. Binding
`subprocess.run` to a name removes the call site, and the binding is an `Any` (an
overloaded function), which silently un-checks every argument at the call site. A
`Protocol` typing that binding fixes the `Any`, fails to match the real overload
(`args`, not `argv`), and trips a parameter-count rule of its own. **Moving a call to
dodge a syntactic rule costs the call its type**, which is a strictly worse trade
than the finding it avoids. The direct spelling stays; the scope is the fix.

⚑⚑⚑ THE WORKING DIRECTORY IS AMBIENT, NOT AN ARGUMENT (operator, 2026-08-31:
*"Contextvars; don't thread."*). A first cut gave this function a `cwd=` parameter and
passed it down from the analyser, which makes every intermediate signature carry a
value it does not use and obliges every future caller to relay a decision made
upstream. `checker_context` holds it for the logical run instead.
"""

from __future__ import annotations

import subprocess

from scripts import checker_context

# A checker's verdict: True clean / False findings / None could-not-run, and a report.
Verdict = tuple[bool | None, str]

# ruff and mypy both use 1 for "flagged something"; anything else is not a finding.
FLAGGED_EXIT = 1

TIMEOUT_S = 120


def run_checker(name: str, argv: list[str], stdin_text: str | None = None) -> Verdict:
    """Run one checker and return ran-clean / ran-and-flagged / could-not-run.

    ⚑ THE TRISTATE IS THE POINT AND IT IS NOT A CONVENIENCE. `False` (findings) and
    `None` (checker absent) must never merge: the first is a verdict this hook is
    built to enforce, the second is an UNKNOWN it must not convert into one. A
    two-valued return forces the caller to spell one of them as the other, which is
    exactly how `check_mypy_ratchet` exits 0 on 116 errors.

    ⚑ `stdin_text` FEEDS A CHECKER THAT READS `-`. ruff is invoked with
    `--stdin-filename <real path>` so its path-keyed configuration resolves against
    the author's file rather than a tempfile; that spelling requires the source on
    stdin. mypy takes a path and passes `None`.

    ⚑⚑⚑ THE WORKING DIRECTORY IS READ FROM CONTEXT, AND NAMING A CONFIG IS NOT ENOUGH.
    A config's RELATIVE paths — `namespace-packages`, `exclude`, `src` — resolve
    against the working directory. MEASURED 2026-08-31: a sibling repo declaring
    `namespace-packages = ["src/mikemol"]` had it honoured when the checker ran FROM
    that repo and IGNORED when the same file and the same `--config` were passed from
    elsewhere, so `INP001` fired on a deliberate PEP 420 namespace and demanded the
    `__init__.py` whose absence is that package's whole design. **Config, staging
    directory and working directory are one decision.**

    ⚑ UNBOUND MEANS THIS PROCESS'S DIRECTORY, which is what an in-repo edit always got.
    """
    try:
        # ⚑ S603 CANNOT SEE WHETHER AN ARGV WAS VALIDATED — its own documentation
        # says so, citing astral-sh/ruff#4045 under *Known problems*. Here it was:
        # every element is a module constant or a `mkstemp` path the hook created,
        # and the untrusted payload becomes the tempfile's CONTENTS — data the
        # checker reads — never a word in the command. The exemption is in the
        # config, scoped to this single-responsibility file.
        #
        # ⚑ NOT `shell=True`, which is the fix that looks obvious and is wrong: that
        # is S602's subject and would trade a lint finding for a REAL injection
        # vector. The argv-list form is the safe one and stays.
        p = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            input=stdin_text,
            timeout=TIMEOUT_S,
            check=False,
            cwd=checker_context.project(),
        )
    except FileNotFoundError:
        return None, f"{name} is not installed in the project venv"
    except (OSError, subprocess.SubprocessError):
        return None, f"{name} could not run"
    if p.returncode == 0:
        return True, ""
    # ⚑⚑ AN ABSENT MODULE EXITS 1, NOT 127 — AND THAT COLLAPSED UNKNOWN INTO A
    # FINDING IN THIS HOOK'S FIRST RUN. `_VENV_PY -m ruff` with ruff uninstalled
    # prints `No module named ruff` and exits **1**, which the returncode test below
    # reads as "flagged something", so the very first dogfood reported the hook as
    # DIRTY when the truth was that a checker was ABSENT. `FileNotFoundError` does
    # not fire either: the INTERPRETER exists, only the module does not.
    #
    # ⚑ THAT IS THE `check_mypy_ratchet` COLLAPSE WITH THE ARROW REVERSED — that
    # ratchet spells FINDINGS as PASS, this spelled ABSENT as FINDINGS — and both
    # come from a verdict channel too narrow to carry the third state. A tristate in
    # the RETURN TYPE does not help if the thing computing it cannot tell the states
    # apart, which is why this test is here and not merely documented.
    if "No module named" in (p.stderr or ""):
        return None, f"{name} is not installed in the project venv"
    # ⚑ A NON-ZERO EXIT IS NOT AUTOMATICALLY A FINDING. ruff and mypy both use 1 for
    # "flagged something" and 2 for "could not run" (a config error, an unreadable
    # path, a duplicate module name). Reading 2 as a finding would report a broken
    # invocation as dirty code — and reading it as clean would be the fail-open this
    # hook exists to refuse. Neither: it is UNKNOWN.
    if p.returncode != FLAGGED_EXIT:
        detail = (p.stderr or p.stdout or "").strip()[:200]
        return None, f"{name} exited {p.returncode}: {detail}"
    return False, f"--- {name} ---\n{p.stdout}{p.stderr}"
