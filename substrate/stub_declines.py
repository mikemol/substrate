#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read what a `.pyi` stub DECLARES it does not cover — its partiality, in its own words.

⚑⚑⚑ A PARTIAL STUB IS LEGITIMATE AND `stubtest` CANNOT KNOW THAT. A stub over a third-party
package SHADOWS the whole package, so `stubtest`'s default demands completeness and reports
every undeclared name as *"not present in stub"*. For `stubs/psycopg` that is hundreds of
findings saying one true thing — *this stub does not cover the async surface* — which the
package docstring already says, deliberately and in detail. Reporting a declared omission as
drift is a fact about the CHECKER'S DEFAULT, not about the stub.

⚑⚑ SO THE RELIEF IS ON THE ENUMERABLE SIDE, AND THIS MODULE IS WHAT MAKES IT ENUMERABLE. The
declaration lives in the STUB, never in a roster here — the `suite_pragmas` pattern, whose
rationale applies verbatim: a hardcoded `{stub: exemptions}` map is current only as of its last
edit. A stub declines a surface by writing a marker in itself, with nothing to remember on this
side, and the gate PRINTS what each stub declined so the relief is reviewable in the same
breath as the verdict.

⚑⚑⚑ THERE ARE TWO MARKERS BECAUSE THERE ARE TWO KINDS OF PARTIALITY, and collapsing them was
the first design's mistake:

  * `⟡declines:` <prose> — a declined SURFACE: names this stub never claimed. Granted to
    `stubtest` as `--ignore-missing-stub`, which is scoped by construction: it can only ever
    silence *absent*, never *contradicted*.
  * `⟡declines-signature:` <dotted names> — declined OPTIONAL PARAMETERS on a signature the
    stub DOES declare. `networkx.descendants` really does take a `backend=` this repo never
    passes, and no flag expresses "that one, deliberately". This is handed to stubtest's own
    `--allowlist`, which names each finding INDIVIDUALLY.

⚑⚑ AND THE SECOND MARKER EXISTS BECAUSE THE FLAG THAT WOULD HAVE BEEN EASIER IS A BLANKET
SKIP. `stubtest --ignore-positional-only` turns `stubs/psycopg` green in one word — and it
would silence that finding class across all 83 modules of the package, including a future
contradiction nobody has looked at yet. An allowlist of named entries costs more to write and
is the only form that can be REVIEWED, so it is the form used. A stub that wants relief must
say which finding, by name.

⚑ NEITHER MARKER CAN SILENCE A CONTRADICTION. A wrong parameter NAME, a wrong type, a wrong
arity, or a name the stub asserts that the runtime lacks fails the gate regardless of what is
declared. `panflute` declines every element constructor AND was still caught renaming `load`'s
parameter — a live latent break that survived only because both call sites passed positionally.
A mechanism that had silenced the whole file would have silenced that too.

⚑ AN UNRECOGNISED MARKER DECLARES NOTHING, fail-closed, as in `suite_pragmas`. A misspelled
`⟡dclines:` is not a declaration, so the gate still reports the findings rather than inventing
an exemption from a typo. Relief must be spelled correctly to be granted.

⚑ AND A DECLARATION IS A CLAIM WITH A COST: what a stub declines, a caller cannot reach. The
prose marker is prose because the point is that a REVIEWER reads it — the thing being declared
is an editorial judgement about which surface this repo means to type.

⚑⚑⚑ THE DOCSTRING IS TAKEN WITH `ast`, NOT SCANNED OUT OF THE TEXT — and this is a NARROWING,
not a refactor with the same extension. Until 2026-09-02 both readers ran their regex over the
WHOLE FILE, so `⟡declines:` at the start of any line declared relief no matter where it sat: in
a `#` comment, in a type alias's string, in a fragment of prose quoted to explain the mechanism.
A `.pyi` IS a Python file, the docstring is a structural fact about it, and `ast.get_docstring`
is the reader that knows the difference between a declaration and a mention of one. The selftest
pins the discriminator: a marker in a COMMENT now declares nothing.

