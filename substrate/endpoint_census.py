# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Every site naming a retired endpoint, DERIVED from a migration declaration.

⚑⚑⚑ FINDING SITES ONE INCIDENT AT A TIME HAS NO TERMINATION CONDITION, AND THAT IS THE
DEFECT THIS EXISTS TO REMOVE. Four sites in this tree surfaced by four unrelated accidents:
a peer noticed one, grepped that one's consumers to find a second, a third turned up because
a positive control failed on a port being used AS the control, and the fourth only appeared
when someone swept against the store owner's own migration registry. Nothing in that process
says when it is finished — after each discovery the honest state is *at least N*, forever.

⚑⚑ SO THE POPULATION IS DERIVED FROM THE DECLARATION, NOT ACCUMULATED FROM INCIDENTS. Given
what was retired and what replaced it, every site is a query with an answer, and the answer
has a denominator. That is the difference between a census and a growing anecdote pile.

⚑⚑⚑ AND A DEGRADING CLIENT IS WHY THIS CLASS HIDES. A cache client that cannot connect falls
through to computing the value; a metrics client reports NOT CONFIRMED, which by this repo's
own rule is not the same as failed. Nothing crashes and nothing logs, so a retired endpoint
is indistinguishable from a cold cache or a quiet store. **The absence of a symptom is not
evidence of absence** — it is what this defect looks like from inside.

⚑ THE READER IS STRUCTURAL FOR PYTHON AND TEXTUAL FOR PROSE, DELIBERATELY. A `.py` constant
is an AST assignment and is read as one; a markdown guide's ports live inside fenced code
blocks, which are opaque to a heading reader and are genuinely text. Reporting them under one
count would be the comparing-two-instruments error (gate-G228), so the two populations are
reported SEPARATELY and never summed.

⚑ THIS DOES NOT REPAIR ANYTHING. It answers *where*, with a denominator. Rewriting a default
is an edit to the file that owns it, and two of the four known sites sit behind a per-file
gate that refuses every edit — so a census that also wrote would report a repair it could not
perform.

⚑⚑⚑ AND ONE RETIRED PORT MAY HAVE SEVERAL SUCCESSORS, SPLIT BY DIRECTION. `:8428` retired to
BOTH `vmagent :30828` (ingest) and `vm-read :30829` (query) — different Deployments, both
live, neither wrong. **So a site's replacement depends on whether it READS or WRITES, which
this tool cannot see.** Every row therefore prints the declared options and says the choice is
the site's; a census that named one would be recommending a repoint in the direction its
reader cannot tell is wrong — and the wrong one moves a client from a dead port to a live
server that refuses its requests, which fails as a 400 someone logs and walks past rather than
loudly at connect.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import NamedTuple

#: The mode this module has, named so a bare run prints the spelling a reader needs next.
MODE = "--retired"

#: What a bare or unknown invocation exits with — usage, not a verdict about the tree.
USAGE_EXIT = 2

#: What counts as a source file this reader parses structurally.
PY = "*.py"

#: What counts as prose this reader scans for live commands.
MD = "*.md"

#: A fenced code block in markdown — where a guide's live commands actually live, and what a
#: heading-oriented reader cannot see.
FENCE = re.compile(r"```.*?```", re.DOTALL)

#: `host:port` inside a URL or a bare pair. Port-only, because a host may be spelled several
#: ways (127.0.0.1, localhost, a Service name) while the PORT is what the migration moved.
PORT = re.compile(r"(?<![\d.])(?::|\b)(\d{4,5})\b")


def _ports(text: str) -> list[int]:
    """Return every port-shaped number in `text`.

    ⚑ A NAMED HELPER BECAUSE `re.findall` RETURNS `Any`, which this repo's gate refuses and
    which has leaked into three modules this session already. Narrowing it once, here, keeps
    every caller's arithmetic checked instead of quietly untyped.
    """
    return [int(m.group(1)) for m in PORT.finditer(text)]


