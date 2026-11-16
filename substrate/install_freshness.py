#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether an installed copy still matches the working tree it was built from.

⚑⚑⚑ THIS IS THE ACCEPTED WEAKNESS OF A LOCAL NON-EDITABLE INSTALL, MADE OBSERVABLE. Adopters
install from this checkout rather than a published package, deliberately: a reinstall is then a
DELIBERATE ACT, so a refactor here stops reaching them until they choose to take it. That
decoupling is the whole point — but it buys itself a cost, which is that `site-packages`
silently diverges from the tree. A developer editing `substrate/md_spans.py` and running an
adopter's copy gets the OLD behaviour with no signal at all, and every symptom of that looks
like a bug in the code they are reading rather than in the copy they are running.

⚑⚑ THE VERSION NUMBER CANNOT CARRY THIS, WHICH IS WHY THIS FILE EXISTS. Measured while building
it: three successive reinstalls of genuinely different trees all reported `substrate-tooling`
at the same version. A hand-maintained version stamp is a promise to remember, and the failure
mode of a forgotten bump is a copy that reads FRESH while being stale — strictly worse than no
mechanism, because it converts an unanswered question into a confidently wrong answer.

⚑⚑⚑ SO THE COMPARISON IS AGAINST A DIGEST NOTHING HAS TO REMEMBER TO UPDATE, AND THE PACKAGING
TOOLING ALREADY WRITES IT. Every wheel install leaves a `RECORD` holding a sha256 of each
installed file, and `direct_url.json` records the source directory it was built from. Both are
produced as a side effect of installing — no stamp to bump, no build step to add, and nothing a
refactor can forget. This reader digests the tree's current files and compares.

⚑ A MISSING SOURCE TREE IS `UNVERIFIABLE`, NEVER `FRESH`. An adopter on a different machine has
the install and not the checkout, so the comparison cannot be made — and that is a fact about
the READING, not a verdict about the copy. Reporting it as fresh would be the census-green
failure exactly: a fact about the instrument banked as a fact about the substrate.

⚑ AND A FILE THE TREE NO LONGER HAS IS REPORTED SEPARATELY FROM ONE WHOSE CONTENT MOVED. They
are different events with different remedies — a DELETED module means the adopter is holding
code that has been withdrawn, a CHANGED one means they are holding an older version of code
that still exists. One count over both tells an operator to do nothing in particular.

⚑⚑⚑ AND THE TOOLS THIS TREE SHELLS OUT TO ARE PART OF THE INSTALL, SO `--binaries` NAMES THEM
(gate-G386/G387, by operator ruling over a `mise.toml` and over a documented install step). The
tree moved hosts and three external tools were simply not there. Each had been a global binary on
the old machine that nothing recorded, and each failed in a DIFFERENT way:

  - `ruff` is run as `python -m ruff` through the venv, and it was absent from `pyproject`. With
    it missing, the per-file gate ran mypy alone and the promotability census read 69 where it
    had read 735 — a FALSE GREEN that would have promoted 666 modules the gate refused the day
    before. Now a declared dev dependency, and a pip package the venv can answer for.
  - `pandoc` is a bare PATH binary. Every `md_*` reader dies at `FileNotFoundError`, and the
    `md_*` suites SKIP loudly — the honest failure, but nine roster rows moved.
  - `shellcheck` is a PATH binary with a mise-shim fallback. `hook_shellcheck` announces itself
    `ARMED BUT INERT` and fails open by its own stated rule — loud, and still half a hook.

⚑⚑ THE ROSTER IS DECLARED HERE BECAUSE A STATIC WALK CANNOT SEE IT. `pycheck_show` builds its
argv from `_VENV_PY` and `"-m"`, so an AST reader finds `subprocess.run(argv, …)` and no head
to name. `hook_shellcheck` resolves through `shutil.which` then a shim path. The exec sites are
real and the binaries they need are NOT recoverable from the sites by a reader — so the roster
is typed, with each entry naming HOW it resolves, and the cost of that is the cost this file
already accepts for the digest check: something a human must update when a gate grows a new
dependency. A roster that reads ABSENT for a tool the tree does not use is a stale roster, and
that is visible; a walk that reads PRESENT for a tool it could not see is not.

