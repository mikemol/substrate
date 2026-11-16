#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the roster renderer, BYTE-FOR-BYTE against the origin it drains.

⚑⚑⚑ BYTE-IDENTICAL IS THE CONTRACT HERE, NOT MERELY EQUIVALENT. Every future diff in the
roster is measured against this shape, so a one-space difference would rewrite the appearance
of every subsequent registration and make one real change indistinguishable from a reformat.
The differential therefore compares the emitted STRING, not a parse of it.

⚑⚑ THE DOUBLE-QUOTED KEY IS ASSERTED DIRECTLY, because `repr` gets it wrong and the failure is
invisible from inside this module. `bibstruct --add` resolves `check=item:<key>` against the
roster with a regex requiring double quotes; a single-quoted key registers fine, resolves fine
at runtime, and is invisible to the one reader whose refusal it must clear.

⚑ AND THE REJOIN IS CHECKED THROUGH `ast.parse`, NEVER `eval` OR `literal_eval`. The wrapper's
output is source text, and a suite that executed it would be running the very agent-supplied
string the `repr` exists to neutralise. Walking the parsed expression for `ast.Constant` nodes
is typed at every step, and it asserts something stronger than a round trip: that the wrapper
emitted STRING literals rather than anything else that merely parses.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import finding_entry, finding_kindspec

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

Case = tuple[str, bool]

# A note long enough to wrap, and one short enough not to.
_LONG = ("This note is deliberately long enough that the wrapper must break it across more "
         "than one literal, so the trailing-space rejoin is exercised rather than assumed, "
         "and it carries a quote-free body so the comparison is about wrapping alone.")
_SHORT = "a short note"
# ⚑ A NOTE THAT WOULD BREAK AN UNQUOTED EMIT — the reason the note goes through `repr`.
_HOSTILE = "it said \"no\" and used a backslash \\ and a single ' quote"


def _text_of(node: ast.Constant) -> str:
    """Return a constant's string value, or a marker when it is not a string.

    ⚑ A NON-STRING CONSTANT IS REPORTED, NOT COERCED. A wrapper emitting something that merely
    parses would otherwise pass a round-trip check by accident.
    """
    return node.value if isinstance(node.value, str) else "<NOT-A-STRING>"


def _rejoined(wrapped: str) -> str:
    """Return the text the emitted literals concatenate back to."""
    try:
        tree = ast.parse("(" + wrapped + ")", mode="eval")
    except SyntaxError:
        return "<DOES-NOT-PARSE>"
    return "".join(_text_of(node) for node in ast.walk(tree)
                   if isinstance(node, ast.Constant))


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    def _wrap(self, note: str, width: int = 94) -> str: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings_entry", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _render_cases() -> list[Case]:
    """Return the cases pinning what an entry looks like for each kind."""
    bare, _ = finding_kindspec.parse("standing")
    cmd, _ = finding_kindspec.parse("selftest:python3 -m substrate.finding_entry_selftest")
    moded, _ = finding_kindspec.parse("mode:toolmodes.py:--divergence")
    if bare is None or cmd is None or moded is None:
        return [("the fixtures parse, so the render cases mean something", False)]
    bare_row = finding_entry.render("k-bare", bare, _SHORT)
    cmd_row = finding_entry.render("k-cmd", cmd, _SHORT)
    mode_row = finding_entry.render("k-mode", moded, _SHORT)
    return [
        # ⚑⚑ THE DOUBLE QUOTE IS THE CONTRACT WITH bibstruct's RESOLVER REGEX.
        ("the key is DOUBLE-quoted, which the resolver regex requires",
         bare_row.startswith('    "k-bare":')),
        ("...and never single-quoted, which repr would emit", "'k-bare'" not in bare_row),
        ("a bare kind renders its builder", "lambda: _standing(" in bare_row),
        ("a command kind renders its argv", "'python3'" in cmd_row),
        ("...under its own builder", "lambda: _selftest(" in cmd_row),
        # ⚑ A mode ENTRY CARRIES TOOL AND FLAG AND NO NOTE — the origin's shape, because the
        #   reader derives its own message and a note here would be a second, unread one.
        ("a mode kind renders tool and flag",
         "'toolmodes.py'" in mode_row and "'--divergence'" in mode_row),
        ("...and carries no note", _SHORT not in mode_row),
        ("every entry is one indented, comma-terminated row",
         all(row.startswith("    ") and row.endswith(",\n")
             for row in (bare_row, cmd_row, mode_row))),
    ]


