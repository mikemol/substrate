# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.endpoint_census` — including the blind spot it genuinely has.

⚑⚑⚑ THE BLIND-SPOT CASE IS THE MOST IMPORTANT ONE HERE. This reader finds a retired port
inside a STRING, and `scratch/shared_cache.py` spells its endpoint as a TUPLE — `("127.0.0.1",
6379)` — so the very site that started this whole arc is INVISIBLE to it. That is not a bug to
quietly fix and forget: it is the reader's reach, and a census whose reach is undeclared
reports its own boundary as a fact about the tree. The arm asserts the blindness so the bound
is stated rather than rediscovered by whoever next trusts a zero.

⚑⚑ EVERY CASE DRIVES A FIXTURE with a fixture migration table, never the live one.
`CASSIAN_CUTOVER` changes at the next cutover, and an arm pinned to it would invert then —
blaming the module for the store moving (gate-G285).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import endpoint_census as ec

#: A fixture migration, so no arm depends on what cassian's ports are today.
FIXTURE = ec.Move(1111, 2222, "fixture-store")

#: A second, so a case can tell "found the right move" from "found any move at all".
OTHER = ec.Move(3333, 4444, "other-store")

MOVES = (FIXTURE,)
TWO_MOVES = (FIXTURE, OTHER)


def _tree(files: dict[str, str]) -> tempfile.TemporaryDirectory[str]:
    """Return a temporary tree holding `files`, for one case's exclusive use."""
    tmp = tempfile.TemporaryDirectory()
    for name, body in files.items():
        path = Path(tmp.name) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return tmp


def _python_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the structural reader over python constants."""
    out: list[tuple[str, bool]] = []
    body = 'BASE = "http://127.0.0.1:1111/x"\nOK = "http://127.0.0.1:2222/x"\n'
    with _tree({"a.py": body}) as t:
        found = ec.census([Path(t)], MOVES)
        hits = found.of_kind("py-const")
        out.append((f"a retired port in a constant is found: {len(hits)}", len(hits) == 1))
        out.append(
            (
                f"and the row names the constant: {hits[0].text if hits else ''}",
                bool(hits) and "BASE" in hits[0].text,
            )
        )
        # ⚑ THE LIVE PORT IS NOT REPORTED — a reader that flagged both would make the repair
        # indistinguishable from the defect, and every repaired site would read as unfixed.
        out.append(
            (
                f"and the LIVE port is not flagged: {[h.text for h in hits]}",
                all(str(FIXTURE.live) not in h.text for h in hits),
            )
        )
    return out


def _mention_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for use-versus-mention in python.

    ⚑⚑ A COMMENT EXPLAINING THE RETIREMENT MUST NOT COUNT AS A SITE. The census module's own
    docstring names every retired port; a textual reader would report its own documentation,
    and a census that flags its explanations teaches readers to ignore it.
    """
    out: list[tuple[str, bool]] = []
    body = f'# the old port was {FIXTURE.retired}, retired\nB = "http://127.0.0.1:2222/x"\n'
    with _tree({"a.py": body}) as t:
        found = ec.census([Path(t)], MOVES)
        out.append(
            (f"a port named only in a COMMENT is not a site: {len(found.sites)}", not found.sites)
        )
    return out


