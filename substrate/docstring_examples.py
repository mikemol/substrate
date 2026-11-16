#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A docstring's WORKED EXAMPLE that no case exercises — a claim with no witness.

⚑⚑⚑ THE MOTIVATING DEFECT IS THE SHARPEST FORM OF THIS, AND IT SHIPPED. `hook_cmdparse.py`'s
`programs()` said *"A wrapper's own flags (env -i, timeout -s KILL) are skipped too."* The
second of those was PRECISELY the broken case: the skip loop consumed the flag and never its
argument, so the program read as the signal name and the real command was invisible to every
hook routing through it. The first passed only because its flag takes NO argument. A docstring
illustrated a capability with the one instance that DISPROVED it, and the instance that worked
was the one someone had checked.

⚑⚑ SO THE POPULATION IS NOT "DOCSTRINGS CONTAINING EXAMPLES" — that is nearly every docstring
here, and a reader flagging it is noise. The population is an example CITED IN PROSE as a worked
case and absent from every case in the module's suite. The two named forms above were in the
docstring and in no arm; the arms that exist today were written afterwards, BECAUSE of the
defect, and they are what makes the sentence true rather than the sentence.

⚑ THIS IS A READER, NOT A GATE, for the reason `prose_numbers` records: the population is large
enough that paying it down is a judgement, and a gate over an untriaged census fires on its first
run and gets routed around — which is how a ratchet decays into an ALLOW-list.

⚑⚑⚑ AND A ZERO HERE IS A FACT ABOUT THE MATCHER, NEVER ABOUT THE TREE. An example exercised
under a DIFFERENT SPELLING reads as unexercised; an example whose case was DELETED reads
identically to one that never had a case; an ILLUSTRATIVE aside reads identically to a claim.
`BOUNDARIES` states each of those and the CLI prints them on every run, clean or not.

⚑ NO MEASURED NUMBER APPEARS IN THIS DOCSTRING, DELIBERATELY — this reader's sibling finds those,
and a tool violating its own subject teaches its reader that the rule is optional.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus
from substrate.suite_gap import SUITE_SUFFIX

#: A backtick-quoted span inside a docstring — the form this repo writes an example in.
#:
#: ⚑ THE BACKTICK IS THE AUTHOR'S OWN MARK THAT A SPAN IS A SPECIMEN rather than prose. Reading
#: examples out of unquoted text would need to guess where one ends, and every guess admits the
#: surrounding sentence. The mark is already there; using it is cheaper and more honest than
#: inferring one.
_SPAN = re.compile(r"`([^`\n]+)`")

#: A FLAG anywhere in the span — the strongest sign a form is being RUN rather than named.
_FLAG = re.compile(r"(?:^|\s)--?[A-Za-z][\w-]*")

#: A span that is a bare symbol: one identifier, dotted or not, possibly called with no argument.
#: These are cross-references, not worked cases.
_BARE_SYMBOL = re.compile(r"^[A-Za-z_][\w.]*(?:\(\))?$")

#: A span that is a path — a file being NAMED, not a command being run.
_PATH_ONLY = re.compile(r"^[\w./-]+\.(?:py|md|agda|mk|sh|toml|json|bib|tsv|yaml)$")

#: A span whose head is a program-shaped word, followed by at least one operand.
_COMMAND = re.compile(r"^[A-Za-z_][\w.]*(?:\(\))?\s+\S")

#: Below this width a span cannot be an invocation — it is a glyph or an operator.
_MIN_SPAN = 3

#: ⚑⚑⚑ THE REFUSALS, IN ORDER, EACH WITH THE NAME IT REPORTS. Table-driven rather than a chain
#: of returns, for the reason `prose_numbers.EXEMPTIONS` is data: an instrument that cannot say
#: WHICH rule refused cannot be audited for over-refusal, and over-refusal is invisible in the
#: census by construction — it makes the tree look clean.
#:
#: ⚑⚑ THIS NEGATIVE HALF IS WHAT MAKES THE READER USABLE. A span holding a bare symbol is a
#: cross-reference; a span holding a path NAMES a file. Neither claims that a form WORKS, and
#: admitting them would put every docstring in this tree into the census — exactly as useless as
#: reporting nothing.
_REFUSALS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("a bare symbol — a cross-reference, not a worked case", _BARE_SYMBOL),
    ("a path — a file NAMED, not a form run", _PATH_ONLY),
)