class Move(NamedTuple):
    """One retirement: a port that was, a port that is, and what the service is called.

    ⚑⚑⚑ `kind` IS A FIELD, NOT PART OF A DISPLAY STRING, AND THAT DISTINCTION IS LOAD-BEARING.
    A first cut folded it into `service` as `"vm (store)"` — legible to a human and INVISIBLE
    TO A PROGRAM, so a consumer wanting only write-direction successors would have had to
    re-parse prose. The peer who owns this registry had the same shape one step worse: their
    generator sliced the first three columns and DROPPED `kind` entirely, so it could not see
    the one column distinguishing two rows that share a retired port — and it re-pointed nine
    writing collectors at a read-only surface, taking down three.

    ⚑⚑ A READER THAT DISCARDS THE DISAMBIGUATING COLUMN CANNOT DETECT THE AMBIGUITY IT CREATES
    DOWNSTREAM. Keeping `kind` typed is what lets a future consumer filter by direction instead
    of guessing, and lets THIS module refuse rather than pick.
    """

    retired: int
    live: int
    service: str
    kind: str = ""

    def why(self) -> str:
        """Return the one-line account of this retirement."""
        named = f"{self.service} ({self.kind})" if self.kind else self.service
        return f"{named}: {self.retired} RETIRED -> {self.live}"


def successors_for(moves: tuple[Move, ...], retired: int, kind: str) -> tuple[Move, ...]:
    """Return the successors of `retired` whose declared `kind` matches — never a guess.

    ⚑⚑⚑ THIS IS THE FUNCTION A REPOINTING CONSUMER MUST CALL, and it exists because the peer's
    generator did the opposite: it keyed a dict on the retired port, kept whichever row came
    last, and emitted live systemd drop-ins pointing writers at a query surface. Nine
    collectors, three failures. **A consumer that cannot state its own direction cannot safely
    repoint anything.**

    ⚑⚑ AN EMPTY RESULT IS THE HONEST ANSWER when nothing of that kind is declared — the caller
    must then refuse, not fall back to whatever else shares the port. Falling back is precisely
    the "keeps one row" behaviour a dict comprehension gives for free.
    """
    return tuple(m for m in moves if m.retired == retired and m.kind == kind)


class Site(NamedTuple):
    """One place a retired port is named, and how it was found.

    ⚑ `kind` RECORDS THE INSTRUMENT, because a python constant and a line of prose are found
    by different readers with different blind spots. A row that did not say which would make
    the two populations look like one, and a count over both would be comparing instruments.

    ⚑⚑ `moves` IS PLURAL BECAUSE A RETIRED PORT MAY HAVE SEVERAL SUCCESSORS. Carrying one
    would make this tool recommend a repoint it cannot justify.
    """

    path: Path
    line: int
    kind: str
    moves: tuple[Move, ...]
    text: str

    def successors(self) -> str:
        """Return the declared successors, naming the choice when there is more than one.

        ⚑⚑ THIS STATES THE AMBIGUITY RATHER THAN RESOLVING IT. Only the site knows whether it
        reads or writes, and the wrong choice moves it from a dead port to a live server that
        refuses its requests — which fails quietly where a dead port fails at connect.
        """
        if len(self.moves) == 1:
            return self.moves[0].why()
        # ⚑⚑ THE KIND IS IN THE LINE, AND A FIRST CUT DROPPED IT — printing only
        # `30828 (vm) OR 30829 (vm-read)` leaves a reader to infer direction from a service
        # NAME, which is the guess this whole repair exists to remove. The column that
        # disambiguates must reach the human too, not only the program.
        every = " OR ".join(
            f"{m.live} for {m.kind or 'unstated'} ({m.service})" for m in self.moves
        )
        return (
            f"{self.moves[0].retired} RETIRED -> {every}  "
            f"⚑ SEVERAL SUCCESSORS — the site's DIRECTION decides, not this tool"
        )

    def why(self) -> str:
        """Return a one-line, clickable account of this site."""
        return f"{self.path}:{self.line}  [{self.kind}]  {self.successors()}  {self.text.strip()}"


