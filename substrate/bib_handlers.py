# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The read handlers: each declared mode bound to the module that already answers it.

⚑⚑⚑ EVERY HANDLER HERE IS A READ, A RENDER AND A CENSUS SUBJECT, AND THAT IS THE MEASURE OF WHETHER
THE DRAIN WORKED. The origin's equivalent branches carried the reading, the formatting and the
denominator inline — so a mode's behaviour could only be learned by reading its branch, and two
branches answering the same question could drift apart unnoticed. **If a handler needs logic, the
logic belongs in a module, and the handler is where you notice that.**

⚑⚑ MODULE-LEVEL HANDLERS OVER A `Context`, NOT CLOSURES INSIDE `bind` — AND THE PER-FILE GATE ASKED
FOR THIS TWICE. The write handlers hit `C901` at complexity 14 with both verbs nested in one
function; this module hit it at 11 the moment a sixth verb was added. **One function accumulating
every verb's logic is the monolith shape at closure scale**, and the limit is the signal rather than
the obstacle. The context holds what a session fixes; each handler reads on its own.

⚑⚑ THE DENOMINATOR IS SUPPLIED BY THE SAME CALL THAT SUPPLIES THE ROWS, WHICH IS WHY IT CANNOT BE
FORGOTTEN. Each read builds a `Census` from what it found AND the population it read over, so a zero
always arrives with the number that says whether the probe looked at anything. The origin printed
those from separate statements, and its totality probe shipped without the second until a reader
could not tell a total read from an empty one.

⚑ THE READER IS INJECTED RATHER THAN IMPORTED, so this module does not decide WHICH parser reads a
bib — a fixture substitutes one without touching anything here, and the origin's suite had to drive
its CLI against real files on disk precisely because that choice was hardcoded.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.witness.warrant_bib import consumer_fields

from substrate import bib_cli, bib_corpus, bib_report, bib_roundtrip

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate import bib_argv

# The bib a read falls back to when the invocation names none.
# ⚑ NAMED ONCE. The origin resolved its default inside the branch bodies, so a mode added later got
# whatever its author remembered.
DEFAULT_BIB = "catalog/worklist/warrants.bib"

# What a mode taking a leading name prints when it is given none.
NAME_USAGE = "usage: bibstruct.py {mode} <name> [bib …]"

# Where a paperkit project states which non-engine fields its bib carries.
# ⚑ THE CONFIG FOLLOWS THE BIB, never a fixed home: `--dropped` is asked about whatever file it is
# given, and a project's declaration lives beside its own warrants.
CONFIG_NAME = "paper.toml"

# ⚑⚑ THE BOUND TRAVELS WITH THE VERDICT, IN BAND. A caveat kept in prose gets summarised away;
# printed beside the result it cannot be. That is ⟡bounds-in-band, applied to the one read whose
# green is most likely to be over-read.
TOTAL_NOTE = (
    "   this read is TOTAL over this input — an ALGEBRA result. It does NOT say the\n"
    "   parser's kernel is empty; it says nothing in THIS file fell into it."
)


@dataclass(frozen=True, slots=True)
class Context:
    """What a read session fixes: how a bib is parsed into entries."""

    parse: Callable[[Path], dict[str, dict[str, str]]]


def _paths(parsed: bib_argv.Parsed) -> list[Path]:
    """Return every bib the invocation named, or the default when it named none."""
    return [Path(p) for p in (parsed.paths or (DEFAULT_BIB,))]


def _read(ctx: Context, parsed: bib_argv.Parsed) -> bib_corpus.Corpus:
    """Compose every bib the invocation named.

    ⚑ EVERY PATH IS READ. The origin collected every positional and passed only the first to its
    parser, so a widened input produced a byte-identical count and the silent drop read as *"the
    finding survives"*.
    """
    return bib_corpus.compose(_paths(parsed), ctx.parse)


def _operand(parsed: bib_argv.Parsed) -> tuple[str | None, bib_argv.Parsed]:
    """Split a mode's leading operand off its trailing paths.

    ⚑ THE ROSTER IS WHAT SAYS THERE IS ONE. `bib_modes` declares `operand="name"` for exactly the
    modes that take one, so this never guesses — the defect that crashed `--key --archive f.py`
    when arity was inferred at the call site.
    """
    if not parsed.paths:
        return None, parsed
    return parsed.paths[0], replace(parsed, paths=parsed.paths[1:])