#: The node kinds that can carry a docstring. Named so the walk narrows concretely.
_DOC_HOLDERS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


@dataclass(frozen=True, slots=True)
class Example:
    """One worked example cited in a docstring, and which signal made it a claim."""

    path: str
    line: int
    span: str
    #: The suite that would have to hold the case, or None when the module has none.
    suite: str | None
    #: Why this span counts as a claim: `flag` (shows a flag) or `command` (program + operand).
    signal: str


@dataclass(frozen=True, slots=True)
class Skipped:
    """One span the discriminator REFUSED, and the rule that refused it.

    ⚑ THE REFUSALS ARE RETURNED, NEVER DISCARDED — `prose_numbers.Exempt`'s ruling applied here.
    A discriminator reporting only its hits cannot be audited: an over-eager rule looks exactly
    like a clean tree, and over-refusal is invisible in the census by construction.
    """

    path: str
    line: int
    span: str
    why: str


#: ⚑⚑⚑ WHAT THIS READER CANNOT SEE. Declared as DATA so it prints with every census — a zero
#: here is a fact about the DISCRIMINATOR, and a reader who does not know its blind spots reads
#: a small number as a clean tree.
BOUNDARIES: tuple[str, ...] = (
    (
        "⚑ AN EXAMPLE EXERCISED UNDER A DIFFERENT SPELLING reads as unexercised. A case driving "
        "one signal name covers the same branch as a docstring citing another, and nothing "
        "structural says so — this compares TEXT, so a paraphrase reports as a finding"
    ),
    (
        "⚑ AN EXAMPLE WHOSE CASE WAS DELETED is indistinguishable from one that never had a case. "
        "Both are absent from today's suite; only the history separates them, and no reader here "
        "reads history"
    ),
    (
        "⚑ AN ILLUSTRATIVE EXAMPLE IS NOT A CLAIM. A docstring showing a mode's spelling to "
        "explain it is not asserting that form works; nothing structural separates showing from "
        "claiming, so this census is an UPPER BOUND on unwitnessed claims, not a defect list"
    ),
    (
        "a module with NO SUITE reports every example as unexercised — correctly but uselessly; "
        "the finding there is the missing suite, which `suite_gap` owns, not the example"
    ),
    (
        "an example exercised by a suite that is NOT the sibling module — a case living in another "
        "module's suite reads as absent, the same convention limit `suite_gap` declares"
    ),
    (
        "an example in a `#` COMMENT rather than a docstring — this reads docstrings, which is "
        "where a capability is CLAIMED; a comment beside the code is a different act"
    ),
    (
        "whether an exercised example actually PASSES — this reports that a case mentions the "
        "form, never that the case is green or that it asserts the right thing"
    ),
    (
        "prose in any artifact but `.py` — a markdown worked example has no suite to be absent "
        "from, so the question this reader asks does not arise there"
    ),
)


def group(m: re.Match[str], n: int) -> str:
    """Return match group `n` as a `str` — the ONE narrowing seam for this module.

    ⚑ THE NARROWING IS AT THE SEAM, and it is `prose_numbers.group`'s ruling applied here rather
    than re-derived. `re.Match.group()` is typed `str | Any`, so every expression downstream of
    a raw `m.group(1)` inherits the `Any` and poisons the readers below it. Asserting `str` ONCE
    keeps every consumer concretely typed — which is also why `findall` is not used: it returns
    a list whose element type is `Any`, with no seam to narrow at.
    """
    got = m.group(n)
    return got if isinstance(got, str) else ""


