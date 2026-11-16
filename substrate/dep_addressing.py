#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read how each declared dependency is ADDRESSED — from an index, from git, or from nowhere.

⚑⚑⚑ THE DEFECT THIS EXISTS TO CATCH SHIPPED, AND NOTHING SAW IT (Ⓝ122b ⟡the-paperkit-dependency).
`pyproject.toml` declared a hard dependency on `paperkit` as a BARE NAME. paperkit is on no
index, so a resolver given that name searched PyPI, found nothing, and failed while naming the
WRONG CAUSE: a package that is merely UNADDRESSED reads exactly like one that does not exist. The
install worked only for a reader who already knew to install paperkit first — which made the
precondition a thing the operator says out loud rather than a thing the manifest states.

⚑⚑ A DEPENDENCY IS RESOLVABLE WHEN ITS ADDRESS IS IN THE DECLARATION, NOT WHEN A MACHINE HAPPENS
TO HOLD IT. That distinction is the whole reading. A bare name is an address only if some index
answers to it; for a package published nowhere, it is a promise that whoever installs this
already did something uninstructed. Both look identical in the manifest, which is why the check
is on the FORM of the requirement and never on an outcome.

⚑⚑⚑ AND IT DELIBERATELY DOES NOT HIT THE NETWORK, WHICH IS THE DESIGN AND NOT A SHORTCUT.
Attempting resolution would make this fail on an offline machine, behind a proxy, or against a
slow index — reporting a fact about THE MACHINE as a fact about THE REPO. That is the collapse
this repo catalogues under `census-green-is-a-fact-about-the-census` and
`report-presence-never-absence`, and a gate committing it is worse than none: its red is
unactionable and its green is unearned. The declaration is finite and reviewable in one file, so
the question asked is the one the artifact can answer.

⚑ THE FOUR FORMS, each a different verdict rather than a shade of one:

  * INDEXED — a bare PEP 508 name, with or without extras or a version specifier (`libcst`,
    `psycopg[binary]`, `salt>=3008.2`). Resolvable from the configured index. This is the common
    case and it PASSES; the point is not to make index dependencies suspicious.
  * DIRECT — a PEP 508 direct reference carrying its own URL (`name @ git+https://…`). The
    address travels IN the requirement, so no index and no install order is presupposed.
  * UNADDRESSED — a bare name for a distribution no index carries. FAILS.
  * LOCAL — a direct reference to a path on this machine (`file://`, `git+file:`). FAILS: it is
    portable-looking and unportable, the `sys.path` search defect relocated into the manifest
    where it reads as official.

⚑⚑ INDEXED AND UNADDRESSED ARE THE SAME SYNTAX, and pretending form alone separates them would
be the false census. The discriminator is `UNPUBLISHED`, an enumerable roster this repo maintains
— so the honest statement of what this gate asserts is narrower than *"every dependency
resolves"*: it asserts that NO dependency is declared as a bare name THIS REPO HAS RECORDED as
unpublished. A package nobody has recorded is unchecked, and that boundary is stated rather than
silent.

⚑ THE ROSTER'S POLARITY IS THE POINT. It lists the KNOWN-UNPUBLISHED, not the permitted. An
allowlist grandfathers debt and goes green by accretion; this grows only when someone learns a
new package is unpublished, and every entry makes the gate STRICTER. Its baseline is therefore
EMPTY by construction — there is no baseline file, because a bare unpublished name is never
admissible, and `check_stub_authority`'s framing applies verbatim: this is a BIJECTION, not a
ratchet. A dependency either carries an address or it does not.