⚑ A MODULE-RESOLVED TOOL IS ASKED OF THE INTERPRETER, A PATH TOOL OF THE PATH — and the two
are never conflated, because `shutil.which("ruff")` finding a system ruff says nothing about
whether `python -m ruff` in THIS venv works, which is the invocation the gate actually makes.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from importlib import metadata
from importlib.util import find_spec
from pathlib import Path

from substrate import build_settings

# The distribution whose freshness this reader answers for.
DISTRIBUTION = "substrate-tooling"

# The metadata files the packaging tooling writes, and what each one supplies.
RECORD = "RECORD"
DIRECT_URL = "direct_url.json"

# The prefix a local-directory install records as its source.
FILE_URL = "file://"

# How a `RECORD` row spells the digest it carries.
SHA_PREFIX = "sha256="

# The fields a usable `RECORD` row must have: the path and its digest.
ROW_FIELDS = 2

# What a reading can conclude. ⚑ UNVERIFIABLE is not a degraded FRESH — it is the
# separate verdict that says the comparison could not be made at all.
FRESH = "FRESH"
STALE = "STALE"
UNVERIFIABLE = "UNVERIFIABLE"

# How an installed file can differ from the tree. ⚑ Kept apart because the remedies differ.
CHANGED = "CHANGED"
DELETED = "DELETED"

# How an external tool is reached. ⚑ THREE KINDS, NEVER CONFLATED: a module is asked of THIS
# interpreter, a binary of the PATH, and a script of the TREE — and a hit for one says nothing
# about the others. `membudget` first landed in this roster as a BINARY and read ABSENT on a
# host where it sits in `scripts/`, which is a roster defect the kind exists to make impossible.
MODULE = "module"
BINARY = "binary"
SCRIPT = "script"

# Where a SCRIPT tool lives, relative to the package's parent — the repo root.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

# A script whose path has a single authority is resolved through it, not through `_SCRIPTS / name`.
_SCRIPT_AUTHORITY: dict[str, Path] = {"membudget": build_settings.MEMBUDGET}
_MEMBUDGET_REL = build_settings.MEMBUDGET.relative_to(build_settings.ROOT).as_posix()

# Any execute bit — owner, group or other. A script is PRESENT only when it can run.
_EXEC_BITS = 0o111


def _runnable(script: Path) -> bool:
    """Report whether a tree script exists AND carries an execute bit.

    ⚑ EXISTENCE IS NOT PRESENCE. The exe-bit sweep exists because a rewrite drops the bit,
    and a script that is on disk but not runnable starves its consumers exactly as an absent
    one does — `make` invoking a non-executable `membudget` shim fails the same way.
    """
    return script.is_file() and bool(script.stat().st_mode & _EXEC_BITS)


# The tools this tree shells out to, each with the resolution the calling site actually uses
# and the gate or reader family that dies without it. ⚑ DECLARED, NOT WALKED — see the header
# for why a static reader cannot recover these from the exec sites.
REQUIRED: tuple[tuple[str, str, str], ...] = (
    ("ruff", MODULE, "pycheck_show, hook_pycheck — the per-file gate's ruff half"),
    ("mypy", MODULE, "pycheck_show, type_gate, check_stub_authority — mypy and its stubtest"),
    ("pandoc", BINARY, "md_pandoc and every md_* reader, the markdown-sync gates"),
    ("shellcheck", BINARY, "mikemol-hook-shellcheck (mtools) — the PreToolUse Bash/edit guard"),
    # ⚑ THE BUILD'S THREE. A literal census of `subprocess.run` over 18 ratchet gates found
    # only ruff, mypy and `sys.executable` — the Phase A gates need nothing else. Phase C
    # (`cap ratchet`, `Set₁ ratchet`) reads cores the BUILD produces, and `agda_build.build`
    # runs `make -C agda`, whose generated recipes call `agda` through the `membudget` shim.
    ("make", BINARY, "agda_build — the full build the Phase C core-reading gates depend on"),
    ("agda", BINARY, "every typecheck; the makefiles resolve it via the membudget PATH shim"),
    (
        "membudget",
        SCRIPT,
        f"{_MEMBUDGET_REL} — the RAM semaphore every agda compile leases from",
    ),
    # ⚑ THE SEMAPHORE'S PEAK PROBE, WHICH ITS ABSENCE MADE INVISIBLE (gate-G450, W24). membudget
    # measures each lease's maxRSS through `/usr/bin/time -v`; without it every peak records as
    # 0, so the autobudget's history is blind and every autosized lease starts at the 64 MB
    # floor. Nothing died, nothing refused — the instrument quietly measured nothing, which is
    # exactly the case this roster exists to name.
    ("time", BINARY, f"{_MEMBUDGET_REL} — the maxRSS probe the autobudget sizes every lease from"),
)