def claim_signal(span: str) -> str | None:
    """Return the signal naming this span a worked case, or None when it is not one.

    ⚑ THE POSITIVE SIGNAL IS DELIBERATELY NARROW. A docstring naming a symbol is citing it, not
    claiming a worked case. What makes a span a CLAIM is that it shows a form BEING RUN — a
    flag, or a program-shaped head with an operand after it.
    """
    text = span.strip()
    if _FLAG.search(text):
        return "flag"
    return "command" if _COMMAND.match(text) else None


def refusal_for(span: str) -> str | None:
    """Return the name of the rule refusing this span, or None when none refuses it."""
    text = span.strip()
    if len(text) < _MIN_SPAN:
        return "too short to be an invocation"
    for why, rx in _REFUSALS:
        if rx.match(text):
            return why
    return None


def docstring_spans(path: Path) -> list[tuple[int, str]]:
    """Return `(line, span)` for every backtick span inside a DOCSTRING of `path`.

    ⚑ THE AST DECIDES WHAT A DOCSTRING IS, not a regex over triple quotes. `ast.get_docstring`
    knows the module, class and function forms and knows a string that merely sits first in a
    body is not one — the same ruling `code_lines` makes for its own question, which is why this
    does not re-derive it from delimiters.

    ⚑⚑ THE LINE REPORTED IS THE DOCSTRING HOLDER'S, NOT THE SPAN'S. A docstring node carries one
    position and a span's offset within it is not a source line without re-tokenizing; naming
    the holder is the honest resolution, and it is the unit a reader acts on anyway.

    ⚑ A MODULE HAS NO `lineno`, WHICH IS WHY THE TWO KINDS ARE READ SEPARATELY. Reaching for it
    through `getattr` would return an untyped value and put an `Any` into every tuple below —
    the poison this module's `group` seam exists to keep out.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return []
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, _DOC_HOLDERS):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        line = 1 if isinstance(node, ast.Module) else node.lineno
        out.extend((line, group(m, 1)) for m in _SPAN.finditer(doc))
    return out


def _string_constants(path: Path, *, skip_docstrings: bool) -> str:
    """Return the string constants of a source, optionally excluding its docstrings.

    ⚑⚑ THE DOCSTRINGS MUST BE EXCLUDED WHEN THE FILE IS ITS OWN SUBJECT, and forgetting that
    makes every example match ITSELF. A module's docstring is where the claim is written; if it
    also counts as case text, the reader reports a clean tree for the most vacuous possible
    reason — the claim witnesses itself. That is a false ZERO, the direction this repo banks
    silently, so the exclusion is a parameter rather than a convention.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return ""
    docs: set[int] = set()
    if skip_docstrings:
        for holder in ast.walk(tree):
            if not isinstance(holder, _DOC_HOLDERS):
                continue
            first = holder.body[0] if holder.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docs.add(id(first.value))
    return "\n".join(
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs
    )


def subject_text(suite: Path) -> str:
    """Return every string constant in a suite's source — what its cases NAME.

    ⚑⚑⚑ THIS IS HOW A CASE NAMES ITS SUBJECT HERE, ESTABLISHED FROM THE SUITES RATHER THAN
    ASSUMED. An arm is a `check` call taking a label, a call under test, and an expectation; the
    worked example it drives appears as a string ARGUMENT to the call under test, while the
    label describes the claim in words. Reading labels alone would miss every exercised example
    and report the whole tree as unwitnessed — a fact about the matcher wearing a finding's
    clothes.

    ⚑ SO THE UNION IS TAKEN, AND OVER-ADMITTING IS THE SAFE DIRECTION. A string constant that is
    neither a label nor an example can only make this reader report FEWER findings, never more —
    the same asymmetry `case_lens` records for its own over-admitting roster.
    """
    return _string_constants(suite, skip_docstrings=False)


def suite_for(module: Path) -> Path | None:
    """Return the sibling suite that would hold this module's cases, or None."""
    candidate = module.with_name(module.stem + SUITE_SUFFIX)
    return candidate if candidate.exists() else None


