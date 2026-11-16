# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Edit ONE field of ONE existing entry, by locating its span and slicing the raw text.

⚑⚑⚑ MATCH ON MASKED, SLICE THE RAW — AND THAT IS ONLY SOUND BECAUSE THE MASK IS LENGTH-PRESERVING.
Comments are blanked to spaces, never removed, so a span computed against the masked text is valid
against the original. MEASURED when it was not: a first cut emitted `""` for a comment line, which
preserves the LINE count and shrinks the file, so every character offset after the first comment
shifted — and the resulting write ERASED all 533 comment lines of the live bib, which is the whole
adjudication record. `entries` never noticed because it only ever reads the masked text; only an
edit that applies a masked span to raw text can see it.

⚑⚑ THE SPAN COMES FROM THE SAME GRAMMAR THE READ USES, WHICH IS WHY THE PATTERNS ARE INJECTED.
Locating a field with a fresh regex here would be a SECOND PARSER of the same question — and this
tool already carries a docstring naming the fourth-parser hazard. The caller supplies the entry and
field patterns it reads with, so a locate that disagrees with a read is impossible rather than
merely unlikely.

⚑⚑ AND THE GRAMMAR IS A `Grammar`, NOT FOUR LOOSE PARAMETERS — the per-file gate named that seam
here exactly as it did for the write protocol. The patterns are fixed for a whole session and
swapped wholesale by a fixture; the key, field and value change every call. Reading the refusal as
an argument count to satisfy would have produced a tuple; reading it as a design signal produced the
split the callers want.

⚑ DECIDE, THEN APPLY. This computes text and writes nothing, so a dry run and a real run share one
code path and cannot disagree — the shape `prune_imports` learned after writing unconditionally.

⚑ AND IT REFUSES RATHER THAN GUESSING, THREE WAYS, EACH A DIFFERENT OPERATION: an unknown key
(appending is not editing, and silently creating is how a typo becomes a phantom item), a field the
entry does not carry (adding a field is its own verb), and an unbalanced value (the field grammar
nests ONE level, so a deeper value truncates at read-back and the write silently loses data).

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re

# The comment marker this grammar recognises.
COMMENT = "%"


@dataclass(frozen=True, slots=True)
class Refusal:
    """An edit that will not proceed, and what the caller should do instead."""

    message: str
    code: int = 2


@dataclass(frozen=True, slots=True)
class Grammar:
    """The patterns a locate must share with the read that produced the entries.

    ⚑ TWO PATTERNS, ONE AUTHORITY. `entry_re` group 2 is the key and group 3 the body span;
    `field_re` group 1 is the name and group 2 the value span. Those group numbers are the contract
    — a caller passing patterns with a different shape gets a located span that is wrong rather
    than absent, which is why `set_field`'s last refusal reports a DEFECT rather than a miss.
    """

    entry_re: re.Pattern[str]
    field_re: re.Pattern[str]


def mask_comments(text: str) -> str:
    """Blank every comment line to spaces, PRESERVING length and every offset after it.

    ⚑⚑ SAME LENGTH, NOT MERELY SAME LINE COUNT, AND THE DIFFERENCE IS A CORRUPTING WRITE. Emitting
    an empty string per comment keeps the line count and shrinks the file, so every character
    offset after the first comment shifts — measured on the live bib as a diff that erased all 533
    comment lines. Replacing each comment with spaces keeps a span computed on one text valid on
    the other.

    ⚑ A `%` INSIDE A BRACED VALUE IS NOT A COMMENT IN BIBTEX, and this blanks it anyway. Recorded
    as a KNOWN NARROWING rather than silently assumed away: widening to a brace-aware scan would be
    a second grammar, which is the hazard this module exists inside. A braced `%` would surface as
    a dropped field, not as a silent success.
    """
    return "\n".join(
        " " * len(line) if line.lstrip().startswith(COMMENT) else line for line in text.split("\n")
    )


def locate(text: str, key: str, field: str, grammar: Grammar) -> tuple[int, int] | None:
    """Return the `(start, end)` of `key`'s `field` VALUE, or None when it is not found.

    ⚑ THE PATTERNS ARE THE CALLER'S — the same ones its reader uses. A regex written here would
    make the locate a second authority over what a field IS, and a read/locate disagreement is the
    one failure this function cannot detect from inside.
    """
    masked = mask_comments(text)
    for entry in grammar.entry_re.finditer(masked):
        if str(entry.group(2)) != key:
            continue
        body_start = entry.start(3)
        for found in grammar.field_re.finditer(masked[body_start : entry.end(3)]):
            if str(found.group(1)) != field:
                continue
            return body_start + found.start(2), body_start + found.end(2)
    return None


