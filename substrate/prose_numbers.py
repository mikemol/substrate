#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Measured numbers written into PROSE — a count is a snapshot the moment it is typed.

⚑⚑⚑ THE RULE HAS NO QUALIFIER. Operator: *"just stop quoting counts in prose."* An earlier
framing said *stop quoting a count that a tool owns*, and that is wrong in a way that matters:
it implies some counts are safe to write down. None are. A count in prose is true at the
instant of typing and the tree moves while the prose does not, so the only open question about
a written count is whether it has drifted YET.

⚑⚑ THE REPO ALREADY STATES THIS AND HAD NO READER FOR IT. `CLAUDE.md` says *"Do not quote a
cap, a lease default, or a build figure from this file — ask the oracle"*, and records a memory
cap restated in several files while its authority said otherwise — including inside the gate
that ENFORCES the cap, whose docstring contradicted a constant two lines below it. The rule was
written down; nothing could find a violation of it.

⚑ THIS IS A READER, NOT A GATE. It is wired into no hook and refuses nothing. The population is
large enough that paying it down is a decision rather than a mechanical consequence, and a gate
over a census nobody has triaged fires on its first run and gets routed around — which is how a
ratchet decays into an ALLOW-list.

⚑⚑ AND THE DISCRIMINATOR IS THE WHOLE DELIVERABLE, NOT THE SCAN. Extracting prose is already
solved: `code_lines` decides by TOKENIZER which lines are code, so its complement is comment and
docstring text. What no existing mode can say is which NUMBER in that text is a MEASUREMENT.
Most numbers in prose are fine — a line reference, a year, a version pin, a label ordinal, an
error code. A reader that flags those is exactly as useless as one that flags nothing, so the
exemptions are tested as hard as the positive signal, with cases driving in both directions.

⚑ NO MEASURED NUMBER APPEARS IN THIS DOCSTRING, DELIBERATELY. It would be this reader's first
finding, and a tool that violates its own subject teaches its reader that the rule is optional.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from substrate import code_lines, corpus

#: Nouns whose count some tool re-derives. A number sitting beside one of these MEASURES a
#: population, and the population is what moves.
#:
#: ⚑ THE LEXICON IS THE POSITIVE SIGNAL AND IT IS DELIBERATELY NARROW. Widening it to every
#: noun would flag "3 ways", "2 halves", "4 reasons" — rhetorical enumeration the writer
#: controls, which no tool re-derives and which therefore cannot drift. What belongs here is a
#: noun naming a set the TREE defines: files, modules, cases, rows. A writer saying "56 cases"
#: is quoting a suite; a writer saying "two directions" is quoting nothing.
#:
#: ⚑⚑ AND IT IS A CONSTANT A CALLER CAN WIDEN, for the reason the struct-tools rule records one
#: level up: a hardcoded vocabulary rots, and this tooling is read by repos whose populations
#: have other names. A miss here is "no entry carries that spelling", never "no measured number
#: exists" — the same distinction `summit capability` prints in its own refusal.
UNIT_WORDS: frozenset[str] = frozenset(
    {
        "byte",
        "bytes",
        "call",
        "caller",
        "callers",
        "calls",
        "case",
        "cases",
        "consumer",
        "consumers",
        "def",
        "defs",
        "edge",
        "edges",
        "entries",
        "entry",
        "error",
        "errors",
        "file",
        "files",
        "finding",
        "findings",
        "gate",
        "gates",
        "hit",
        "hits",
        "importer",
        "importers",
        "insert",
        "inserts",
        "instance",
        "instances",
        "item",
        "items",
        "line",
        "lines",
        "match",
        "matches",
        "member",
        "members",
        "mode",
        "modes",
        "module",
        "modules",
        "node",
        "nodes",
        "occurrence",
        "occurrences",
        "record",
        "records",
        "row",
        "rows",
        "rule",
        "rules",
        "site",
        "sites",
        "suite",
        "suites",
        "target",
        "targets",
        "tool",
        "tools",
        "warning",
        "warnings",
    }
)