⚑⚑⚑ AND A `.pyi` THAT WILL NOT PARSE IS LOUD, BECAUSE THE SILENT VERSION IS THIS REPO'S
RECORDED FALSE-ZERO SHAPE. A syntactically broken stub used to read EXACTLY like a stub that
declines nothing — both produced `None` — so a typo in a marker's own file could withdraw every
exemption in it and the gate would report the resulting findings as drift in the MODULE, sending
the reader to repair source that was never wrong. `Declaration.state` carries that difference
explicitly and `reason` says which error, so a caller can refuse rather than infer. This is
`census-green-is-a-fact-about-the-census` at the level of one file: absent and unparseable are
OPPOSITE findings and must not share a representation.

⚑⚑ MEMBER DOCSTRINGS ARE READ FOR THE SIGNATURE MARKER ONLY, AND THE ASYMMETRY IS THE POINT —
it was measured on the live tree, not assumed. `⟡declines-signature:` names a DOTTED PATH to one
member, so its natural home is that member's own docstring, next to the signature it excuses;
`stubs/psycopg/rows.pyi` is the standing case, where three protocol `__call__` findings are
documented at length beside the three protocols. `⟡declines:` is the opposite kind: it grants
`--ignore-missing-stub` across the WHOLE UNIT, and a surface nobody declared at module level is
not one a single class may quietly widen. So a class or function may name its own exemption; it
may not relieve the package it lives in.

Usage: stub_declines.py [--selftest]
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ `⟡declines: <prose>` inside a docstring, running to a blank line or the docstring's end.
# The marker is the repo's ⟡ arc-tag character, so it cannot collide with ordinary stub syntax.
# ⚑ `\Z` and not the old `\n\"\"\"`: the pattern is applied to the EXTRACTED docstring, which no
# longer carries the closing quotes the whole-file form had to stop at.
DECLINES = re.compile(r"^⟡declines:[ \t]*(.+?)(?=\n[ \t]*\n|\Z)", re.MULTILINE | re.DOTALL)

# ⚑ `⟡declines-signature: a.b, c.d` — the named entries handed to stubtest's `--allowlist`.
DECLINES_SIGNATURE = re.compile(
    r"^⟡declines-signature:[ \t]*(.+?)(?=\n[ \t]*\n|\Z)", re.MULTILINE | re.DOTALL
)

# ⚑ A stubtest allowlist entry is a dotted name (its regex form is never needed here — a
# LITERAL name is the reviewable spelling, and a pattern would let one entry cover a surface
# nobody enumerated). Anything else in the marker is not an entry and is dropped.
_ENTRY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")

# ⚑ The node kinds that may carry a member-level declaration. `ast.get_docstring` accepts
# exactly these three besides `Module`, so the tuple is the library's own boundary rather than
# a roster this module has to keep current.
_MEMBER = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)

# ⚑ THE TWO STATES A READ CAN END IN, spelled as words rather than a bool — `read` and `parsed`
# are what a caller prints, and a boolean positional argument is unreadable at the call site.
UNREADABLE = "unreadable"
PARSED = "parsed"

# ⚑ The multi-line cases as source fragments, so the long ones do not overflow a line in the
# selftest body. A stub's docstring is what the reader actually parses.
_MULTI = '"""Doc.\n\n⟡declines: element constructors,\n    and `walk`\'s stop_if.\n"""'
_BLANK_STOP = '"""Doc.\n\n⟡declines: the adapter layer.\n\nUnrelated prose.\n"""'
_SIG_MULTI = '"""Doc.\n\n⟡declines-signature: nx.DiGraph.__init__,\n    nx.descendants\n"""'

# ⚑ THE DISCRIMINATING FIXTURES FOR THE `ast` NARROWING. Each is a file the OLD whole-file regex
# read as a declaration and the docstring reader correctly does not.
_IN_COMMENT = '"""Doc."""\n# ⟡declines: the async surface.\n'
_IN_STRING = '"""Doc."""\n_note: str\n_note = "⟡declines: the async surface."\n'

# ⚑ A member declaration, its home being the signature it excuses — the `rows.pyi` shape.
_IN_METHOD = (
    '"""Doc."""\n\nclass RowMaker:\n'
    '    """Build a row.\n\n    ⟡declines-signature: psycopg.rows.RowMaker.__call__\n    """\n'
)