def set_field(
    text: str,
    edit: tuple[str, str, str],
    entries: dict[str, dict[str, str]],
    grammar: Grammar,
) -> str | Refusal:
    """Return the text with one field set, or why it must not be. `edit` is `(key, field, value)`.

    ⚑⚑ THE LAST REFUSAL IS A DEFECT REPORT, NOT A MISSING FIELD. If the entry parsed and carries
    the field but no span can be located, the READ and the LOCATE disagree — which is a bug in this
    module or its patterns, and saying *"no such field"* there would blame the caller for a defect
    they cannot fix.
    """
    key, field, value = edit

    if key not in entries:
        return Refusal(
            f"bibstruct --set: no entry {key!r} (have {len(entries)}). "
            f"Adding an entry is a different operation."
        )

    if field not in entries[key]:
        carried = ", ".join(sorted(n for n in entries[key] if not n.startswith("_")))
        return Refusal(
            f"bibstruct --set: {key} carries no {field!r} (has: {carried}). "
            f"Adding a field is a different operation."
        )

    if value.count("{") != value.count("}"):
        return Refusal(
            "bibstruct --set: unbalanced braces in the value; the field grammar "
            "nests one level and would truncate it."
        )

    span = locate(text, key, field, grammar)
    if span is None:
        return Refusal(
            f"bibstruct --set: {key}.{field} parsed but its span was not located — "
            f"the read and the locate disagree, which is a defect, not a missing "
            f"field."
        )

    lo, hi = span
    return text[:lo] + value + text[hi:]


def last_field_end(text: str, key: str, grammar: Grammar) -> int | None:
    """Return the offset just past `key`'s LAST field value, or None when it has none.

    ⚑ AFTER THE LAST FIELD, NOT BEFORE THE FIRST. An entry conventionally opens with `section`,
    so prepending a new field would put it above that — a diff that changes the entry's SHAPE
    rather than extending it, which is noise in every subsequent read of that entry's history.
    """
    masked = mask_comments(text)
    for entry in grammar.entry_re.finditer(masked):
        if str(entry.group(2)) != key:
            continue
        last = None
        for found in grammar.field_re.finditer(masked[entry.start(3) : entry.end(3)]):
            last = found
        if last is None:
            return None
        at = entry.start(3) + last.end(2)
        # ⚑ THE SPAN ENDS AT THE VALUE, so the closing brace is stepped over here. Inserting
        # before it would put the new field INSIDE the previous one's value.
        while at < len(text) and text[at] == "}":
            at += 1
        return at
    return None


def add_field(
    text: str,
    edit: tuple[str, str, str],
    entries: dict[str, dict[str, str]],
    grammar: Grammar,
) -> str | Refusal:
    """Return the text with a NEW field on an EXISTING entry. `edit` is `(key, field, value)`.

    ⚑⚑⚑ THE THIRD VERB EXISTS BECAUSE THE OTHER TWO LEFT A GAP NEITHER COULD REACH. `set_field`
    refuses a field the entry does not carry (*"adding a field is a different operation"*) and the
    entry writer refuses a key that already exists (*"this only creates"*) — both correct, and
    together they mean **an entry filed with a MISSING field is fixable by neither.** Measured on a
    peer's live floor: a corroboration written without `note` reads back as `kind ? by ?` and
    cannot say what it corroborates. The only routes left were hand-editing a peer's file — the
    thing this tool exists to prevent — or deleting and re-adding, which loses the entry if the
    re-add refuses.

    ⚑⚑ AND IT REFUSES A FIELD THAT ALREADY EXISTS, WHICH IS `set_field`'S JOB. The three verbs
    partition: one mints an entry, one WIDENS one, one edits a value. An upsert would make *"did I
    mean to create this?"* unanswerable at the call site, which is why they were split at all.
    """
    key, field, value = edit

    if key not in entries:
        return Refusal(
            f"bibstruct --addfield: no entry {key!r} (have {len(entries)}). "
            f"Creating an entry is `--add`."
        )

    if field in entries[key]:
        return Refusal(
            f"bibstruct --addfield: {key} already carries {field!r} "
            f"(= {entries[key][field]!r}). Editing a value is `--set`."
        )

    if value.count("{") != value.count("}"):
        return Refusal(
            "bibstruct --addfield: unbalanced braces in the value; the field grammar "
            "nests one level and would truncate it."
        )

    at = last_field_end(text, key, grammar)
    if at is None:
        return Refusal(
            f"bibstruct --addfield: {key} parsed but its last field was not located — "
            f"the read and the locate disagree, which is a defect."
        )

    return f"{text[:at]},\n  {field:<8} = {{{value}}}{text[at:]}"