#: `N of M`, `N/M`, `N out of M`. A RATIO over a population is a measurement whatever noun
#: follows it, because both halves move independently.
#:
#: ⚑ THE SHAPE ALONE SUFFICES HERE, WHICH IS WHY IT IS A SEPARATE SIGNAL. "59 of 130" names no
#: unit and is unambiguously a census reading; demanding a unit word would miss precisely the
#: form this repo's own tools PRINT, which is the form a writer copies into prose.
_RATIO = re.compile(r"(?<![\w/.-])(\d[\d,]*)\s*(?:/|of|out\s+of)\s*(\d[\d,]*)(?![\w/.-])")

#: A number, and the words that follow it.
#:
#: ⚑ THE GAP IS ALLOWED BECAUSE AN ADJECTIVE DOES NOT STOP A NUMBER BEING A MEASUREMENT.
#: "57 green cases", "8 declared gates", "3 remaining modules" are all census readings, and an
#: adjacency-only matcher misses every one of them.
#:
#: ⚑⚑ THE FOLLOWING WORDS ARE SCANNED IN CODE RATHER THAN ENCODED AS A REGEX GAP, and the first
#: cut got this WRONG in a way this module's own cases caught. A lazy `(?:\w+\s+){0,2}?` before
#: the noun matches the FEWEST repetitions that let the overall pattern succeed — and since the
#: trailing word matches any word at all, ZERO always succeeds. So "57 green cases" bound
#: `green` as the noun, found it outside `UNIT_WORDS`, and reported nothing: the gap was written
#: as a window and behaved as strict adjacency. A counted scan is easier to get right than a
#: lazy quantifier whose success condition is supplied by the pattern after it.
_NUMBER_THEN_WORDS = re.compile(r"(?<![\w.-])(\d[\d,]*)((?:\s+[A-Za-z][\w-]*){1,3})")

#: A number bound to its unit by a HYPHEN — `a 56-case suite`, `a 3-row table`.
#:
#: ⚑⚑⚑ THIS IS A SEPARATE PATTERN BECAUSE THE HYPHEN MAKES ONE TOKEN, AND MISSING IT MISSED THE
#: OPERATOR'S OWN CALIBRATION INSTANCE. `suite_declared.py`'s `why=` reads *"a 56-case suite"*,
#: which was the measured example this reader was commissioned to find — and the first cut did
#: NOT flag it, because `56-case` has no whitespace for a word-gap scan to cross. The reader
#: reported that file's OTHER drifted count and stayed silent on the one it was pointed at.
#:
#: ⚑⚑ A CENSUS THAT MISSES ITS OWN WORKED EXAMPLE IS A FACT ABOUT THE METHOD, and it would have
#: shipped unnoticed: nothing about the output says a form was unreachable, and the file did
#: appear in the census on the strength of a different line. Only checking the named instance
#: caught it — which is why a brief's worked example belongs in the cases, not just in the prose.
_HYPHEN_UNIT = re.compile(r"(?<![\w.-])(\d[\d,]*)-([A-Za-z][\w]*)")

#: Every run of digits, the population the exemptions are asked about.
_ANY_NUMBER = re.compile(r"\d[\d,]*")

# ── THE EXEMPTIONS. Each names a form whose number is NOT a measurement. ─────────────────────
#
# ⚑⚑⚑ THESE ARE THE HALF THAT MAKES THE READER USABLE, and each one is a false positive
# MEASURED by running the scan over this repo before the exemption existed. A reader that flags
# a line reference or a date trains its reader to skim, and a census everyone skims is worse
# than no census: it reads as authoritative while being noise.

