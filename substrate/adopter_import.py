#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which installed modules an ADOPTER can actually import, and why each failure fails.

⚑⚑⚑ THIS IS A RUNTIME PROBE, AND EVERY OTHER IMPORT READER HERE IS STATIC. `import_edges`,
`import_reach`, `import_manifest` and `self_import` all parse source and resolve names against
the working tree — so all four answer questions about THIS CHECKOUT and none of them can see
what an installed distribution does when a foreign interpreter actually executes it. The
distinction is not pedantic: a module whose import-time body reads a repo-relative path, opens
a store, or reaches for a sibling checkout PARSES clean in every static reader and raises under
an adopter. Only running the import finds those.

⚑⚑ EACH MODULE IS PROBED IN ITS OWN SUBPROCESS, and that is a correctness requirement rather
than isolation hygiene. A module that dies partway through its import leaves a half-initialised
entry in `sys.modules`, and the next module importing it gets that corpse instead of a fresh
attempt — so a single-process sweep reports the FIRST failure honestly and everything downstream
of it as a fact about the sweep. `sys.modules` cannot be un-poisoned from inside the process
that poisoned it, which is why there is no cheaper spelling.

⚑ THE FAILURE KIND IS THE DELIVERABLE, NOT THE COUNT. A bare ratio tells an adopter nothing they
can act on; `ModuleNotFoundError` on an undeclared dependency, `FileNotFoundError` on a
repo-relative path read at import time, and `ImportError` on a circular edge are three different
remedies owned by three different people. The renderer therefore groups by exception type and
never emits a ratio without the named groups beside it.

⚑ AND AN EMPTY FAILURE LIST IS A FACT ABOUT THE PROBE'S POPULATION. This reader can only probe
what `find_spec` locates in the INSTALLED distribution; a module excluded from `packages` in
`pyproject.toml` is not reported as broken, it is not reported at all. `--population` prints
what would be swept, so an absence reads as absence rather than as success.

⚑⚑⚑ `--reach-back` IS THE PAYDOWN QUEUE, AND IT EXISTS BECAUSE THE FAILURES ARE NOT A BUG LIST.
`scratch/` is a STAGING AREA that must be DRAINED into `substrate/`, and its absence from
`packages` is a deliberate constraint rather than an oversight — packaging it, or shimming bare
`scratch` names into resolution, would license permanent dependence on the staging area and
freeze a drain that is actively running. So a packaged module that cannot import under an
adopter is not broken: it is one still reaching BACK into the staging area, and the list of
those is a paydown queue with a natural finish.

⚑⚑ THE GROUPING IS BY THE MODULE DEPENDED UPON, NOT BY THE MODULE FAILING, and that inversion is
the whole point. Grouped by the failing module the list is a pile of unrelated breakages; grouped
by the callee it is a RANKING — the staging module with the most consumers is the drain that
unblocks the most work, and the one with a single consumer is the drain that can be finished
without coordinating anyone. Both readings are useful and neither is visible in the other
grouping.

⚑ AND `--reach-back` DOES NOT ASSUME THE CALLEE IS IN `scratch/`. It reports every module-scope
import that does not resolve as a packaged name, whatever tree it lives in — because the
assumption failed the first time it was made here. Four of this package's own failures name
`gen_build_makefiles`, which lives in `scripts/` and IS packaged; they fail on the bare SPELLING,
not on the staging area, and a reader that had filtered to `scratch/` would have reported them as
drain debt and hidden a defect fixable today.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from mikemol.corpus import import_edges

# The probe body the child interpreter runs. It writes the exception TYPE on the first
# line and the message on the second, so the parent never has to parse a traceback.
CHILD = (
    "import importlib,sys\n"
    "try:\n"
    "    importlib.import_module(sys.argv[1])\n"
    "except BaseException as exc:\n"
    "    sys.stderr.write(type(exc).__name__+chr(10)+str(exc)[:300].replace(chr(10),' '))\n"
    "    raise SystemExit(1) from None\n"
)

# How long one import may take before the probe calls it a failure. An import that
# blocks this long is doing work no import should do, which is itself the finding.
TIMEOUT_S = 120