#: Where the store owner DECLARES what moved. ⚑ READ, NEVER TRANSCRIBED: a table typed here
#: is a second roster that drifts the moment the owner adds a row, which is the defect this
#: module was built to remove and then committed against itself.
REGISTRY = Path.home() / "github" / "cassian-observability" / "host" / "store-migration.tsv"

#: The registry's columns, so a reader states the shape it expects rather than indexing blind.
#: ⚑ `old_port` IS EXPLICITLY NOT A KEY — the owner's own header says so, and this reader
#: treated it as one for a tick after reading that file. A declaration is only derived-from if
#: the reader honours its schema.
COLUMNS = ("store", "old_port", "new_port", "var_suffix", "kind")

#: The fallback, used ONLY when the registry cannot be read — and every reading says which
#: source answered, because a figure whose provenance is implied is the laundering defect
#: this arc has already paid for once.
#:
#: ⚑⚑⚑ THIS TABLE WAS THE SOLE SOURCE AND COULD NOT SEE ITSELF. Its ports are integer
#: literals inside tuples and this module's reader matches ports inside STRINGS, so
#: `--retired` over its own file reported ZERO — the instrument blind to exactly the defect
#: it hunts. Measured, not theorised.
#:
#: ⚑⚑ AND IT HELD ONLY ONE SUCCESSOR FOR `:8428`, WHICH IS THE DISTINCTION THE REGISTRY NOW
#: CARRIES. A transcription cannot represent two directional successors without someone
#: noticing there are two — and whichever number was typed last would have won, turning a
#: real distinction into a typo somebody "corrected".
FALLBACK: tuple[Move, ...] = (
    Move(6379, 30637, "cache", "peer"),
    Move(8428, 30828, "vm", "store"),
    Move(8428, 30829, "vm-read", "read"),
    Move(9428, 30928, "vlogs", "store"),
    Move(10428, 30428, "vtraces", "store"),
    Move(9464, 31464, "buildbuddy", "source"),
)


class Declaration(NamedTuple):
    """The migration table plus WHERE it came from.

    ⚑⚑ PROVENANCE TRAVELS WITH THE DATA, because a reading whose source is implied cannot be
    audited. The peer who owns this registry reported a sweep result that was actually a
    hand-found site, and the laundering hid a gap in the registry itself — a table that
    cannot say where it came from makes that class unrepresentable to catch.
    """

    moves: tuple[Move, ...]
    source: str
    derived: bool

    def why(self) -> str:
        """Return a one-line account of where this declaration came from."""
        if self.derived:
            return f"declaration: {self.source} ({len(self.moves)} row(s))"
        return (
            f"declaration: LOCAL FALLBACK ({len(self.moves)} row(s)) — "
            f"{self.source}. ⚑ this table is transcribed and MAY BE STALE."
        )


def read_registry(path: Path = REGISTRY) -> Declaration:
    """Return the migration table, from the owner's registry when readable.

    ⚑ A MISSING REGISTRY IS NOT AN ERROR AND NOT A SILENT DEFAULT. Substrate runs in trees
    that have no cassian checkout, so falling back is correct — and saying so in every report
    is what keeps a fallback reading from being mistaken for a derived one.
    """
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as exc:
        return Declaration(FALLBACK, f"{path} unreadable: {exc}", derived=False)

    moves: list[Move] = []
    for line in body.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(COLUMNS) or cells[0] == COLUMNS[0]:
            continue
        name, old, new, kind = cells[0], cells[1], cells[2], cells[4]
        if old.isdigit() and new.isdigit():
            # ⚑ `kind` IS CARRIED AS DATA, not folded into the display name. The column that
            # distinguishes two rows sharing a retired port is the one a consumer needs most,
            # and a reader that drops it cannot detect the ambiguity it hands downstream.
            moves.append(Move(int(old), int(new), name, kind))
    if not moves:
        return Declaration(FALLBACK, f"{path} held no rows this reader could parse", derived=False)
    return Declaration(tuple(moves), str(path), derived=True)