def entries(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """List every key and the field names it carries."""
    corpus = _read(ctx, parsed)
    rows = bib_report.rows(
        [
            (key, ", ".join(sorted(n for n in fields if not n.startswith("_"))))
            for key, fields in sorted(corpus.entries.items())
        ]
    )
    census = bib_report.Census("entries", len(corpus.entries), len(corpus.entries))
    return bib_cli.render(rows, census), 0


def field(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Show one field's value across every entry that carries it."""
    name, rest = _operand(parsed)
    if name is None:
        return (NAME_USAGE.format(mode=parsed.mode),), bib_cli.REFUSED
    corpus = _read(ctx, rest)
    found = [
        (key, fields[name]) for key, fields in sorted(corpus.entries.items()) if name in fields
    ]
    census = bib_report.Census(name, len(found), len(corpus.entries))
    return bib_cli.render(bib_report.rows(found), census), 0


def mentions(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Show entries whose PROSE names a key — evidence, never a verdict."""
    key, rest = _operand(parsed)
    if key is None:
        return (NAME_USAGE.format(mode=parsed.mode),), bib_cli.REFUSED
    corpus = _read(ctx, rest)
    found = bib_corpus.mentions(corpus, key)
    rows = tuple(f"  {other:<16} {name:<8} {ctx_text}" for other, name, ctx_text in found)
    # ⚑ THE DENOMINATOR EXCLUDES THE ENTRY ITSELF, because a key cannot mention itself and
    # counting it would make a total read look partial.
    census = bib_report.Census(key, len(found), max(0, len(corpus.entries) - 1))
    return bib_cli.render(rows, census), 0


def edges(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """List every declared edge across the composed corpus."""
    corpus = _read(ctx, parsed)
    found = bib_corpus.edges(corpus)
    census = bib_report.Census("edges", len(found), len(corpus.entries))
    return bib_cli.render(bib_report.edge_rows(list(found)), census), 0


def orphans(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """List edges whose target is no entry in the corpus READ.

    ⚑⚑ THE GAP LINE IS APPENDED WHEN KEYS COLLIDE, and it is not decoration: a composed read
    counts DISTINCT keys while a record-counting parser counts DECLARATIONS, and an unexplained
    difference between them reads as a parse defect. A peer ruled exactly that out by hand before
    the line existed.
    """
    corpus = _read(ctx, parsed)
    found = bib_corpus.orphans(corpus)
    census = bib_report.Census("orphans", len(found), len(corpus.entries))
    lines = bib_cli.render(bib_report.dangling_rows(list(found)), census)
    gap = corpus.gap_line()
    return ((*lines, gap) if gap else lines), (1 if found else 0)


def _dropped_rows(ctx: Context, path: Path) -> list[tuple[str, str]]:
    """Return `(key.field, value)` for every field one bib sets that the engine discards."""
    # ⚑⚑⚑ THE ENGINE IS IMPORTED HERE, NOT AT MODULE SCOPE, AND A PEER WAS BLOCKED BY THE
    # DIFFERENCE (gate-G209). `warrant_records` imports `paperkit.bib` at top level — correctly,
    # since it is a declared dependency — but `bib_handlers` is pulled by `bibstruct_main`, so a
    # module-scope import here made EVERY mode of the CLI unreachable for a consumer without a
    # paperkit venv. Not one mode: all of them, because the chain runs at load.
    #
    # ⚑ THIS IS THE ONE FUNCTION THAT NEEDS THE ENGINE, so the import sits where the dependency
    # actually is. `--dropped` still fails honestly for a consumer lacking paperkit; every other
    # mode now runs.
    # ⚑⚑⚑ THE IMPORT IS INSIDE THE `try`, AND A PEER MEASURED WHY THAT IS NOT PEDANTRY. A first
    # cut put it one line ABOVE the block — so `warrant_records`' own module-scope engine import
    # raised from the import STATEMENT, outside the handler written to catch it. The guard read
    # as present in every review and fired never.
    #
    # ⚑⚑ AND NOTHING AVAILABLE WOULD HAVE CAUGHT IT. A run WITH paperkit never enters the branch,
    # so a suite passes; a run WITHOUT it tracebacks, but only if someone invokes `--dropped` in
    # that configuration — precisely the consumer environment the owner's verification cannot
    # reach. `swap_readiness` still reports READY, because the import is package-shaped. The
    # instrument, the suite and the reader all agreed, and none was looking at the line.
    try:
        from substrate import warrant_records  # noqa: PLC0415 — see above

        kept = warrant_records.records(path)
    except ImportError:
        # ⚑⚑ AN ABSENT ENGINE IS A THIRD OUTCOME, not a dropped field and not a crash. A consumer
        # without paperkit installed gets an empty census rather than a traceback — the honest
        # answer being that this mode cannot be measured here, which the caller's own denominator
        # reports as `0 of N`.
        return []
    except warrant_records.BibError:
        # ⚑ AN ENGINE THAT CANNOT READ THE FILE IS NOT A DROPPED FIELD. Reporting its refusal as a
        # row would put a fact about the READ into a census about the CONTENT.
        return []

    declared = set(consumer_fields(path.parent / CONFIG_NAME))
    return [
        (f"{key}.{name}", value)
        for key, fields in sorted(ctx.parse(path).items())
        for name, value in sorted(fields.items())
        if not name.startswith("_") and name not in kept.get(key, {}) and name not in declared
    ]


def dropped(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Report fields the FILE sets that the ENGINE silently discards.

    ⚑⚑⚑ THIS IS THE ONE READ THAT ASKS A SECOND AUTHORITY, AND ROUTING IT THROUGH THE PACKAGED
    ENGINE IS THE WHOLE POINT. The difference between what the bytes declare and what the engine
    keeps cannot be computed from either side alone — re-deriving the whitelist here would recreate
    the disagreement the engine's parser exists to have ended.

    ⚑⚑ AND THE PROJECT'S DECLARED CONSUMER FIELDS ARE SUBTRACTED, WHICH IS THE FIX FOR A DEFAULT
    THAT SILENTLY NARROWS AN AUTHORITY. The engine's bare parse applies its OWN defaults, so a
    project widening the whitelist in its `paper.toml` had every declared field reported as dropped
    forever. The config follows the BIB rather than a fixed home, so the answer is about the file
    the caller named.

    ⚑ A FIELD THE FILE SETS AND THE ENGINE DROPS is either a consumer's own concern — legitimate,
    but it must then be DECLARED — or a typo that will never be reported. Both are worth a row, and
    the declaration is what separates them.
    """
    corpus = _read(ctx, parsed)
    rows = [row for path in _paths(parsed) for row in _dropped_rows(ctx, path)]
    census = bib_report.Census("dropped", len(rows), len(corpus.entries))
    return bib_cli.render(bib_report.rows(rows), census), 0


def roundtrip(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Report every construct the file holds that the parse did not account for.

    ⚑⚑ THIS IS THE ONE READ WHOSE ROWS ARE FAILURES, so it exits NON-ZERO on a finding while every
    other read exits 0 with results. A totality probe that reported its losses and exited 0 would
    be a gate that cannot go red.

    ⚑ AND EACH PATH IS PROBED SEPARATELY, because the question is about a FILE. Composing first
    would ask whether the corpus accounts for itself — a different question, and one the orphan
    reader already answers.
    """
    losses: list[bib_roundtrip.Loss] = []
    for path in _paths(parsed):
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        losses.extend(bib_roundtrip.probe(text, ctx.parse(path)))

    corpus = _read(ctx, parsed)
    rows = tuple(f"  {loss.kind:<16} {loss.what:<24} {loss.detail}" for loss in losses)
    census = bib_report.Census("roundtrip", len(losses), len(corpus.entries))
    lines = bib_cli.render(rows, census)
    if not losses:
        # ⚑ AN ALGEBRA RESULT, AND THE CAVEAT SHIPS WITH IT. A green here says nothing in THIS
        # file fell into the kernel — not that the kernel is empty. Printing the verdict without
        # the bound is how a reader banks the stronger claim.
        lines = (*lines, TOTAL_NOTE)
    return lines, (1 if losses else 0)


def bind(ctx: Context) -> dict[str, Callable[[bib_argv.Parsed], bib_cli.Result]]:
    """Return the read-handler table over `ctx`.

    ⚑ THE TABLE IS A LOOKUP, AND SO IS ITS CONSTRUCTION. Each entry binds a module-level handler
    to the context — nothing here is a place logic can accumulate, which is what the complexity
    refusal was pointing at, twice.
    """
    return {
        "--entries": partial(entries, ctx),
        "--field": partial(field, ctx),
        "--mentions": partial(mentions, ctx),
        "--edges": partial(edges, ctx),
        "--orphans": partial(orphans, ctx),
        "--dropped": partial(dropped, ctx),
        "--roundtrip": partial(roundtrip, ctx),
    }
