# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which files in this repo are ratchet gates — derived by predicate, over every gate home.

⚑⚑⚑ THE POPULATION IS THE THING THAT KEEPS BEING WRONG, AND IT IS ALWAYS WRONG THE SAME WAY:
a predicate is widened while the SEARCH SCOPE stays where it was. `gate_census.ratchet_consumers`
records four rounds of this in its own docstring — mention-vs-call, a one-line `os.path.join`
that reported three of fifteen, an inline call site, and a second ratchet KIND that compares a
scalar instead of a key set. Each fix made the predicate see more; none moved the directory.

⚑⚑ SO THE FIFTH INSTANCE WAS BUILT IN. That function opens `os.path.join(REPO, "scripts")`, and
a gate that moves into the package leaves the census's view entirely. MEASURED: the population
is 18 files, all under `scripts/`, and both `substrate/type_gate.py` and
`substrate/private_gate.py` — live gates, one of them running in the hook — are absent. **Not
UNREAD, which is the state the census provides for "this reader could not resolve it": ABSENT,
with no row at all.** A census that cannot see a gate cannot report that it cannot see it, and
that sentence is quoted from the function this one exists to correct.

⚑ THE PREDICATE IS BORROWED, NOT REWRITTEN. Ratchet-ness is already correctly derived — the
shared `set_ratchet` API, or a baseline the file OWNS (a WRITE to the literal, since a reader
never performs one). Re-deriving it here would create the rival authority this repo files
against everywhere else. What is new is only WHERE to look, and that is a declared roster of
gate homes rather than a single hardcoded path.

⚑⚑ AND THE HOMES ARE DECLARED RATHER THAN DISCOVERED, DELIBERATELY. Walking the whole repo for
anything matching the predicate would sweep in `build/lib/` copies, the scratch tools that
discuss the API, and any future vendored tree — and a population that grows silently is the
same defect pointed the other way. Two homes are named because two homes hold gates today; a
third is a one-line addition with a reason attached.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ WHERE GATES LIVE. `scripts/` is the historical home; `substrate/` is where the migration
# puts them, and a gate that moved must not leave the census.
GATE_HOMES = ("scripts", "substrate")

# ⚑ NOT A GATE, THOUGH IT NAMES THE API. The shared ratchet module IS the authority every gate
# calls; counting it would report the library as one of its own consumers.
#
# ⚑⚑ AND `ratchet_legacy.py` IS DELIBERATELY ABSENT FROM THIS SET. A first cut excluded it as
# "obviously library", and the scoped census — the authority being corrected — counts it. It
# DEFINES the twelve-argument `set_ratchet` adapter, so it owns a real write path; excluding it
# was me overruling the existing reader on a guess. The exclusions are only the modules that
# neither define nor drive a baseline write.
#
# ⚑⚑⚑ AND THIS FILE EXCLUDES ITSELF, WHICH IS NOT VANITY. Its own prose quotes `run_gate(` and
# the baseline-write spellings in order to EXPLAIN them, so a source-text predicate matches its
# own documentation — the census that listed its author as a ratchet, exactly. Excluding by
# filename is honest here because the exclusion is about IDENTITY (the instrument is not its
# subject), not about a property some other file might share.
NOT_A_GATE = frozenset({"ratchet.py", "ratchet_core.py", "gate_population.py"})

# ⚑ A CALL, NOT A MENTION — the first of the four recorded false zeroes. Substring-matching the
# name also catches every file that merely discusses the API, including a census of gates.
_CALL = re.compile(r"\bratchet\.set_ratchet\s*\(|(?<![\w.])set_ratchet\s*\(")

# ⚑ OWNS, NOT MENTIONS. A ratchet is the thing that can LOWER its baseline, so the witness is a
# WRITE to the literal. A reader of baselines — a census, a key-schema tool — never performs
# one, which is what keeps the instrument out of its own population.
#
# ⚑⚑⚑ AND A `*baseline*.txt` LITERAL ALONE IS NOT THE WITNESS — I TRIED IT AND IT ADMITTED
# EVERY READER. Reaching for the literal to catch `set1_ratchet_cores` (a ratchet KIND that
# compares a scalar over a denominator, so it calls neither shared function) pulled in
# `gate_census`, `gate_keys`, `ratchet_key` and this very file: four tools that READ baselines,
# which is what a census over the gates does. That is the OWNS-not-MENTIONS distinction the
# borrowed docstring records — reintroduced by me, in the widening direction, one paragraph
# after quoting it. The write is the whole witness: a reader never performs one.
_OWNS = re.compile(
    r"open\s*\(\s*[A-Z_]*BASELINE[A-Z_]*\s*,\s*[\"']w[\"']|"
    r"write_baseline\s*\("
)

