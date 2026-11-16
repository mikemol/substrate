#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `bibstruct --rename`: the header rename and the handler's cross-bib repoint.

⚑ CASED ON WHAT MUST SURVIVE, as the delete is: the renamed entry keeps every field, its neighbours
are untouched, and a COMMENT that mentions the old key is left alone — the rename edits the header
span the read grammar locates, never a textual occurrence. Every refusal is cased too: renaming
into an existing key would silently merge two findings, and a key the header cannot read back
would make the entry vanish at the next parse.

⚑⚑ THE HANDLER IS DRIVEN THROUGH THE CLI, over a TWO-bib corpus, because an inbound edge may live
in another file. The sibling's edge list holds `OLD-key` AND `OLD-key-as`: a substring repoint
would corrupt the second, so the case asserts it is left exactly as it was.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import bib_cli, bib_edit, bib_parse, bib_write, bib_write_handlers

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate import bib_argv

FIXTURE = """% OLD-key is mentioned in this comment and must stay spelled OLD-key

@misc{OLD-key,
  section  = {finding},
  claim    = {renamed},
  from     = {B}
}

@misc{B,
  section  = {finding},
  claim    = {neighbour}
}
"""

TARGET = """@misc{OLD-key,
  claim    = {renamed}
}

@misc{X,
  claim    = {points at the renamed entry},
  from     = {OLD-key}
}
"""

SIBLING = """@misc{OLD-key-as,
  claim    = {a key the old one is a PREFIX of}
}

@misc{Y,
  claim    = {rests on both},
  rests-on = {OLD-key, OLD-key-as}
}
"""


def _rename(old: str, new: str) -> str | bib_edit.Refusal:
    """Return the fixture with `old` renamed to `new`, through the real grammar."""
    entries = bib_parse.parse(FIXTURE)
    return bib_edit.rename_entry(FIXTURE, (old, new), entries, bib_parse.GRAMMAR)


def _refused(old: str, new: str) -> bool:
    """Report whether renaming `old` to `new` is refused."""
    return isinstance(_rename(old, new), bib_edit.Refusal)


def _header_cases() -> list[tuple[str, bool]]:
    """Return the cases for the pure header rename."""
    done = _rename("OLD-key", "NEW-key")
    if not isinstance(done, str):
        return [("renaming a present key does not refuse", False)]
    after = bib_parse.parse(done)
    return [
        ("renaming a present key does not refuse", True),
        ("the old key is gone", "OLD-key" not in after),
        ("the new key is present", "NEW-key" in after),
        ("the renamed entry keeps every field", after.get("NEW-key", {}).get("from") == "B"),
        ("the neighbour is untouched", after.get("B", {}).get("claim") == "neighbour"),
        ("a comment naming the old key is left alone", done.startswith("% OLD-key is mentioned")),
        ("an unknown key is refused", _refused("Z", "Y")),
        ("renaming into an existing key is refused", _refused("OLD-key", "B")),
        ("a key with a comma is refused", _refused("OLD-key", "a,b")),
        ("an empty key is refused", _refused("OLD-key", "")),
    ]


def _handlers() -> dict[str, Callable[[bib_argv.Parsed], bib_cli.Result]]:
    """Return the write handlers over a bench that records rather than snapshots."""
    bench = bib_write.Bench(
        snapshot=lambda _what, _targets: None,
        roundtrip=lambda _target: [],
        read_back=lambda target: dict.fromkeys(bib_parse.read(target), ""),
    )
    ctx = bib_write_handlers.Context(read=bib_parse.read, bench=bench, grammar=bib_parse.GRAMMAR)
    return bib_write_handlers.bind(ctx)


def _handler_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the handler cases: dry run first, then the applied cross-bib repoint."""
    target, sibling = tmp / "t.bib", tmp / "s.bib"
    target.write_text(TARGET, encoding="utf-8")
    sibling.write_text(SIBLING, encoding="utf-8")
    argv = ["--rename", "OLD-key", "NEW-key", "--bib", str(target), "--corpus", str(sibling)]
    handlers = _handlers()
    _lines, dry = bib_cli.run(argv, handlers)
    untouched = target.read_text(encoding="utf-8") == TARGET
    _lines, code = bib_cli.run([*argv, bib_write.APPLY_FLAG], handlers)
    t_after, s_after = bib_parse.read(target), bib_parse.read(sibling)
    moved = "NEW-key" in t_after and "OLD-key" not in t_after
    _lines, taken = bib_cli.run(
        ["--rename", "NEW-key", "X", "--bib", str(target), bib_write.APPLY_FLAG], handlers
    )
    return [
        ("a dry run succeeds and writes nothing", dry == bib_write.OK and untouched),
        ("an applied rename succeeds", code == bib_write.OK),
        ("the target holds the new key and not the old", moved),
        ("an edge in the TARGET is repointed", t_after.get("X", {}).get("from") == "NEW-key"),
        (
            "an edge in a SIBLING is repointed, whole tokens only",
            s_after.get("Y", {}).get("rests-on") == "NEW-key, OLD-key-as",
        ),
        ("a key the old one prefixes is untouched", "OLD-key-as" in s_after),
        ("renaming into a taken key is refused", taken == bib_cli.REFUSED),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _header_cases() + _handler_cases(Path(tmp))
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"bib-rename selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