#: A path-and-line or symbol-and-line REFERENCE. It names a location, not a size, and it is the
#: single most common number in this corpus's commentary.
#:
#: ⚑ THE RANGE DASH IS BUILT FROM ITS CODEPOINT, NOT TYPED. This repo's prose writes ranges
#: with an en dash, so the class must admit it. A literal one inside a regex is a character no
#: reader can tell apart from a hyphen, which is exactly the ambiguity `RUF001` refuses; naming
#: the codepoint says which is meant, where the typed glyph only looks like it does.
_DASHES = "[-" + chr(0x2013) + "]"
_RANGE = r"(?:\s*" + _DASHES + r"\s*\d+)?"
_LINE_REF = re.compile(
    r"[\w./-]*\.(?:py|md|agda|mk|sh|toml|json|bib|tsv|yaml)\s*:\s*\d+"
    + _RANGE
    + r"|(?<![\w.])[a-z_]\w*\s*:\s*\d+"
    + _RANGE
)

#: A DATE or a bare year. A date is a STAMP: it does not drift, it ages.
_DATE = re.compile(r"(?<![\w-])(?:19|20)\d{2}(?:-\d{1,2}(?:-\d{1,2})?)?(?![\w-])")

#: A VERSION, a STANDARD, an ERROR CODE, a LABEL ORDINAL or a SIZE UNIT. Every one of these is
#: an IDENTIFIER that happens to contain digits: it NAMES a thing rather than counting one, and
#: it changes only when the thing it names is replaced.
_IDENT_NUM = re.compile(
    r"(?<![\w.])\d+\.\d+(?:\.\d+)*(?![\w.])"
    r"|(?<!\w)v\d+(?:\.\d+)*(?!\w)"
    r"|(?<!\w)PEP\s*\d+(?!\w)"
    r"|(?<!\w)[A-Z]{1,4}\d{3,}(?!\w)"
    r"|[Ⓐ-ⓩ⟡Λ]\s*\w*\d+\w*"
    r"|(?<!\w)[A-Za-z]{1,4}\d+[a-z]?(?!\w)"
    r"|-M\d+[a-z]?(?!\w)"
    r"|(?<!\w)\d+\s*(?:MB|MiB|GB|GiB|KB|KiB|kB|MHz|GHz|px|pt|em|ms)(?!\w)"
)

#: A number inside a code span is CODE, not prose. The writer is quoting an invocation, and the
#: number is that invocation's argument.
_CODE_SPAN = re.compile(r"`[^`]*`")

#: The exemptions, in the order they are applied, each with the name it reports.
#:
#: ⚑ ORDERED AND NAMED AS DATA so a caller can attribute a refusal to a RULE rather than to
#: "the discriminator". An instrument that cannot say WHICH rule refused cannot be audited for
#: over-refusal, and over-refusal is invisible in the census by construction.
EXEMPTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("code span", _CODE_SPAN),
    ("line reference", _LINE_REF),
    ("date", _DATE),
    ("identifier/version/size", _IDENT_NUM),
)