# ⚑ THE PACKAGE'S OWN SPELLING OF OWNERSHIP. A `substrate/` gate declares its baseline and hands
# it to `Gate(...)` rather than opening it — the write happens inside the shared authority — so
# the `scripts/`-era witness cannot see it. Same capability, second spelling.
#
# ⚑⚑⚑ IT REQUIRES `run_gate` TOO, AND THE FIRST CUT DID NOT — WHICH PUT THIS FILE IN ITS OWN
# POPULATION. Matching `Gate(` or `baseline_path=` alone admitted `baseline_io` (the library
# that performs the write), `commit_refusal`, `argument_consumed`, and `gate_population` itself:
# four files that MENTION the vocabulary and gate nothing. That is precisely the mention-vs-call
# error the borrowed docstring records as the first of four false zeroes, reproduced here in the
# widening direction — and it was caught only by diffing against the reader being corrected.
# A gate DECLARES a Gate and RUNS it; naming either half alone is not the capability.
_DECLARES = re.compile(r"\brun_gate\s*\(")


def defines(source: str, name: str) -> bool:
    """Report whether `source` DEFINES `name` rather than calling it."""
    return re.search(rf"^\s*def\s+{re.escape(name)}\s*\(", source, re.MULTILINE) is not None


def is_gate(source: str) -> bool:
    """Report whether `source` is a ratchet gate, by any of the three witnesses.

    ⚑ THREE SUFFICIENT WITNESSES, NOT ONE. The two-spelling collapse is the recurring defect
    in this family: a capability spelled a second way reads as absent, and `--dead` deletes on
    exactly that reading. A file is a gate if it CALLS the shared ratchet, if it OWNS a
    baseline by writing one, or if it DECLARES one to the shared gate runner.

    ⚑⚑⚑ A DEFINITION IS NOT A USE, AND EVERY OVER-ADMISSION HERE WAS THAT ONE ERROR. A regex
    for `run_gate(` matches the `def run_gate(` that implements it; one for `write_baseline(`
    matches its definition too. So `gate_main` and `baseline_io` — the two authorities the
    gates call — entered the population as gates, which is the library-counted-as-its-own-
    consumer shape the `NOT_A_GATE` list exists to prevent, arriving through a second door.
    Excluding by NAME would have needed a new list entry per authority; excluding by the
    STRUCTURE (a file that defines the capability is its home, not its user) needs none.
    """
    if _CALL.search(source) and not defines(source, "set_ratchet"):
        return True
    if _OWNS.search(source) and not defines(source, "write_baseline"):
        return True
    return bool(_DECLARES.search(source) and not defines(source, "run_gate"))


def candidates() -> list[Path]:
    """Return every file a gate could live in, across the declared homes."""
    root = corpus.ROOT
    out: list[Path] = []
    for home in GATE_HOMES:
        base = root / home
        if not base.is_dir():
            continue
        out.extend(sorted(p for p in base.glob("*.py") if p.name not in NOT_A_GATE))
    return out


def gates() -> list[str]:
    """Return the repo-relative path of every ratchet gate, across every home.

    ⚑ A SELFTEST IS NOT A GATE. `<name>_selftest.py` exercises one, and it names the API to do
    so — the mention-vs-call distinction one level out. Counting them would roughly double the
    population with files that gate nothing.
    """
    root = corpus.ROOT
    found: list[str] = []
    for path in candidates():
        if path.name.endswith("_selftest.py"):
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        if is_gate(source):
            found.append(str(path.relative_to(root)))
    return sorted(found)


