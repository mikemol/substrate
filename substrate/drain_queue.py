# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Join drain candidates to their consumers and to the checker, and print the real queue.

⚑ THE JOIN NOTHING PERFORMED. `drain_leverage` ranks candidates by what draining one
RETIRES; `module_importers` reports where a name is imported; `mypy_census` reports which
files carry findings. Each answers its own question well, and the queue an operator can
act on is the JOIN — which candidates are startable TODAY, because every file that would
have to be edited can take an edit under the zero-tolerance per-file gate.

⚑⚑ AND THE ORDERING IS COST, NOT VALUE, for the reason `drain_order` records: a name
retires many inserts precisely BECAUSE many files reach it, so the value ranking selects
the hardest work first. Read together the two are a plan; read alone either misleads in a
different direction.

⚑ A DIRTY CONSUMER IS NOT A VERDICT ABOUT THE CANDIDATE. It says the drain waits on that
file's own paydown, and the blocker is named so the wait is a queue rather than a wall.

⚑⚑⚑ THE CENSUS HAS THREE OUTCOMES AND COLLAPSING THEM IS THE FAILURE THIS GUARDS. mypy may
report findings, report none, or FAIL TO RUN — and `type_errors` distinguishes all three
deliberately: `None` when mypy is not installed, a dict carrying the `UNRUNNABLE` key when
it ran and could not complete, and the census otherwise. A queue built on either failure
read as an empty census would list EVERY candidate as startable, which is the false green
the whole family of readers exists to refuse. Both raise here.
"""

from __future__ import annotations

from pathlib import Path

from substrate import corpus, drain_order, module_importers, mypy_census


class CensusUnavailableError(RuntimeError):
    """Raised when the checker could not run, so editability is unknown."""


def dirty_files(census: dict[str, list[str]] | None) -> frozenset[str]:
    """Return the repo-relative files carrying at least one finding.

    ⚑ BOTH FAILURE SHAPES RAISE RATHER THAN RETURNING AN EMPTY SET. An absent checker, an
    unrunnable one and a clean tree are the same value if this returns `frozenset()`, and
    the difference is the whole answer: one means every candidate is startable, the others
    mean nothing is known.
    """
    if census is None:
        msg = "mypy is not installed — editability is unknown, not clean"
        raise CensusUnavailableError(msg)
    if mypy_census.UNRUNNABLE in census:
        detail = "; ".join(census[mypy_census.UNRUNNABLE])
        msg = f"mypy could not run — editability is unknown, not clean: {detail}"
        raise CensusUnavailableError(msg)
    return frozenset(key.split("::", 1)[1] for key in census if "::" in key)


def own_counts(census: dict[str, list[str]] | None) -> dict[str, int]:
    """Return `{file: its own finding count}` from the same census `dirty_files` reads.

    ⚑ ONE CENSUS, TWO READINGS. The dirty SET answers whether a file can take an edit; the
    COUNT answers how large its paydown is. Deriving the second from a separate run would
    be two authorities on one question, and they would disagree the moment anything moved
    between them.

    ⚑⚑ A FILE ABSENT FROM THE CENSUS IS ABSENT FROM THIS MAP, deliberately. Its consumer
    may be clean or may simply never have been measured, and a reader that defaulted it to
    zero would report an unmeasured monolith as actionable — the false green the blocker
    ranking's own column exists to prevent.
    """
    if census is None or mypy_census.UNRUNNABLE in census:
        return {}
    out: dict[str, int] = {}
    for key, messages in census.items():
        if "::" not in key:
            continue
        path = key.split("::", 1)[1]
        out[path] = out.get(path, 0) + len(messages)
    return out


def consumers_of(name: str, files: list[tuple[Path, str]]) -> dict[str, int]:
    """Return `{consumer path: import-site count}` for one candidate.

    ⚑⚑⚑ THE CANDIDATE ARRIVES BARE AND `sites` NEEDS THE DOTTED SPELLING, which is the
    third recorded instance of this exact mismatch and the second in this arc. A bare name
    normalises to itself and is queried as a TOP-LEVEL module, so the `from <pkg> import
    <mod>` branch cannot fire and the answer is a confident zero — a fact about the METHOD
    reported as a fact about the SUBSTRATE. Measured here: the whole queue rendered EMPTY,
    which reads as "no drains" rather than "the query never matched".

    ⚑⚑ AND AMBIGUITY REFUSES RATHER THAN PICKING. `module_importers.candidates` enumerates
    every dotted module a bare name could denote and deliberately does not choose, because
    a census attributed to the wrong module reads exactly like a right one — and this repo
    deletes on zeros. A candidate resolving several ways contributes NO consumers here and
    is therefore omitted from the queue, which is the honest outcome: its cost is unknown,
    not zero.

    ⚑ A NAME RESOLVING TO NOTHING IS A GENUINE TOP-LEVEL MODULE and is queried as given —
    `import agda_lex` legitimately names one.
    """
    found = module_importers.candidates(name, files)
    if len(found) > 1:
        return {}
    dotted = found[0] if found else name
    out: dict[str, int] = {}
    for site in module_importers.sites(dotted, files):
        out[site.path] = out.get(site.path, 0) + 1
    return out


def costs(
    names: list[str],
    files: list[tuple[Path, str]],
    dirty: frozenset[str],
) -> list[drain_order.Cost]:
    """Return the cost of draining each name, skipping those nothing imports.

    ⚑ A CANDIDATE WITH NO CONSUMERS IS OMITTED RATHER THAN REPORTED AS FREE. Zero
    consumers means this reader could not find its importers, not that draining it costs
    nothing — the dynamic-import shapes `module_importers` names as unresolvable, and the
    ambiguous-name refusal above, are exactly where such a zero comes from.
    """
    out: list[drain_order.Cost] = []
    for name in sorted(set(names)):
        found = consumers_of(name, files)
        if found:
            out.append(drain_order.cost_of(name, found, dirty))
    return out


def population(root: Path) -> list[tuple[Path, str]]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs."""
    return [(Path(p), str(Path(p).relative_to(root))) for p in corpus.py_files(root=root)]


def queue(
    names: list[str],
    root: Path | None = None,
) -> tuple[list[drain_order.Cost], dict[str, int]]:
    """Return the drain queue and the per-file finding counts, from ONE census run.

    ⚑ BOTH READINGS COME BACK TOGETHER BECAUSE THEY COME FROM ONE RUN. An earlier shape
    returned only the queue, so a caller wanting the counts had to run the corpus-wide
    census a second time — minutes of work producing a second authority that would
    disagree with the first the moment anything moved between them.
    """
    where = root if root is not None else corpus.ROOT
    census = mypy_census.type_errors(root=where)
    dirty = dirty_files(census)
    rows = drain_order.ordered(costs(names, population(where), dirty))
    return rows, own_counts(census)