# Characters that cannot appear in a key: the header grammar ends a key at the first `,`, and a
# brace or whitespace would make the header unreadable. A key is refused if it holds any of them.
_KEY_BREAKERS = frozenset(",{}% \t\n")


def rename_entry(
    text: str,
    edit: tuple[str, str],
    entries: dict[str, dict[str, str]],
    grammar: Grammar,
) -> str | Refusal:
    """Return the text with ONE entry's key renamed in its header, or why it must not be.

    `edit` is `(old, new)`.

    ⚑⚑ THE FIFTH VERB, AND IT IS THE RE-KEY'S SUCCESSOR. While the findings roster was a Python
    literal, re-keying edited that literal (`witness_rekey`). Once the bibs ARE the roster, a re-key
    is a bib-key rename — and add-then-delete by hand would be the untooled write this module
    exists to replace. This function renames the HEADER only; repointing the inbound `from` /
    `rests-on` edges across a corpus is the handler's job, because an edge may live in another bib.

    ⚑ THE SPAN IS THE READ'S OWN — `entry_re` group 2, located on the masked text and sliced from
    the raw — so a key mentioned in a comment or a note is never touched.
    """
    old, new = edit
    if old not in entries:
        return Refusal(f"bibstruct --rename: no entry {old!r} (have {len(entries)}).")
    if new in entries:
        return Refusal(f"bibstruct --rename: {new!r} already names an entry; never a merge.")
    if not new or _KEY_BREAKERS & set(new):
        return Refusal(f"bibstruct --rename: {new!r} is not a key the header can read back.")
    masked = mask_comments(text)
    for entry in grammar.entry_re.finditer(masked):
        if str(entry.group(2)) == old:
            return text[: entry.start(2)] + new + text[entry.end(2) :]
    return Refusal(
        f"bibstruct --rename: {old} parsed but its header was not located — the read and the "
        f"locate disagree, which is a defect."
    )


def remove_entry(
    text: str,
    key: str,
    entries: dict[str, dict[str, str]],
    grammar: Grammar,
) -> str | Refusal:
    """Return the text with ONE whole entry removed, or why it must not be.

    ⚑⚑ THE FOURTH VERB, AND THE GAP IT CLOSES WAS A HAND-EDIT. With only create, widen and set,
    removing a duplicated entry (sql-F34/F35, declared in two bibs) had one route left: editing
    the bib by hand, which is the untooled write this module exists to replace.

    ⚑ THE SPAN IS THE READ'S OWN — `entry_re`'s whole match, `@type{key,` through the column-0
    `}` — located on the masked text and sliced from the raw, so the comment-length invariant
    this module depends on holds here too. One blank separator line is taken with it, so the
    file keeps a single blank between its neighbours rather than accreting a gap per delete.

    ⚑ COMMENTS ABOVE THE ENTRY ARE LEFT IN PLACE, deliberately: whether a comment belongs to the
    entry below it or to the section it opens is not something the grammar records, and guessing
    would delete prose. The dry-run diff shows exactly what goes.
    """
    if key not in entries:
        return Refusal(
            f"bibstruct --delete: no entry {key!r} (have {len(entries)}). Nothing to remove."
        )
    masked = mask_comments(text)
    for entry in grammar.entry_re.finditer(masked):
        if str(entry.group(2)) != key:
            continue
        lo, hi = entry.start(0), entry.end(0)
        if text[hi : hi + 1] == "\n":
            hi += 1
        if text[hi : hi + 1] == "\n" and (lo == 0 or text[lo - 2 : lo] == "\n\n"):
            hi += 1
        return text[:lo] + text[hi:]
    return Refusal(
        f"bibstruct --delete: {key} parsed but its span was not located — the read and the "
        f"locate disagree, which is a defect."
    )