def _wrap_cases() -> list[Case]:
    """Return the cases pinning the wrap, including the trailing-space rejoin."""
    wrapped = finding_entry.wrap_note(_LONG)
    short = finding_entry.wrap_note(_SHORT)
    hostile = finding_entry.wrap_note(_HOSTILE)
    return [
        ("a long note breaks across literals", finding_entry.CONT in wrapped),
        ("a short note does not", finding_entry.CONT not in short),
        # ⚑ THE REJOIN IS THE PROPERTY, checked by PARSING the emitted source rather than by
        #   inspecting its quoting — the literals must concatenate back to the note.
        ("the wrapped literals rejoin to the original note",
         _rejoined(wrapped) == " ".join(_LONG.split())),
        ("a short note rejoins too", _rejoined(short) == _SHORT),
        # ⚑⚑ THE HOSTILE NOTE IS WHY repr IS USED. An unquoted emit writes a file that does not
        #   parse, and that failure lands on the NEXT reader of the roster.
        ("a note with quotes and a backslash survives the round trip",
         _rejoined(hostile) == _HOSTILE),
        ("an empty note still emits a literal", finding_entry.wrap_note("") == "''"),
    ]


def _splice_cases() -> list[Case]:
    """Return the cases pinning that the anchor is counted, never searched-and-hoped."""
    body = 'WITNESSES = {\n    "a": 1,\n' + finding_entry.ANCHOR
    entry = '    "b": 2,\n'
    spliced, why = finding_entry.splice(body, entry)
    missing, missing_why = finding_entry.splice("no terminator here", entry)
    doubled, doubled_why = finding_entry.splice(body + body, entry)
    return [
        ("a unique anchor splices", why == ""),
        # ⚑ THE ENTRY LANDS BEFORE THE CLOSING BRACE, not after it.
        ("...with the entry ahead of the terminator",
         spliced.index(entry) < spliced.index(finding_entry.ANCHOR)),
        ("...and the original content survives", '"a": 1' in spliced),
        # ⚑⚑ BOTH REFUSALS. A wrong-offset splice can still PARSE, so guessing is worse than
        #   refusing — neither a round-trip nor a diff review reliably catches it.
        ("a missing anchor REFUSES rather than appending", missing == ""),
        ("...and says how many it found", "0 occurrence" in missing_why),
        ("a duplicated anchor REFUSES rather than picking one", doubled == ""),
        ("...and says how many it found", "2 occurrence" in doubled_why),
        ("...and says why guessing is unsafe", "can still parse" in doubled_why),
    ]


def _differential_cases() -> list[Case]:
    """Compare the wrap BYTE-FOR-BYTE with the origin's over several notes.

    ⚑⚑⚑ THE BYTES ARE THE CONTRACT. Every future roster diff is measured against this shape, so
    an equivalent-but-different rendering would make one real change indistinguishable from a
    reformat of the whole file.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    probes = (_SHORT, _LONG, _HOSTILE, "one " * 60)
    same = all(origin._wrap(probe) == finding_entry.wrap_note(probe)  # noqa: SLF001
               for probe in probes)
    return [
        ("the origin loaded, so this differential means something", True),
        ("the wrap is byte-identical to the origin on every probe", same),
        # ⚑ THE EMPTY NOTE IS THE ONE DELIBERATE DIVERGENCE: the origin emits nothing, which
        #   splices a syntax error. Emitting a literal is a repair, and an intended divergence
        #   that is not cased reads exactly like an accidental one.
        ("...except the empty note, where the origin emits nothing and this emits a literal",
         origin._wrap("") == "" and finding_entry.wrap_note("") == "''"),  # noqa: SLF001
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _render_cases() + _wrap_cases() + _splice_cases() + _differential_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"finding_entry: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