# Where `hook_shellcheck` falls back to when PATH has nothing. Mirrored, not imported: this
# reader must load on a host where that hook's own imports do not.
_MISE_SHIM = Path("~/.local/share/mise/shims").expanduser()

# The flag that asks about external tools rather than installed files.
BINARIES = "--binaries"


@dataclass(frozen=True)
class Divergence:
    """One installed file that no longer matches the tree."""

    relpath: str
    kind: str


@dataclass(frozen=True)
class Reading:
    """Whether an installed copy still matches its source tree, and what differs."""

    verdict: str
    source: str
    changed: tuple[Divergence, ...]
    why: str = ""

    @property
    def fresh(self) -> bool:
        """Whether the copy provably matches. ⚑ False for UNVERIFIABLE, which is not FRESH."""
        return self.verdict == FRESH


@dataclass(frozen=True)
class Tool:
    """One external tool the tree needs: how it is reached, and whether it is."""

    name: str
    kind: str
    needed_by: str
    found: str

    @property
    def present(self) -> bool:
        """Whether the tool resolves the way its calling site resolves it."""
        return bool(self.found)


def _record_digest(path: Path) -> str:
    """Return a file's digest in the urlsafe-base64 form `RECORD` uses."""
    raw = hashlib.sha256(path.read_bytes()).digest()
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def source_tree(dist: metadata.Distribution) -> str:
    """Return the local directory this distribution was installed from, or the empty string.

    ⚑ THE `Any` FROM `json.loads` IS NARROWED HERE, AT THE SEAM. A raw return would carry it
    into every field read downstream — the recorded boundary shape.
    """
    text = dist.read_text(DIRECT_URL)
    if not text:
        return ""
    try:
        parsed: object = json.loads(text)
    except ValueError:
        return ""
    if not isinstance(parsed, dict):
        return ""
    url = parsed.get("url")
    if not isinstance(url, str) or not url.startswith(FILE_URL):
        return ""
    return url[len(FILE_URL) :]


def recorded(dist: metadata.Distribution) -> dict[str, str]:
    """Return `{relpath: recorded digest}` for every installed file that carries one.

    ⚑ Entries without a digest are SKIPPED rather than defaulted. `RECORD` leaves the hash
    empty for files the installer generates itself, and inventing a value for those would
    manufacture a divergence the tree never had.
    """
    text = dist.read_text(RECORD)
    if not text:
        return {}
    found: dict[str, str] = {}
    for row in csv.reader(text.splitlines()):
        if len(row) < ROW_FIELDS or not row[1].startswith(SHA_PREFIX):
            continue
        found[row[0]] = row[1].removeprefix(SHA_PREFIX)
    return found


def compare(dist: metadata.Distribution) -> Reading:
    """Return whether the installed copy still matches the tree it was built from."""
    root = source_tree(dist)
    if not root:
        return Reading(UNVERIFIABLE, "", (), "no local source directory recorded for this install")
    tree = Path(root)
    if not tree.is_dir():
        return Reading(UNVERIFIABLE, root, (), f"the recorded source tree is not present: {root}")
    entries = recorded(dist)
    if not entries:
        return Reading(UNVERIFIABLE, root, (), "the install records no file digests")
    moved: list[Divergence] = []
    for relpath, digest in sorted(entries.items()):
        if not relpath.endswith(".py"):
            continue
        current = tree / relpath
        if not current.is_file():
            moved.append(Divergence(relpath, DELETED))
        elif _record_digest(current) != digest:
            moved.append(Divergence(relpath, CHANGED))
    verdict = STALE if moved else FRESH
    return Reading(verdict, root, tuple(moved))