# The verdict recorded when the import returned cleanly.
CLEAN = "OK"

# The packages probed when the caller names none — the two this project declares.
DEFAULT_PACKAGES = ("substrate", "scripts")


@dataclass(frozen=True)
class Probe:
    """One module's runtime import result under the installed distribution."""

    module: str
    verdict: str
    detail: str

    @property
    def clean(self) -> bool:
        """Whether the module imported without raising."""
        return self.verdict == CLEAN


@dataclass(frozen=True)
class ReachBack:
    """One unpackaged module a packaged tree still imports, and who imports it."""

    depended: str
    consumers: tuple[str, ...]

    @property
    def thin(self) -> bool:
        """Whether a single consumer reaches for this — the cheapest drain to finish.

        ⚑ THIN MEANS FEW CONSUMERS, NOT A SMALL CALLEE, and the two rank OPPOSITELY. A
        one-consumer edge is drainable without coordinating anyone else; a many-consumer
        edge unblocks the most modules per drain. Both are worth doing and this property
        answers only the first — a caller wanting the second reads `len(consumers)`.
        """
        return len(self.consumers) == 1


@dataclass(frozen=True)
class Request:
    """The command line this reader was invoked with, with argparse's `Any` walled off."""

    packages: tuple[str, ...]
    census_only: bool
    reach_back: bool


def _dotted(root: Path, path: Path, package: str) -> str:
    """Return the dotted name a file under an installed package root carries."""
    parts = list(path.relative_to(root).parts)
    if parts[-1] == "__init__.py":
        parts.pop()
    else:
        parts[-1] = parts[-1].removesuffix(".py")
    return ".".join([package, *parts])


def sources(package: str) -> dict[str, str]:
    """Return `{dotted module name: its file}` for the INSTALLED `package`.

    ⚑ This walks the located distribution, never the working tree, so a module present in
    the checkout but absent from `packages` is simply not in the population.
    """
    spec = importlib.util.find_spec(package)
    if spec is None or spec.submodule_search_locations is None:
        return {}
    found: dict[str, str] = {}
    for location in spec.submodule_search_locations:
        root = Path(location)
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            found[_dotted(root, path, package)] = str(path)
    return found


def population(package: str) -> list[str]:
    """Return every importable dotted name the INSTALLED `package` contains, sorted."""
    return sorted(sources(package))