#: The table this module uses by default — derived where possible, transcribed where not.
CASSIAN_CUTOVER: tuple[Move, ...] = read_registry().moves


def _retired(moves: tuple[Move, ...]) -> dict[int, tuple[Move, ...]]:
    """Return the retired-port lookup — EVERY successor per port, never the last one seen.

    ⚑⚑⚑ `old_port` IS NOT A KEY, AND A DICT COMPREHENSION HERE SILENTLY ASSUMED IT WAS. When
    the owner declared a second successor for `:8428` — `vmagent :30828` for writes and
    `vm-read :30829` for queries, different Deployments rather than two ports on one Service —
    a `{m.retired: m}` build kept whichever row came last and DROPPED the other. Every `:8428`
    site then displayed one successor with no sign a second existed, which is worse than the
    transcription it replaced: a DERIVED reading carries more authority, so its omissions are
    less likely to be questioned.

    ⚑⚑ THE HARM IS ASYMMETRIC, WHICH IS WHY ALL SUCCESSORS ARE CARRIED. Repointing an OTLP
    writer at the query surface, or a query client at the ingest surface, moves it from a dead
    port to a LIVE SERVER THAT REFUSES ITS REQUESTS — a 400 a caller logs and walks past,
    where a dead port fails loudly at connect.
    """
    out: dict[int, list[Move]] = {}
    for move in moves:
        out.setdefault(move.retired, []).append(move)
    return {port: tuple(found) for port, found in out.items()}


def scan_python(path: Path, moves: tuple[Move, ...]) -> list[Site]:
    """Return every module-level constant in `path` whose value names a retired port.

    ⚑ STRUCTURAL, NOT TEXTUAL. The question is which CONSTANT carries a dead default, and an
    AST answers it where a line match would also hit a comment explaining the retirement —
    use-versus-mention, which this repo has paid for in a checker before.
    """
    retired = _retired(moves)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        # ⚑ AN UNREADABLE FILE IS ACCOUNTED FOR BY THE CALLER'S DENOMINATOR, not silently
        # skipped as though it were clean.
        return []
    out: list[Site] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for found in ast.walk(node.value):
            if not isinstance(found, ast.Constant) or not isinstance(found.value, str):
                continue
            names = ", ".join(t.id for t in node.targets if isinstance(t, ast.Name))
            out.extend(
                Site(path, node.lineno, "py-const", retired[port], f"{names} = {found.value!r}")
                for port in _ports(found.value)
                if port in retired
            )
    return out


def scan_prose(path: Path, moves: tuple[Move, ...]) -> list[Site]:
    """Return every FENCED-CODE line in `path` naming a retired port.

    ⚑⚑ ONLY INSIDE FENCES, AND THAT NARROWNESS IS THE POINT. A guide's prose may DISCUSS a
    retirement — this module's own docstring names every one of these ports — while its code
    blocks are what a reader copies and runs. Matching the whole document would report every
    correct explanation as a defect, and a census that flags its own documentation teaches
    readers to ignore it.

    ⚑ A STALE INSTRUCTION IS A DEFECT WITH A HUMAN EXECUTING IT, which is why prose is in
    scope at all rather than dismissed as not-code.
    """
    retired = _retired(moves)
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return []
    out: list[Site] = []
    for block in FENCE.finditer(body):
        start = body[: block.start()].count("\n") + 1
        for offset, line in enumerate(block.group().splitlines()):
            out.extend(
                Site(path, start + offset, "prose-fence", retired[port], line)
                for port in _ports(line)
                if port in retired
            )
    return out