def reading(name: str = DISTRIBUTION) -> Reading:
    """Return the freshness reading for one installed distribution."""
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        return Reading(UNVERIFIABLE, "", (), f"{name} is not installed in this environment")
    return compare(dist)


def locate(name: str, kind: str) -> str:
    """Return where a tool resolves the way its calling site resolves it, or empty.

    ⚑ A MODULE IS ASKED OF THIS INTERPRETER, NEVER OF THE PATH. `python -m ruff` in the venv
    is the invocation the gate makes, and a system `ruff` on PATH does not satisfy it — so a
    PATH hit for a MODULE tool would be a false PRESENT of exactly the shape this mode exists
    to refuse. A BINARY is asked of the PATH first, then of the mise shim directory that
    `hook_shellcheck` falls back to, because mise tools are not on a non-interactive PATH.
    """
    if kind == MODULE:
        try:
            spec = find_spec(name)
        except (ImportError, ValueError):
            return ""
        return spec.origin or name if spec is not None else ""
    if kind == SCRIPT:
        script = _SCRIPT_AUTHORITY.get(name, _SCRIPTS / name)
        return str(script) if _runnable(script) else ""
    on_path = shutil.which(name)
    if on_path:
        return on_path
    shim = _MISE_SHIM / name
    return str(shim) if shim.is_file() else ""


def tools(roster: tuple[tuple[str, str, str], ...] = REQUIRED) -> tuple[Tool, ...]:
    """Return every required tool with where it resolved, in roster order."""
    return tuple(
        Tool(name, kind, needed_by, locate(name, kind)) for name, kind, needed_by in roster
    )


def render_tools(found: tuple[Tool, ...]) -> str:
    """Render the tool census, naming every absence and what it takes down.

    ⚑ THE DENOMINATOR IS PRINTED EITHER WAY, so a clean line reads as a census over N tools
    rather than as silence — and an absence names the family it starves, because a bare
    ABSENT tells an operator to do nothing in particular.
    """
    missing = [tool for tool in found if not tool.present]
    out = [f"{'tool':<12} {'kind':<7} {'where':<48} needed by"]
    out.extend(
        f"{tool.name:<12} {tool.kind:<7} {(tool.found or '⚑ ABSENT'):<48} {tool.needed_by}"
        for tool in found
    )
    verdict = (
        f"{len(missing)} of {len(found)} required tool(s) ABSENT"
        if missing
        else f"all {len(found)} required tool(s) present"
    )
    out.append(f"\n{verdict}")
    if missing:
        out.append(
            "  ⚑ A MODULE tool is installed with `uv add`; a BINARY tool is a system "
            "package or a mise tool — `uv` cannot declare it, so its absence is a "
            "fact about THIS HOST that nothing in the tree records."
        )
    return "\n".join(out)


def render(found: Reading) -> str:
    """Render the reading, keeping UNVERIFIABLE visibly distinct from FRESH."""
    if found.verdict == UNVERIFIABLE:
        return f"{UNVERIFIABLE}: {found.why}"
    if found.fresh:
        return f"{FRESH}: the installed copy matches {found.source}"
    changed = [item for item in found.changed if item.kind == CHANGED]
    deleted = [item for item in found.changed if item.kind == DELETED]
    headline = (
        f"{STALE}: {len(found.changed)} file(s) differ from {found.source} — reinstall to take them"
    )
    out = [headline]
    if changed:
        out.append(f"  {CHANGED} : {len(changed)}")
        out.extend(f"    {item.relpath}" for item in changed)
    if deleted:
        out.append(f"  {DELETED} : {len(deleted)}")
        out.extend(f"    {item.relpath}" for item in deleted)
    return "\n".join(out)


if __name__ == "__main__":
    if BINARIES in sys.argv:
        _tools = tools()
        sys.stdout.write(render_tools(_tools) + "\n")
        sys.exit(0 if all(tool.present for tool in _tools) else 1)
    _name = sys.argv[1] if len(sys.argv) > 1 else DISTRIBUTION
    _found = reading(_name)
    sys.stdout.write(render(_found) + "\n")
    sys.exit(0 if _found.fresh else 1)