def probe(module: str) -> Probe:
    """Import `module` in a fresh interpreter and return what happened."""
    try:
        done = subprocess.run(  # noqa: S603 - fixed argv built in this file, never a shell
            [sys.executable, "-c", CHILD, module],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Probe(module, "Timeout", f"no result in {TIMEOUT_S}s")
    if done.returncode == 0:
        return Probe(module, CLEAN, "")
    lines = done.stderr.splitlines()
    verdict = lines[0].strip() if lines else f"exit{done.returncode}"
    detail = lines[1].strip() if len(lines) > 1 else ""
    return Probe(module, verdict, detail)


def sweep(package: str) -> list[Probe]:
    """Probe every module of the installed `package`."""
    return [probe(name) for name in population(package)]


def by_verdict(probes: list[Probe]) -> dict[str, list[Probe]]:
    """Group the failures by exception type, dropping the clean ones."""
    grouped: dict[str, list[Probe]] = {}
    for item in probes:
        if item.clean:
            continue
        grouped.setdefault(item.verdict, []).append(item)
    return dict(sorted(grouped.items()))


def _resolvable(name: str, packages: tuple[str, ...]) -> bool:
    """Whether a module-scope import name resolves for an adopter.

    ⚑ A name resolves when it is a packaged module of this distribution, or when the
    interpreter can already find it (stdlib, or a declared third-party dependency). Anything
    else is a reach into a tree the wheel does not carry.
    """
    if name in packages or name.split(".", 1)[0] in packages:
        return True
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def reach_backs(packages: tuple[str, ...]) -> list[ReachBack]:
    """Return every unpackaged module the packaged trees import at module scope.

    ⚑ MODULE SCOPE ONLY, because that is what an adopter's `import` actually executes. A
    deferred import inside a function is a different obligation with a different remedy, and
    `import_edges` keeps the two apart precisely so one boolean never answers both.
    """
    consumers: dict[str, set[str]] = {}
    for package in packages:
        for module, path in sources(package).items():
            for name in import_edges.module_level(path):
                if _resolvable(name, packages):
                    continue
                consumers.setdefault(name, set()).add(module)
    ranked = [ReachBack(name, tuple(sorted(who))) for name, who in consumers.items()]
    ranked.sort(key=lambda item: (-len(item.consumers), item.depended))
    return ranked


def clean_modules(packages: tuple[str, ...]) -> list[str]:
    """Return the packaged modules reaching for NOTHING unpackaged — usable by an adopter now.

    ⚑ THIS IS THE POSITIVE READING, AND IT IS THE ONE THE COUPLING ARGUMENT TURNS ON. A failure
    list says what is owed; this says what another repo can depend on TODAY, which is the
    question that decides whether vendoring can stop.
    """
    blocked = {who for item in reach_backs(packages) for who in item.consumers}
    every = {name for package in packages for name in sources(package)}
    return sorted(every - blocked)


def render(package: str, probes: list[Probe]) -> str:
    """Render the sweep, keeping every failure NAMED beside the ratio."""
    if not probes:
        return f"{package}: not installed, or the distribution contains no modules"
    clean = [item for item in probes if item.clean]
    out = [f"{package}: {len(clean)} of {len(probes)} module(s) import from a foreign cwd"]
    grouped = by_verdict(probes)
    if not grouped:
        out.append("  every module in the installed population imported")
        return "\n".join(out)
    for verdict, items in grouped.items():
        out.append(f"  {verdict:<24} : {len(items)}")
        for item in items:
            out.append(f"    {item.module}")
            if item.detail:
                out.append(f"      {item.detail}")
    return "\n".join(out)


def render_reach(packages: tuple[str, ...]) -> str:
    """Render the paydown queue: which unpackaged module blocks how many consumers."""
    found = reach_backs(packages)
    usable = clean_modules(packages)
    if not found:
        return f"no packaged module imports an unpackaged name; all {len(usable)} are usable"
    blocked = sorted({who for item in found for who in item.consumers})
    header = (
        f"{len(found)} unpackaged name(s) reached at module scope, "
        f"blocking {len(blocked)} of {len(blocked) + len(usable)} packaged module(s); "
        f"{len(usable)} usable by an adopter today"
    )
    out = [header]
    for item in found:
        mark = "  THIN" if item.thin else ""
        out.append(f"  {item.depended:<28} {len(item.consumers)} consumer(s){mark}")
        out.extend(f"    {who}" for who in item.consumers)
    return "\n".join(out)


def parsed() -> Request:
    """Return the invocation as concrete types.

    ⚑ `argparse.Namespace` attributes are `Any`, which this project's mypy settings forbid
    from being spelled OR propagated. The casts here are the wall: every expression
    downstream of this function is concrete, so the untyped surface stops at one boundary
    instead of leaking into the render path.
    """
    parser = argparse.ArgumentParser(description="probe an installed package's importability")
    parser.add_argument("packages", nargs="*", help="installed packages to probe")
    parser.add_argument(
        "--population",
        action="store_true",
        help="print what WOULD be swept, so an absence reads as absence",
    )
    parser.add_argument(
        "--reach-back",
        action="store_true",
        help="rank the unpackaged names the packaged trees still import, by consumer count",
    )
    namespace = parser.parse_args()
    named = tuple(cast("list[str]", namespace.packages))
    return Request(
        named or DEFAULT_PACKAGES,
        cast("bool", namespace.population),
        cast("bool", namespace.reach_back),
    )


if __name__ == "__main__":
    _request = parsed()
    if _request.reach_back:
        sys.stdout.write(render_reach(_request.packages) + "\n")
    else:
        for _package in _request.packages:
            if _request.census_only:
                sys.stdout.write("".join(f"{_name}\n" for _name in population(_package)))
            else:
                sys.stdout.write(render(_package, sweep(_package)) + "\n")
    sys.exit(0)
