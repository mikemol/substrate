#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print a document's section spans — the CLI over `mikemol.mdstruct.spans`.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE READER SHOULD NOT PRINT, the same split the rest of
this toolkit uses: `spans` returns data, this decides how to render it.

    md_spans_show.py FILE.md

⚑ IT PRINTS THE LEVEL AS INDENTATION, because the nesting is the thing a reader most needs to
check: a span that ends at its own child looks entirely plausible as a number pair and obviously
wrong as an indented tree.

⚑⚑ THE SELFTEST IS SELF-CONTAINED (W9). It used to delegate to `substrate.md_spans_selftest`,
which tested `substrate.md_spans` — a module retired onto `mikemol.mdstruct.spans` in the same
tick that made this file import the replacement. Delegating to a second file for coverage this
module can hold itself would only recreate the two-body problem that retirement exposed.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from mikemol.mdstruct import spans as md_spans

_DOC = "# Top\nbody\n\n## Child\nmore body\n"
_HEADERLESS = "just prose, no headers\n"

# The exit codes `main`'s four branches take.
_OK = 0
_REFUSED = 2


def render(spans: list[md_spans.Span]) -> list[str]:
    """Render one line per span, indented by level."""
    out = []
    for span in spans:
        indent = "  " * span.level
        out.append(f"  L{span.start:>4}-{span.end - 1:<4} {indent}{'#' * span.level} {span.text}")
    return out


def main(argv: list[str]) -> int:
    """Print every section span in the named document."""
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        sys.stderr.write("usage: md_spans_show.py FILE.md\n")
        return 2

    path = Path(args[0])
    if not path.exists():
        sys.stderr.write(f"md-spans: no such file: {path}\n")
        return 2

    spans = md_spans.spans(path)
    if not spans:
        # ⚑ NO SECTIONS IS A FACT ABOUT THE DOCUMENT, and it says so rather than printing
        # nothing — a bare silence reads as a tool that failed.
        sys.stdout.write(f"md-spans: {path} declares no headers\n")
        return 0

    sys.stdout.write("\n".join(render(spans)) + "\n")
    sys.stdout.write(f"  {len(spans)} section(s) in {path}\n")
    return 0


def _render_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `render`'s own formatting decision."""
    doc = tmp / "doc.md"
    doc.write_text(_DOC, encoding="utf-8")

    spans = md_spans.spans(doc)
    lines = render(spans)

    return [
        (f"one line per section: {lines}", len(lines) == len(spans)),
        (
            f"the child is indented deeper than the parent: {lines}",
            lines[1].index("#") > lines[0].index("#"),
        ),
    ]


def _main_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `main`'s own branches: missing file, no headers, success."""
    missing = tmp / "absent.md"
    missing_rc = main(["md_spans_show.py", str(missing)])

    headerless = tmp / "headerless.md"
    headerless.write_text(_HEADERLESS, encoding="utf-8")
    headerless_rc = main(["md_spans_show.py", str(headerless)])

    doc = tmp / "doc.md"
    doc.write_text(_DOC, encoding="utf-8")
    doc_rc = main(["md_spans_show.py", str(doc)])

    bare_rc = main(["md_spans_show.py"])

    return [
        (f"a missing file refuses: {missing_rc}", missing_rc == _REFUSED),
        (f"a headerless document is reported, not silent: {headerless_rc}", headerless_rc == _OK),
        (f"a sectioned document succeeds: {doc_rc}", doc_rc == _OK),
        (f"no operand refuses: {bare_rc}", bare_rc == _REFUSED),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    tmp = Path(tempfile.mkdtemp())
    try:
        cases = _render_cases(tmp) + _main_cases(tmp)
    finally:
        shutil.rmtree(tmp)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"md-spans-show selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sys.exit(main(sys.argv))