def _prose_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the fenced-code reader over markdown."""
    out: list[tuple[str, bool]] = []
    doc = (
        f"The store moved off {FIXTURE.retired} last month.\n\n"
        f"```\ncurl http://127.0.0.1:{FIXTURE.retired}/api\n```\n"
    )
    with _tree({"g.md": doc}) as t:
        found = ec.census([Path(t)], MOVES)
        hits = found.of_kind("prose-fence")
        out.append((f"a retired port inside a FENCE is found: {len(hits)}", len(hits) == 1))
        # ⚑⚑ AND THE PROSE SENTENCE ABOVE IT IS NOT — the same use-versus-mention split, on
        # the other instrument. A guide that DISCUSSES a retirement is correct, not stale.
        out.append(
            (
                f"and the surrounding prose is not: {[h.line for h in hits]}",
                all(h.line > 1 for h in hits),
            )
        )
    return out


def _blind_spot_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what this reader CANNOT see.

    ⚑⚑⚑ THE SITE THAT STARTED THE ARC IS INVISIBLE TO THIS CENSUS. `shared_cache.py` spells
    its endpoint as a TUPLE of a host string and an integer port, and this reader matches a
    port inside a STRING. Asserting the blindness is what turns a silent gap into a declared
    reach — and a zero from this tool must be read against it.

    ⚑ THE ARM WOULD GO RED IF SOMEONE WIDENED THE READER, which is correct: at that point the
    stated bound is false and the docstring claiming it must change in the same act.
    """
    out: list[tuple[str, bool]] = []
    with _tree({"a.py": f'ENDPOINT = ("127.0.0.1", {FIXTURE.retired})\n'}) as t:
        found = ec.census([Path(t)], MOVES)
        out.append(
            (
                f"a TUPLE endpoint is NOT seen — a declared bound: {len(found.sites)}",
                not found.sites,
            )
        )
    return out


def _denominator_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the denominator that makes a zero readable.

    ⚑⚑ A BARE ZERO CANNOT DISTINGUISH *SCANNED AND CLEAN* FROM *NEVER SCANNED*. Both arms
    are here because only their pair establishes the property — a report that always printed
    a denominator would satisfy the first alone.
    """
    out: list[tuple[str, bool]] = []
    with _tree({"a.py": 'OK = "http://127.0.0.1:2222/x"\n'}) as t:
        clean = ec.census([Path(t)], MOVES)
        out.append(
            (
                f"a clean tree reports a real denominator: {clean.py_scanned}",
                clean.py_scanned == 1 and not clean.sites,
            )
        )
        out.append((f"and says it scanned something: {clean.total()}", clean.total()))

    empty = ec.census([], MOVES)
    out.append((f"an EMPTY sweep is not a clean bill: {empty.total()}", not empty.total()))
    out.append(
        (f"and the report says so: {empty.lines()[-1]}", "NOTHING WAS SCANNED" in empty.lines()[-1])
    )
    # ⚑ AND THE TWO POPULATIONS ARE NEVER SUMMED — an AST reading and a fence match have
    # different blind spots, so one total over both would compare instruments (gate-G228).
    out.append(
        (
            f"and the report refuses to sum them: {'NOT summed' in ' '.join(empty.lines())}",
            "NOT summed" in " ".join(empty.lines()),
        )
    )
    return out


def _selectivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the right move being attached to each site.

    ⚑ A READER THAT FOUND *ANY* MOVE WOULD PASS EVERY ARM ABOVE. Two moves in one table, and
    a file naming only one of them, is what forces the attribution to be checked.

    ⚑⚑ THE EXPECTED MOVE IS THE TABLE ENTRY ITSELF, never a retyped pair. A literal beside a
    declaration is a second roster, and it drifts the first time the declaration changes.
    """
    out: list[tuple[str, bool]] = []
    with _tree({"a.py": f'BASE = "http://127.0.0.1:{OTHER.retired}/x"\n'}) as t:
        found = ec.census([Path(t)], TWO_MOVES)
        got = found.sites[0].moves if found.sites else ()
        out.append((f"the site carries the RIGHT move: {got}", got == (OTHER,)))
    return out