class Census(NamedTuple):
    """What the sweep found, with the denominator that makes a zero readable.

    ⚑⚑ A BARE ZERO CANNOT DISTINGUISH *SCANNED AND CLEAN* FROM *NEVER SCANNED*, which is this
    repo's most-repeated instrument defect. Carrying the population makes the difference
    representable rather than a fact a reader has to ask for separately.
    """

    sites: list[Site]
    py_scanned: int
    prose_scanned: int

    def total(self) -> bool:
        """Report whether the sweep read anything — a zero over zero is not a clean bill."""
        return (self.py_scanned + self.prose_scanned) > 0

    def of_kind(self, kind: str) -> list[Site]:
        """Return the sites one instrument found, so neither population stands for both."""
        return [s for s in self.sites if s.kind == kind]

    def lines(self) -> list[str]:
        """Return the report: every site, then the two denominators, never summed."""
        out = [s.why() for s in sorted(self.sites, key=_order)]
        out.append("")
        out.append(
            f"{len(self.of_kind('py-const'))} python constant(s) over {self.py_scanned} file(s)"
        )
        out.append(
            f"{len(self.of_kind('prose-fence'))} prose line(s) over {self.prose_scanned} file(s)"
        )
        # ⚑ THE TWO ARE NEVER ADDED. One is an AST reading and one is a text match over code
        # fences — different instruments with different blind spots, so a combined figure
        # would be a count from one instrument compared against another (gate-G228).
        out.append(
            "⚑ the two populations are NOT summed — different instruments, different blind spots."
        )
        if not self.total():
            out.append("⚑ NOTHING WAS SCANNED — this zero is a fact about the invocation.")
        return out


def _order(site: Site) -> tuple[str, int]:
    """Return the sort key — by path, then line. Named so the order is one stated thing."""
    return (str(site.path), site.line)


def census(roots: list[Path], moves: tuple[Move, ...] = CASSIAN_CUTOVER) -> Census:
    """Return every site under `roots` naming a port `moves` retired.

    ⚑ THE MOVES ARE A PARAMETER, so a case can state a table rather than depending on the
    live one — which changes at the next cutover, and would invert every arm that pinned it.
    """
    sites: list[Site] = []
    py_seen = prose_seen = 0
    for root in roots:
        for path in sorted(root.rglob(PY)) if root.is_dir() else [root]:
            if path.suffix == ".py":
                py_seen += 1
                sites.extend(scan_python(path, moves))
        for path in sorted(root.rglob(MD)) if root.is_dir() else []:
            prose_seen += 1
            sites.extend(scan_prose(path, moves))
    return Census(sites, py_seen, prose_seen)


def run(argv: list[str]) -> int:
    """Print the census over the named roots, or the usage.

    ⚑ A NON-EMPTY CENSUS EXITS 1, so this can be wired as a gate later without rewriting the
    contract. ⚑⚑ AND AN UNSCANNED RUN EXITS 2 RATHER THAN 0: a zero over a zero denominator
    is a fact about the invocation, and exiting clean on it would bank exactly the false green
    this module exists to make unrepresentable.
    """
    if not argv or argv[0] != MODE:
        print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
        print(
            f"    endpoint_census.py {MODE} <root>...   "  # noqa: T201
            f"# every site naming a port the declaration retired"
        )
        return USAGE_EXIT
    roots = [Path(a) for a in argv[1:]] or [Path()]
    # ⚑ THE PROVENANCE LEADS THE REPORT. A reader must know whether these rows were DERIVED
    # from the owner's declaration or transcribed here before they can weigh a zero — and a
    # figure whose source is implied is the laundering defect this arc has already paid for.
    said = read_registry()
    print(said.why())  # noqa: T201 - this module IS the report
    print()  # noqa: T201
    found = census(roots, said.moves)
    for line in found.lines():
        print(line)  # noqa: T201 - this module IS the report
    if not found.total():
        return USAGE_EXIT
    return 1 if found.sites else 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