⚑⚑⚑ AND THE READER ANSWERS ABOUT ANY MANIFEST, WHICH `main` SPENT ITS FIRST DAY NOT DOING
(Ⓝ124a ⟡dep-gate-ignores-its-operand). See `operand`.
"""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus

# ⚑ `Path` IS A RUNTIME IMPORT, NOT AN ANNOTATION-ONLY ONE, AND THAT CHANGED IN Ⓝ124a. It sat
# under `if TYPE_CHECKING:` while every use was a type hint — correct for a reader whose `main`
# read one fixed file. Honouring the operand means CONSTRUCTING a path from argv, so the guard
# became wrong the moment the argument was read. The import's placement was a faithful record of
# the defect: nothing in this module had ever built a path, because nothing had ever been given
# one.

# The manifest this reader answers about. ⚑ NAMED ONCE: a second spelling at a call site is how
# a reader starts disagreeing with the gate about what it read.
MANIFEST = corpus.ROOT / "pyproject.toml"

# Where the requirement strings live in that manifest.
PROJECT_TABLE = "project"
DEPENDENCIES_KEY = "dependencies"

# ⚑ THE PEP 508 MARKER separating a distribution name from a direct URL. The surrounding spaces
# are REQUIRED by the specification, which is exactly what keeps this from matching an extras
# bracket or a version expression that happens to contain an `@`.
DIRECT_MARKER = " @ "

# ⚑ `git+` COVERS EVERY TRANSPORT git ACCEPTS (`git+https`, `git+ssh`, `git+file`) and only the
# first two are portable. `git+file:` is caught by `_LOCAL_SCHEMES` FIRST — see `classify`.
GIT_PREFIX = "git+"

# The schemes that address a machine rather than a network location.
_LOCAL_SCHEMES = ("file://", "git+file:")

# The remote schemes a direct reference may legitimately use.
_REMOTE_SCHEMES = ("https://", "http://")

# ⚑⚑ THE ENUMERABLE ROSTER: distributions THIS REPO KNOWS are published on no index. A bare name
# for one of these is the Ⓝ122b defect, caught before it ships rather than after.
#
# ⚑ IT IS SIBLING-REPO SHAPED BECAUSE THAT IS WHERE THE FAILURE COMES FROM. Each of these is a
# `~/github` peer a developer has installed locally and can therefore import without ever
# noticing it was never declared addressably — the exact way `paperkit` shipped. The names are
# normalised (lowercase, `_`→`-`) to match `distribution_name`.
UNPUBLISHED = frozenset(
    {
        "paperkit",
        "gabion",
        "summit",
        "bibstruct",
        "v4cat",
    }
)

# ⚑ THE NAME AT THE HEAD OF A REQUIREMENT, stopping at whatever ends it: an extras bracket, a
# version specifier, a direct-reference marker, or an environment marker. ANCHORED, so a name is
# read from the START and can never be found in the middle of a URL.
_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

# How a requirement is addressed.
INDEXED = "INDEXED"
DIRECT = "DIRECT"
UNADDRESSED = "UNADDRESSED"
LOCAL = "LOCAL"

# ⚑ WHICH STATES ABORT, DECLARED AS A SET AND NOT RE-DERIVED AT EACH READER. Three call sites ask
# "did this fail"; spelling the predicate once is what stops a newly-added state from being
# silently admitted as passing by whichever reader nobody updated. The shape is adopted from
# `check_stub_authority._FAILING`, whose comment records why it is a set.
_FAILING = frozenset({UNADDRESSED, LOCAL})

# ⚑ THE REFUSAL NAMES ITS SUCCESSOR. A gate that says only *no* teaches the reader to route
# around it; the remedy here is mechanical, so withholding it is what makes a correct verdict
# read as an obstacle. Both wrong spellings are named, because both are the ones actually
# reached for.
_NEXT_STEPS = (
    "  ⚑ A bare name for an unpublished distribution is not a declaration — it is an\n"
    "  INSTRUCTION nobody shipped, so the install works only for a reader who already\n"
    "  knew the order. NEXT: give the requirement its own address, e.g.\n"
    '      "<name> @ git+https://github.com/<org>/<repo>.git@<branch>"\n'
    "  ⚑ NOT `[tool.uv.sources]`: that is uv's own extension and `pip` ignores it, so it\n"
    "  never reaches the built wheel's metadata and an adopter inherits the failure.\n"
    "  ⚑ NOT a `file://` path: it resolves on one machine and breaks for every other\n"
    "  checkout — the unportable address wearing a manifest's uniform."
)


@dataclass(frozen=True, slots=True)
class Requirement:
    """One declared dependency, with how it is addressed and why that reading was made."""

    raw: str
    name: str
    form: str
    why: str

    @property
    def failed(self) -> bool:
        """True when this requirement must abort the commit."""
        return self.form in _FAILING


def distribution_name(raw: str) -> str:
    """Return the distribution name at the head of a requirement string, or the empty string.

    ⚑ NORMALISED TO LOWERCASE WITH `_` FOLDED TO `-`, because PEP 503 says `Paper_Kit` and
    `paper-kit` are ONE name. Comparing an un-normalised spelling against the roster would let a
    rename by punctuation walk straight past the gate.
    """
    found = _NAME_RE.match(raw)
    if found is None:
        return ""
    head: object = found.group(1)
    if not isinstance(head, str):
        return ""
    return head.lower().replace("_", "-")


def classify(raw: str) -> Requirement:
    """Return how one requirement string is addressed.

    ⚑ THE LOCAL CHECK RUNS BEFORE THE GIT CHECK, AND THE ORDER IS LOAD-BEARING. `git+file:` is a
    direct reference AND a local path; reading it as DIRECT because it starts with `git+` would
    admit exactly the unportable address this gate refuses. The narrower predicate wins.

    ⚑ AN UNRECOGNISED SCHEME FAILS RATHER THAN PASSING. A direct reference this reader cannot
    place is not evidence of a good address, and defaulting it to DIRECT would make every future
    scheme silently admissible — the fail-open shape.
    """
    name = distribution_name(raw)
    if DIRECT_MARKER in raw:
        url = raw.split(DIRECT_MARKER, 1)[1].strip()
        if url.startswith(_LOCAL_SCHEMES):
            return Requirement(
                raw, name, LOCAL, "addresses a path on this machine, so it resolves nowhere else"
            )
        if url.startswith(GIT_PREFIX) or url.startswith(_REMOTE_SCHEMES):
            return Requirement(raw, name, DIRECT, f"carries its own address: {url}")
        return Requirement(raw, name, LOCAL, f"direct reference with an unrecognised scheme: {url}")
    if name in UNPUBLISHED:
        return Requirement(
            raw,
            name,
            UNADDRESSED,
            f"{name} is published on no index, so a bare name resolves nowhere",
        )
    return Requirement(raw, name, INDEXED, "a bare name, resolvable from the package index")


def declared(manifest: Path = MANIFEST) -> list[str]:
    """Return the requirement strings `manifest` declares, in declaration order.

    ⚑ THE `Any` FROM `tomllib` IS NARROWED HERE, AT THE SEAM, so every expression downstream is
    concrete. An un-narrowed return would carry it into each field read — the boundary shape
    this repo's mypy settings exist to force.

    ⚑ A MANIFEST WITH NO `dependencies` READS AS AN EMPTY LIST, and `render` reports that as a
    fact about the POPULATION rather than as a pass. An absent table and a declared-empty one are
    the same for this reader; neither is evidence that anything was checked.
    """
    parsed: object = tomllib.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        return []
    project: object = parsed.get(PROJECT_TABLE)
    if not isinstance(project, dict):
        return []
    deps: object = project.get(DEPENDENCIES_KEY)
    if not isinstance(deps, list):
        return []
    return [item for item in deps if isinstance(item, str)]


def requirements(manifest: Path = MANIFEST) -> list[Requirement]:
    """Return every declared dependency, classified by how it is addressed."""
    return [classify(raw) for raw in declared(manifest)]


def failures(found: list[Requirement]) -> list[Requirement]:
    """Return the requirements that must abort the commit."""
    return [item for item in found if item.failed]


def by_form(found: list[Requirement]) -> dict[str, list[Requirement]]:
    """Group requirements by addressing form, so a count never travels without its members."""
    grouped: dict[str, list[Requirement]] = {}
    for item in found:
        grouped.setdefault(item.form, []).append(item)
    return dict(sorted(grouped.items()))


def render(found: list[Requirement]) -> str:
    """Render the population, naming every offender beside the counts.

    ⚑ AN EMPTY POPULATION IS REPORTED, NEVER PASSED SILENTLY. Zero dependencies is a legitimate
    state and it is also what a moved table or a renamed key looks like; a gate saying nothing in
    both cases certifies its own blind spot.
    """
    if not found:
        return (
            "dep-addressing: the manifest declares NO dependencies — a fact about the "
            "POPULATION, not a pass"
        )
    bad = failures(found)
    grouped = by_form(found)
    tally = ", ".join(f"{form} {len(items)}" for form, items in grouped.items())
    if not bad:
        return f"dep-addressing: clean ({len(found)} dependency(ies): {tally})"
    headline = (
        f"dep-addressing: BROKEN — {len(bad)} of {len(found)} dependency(ies) resolve from "
        f"neither an index nor a git URL ({tally}):"
    )
    out = [headline]
    out.extend(f"    ✗ {item.raw} — {item.form}: {item.why}" for item in bad)
    out.append(_NEXT_STEPS)
    return "\n".join(out)


def operand(argv: list[str]) -> Path | None:
    """Return the manifest a command line names, or None for this repo's own.

    ⚑⚑⚑ THIS EXISTS BECAUSE `main` READ ITS OWN FIXED FILE WHILE ACCEPTING A PATH (Ⓝ124a,
    2026-09-03). Passed `pyproject.toml`, the gate exited 0 having never opened it — a CONFIDENT
    answer to a question the tool was never asked, which is the wording `ratchet_flags.check_argv`
    uses for a silently-dropped FLAG. The same collapse, one argument KIND over: that guard
    refuses an unknown flag and nothing anywhere refused an unread operand.

    ⚑⚑ AND IT WAS THE FOURTH INSTANCE IN ONE DAY — after `module_size.py <path>`, `type_gate`'s
    ignored path, and `store.py`'s CLI dropping every flag it did not know. What makes this one
    the sharpest is that NOTHING WAS MISSING: `requirements(manifest)` and `declared(manifest)`
    were already parameterised, each with a docstring arguing for the parameter. Only `main`
    called them bare. The capability was written, justified, and left unwired — the
    `split_pipeline.rewire_only` shape, in a gate written the same session as its own rule.

    ⚑⚑ SO HONOURING IT IS THE FIX AND REFUSING IT WOULD HAVE BEEN THE WRONG ONE. A refusal is
    right when the operand names a capability the tool lacks; here the tool had it and only the
    wire was missing. Refusing would have FROZEN a reader that can already answer about any
    manifest into answering about exactly one — paying down a dropped argument by promoting the
    drop to policy.

    ⚑ THE FIRST NON-FLAG WORD IS THE OPERAND, and `argv[0]` is dropped only when it is actually a
    program path — never by a blind `argv[1:]`. That is the reading `ratchet_flags._rest` arrived
    at after an unchecked slicing precondition made a guard inert for the one caller that had
    sliced already; a program path never starts with `-` and a flag always does.
    """
    rest = argv[1:] if argv and not argv[0].startswith("-") else argv
    named = [a for a in rest if not a.startswith("-")]
    return Path(named[0]) if named else None


def main(argv: list[str]) -> int:
    """Report the addressing of every declared dependency; 1 when any is unaddressed.

    ⚑⚑ THE MANIFEST READ IS NAMED IN THE OUTPUT WHENEVER IT IS NOT THE DEFAULT, and that line is
    part of the repair rather than a convenience. The dropped operand survived because the output
    was BYTE-IDENTICAL whether or not a path was given: nothing an operator could read
    distinguished "checked your file" from "checked mine". A verdict that does not say what it
    read cannot be caught being wrong about it.
    """
    manifest = operand(argv)
    found = requirements(manifest) if manifest is not None else requirements()
    if manifest is not None:
        sys.stdout.write(f"dep-addressing: reading {manifest}\n")
    if "--list" in argv:
        for item in found:
            sys.stdout.write(f"    {item.form:<12} {item.name:<20} {item.raw}\n")
        sys.stdout.write(f"dep-addressing: {len(found)} declared dependency(ies)\n")
        return 0
    text = render(found)
    if failures(found):
        sys.stdout.write(text + "\n")
        return 1
    if "--quiet" not in argv:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