def _several_successor_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a retired port with more than one successor.

    ⚑⚑⚑ THE DEFECT THIS PINS WAS LIVE AND DERIVED, WHICH MADE IT WORSE THAN THE TRANSCRIPTION
    IT REPLACED. `_retired` built `{m.retired: m}`, so when the owner declared a second
    successor for one retired port the later row silently overwrote the earlier and every site
    showed ONE option with no sign a second existed. A derived reading carries more authority
    than a typed one, so its omissions are questioned less.

    ⚑⚑ AND THE REAL INSTANCE IS TWO ADJACENT LINES WANTING OPPOSITE PORTS — an OTLP writer and
    a query base, one line apart, in one file. A census naming a single successor would have
    recommended a wrong repoint for exactly one of them, in the direction that lands on a live
    server which refuses the request rather than on a dead port that fails at connect.
    """
    out: list[tuple[str, bool]] = []
    split = (ec.Move(5555, 6001, "ingest"), ec.Move(5555, 6002, "query"))
    with _tree({"a.py": 'BASE = "http://127.0.0.1:5555/x"\n'}) as t:
        found = ec.census([Path(t)], split)
        site = found.sites[0] if found.sites else None
        out.append(
            (f"the site is reported once, not twice: {len(found.sites)}", len(found.sites) == 1)
        )
        out.append(
            (
                f"and carries BOTH successors: {site.moves if site else ()}",
                site is not None and site.moves == split,
            )
        )
        out.append(
            (
                f"and says the direction decides: {site.successors() if site else ''}",
                site is not None and "DIRECTION decides" in site.successors(),
            )
        )

    # ⚑ THE SINGLE-SUCCESSOR CASE MUST STAY QUIET — a row announcing a choice where there is
    # none would train readers to skip the warning on the rows that have one.
    with _tree({"a.py": f'B = "http://127.0.0.1:{FIXTURE.retired}/x"\n'}) as t:
        one = ec.census([Path(t)], MOVES).sites[0]
        out.append(
            (
                f"a single successor states no choice: {one.successors()}",
                "DIRECTION decides" not in one.successors(),
            )
        )
    return out


def _exit_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three exit codes.

    ⚑ AN UNSCANNED RUN EXITS 2, NOT 0. Exiting clean on a zero-over-zero would bank exactly
    the false green this module exists to make unrepresentable.
    """
    out: list[tuple[str, bool]] = []
    out.append((f"a bare run prints usage and exits {ec.USAGE_EXIT}", ec.run([]) == ec.USAGE_EXIT))

    # ⚑ EACH `run` IS CALLED ONCE AND ITS CODE BOUND, never re-invoked inside the label. A
    # first cut called it twice per arm — once to report and once to assert — which printed
    # every census into the suite's own output and buried the verdict line the reader needs.
    live = ec.CASSIAN_CUTOVER[0].retired
    with _tree({"a.py": f'BASE = "http://127.0.0.1:{live}/x"\n'}) as t:
        dirty = ec.run([ec.MODE, t])
        out.append((f"a tree with a site exits 1: {dirty}", dirty == 1))
    with _tree({"a.py": "X = 1\n"}) as t:
        clean = ec.run([ec.MODE, t])
        out.append((f"a clean tree exits 0: {clean}", clean == 0))
    return out