#: ⚑⚑⚑ WHAT THIS READER CANNOT SEE. Declared as DATA so it prints with every census — a zero
#: here is a fact about the DISCRIMINATOR, and a reader who does not know its blind spots reads
#: a small number as a clean tree.
BOUNDARIES: tuple[str, ...] = (
    (
        "a count spelled in WORDS ('a three-case suite') — number words collide head-on with "
        "rhetorical enumeration ('two halves') and nothing structural separates them"
    ),
    (
        "a count in a TABLE CELL — a markdown row is scanned as one prose line, so a cell reads "
        "as text; a per-cell parse would need the table reader and is not wired here"
    ),
    (
        "a STALE number that happens to still be correct — indistinguishable from a fresh one "
        "without re-deriving every figure, which no reader can do"
    ),
    (
        "a count whose UNIT NOUN is outside `UNIT_WORDS` — a miss is 'no entry carries that "
        "spelling', never 'no measured number'"
    ),
    (
        "whether a flagged number is TRUE — this reports that a measurement was WRITTEN DOWN, "
        "never whether it has drifted; verification is per-figure and mostly manual"
    ),
    (
        "prose in any artifact but `.py` and `.md` — Agda comments, TSV ledgers and shell "
        "scripts carry measured numbers and no corpus here extracts them"
    ),
    (
        "⚑ a measured number inside a python STRING LITERAL — `code_lines` calls a data string "
        "CODE, correctly, so a count written into a table's `why=` field is invisible here. "
        "MEASURED: `suite_declared.py`'s entry reads 'a 56-case suite' against a suite that "
        "reports 57, and this reader finds the drifted counts in that file's COMMENTS while "
        "staying silent on the one in its DATA. Reaching it means classifying which string "
        "literals are prose-bearing, which is a different judgement from where the text sits"
    ),
    (
        "⚑ AN ILLUSTRATIVE EXAMPLE READS AS A CLAIM. A quoted specimen — this module's own "
        "\"57 green cases\", a doc's sample output, a case's fixture text — is a MENTION rather "
        "than a USE, and nothing structural separates the two: both are a number beside a unit "
        "noun in prose. MEASURED by running this reader over itself, where every hit is a "
        "specimen and none is a claim about the tree. So a holder that DOCUMENTS counting is "
        "over-reported, and the census is an upper bound rather than a defect list"
    ),
)


@dataclass(frozen=True, slots=True)
class Finding:
    """One measured number written into prose."""

    path: str
    line: int
    number: str
    unit: str
    text: str
    #: Which signal fired: `ratio` (N/M, N of M) or `unit` (adjacent to a counted noun).
    signal: str


@dataclass(frozen=True, slots=True)
class Exempt:
    """One number the discriminator REFUSED, and the rule that refused it.

    ⚑ THE REFUSALS ARE RETURNED, NEVER DISCARDED. A discriminator reporting only its hits
    cannot be audited: an over-eager exemption looks identical to a clean tree. Same reason
    `suite_declared.standings` returns its undeclared population — a reader must be able to
    see what the instrument decided NOT to say.
    """

    path: str
    line: int
    number: str
    why: str
    text: str


def group(m: re.Match[str], n: int) -> str:
    """Return match group `n` as a `str` — the ONE narrowing seam for this module.

    ⚑ THE NARROWING IS AT THE SEAM, DELIBERATELY, and it is `suite_pragmas._captured`'s ruling
    applied here rather than re-derived. `re.Match.group()` is typed `str | Any`, so every
    expression downstream of a raw `m.group(1)` inherits the `Any` and poisons the readers
    below it. Asserting `str` ONCE keeps every consumer concretely typed.

    ⚑ A NON-`str` GROUP IS THE EMPTY STRING, NOT AN ERROR. Every pattern here captures from a
    `str` subject, so the branch is unreachable in fact; making it a raise would add a failure
    mode the callers would have to carry for a case the types already exclude.
    """
    got = m.group(n)
    return got if isinstance(got, str) else ""


def mask(text: str) -> str:
    """Blank every exempt form, PRESERVING length so surviving offsets stay true.

    ⚑ MASKING RATHER THAN DELETING, because the forms OVERLAP and deletion joins neighbours
    that were never adjacent. A path-and-line reference holds digits that would otherwise read
    as a bare number two words from a unit noun; removing the span would splice the surrounding
    words into a phrase the author never wrote. Replacing each character with a space keeps
    every remaining match at its real column.
    """

    def blank(m: re.Match[str]) -> str:
        """Return a run of spaces the same width as the matched span."""
        return " " * len(group(m, 0))

    out = text
    for _name, rx in EXEMPTIONS:
        out = rx.sub(blank, out)
    return out


def exemption_for(text: str, at: int) -> str | None:
    """Return the name of the exemption covering offset `at`, or None."""
    for name, rx in EXEMPTIONS:
        for m in rx.finditer(text):
            if m.start() <= at < m.end():
                return name
    return None