def known_misses() -> tuple[tuple[str, str], ...]:
    """Return `(path, why)` for gates the scoped census sees and this reader does not.

    ⚑⚑⚑ CARRIED IN CODE BECAUSE A DIFFERENCE NOBODY RECORDS IS A DIFFERENCE NOBODY FIXES.
    This reader was built to widen a population and it currently MISSES two files the reader
    it corrects can see. Reporting only the newly-visible rows would make it look like a pure
    gain, which is the shape that lets a replacement quietly lose coverage.

    ⚑⚑ AND NEITHER IS A REGEX TO GUESS AT. Three attempts to catch them by widening the
    pattern admitted, in turn, every baseline READER, then every file that writes any text at
    all — the OWNS-not-MENTIONS collapse the borrowed docstring records, reproduced twice in
    one sitting. Both need a witness derived from what the file DOES, which is work, not a
    tuning pass.
    """
    return (
        (
            "scripts/ratchet_legacy.py",
            (
                "DEFINES the twelve-argument set_ratchet adapter, so the definer-exclusion that "
                "keeps gate_main and baseline_io out also removes it; the scoped census counts it"
            ),
        ),
        (
            "scripts/set1_ratchet_cores.py",
            (
                "a different ratchet KIND — a scalar over a denominator — so it calls neither "
                "set_ratchet nor write_baseline; its baseline literal is the only static witness "
                "and matching that admits every baseline reader"
            ),
        ),
    )


def outside(home: str = "scripts") -> list[str]:
    """Return the gates that do NOT live in `home` — what a scoped census misses.

    ⚑ THIS IS THE MODE THAT MAKES THE OMISSION VISIBLE. The defect is invisible by
    construction: a census scoped to one directory reports a clean total, and nothing in that
    total says a second directory exists. Naming the miss as its own reading is what turns it
    from a silent absence into a number an operator can act on.
    """
    prefix = f"{home}/"
    return [g for g in gates() if not g.startswith(prefix)]


USAGE = """\
gate_population.py — which files are ratchet gates, across every declared home.

  gate_population.py --gates      every gate, one repo-relative path per line
  gate_population.py --outside    the gates a `scripts/`-scoped census cannot see
  gate_population.py --misses     gates the scoped census sees and this reader does NOT
  gate_population.py --selftest   the cases

⚑ THREE SUFFICIENT WITNESSES, not one: a file is a gate if it CALLS the shared ratchet,
  OWNS a baseline by writing one, or DECLARES one to the shared gate runner. A file that
  DEFINES any of those is its home, not its user, and is excluded structurally.

⚑ `--misses` IS NOT AN EMPTY LIST AND IS NOT MEANT TO BE. This reader was built to widen a
  population and currently misses two files the reader it corrects can see. Printing only
  the newly-visible rows would make a replacement look like a pure gain — the shape that
  lets coverage be lost quietly.
"""


# ⚑ THE REFUSAL CODE IS NAMED, not spelled at each site. `2` is what `check_argv` and
# `gate_main` both return for "could not answer", and a bare integer at a comparison says
# nothing about which of those it means.
REFUSED = 2


def render_gates(_arg: str) -> str:
    """Render every gate, with a count."""
    found = gates()
    return "".join(f"{g}\n" for g in found) + f"{len(found)} gate(s)\n"


def render_outside(arg: str) -> str:
    """Render the gates outside `arg` (default `scripts`), with a count."""
    home = arg or "scripts"
    found = outside(home)
    return "".join(f"{g}\n" for g in found) + f"{len(found)} gate(s) outside {home}/\n"


def render_misses(_arg: str) -> str:
    """Render the gates this reader cannot see, each with its reason."""
    rows = known_misses()
    return "".join(f"{path}\n    {why}\n" for path, why in rows) + f"{len(rows)} known miss(es)\n"


# ⚑ A DISPATCH TABLE, matching the other readers in this family. Routing as data rather than
# as branches is what keeps a mode from existing in the code and nowhere in the usage.
MODES = {
    "--gates": render_gates,
    "--outside": render_outside,
    "--misses": render_misses,
}


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code.

    ⚑⚑⚑ THIS MODULE HAD NO CLI AT ALL, AND EXITED 0 PRINTING NOTHING — bare AND on `--help`.
    That is the exact defect the codemod skill records as its second fact: "run the tool bare
    to read its modes" is this repo's instruction to every reader, and a silent exit 0 is
    indistinguishable from a tool that ran and found nothing. Its findings (`known_misses`,
    `outside`) were reachable only by importing it, so the omission it exists to surface was
    itself unreachable from a command line.
    """
    import sys  # noqa: PLC0415 — kept local so importing this module costs nothing

    if "--selftest" in argv:
        from substrate import gate_population_selftest  # noqa: PLC0415

        return 0 if gate_population_selftest.selftest() else 1

    flags = [a for a in argv[1:] if a.startswith("--")]
    rest = [a for a in argv[1:] if not a.startswith("--")]
    mode = MODES.get(flags[0]) if flags else None
    if mode is None:
        sys.stdout.write(USAGE)
        return REFUSED

    sys.stdout.write(mode(rest[0] if rest else ""))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