def _direction_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `kind` being DATA rather than decoration.

    ⚑⚑⚑ THE PEER'S GENERATOR IS THE CASE THIS PINS, AND IT WAS NOT A NEAR MISS. Theirs sliced
    the registry's first three columns and DROPPED `kind` — the only column distinguishing two
    rows that share a retired port — then keyed a dict on that port. Nine collectors which
    WRITE were re-pointed to the read-only surface, three failed, and the drop-ins were
    generated, committed by a hook and symlinked into the live systemd tree. The wrong value
    arrived wearing every mark of a derivation and then executed on a timer.

    ⚑⚑ SO THESE ARMS ASSERT THAT A CONSUMER CAN FILTER BY DIRECTION WITHOUT PARSING PROSE. A
    first cut here folded the kind into the service name as `"vm (store)"`: legible to a human,
    invisible to a program, and a direction-aware caller would have had to re-parse a display
    string to recover it.
    """
    out: list[tuple[str, bool]] = []
    split = (ec.Move(5555, 6001, "ingest", "store"), ec.Move(5555, 6002, "query", "read"))

    writes = ec.successors_for(split, 5555, "store")
    out.append((f"a write-direction lookup gets ONE answer: {writes}", writes == (split[0],)))
    reads = ec.successors_for(split, 5555, "read")
    out.append((f"a read-direction lookup gets the OTHER: {reads}", reads == (split[1],)))
    # ⚑⚑ AND THE TWO MUST DIFFER, which is the property. A lookup returning the same row for
    # both directions would satisfy each arm above on its own.
    out.append((f"and they are different rows: {writes} vs {reads}", writes != reads))

    # ⚑⚑⚑ AN UNDECLARED DIRECTION RETURNS NOTHING RATHER THAN FALLING BACK. Falling back to
    # whatever else shares the port is exactly the "keeps one row" behaviour a dict
    # comprehension gives for free, and it is what put writers on a read surface.
    none = ec.successors_for(split, 5555, "peer")
    out.append((f"an undeclared direction returns EMPTY, never a guess: {none}", not none))

    # ⚑ AND THE KIND REACHES THE HUMAN TOO — a line naming only ports and service names leaves
    # direction to be inferred from a name, which is the guess this repair removes.
    with _tree({"a.py": 'BASE = "http://127.0.0.1:5555/x"\n'}) as t:
        line = ec.census([Path(t)], split).sites[0].successors()
        out.append(
            (
                f"the report names each successor's kind: {line}",
                "for store" in line and "for read" in line,
            )
        )
    return out


def _repeated_key_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a registry that repeats `old_port` — the outage's shape.

    ⚑⚑⚑ THIS IS THE ARM NEITHER REPO HAD, AND ITS ABSENCE COST AN OUTAGE. The peer's generator
    keyed a dict on the retired port; when a second row declared the same port, the later row
    won and nine collectors that WRITE were re-pointed at a read-only surface. Three failed.
    My reader had the same shape until a tick ago. Both are fixed and NOTHING WOULD CATCH THE
    NEXT ONE — so this arm forces the repeat rather than waiting for a registry to contain one.

    ⚑⚑ IT DRIVES A REAL FILE, not `FALLBACK`, because the defect lives in the PARSE. A case
    that handed `read_registry`'s output straight to `_retired` would skip the line where the
    rows are built, which is exactly where a comprehension would drop one.

    ⚑ AND IT COVERS THIS REPO'S CONSUMER ONLY. The peer has their own readers and their own
    gate; a substrate arm asserting anything about their tree would be a rival authority. The
    bound is stated rather than implied.
    """
    out: list[tuple[str, bool]] = []
    header = "\t".join(ec.COLUMNS)
    rows = ("vm\t8428\t30828\t_VM_URL\tstore", "vm-read\t8428\t30829\t_VM_READ_URL\tread")
    with _tree({"reg.tsv": f"# a comment\n{header}\n" + "\n".join(rows) + "\n"}) as t:
        said = ec.read_registry(Path(t) / "reg.tsv")
        out.append(
            (
                f"a repeated old_port yields BOTH rows: {len(said.moves)}",
                len(said.moves) == len(rows),
            )
        )
        # ⚑ AND BOTH DIRECTIONS SURVIVE THE PARSE — a reader that kept one row would still
        # report a plausible count if it kept the wrong one, so the KINDS are what is asserted.
        kinds = {m.kind for m in said.moves}
        out.append((f"and both directions survive: {sorted(kinds)}", kinds == {"store", "read"}))
        # ⚑⚑ THE LOOKUP MUST NOT COLLAPSE THEM EITHER. The parse and the index are two places
        # a key assumption can hide, and fixing one leaves the other — which is how this
        # defect reached a formatter after the reader was already correct.
        writes = ec.successors_for(said.moves, 8428, "store")
        reads = ec.successors_for(said.moves, 8428, "read")
        out.append(
            (
                f"and the index keeps them apart: {writes} vs {reads}",
                len(writes) == 1 and len(reads) == 1 and writes != reads,
            )
        )
        out.append((f"and the reading is DERIVED, not the fallback: {said.derived}", said.derived))

        # ⚑⚑⚑ THE SENSITIVITY ARM. Everything above passes today, which says the checks RUN
        # and not that they would CATCH the defect — so the defect is CONSTRUCTED: the exact
        # dict comprehension both repos shipped, keyed on the retired port. The claim is that
        # it loses a row where the real index does not. Asserted, not assumed.
        #
        # ⚑⚑ AND IT IS THE INDEX RATHER THAN THE PARSE, because that is where the reachable
        # defect lives. `read_registry` appends to a list and cannot collapse; both outages
        # came from a lookup built over rows that were parsed correctly. A sensitivity arm
        # aimed at the parse would be testing a state neither repo was ever in.
        collapsed = {m.retired: m for m in said.moves}
        kept = ec.successors_for(said.moves, 8428, "store")
        lost = f"{len(collapsed)} of {len(said.moves)}"
        out.append(
            (f"a port-keyed dict WOULD lose a row: {lost}", len(collapsed) < len(said.moves))
        )
        both = f"{collapsed[8428].kind} vs {kept[0].kind}"
        out.append(
            (
                f"and would keep the wrong direction for a writer: {both}",
                collapsed[8428].kind != kept[0].kind,
            )
        )
    return out