def _ratios(path: str, line: int, text: str, masked: str) -> list[Finding]:
    """Return the RATIO findings, the signal that needs no unit noun."""
    return [
        Finding(path, line, f"{group(m, 1)}/{group(m, 2)}", "ratio", text.strip(), "ratio")
        for m in _RATIO.finditer(masked)
    ]


def _unit_hits(path: str, line: int, text: str, masked: str) -> list[Finding]:
    """Return the UNIT findings — a number within two words of a counted noun.

    ⚑ A SPAN ALREADY CLAIMED BY A RATIO IS SKIPPED, so "59 of 130 files" is one finding rather
    than two. Double-reporting a single written figure would inflate every holder's total by
    however often its author wrote a ratio, which is a fact about phrasing, not about drift.
    """
    taken = [m.span() for m in _RATIO.finditer(masked)]
    out: list[Finding] = []
    seen: set[int] = set()
    for m in _HYPHEN_UNIT.finditer(masked):
        if group(m, 2).casefold() not in UNIT_WORDS:
            continue
        if any(s <= m.start(1) < e for s, e in taken):
            continue
        seen.add(m.start(1))
        out.append(Finding(path, line, group(m, 1), group(m, 2).casefold(), text.strip(), "unit"))
    for m in _NUMBER_THEN_WORDS.finditer(masked):
        if m.start(1) in seen or any(s <= m.start(1) < e for s, e in taken):
            continue
        words = group(m, 2).split()
        hit = next((w for w in words if w.strip(".,;:").casefold() in UNIT_WORDS), None)
        if hit is not None:
            out.append(
                Finding(path, line, group(m, 1), hit.strip(".,;:").casefold(), text.strip(), "unit")
            )
    return out


def _refusals(path: str, line: int, text: str) -> list[Exempt]:
    """Return one refusal per exempt SPAN, never one per digit run inside it.

    ⚑⚑ THE UNIT OF A REFUSAL IS THE FORM, NOT THE DIGITS, and the first cut got this wrong in a
    way this module's own cases caught. Asking the exemptions about every digit run reports a
    dated line THREE TIMES — once per run — so `--exempt`'s per-rule tally counted
    forms by how many numbers they happen to contain. That inflates whichever rule matches the
    longest spans, which is exactly the tally a reader consults to spot an over-broad exemption.

    ⚑ AND THE SPANS ARE WALKED IN RULE ORDER, FIRST MATCH WINNING, so a form covered by two
    rules is attributed once rather than to each. Overlaps are real here — a dated line
    reference is both — and double-attribution would make the shares sum past the population.
    """
    out: list[Exempt] = []
    claimed: list[tuple[int, int]] = []
    for name, rx in EXEMPTIONS:
        for m in rx.finditer(text):
            if not _ANY_NUMBER.search(group(m, 0)):
                continue
            if any(s <= m.start() < e for s, e in claimed):
                continue
            claimed.append(m.span())
            out.append(Exempt(path, line, group(m, 0).strip(), name, text.strip()))

    def by_number(e: Exempt) -> str:
        """Order refusals by the text they refused, so a line's report is canonical."""
        return e.number

    return sorted(out, key=by_number)


def scan_line(path: str, line: int, text: str) -> tuple[list[Finding], list[Exempt]]:
    """Return the measured numbers and the refusals for ONE line of prose.

    ⚑⚑ TWO SIGNALS, NOT ONE, AND THEY ANSWER DIFFERENT QUESTIONS. The RATIO shape is
    self-evidently a census reading whatever noun it carries — both halves move, and a writer
    only writes a ratio because a tool printed one. The UNIT shape needs its noun, because a
    bare number is ambiguous. Requiring both would miss every bare ratio; accepting either
    WITHOUT the exemptions would flag every line reference in the corpus.

    ⚑ THE EXEMPTIONS RUN FIRST AND ARE REPORTED, never silently dropped. A refused number comes
    back as an `Exempt` carrying the rule that refused it, so the boundary is readable.
    """
    masked = mask(text)
    found = _ratios(path, line, text, masked) + _unit_hits(path, line, text, masked)
    return found, _refusals(path, line, text)


