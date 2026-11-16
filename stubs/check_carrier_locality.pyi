# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scripts/check_carrier_locality.py` — the carrier-locality gate.

⚑⚑ WRITTEN SO A TEST CAN IMPORT THE THING UNDER TEST RATHER THAN A COPY OF IT. The
declaration-visibility guard asserts that THIS gate's own `DECL` sees every declaration the
indent-aware definition index sees. The first version of that test compared two regexes it
defined ITSELF, so it could pass while the gate stayed broken — and would have kept reporting
`expectedFailure` after the gate was FIXED, which is how the mistake surfaced. Importing the gate
is what makes the test about the gate; without a stub the import is `import-not-found`, the
resulting `Any` propagates, and the strict bar refuses the file. So this stub is what keeps that
assertion pointed at its subject.

⚑⚑ `DECL` IS THE REASON THIS FILE EXISTS, and it is now declared `re.Pattern[str]` — REVERSING an
earlier `object` and the argument for it. That argument was: *the consumer must narrow it, because
the CLAIM under test is about what the pattern MATCHES, and a stub promising a richer type would
assert a property no one verified.* It presumed every `.pyi` line is somebody's CLAIM. It is not.
`DECL = re.compile(...)` is read off the assignment's own constructor, and a type obtained by
DERIVATION is correct by construction — unfalsifiable, which is not the same as unwarranted.
`substrate.iface_construct --module scripts/check_carrier_locality.py` computes both slots with a
`file:line` witness (`:124`, `:125`), so the derivation IS the verification and there is nothing
left for a consumer to establish by narrowing.

⚑⚑⚑ AND THE `object` SPELLING WAS COSTING THE ONE THING IT CLAIMED TO PROTECT: LEGIBILITY. `object`
is the TOP TYPE, so `stubtest` cannot contradict it — a green verdict on such a slot is a fact about
what `object` admits, not about this stub. Worse, it made a DECISION and an INABILITY indistinguishable:
the sibling `agda_lex.pyi` REFUSED `object` for `HEADER` and wrote a Protocol, because that runtime
value genuinely is not a `re.Pattern`. That refusal is legible only because the lazy spelling was
declined there. Spelling a derivable slot `object` spends the same characters and says nothing.

⚑⚑ THE WHOLE PUBLIC SURFACE IS DECLARED, NOT THE ONE NAME THE TEST READS. `stubtest` requires
every runtime name to be present, so a narrow stub fails with one error per undeclared name — the
measured reason `tsdbprobe.pyi` declares its whole surface too.

⚑ EVERY FUNCTION HERE IS UNANNOTATED AT SOURCE, so these types are a READING of the
implementation, not a transcription. `scan` and `judge` return nested structures the source never
names; they are spelled out wherever the body makes the shape unambiguous. `judge`'s second element
is `canon`, a comprehension that FILTERS `opsigs` without rebuilding its elements, so it carries
`opsigs`' own element type — `list[tuple[str, str, str]]`. It was `object` only because the
dataflow reader stops at `tuple[Any, ...]` for a tuple display and does not follow a comprehension
through to its source; a reader's stopping point is a fact about the READER, never about the slot.

⚑ A STUB IS A CLAIM, AND AN UNVERIFIED CLAIM ABOUT TYPES IS WORTH LESS THAN NO CLAIM — because it
TYPE-CHECKS. Both prior stubs in this tree record that their first draft invented declarations
from the shape the module *ought* to have; the first draft of the sibling `agda_lex.pyi` invented
four, and `scripts/check_stub_authority.py` reported all four in one run. That gate is the only
thing keeping this file honest.
"""

import re
from collections.abc import Iterable

ROOT: str
SRC: str
BASELINE: str

# The sanctioned-exemption set — DEBT that may be paid down, never grown.
ALLOW: set[str]

# ⚑ THE SUBJECT OF THE VISIBILITY GUARD. Widened to `^\s*(?:data|record)\s+([^\s({]+)` after a
# column-0 anchor made 142 indented type names invisible to five gates.
# ⚑ DERIVED, NOT ASSERTED: both are `re.compile(<str>)` at source, which states the type as
# plainly as a literal does. `tests/test_declaration_visibility.py` still asserts
# `isinstance(DECL, re.Pattern)` at the use; that assert is now a RUNTIME confirmation of the
# derivation rather than the only thing standing between the test and `object`.
DECL: re.Pattern[str]
SIG: re.Pattern[str]

def strip_comments(s: str) -> str: ...
def agda_files() -> list[str]: ...
def split_top_arrows(t: str) -> list[str]: ...
def carrier_of(t: str) -> str | None: ...
def scan(
    paths: Iterable[str] | None = ...,
) -> tuple[dict[str, set[str]], list[tuple[str, str, str]]]: ...
def judge(
    carrier_decls: dict[str, set[str]], opsigs: list[tuple[str, str, str]]
) -> tuple[
    dict[str, str],
    list[tuple[str, str, str]],
    list[tuple[str, str, str]],
    list[tuple[str, list[tuple[str, str]]]],
    set[str],
]: ...
def main() -> int: ...