# ⚑ THE ASYMMETRY FIXTURE: a class trying to grant the PACKAGE-WIDE surface flag. Refused.
_SURFACE_IN_METHOD = (
    '"""Doc."""\n\nclass RowMaker:\n'
    '    """Build a row.\n\n    ⟡declines: the whole async surface.\n    """\n'
)

_BROKEN = '"""Doc.\n\n⟡declines: the async surface.\n"""\n\ndef f(x: int -> None: ...\n'


@dataclass(frozen=True, slots=True)
class Declaration:
    """What one `.pyi` declares — and whether it could be read at all.

    ⚑ `state == UNREADABLE` IS NOT `surface is None`. A stub that declines nothing and a stub
    that will not parse are OPPOSITE findings; giving them one representation is the false zero
    this module's docstring records. `reason` carries the parse error so a caller can print it.
    """

    surface: str | None
    signatures: tuple[str, ...]
    state: str
    reason: str


def _captured(pattern: re.Pattern[str], text: str) -> str | None:
    """Return a pattern's first group collapsed to one line, or None when it did not match.

    ⚑ THE NARROWING IS AT THE SEAM, DELIBERATELY. `re.Match.group()` is typed `str | Any`, so
    every expression downstream of a raw `m.group(1)` inherits the `Any`. Asserting `str` ONCE,
    here, is what keeps both readers below concretely typed.
    """
    m = pattern.search(text)
    if m is None:
        return None
    got = m.group(1)
    if not isinstance(got, str):
        return None
    return " ".join(got.split()) or None


def _entries(text: str) -> tuple[str, ...]:
    """Return the allowlist entries one docstring declares, dropping anything malformed.

    ⚑ A MALFORMED ENTRY IS DROPPED, NOT PASSED THROUGH. An allowlist entry reaches stubtest as
    a regex; letting prose through would make an unreviewed pattern silence findings nobody
    enumerated, which is the blanket skip this whole mechanism refuses.
    """
    declared = _captured(DECLINES_SIGNATURE, text)
    if declared is None:
        return ()
    return tuple(e for raw in declared.split(",") if (e := raw.strip()) and _ENTRY.match(e))


def _walk_entries(tree: ast.Module) -> tuple[str, ...]:
    """Collect signature entries from the module docstring and every member docstring."""
    seen: list[str] = []
    docs = [ast.get_docstring(tree)]
    docs += [ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, _MEMBER)]
    for doc in docs:
        if doc is None:
            continue
        seen += [e for e in _entries(doc) if e not in seen]
    return tuple(seen)


def read_source(src: str) -> Declaration:
    """Read one stub's source into a `Declaration`, reporting a parse failure as such.

    ⚑⚑ THE PARSE FAILURE IS THE RETURN VALUE, NOT AN EXCEPTION AND NOT A ZERO. A caller asks
    every `.pyi` in a package; one broken file must not abort the unit, and must not read as
    "this file declines nothing" either. Both of those lose the finding — the first noisily and
    in the wrong place, the second silently.
    """
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError) as e:
        return Declaration(None, (), UNREADABLE, f"{type(e).__name__}: {e}")
    doc = ast.get_docstring(tree)
    surface = None if doc is None else _captured(DECLINES, doc)
    return Declaration(surface, _walk_entries(tree), PARSED, "")


def read(path: Path) -> Declaration:
    """Read the stub at `path`, reporting an unreadable or unparseable file as such."""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return Declaration(None, (), UNREADABLE, f"{type(e).__name__}: {e}")
    return read_source(src)


def declines_text(src: str) -> str | None:
    """Return the surface prose a stub's MODULE docstring declares, or None.

    ⚑ MODULE-LEVEL ONLY. This marker grants `--ignore-missing-stub` over the whole unit, so a
    class may not widen it — see this module's docstring for the measured asymmetry.
    """
    return read_source(src).surface


def declines_signature_text(src: str) -> tuple[str, ...]:
    """Return every allowlist entry a stub declares, module docstring and members alike."""
    return read_source(src).signatures


def declines(path: Path) -> str | None:
    """Return what the stub at `path` declares it declines as a SURFACE, or None."""
    return read(path).surface


def declines_signature(path: Path) -> tuple[str, ...]:
    """Return the signature-level allowlist entries the stub at `path` declares."""
    return read(path).signatures