def python_prose(path: Path) -> list[tuple[int, str]]:
    """Return `(line, text)` for every COMMENT or DOCSTRING line of a python source.

    ⚑ THE COMPLEMENT OF `code_lines`, WHICH IS THE TOKENIZER'S ANSWER RATHER THAN A REGEX'S.
    A `#` inside a string is not a comment and a docstring's interior is not code; `code_lines`
    already decides both from `tokenize`, so the prose is exactly the non-blank lines it does
    not claim. Re-deriving that with a line regex is the stripper defect its own docstring
    records.

    ⚑⚑ AND THIS SEES UNMARKED COMMENTS, which is the reach a mark-keyed extractor does not
    have. A plain comment carries a measurement as surely as a flagged paragraph does, and
    keying on the incident glyph would make the census a fact about which comments someone
    thought worth marking.
    """
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    code = code_lines.code_lines(source)
    return [
        (i, line) for i, line in enumerate(source.splitlines(), 1) if line.strip() and i not in code
    ]


def markdown_prose(path: Path) -> list[tuple[int, str]]:
    """Return `(line, text)` for every markdown BODY line outside a fenced block.

    ⚑ FENCED CODE IS SKIPPED, because a number inside a fence is an invocation's argument or a
    tool's recorded OUTPUT — neither is a claim the document is making. This repo's markdown is
    dense with shell and Agda fences, so admitting them would make the census mostly transcript.
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    out: list[tuple[int, str]] = []
    fenced = False
    for i, line in enumerate(raw, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and line.strip():
            out.append((i, line))
    return out


def md_files(*requested: str, root: Path = corpus.ROOT) -> list[str]:
    """Return every `.md` under the given roots, corpus exclusions applied.

    ⚑ THE EXCLUSION RULE IS `corpus.excluded`, NOT A SECOND LIST. A private copy here would be
    a second answer to "what is this repo's corpus", and the two would drift — the defect
    `corpus.roots` records from the other side.
    """
    out: list[str] = []
    for r in requested or corpus.roots(root):
        base = corpus.resolve_root(r, root)
        if base.is_file():
            if base.suffix == ".md":
                out.append(str(base))
            continue
        out.extend(
            str(p) for p in base.rglob("*.md") if not corpus.excluded(p.parent.relative_to(base))
        )
    return sorted(out)


def census(*requested: str, root: Path = corpus.ROOT) -> tuple[list[Finding], list[Exempt], int]:
    """Return `(findings, exempts, files_read)` over the `.py` and `.md` under `requested`.

    ⚑ `files_read` IS RETURNED BECAUSE A BARE LIST CANNOT DISTINGUISH *no matches* FROM *no
    file read* — the house rule every reader in this tree prints, and the one that would make
    an empty census indistinguishable from a mistyped path argument.
    """
    findings: list[Finding] = []
    refused: list[Exempt] = []
    seen = 0
    lines: list[tuple[str, int, str]] = []
    for name in corpus.py_files(*requested, root=root):
        seen += 1
        lines.extend((name, i, t) for i, t in python_prose(Path(name)))
    for name in md_files(*requested, root=root):
        seen += 1
        lines.extend((name, i, t) for i, t in markdown_prose(Path(name)))
    for name, line, text in lines:
        f, x = scan_line(name, line, text)
        findings.extend(f)
        refused.extend(x)
    return findings, refused, seen


def by_holder(findings: list[Finding]) -> list[tuple[str, int]]:
    """Return `(path, n)` per file, largest holder first."""
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.path] = counts.get(f.path, 0) + 1

    def rank(kv: tuple[str, int]) -> tuple[int, str]:
        """Order by descending count, then by path so ties are canonical."""
        return (-kv[1], kv[0])

    return sorted(counts.items(), key=rank)