def _provenance_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the declaration saying where it came from.

    ⚑⚑⚑ THESE ARMS EXIST BECAUSE A TRANSCRIBED TABLE READ AS A DERIVED ONE FOR A WHOLE TICK.
    The module carried its migration rows as typed literals and reported them with the same
    confidence a registry reading would have — and a peer independently laundered a hand-found
    site into a sweep result, which hid a gap in the registry itself. A reading whose source is
    implied cannot be audited, so the source is a FIELD and the report leads with it.

    ⚑⚑ AND THE FALLBACK ARM IS THE ONE THAT MATTERS. A derived reading is self-evidently fine;
    the failure mode is a fallback that presents as derived. Forcing an unreadable path is what
    makes that state reachable at all — it cannot be exercised by running against a machine
    that happens to have the registry.
    """
    out: list[tuple[str, bool]] = []
    missing = ec.read_registry(Path("/nonexistent/store-migration.tsv"))

    out.append((f"an unreadable registry falls back: {missing.derived}", not missing.derived))
    out.append(
        (f"and the fallback carries rows: {len(missing.moves)}", missing.moves == ec.FALLBACK)
    )
    # ⚑ AND IT SAYS SO IN BAND — a caveat kept in prose gets summarised away, so the warning
    # travels with the verdict rather than beside it.
    out.append(
        (
            f"and the report SAYS it is a fallback: {missing.why()[:40]}",
            "FALLBACK" in missing.why() and "STALE" in missing.why(),
        )
    )

    live = ec.read_registry()
    if live.derived:
        out.append(
            (
                f"a readable registry is marked derived: {live.why()[:48]}",
                "FALLBACK" not in live.why(),
            )
        )
        # ⚑ THE TWO READINGS MUST BE DISTINGUISHABLE, which is the whole property. A `why()`
        # that read alike for both would make the field decorative.
        out.append(
            (
                f"and the two provenances differ: {live.derived} vs {missing.derived}",
                live.why() != missing.why(),
            )
        )
    else:
        # ⚑ NO REGISTRY HERE IS A FACT ABOUT THIS MACHINE, not a failure — substrate runs in
        # trees with no cassian checkout. Reported as SKIPPED rather than vacating silently.
        out.append((f"no registry here, so the derived arm is SKIPPED: {live.why()[:32]}", True))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _python_cases()
        + _mention_cases()
        + _prose_cases()
        + _blind_spot_cases()
        + _denominator_cases()
        + _selectivity_cases()
        + _several_successor_cases()
        + _direction_cases()
        + _repeated_key_cases()
        + _provenance_cases()
        + _exit_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"endpoint-census selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