def case_text(module: Path) -> str:
    """Return every string a case could name this module's examples in — sibling AND tail.

    ⚑⚑⚑ THE SIBLING ALONE IS THE WRONG POPULATION, AND THIS READER'S FIRST RUN PROVED IT ON THE
    INSTANCE IT WAS BUILT FOR. `hook_cmdparse.py` carries its cases INLINE, in its own
    `_selftest`, so a sibling-only lookup found no suite and reported the wrapper-flag example
    as unwitnessed — while the arm driving that exact string sits in the same file, and is the
    arm that MADE the docstring true. A census that flags a repaired claim as debt has inverted
    its own subject.

    ⚑⚑ `suite_gap` ALREADY NAMES THE INLINE SHAPE, so this is not a new judgement — it is that
    ruling applied on this side. Inline cases are DEBT (they owe a split) and they are still
    CASES: a reader asking *is this example exercised* must see them, or it reports a fact about
    the naming convention as a fact about the claim.

    ⚑ THE UNION IS TAKEN AND OVER-ADMITTING IS THE SAFE DIRECTION, the same asymmetry
    `case_lens` records: an extra string can only make this reader report FEWER findings, never
    more. The cost of missing a case is a false positive on a true claim; the cost of an extra
    string is silence on a claim someone happened to quote.
    """
    suite = suite_for(module)
    sibling = subject_text(suite) if suite is not None else ""
    return sibling + "\n" + _string_constants(module, skip_docstrings=True)


def scan(module: Path) -> tuple[list[Example], list[Skipped]]:
    """Return the unexercised worked examples of ONE module, and the spans refused.

    ⚑ AN EXAMPLE PRESENT IN THE CASE TEXT IS NOT REPORTED, which is the half that makes this a
    discriminator rather than a lister. An exercised example is fine and must not be flagged —
    `hook_cmdparse`'s arms are exactly that case, and they are why its docstring is now true.

    ⚑⚑ AND THE CASE TEXT IS `case_text`, NOT THE SIBLING ALONE — see its header for the false
    positive that ruling was bought with, measured on this reader's first live run against the
    very module it was built for.
    """
    name = str(module)
    suite = suite_for(module)
    haystack = case_text(module)
    found: list[Example] = []
    refused: list[Skipped] = []
    for line, span in docstring_spans(module):
        text = span.strip()
        signal = claim_signal(text)
        why = refusal_for(text)
        if why is None and signal is None:
            why = "no flag and no program-shaped head — not an invocation"
        if why is not None:
            refused.append(Skipped(name, line, text, why))
            continue
        if text in haystack:
            refused.append(Skipped(name, line, text, "exercised by a case"))
            continue
        found.append(
            Example(
                name, line, text, str(suite) if suite is not None else None, signal or "command"
            )
        )
    return found, refused


def census(*requested: str, root: Path = corpus.ROOT) -> tuple[list[Example], list[Skipped], int]:
    """Return `(examples, skipped, files_read)` over the `.py` under `requested`.

    ⚑ `files_read` IS RETURNED BECAUSE A BARE LIST CANNOT DISTINGUISH *no matches* FROM *no file
    read* — the house rule every reader in this tree prints.

    ⚑ A SUITE IS NOT ITS OWN SUBJECT. A suite's docstring cites the forms it drives, so scanning
    suites would report each example against itself and invert the question this reader asks.
    """
    found: list[Example] = []
    refused: list[Skipped] = []
    seen = 0
    for name in corpus.py_files(*requested, root=root):
        if name.endswith(SUITE_SUFFIX):
            continue
        seen += 1
        f, s = scan(Path(name))
        found.extend(f)
        refused.extend(s)
    return found, refused, seen


def by_holder(found: list[Example]) -> list[tuple[str, int]]:
    """Return `(path, n)` per file, largest holder first."""
    counts: dict[str, int] = {}
    for e in found:
        counts[e.path] = counts.get(e.path, 0) + 1

    def rank(kv: tuple[str, int]) -> tuple[int, str]:
        """Order by descending count, then by path so ties are canonical."""
        return (-kv[1], kv[0])

    return sorted(counts.items(), key=rank)
