# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The write handlers: validate, resolve the witness, then run the one write protocol.

⚑⚑⚑ THE ORDER IS THE DESIGN. Validate BEFORE the witness probe (a malformed entry should not cost a
subprocess), probe BEFORE the write (an unresolvable witness files an item nobody can ever close),
and write through ONE protocol (so the diff, the dry-run gate, the snapshot, the round-trip and the
read-back are the same for every verb). The origin ran that sequence three times with the arms
drifting — only `--add` verified the key read back, and only `--set` checked for a no-op.

⚑⚑ THE WITNESS PROBE IS `witness_resolves`, WHICH ASKS THE RESOLVER RATHER THAN SCANNING TEXT — and
that is the whole point of Ⓑ24. The origin text-scanned `catalog/library/items.py` for `def <KEY>(`,
a file the witnesses had VACATED, so a key that resolves perfectly at runtime was unwritable.
MEASURED in the origin's own suite: `--add … check=item:T27` refuses while `items.py T27` exits 0
and reports the item CLOSED. **The guard refuses a key the resolver answers.**

⚑⚑ THE HANDLERS ARE MODULE-LEVEL OVER A `Context`, NOT CLOSURES INSIDE `bind` — AND THE PER-FILE
GATE NAMED THAT SEAM TOO. A first cut nested both verbs in one function and was refused at `C901`
(complexity 14): one function carrying two verbs' logic is the monolith shape at the scale of a
closure. The context holds what a session fixes (the reader, the bench, the grammar); each handler
is a top-level function that can be read on its own.

⚑⚑⚑ THE CHECK GUARD HAS TWO ARMS BECAUSE A `check` NAMES TWO DIFFERENT KINDS OF THING, and the
second arm was missing for as long as this file existed (gate-F92). An `item:` check names a
witness that must RESOLVE. A `refuses:`/`selftest:` check names a COMMAND whose exit code must
already match the polarity its kind asserts — and `findings.py --register` probes exactly that at
filing time while `--add` probed nothing, so one hazard had two paths and only one guard. The
unguarded path is the one that writes the DURABLE record. A `traces:` check is still not probed,
and that is not an exemption: a claim about a peer's document has no item to resolve and no exit
code to assert, so both arms fall through and the honest kinds carry it.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import (
    bib_check,
    bib_cli,
    bib_edit,
    bib_entry,
    bib_pairs,
    bib_write,
    corpus,
    witness_resolves,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate import bib_argv

# The bib a write targets when the invocation names none.
# ⚑ ONE DEFAULT, NAMED ONCE. The origin resolved it inside each branch, so a verb added later got
# whatever its author remembered — and `--corpus` eating `--bib`'s operand made a write fall
# through to it silently.
DEFAULT_BIB = "catalog/worklist/warrants.bib"

# ⚑ THE VALUE MAY CONTAIN SPACES, so `--set` takes three operands and JOINS the tail. Taking only
# the third would silently truncate `enables = {A, B}` to `{A,` — the operand-ownership class this
# tool has now paid for five times.
SET_OPERANDS = 3
SET_USAGE = (
    "usage: bibstruct.py --set <key> <field> <value...> --apply\n"
    "  edits ONE field of ONE existing entry. Adding an entry or a field is a\n"
    "  different operation and is refused. Without --apply this prints the diff\n"
    "  and writes nothing."
)

# ⚑⚑ SAME OPERAND SHAPE AS `--set`, DELIBERATELY. A third verb with a fourth calling convention is
# how a toolkit becomes unlearnable — the difference between these verbs is what they REFUSE, not
# how they are typed, so the usage differs only in what it says is refused.
ADDFIELD_USAGE = (
    "usage: bibstruct.py --addfield <key> <field> <value...> --apply\n"
    "  adds a field an EXISTING entry does not carry. Creating an entry is\n"
    "  `--add`; editing an existing value is `--set`; both are refused here.\n"
    "  Without --apply this prints the diff and writes nothing."
)


@dataclass(frozen=True, slots=True)
class Context:
    """What a write session fixes: how bibs are read, how writes are guarded, the grammar.

    ⚑ ALL THREE ARE INJECTED SO A FIXTURE CAN DRIVE THE WHOLE WRITE PATH WITHOUT A REAL BIB. The
    origin hardcoded its parser, its snapshot guard and its patterns, which is why its suite had to
    write real files — and why a refusal reached through the CLI killed the run.
    """

    read: Callable[[Path], dict[str, dict[str, str]]]
    bench: bib_write.Bench
    grammar: bib_edit.Grammar


def _keys(ctx: Context, path: Path) -> frozenset[str]:
    """Return the keys one bib declares, or none when it is absent."""
    return frozenset(ctx.read(path)) if path.exists() else frozenset()


def _text(path: Path) -> str:
    """Return a bib's current text, or empty when it does not exist yet."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _target(parsed: bib_argv.Parsed) -> Path:
    """Return the bib this write targets."""
    return Path(parsed.target or DEFAULT_BIB)


def _applying(parsed: bib_argv.Parsed) -> bool:
    """Whether the invocation asked to write.

    ⚑ THE PREVIEW IS THE ABSENCE OF `--apply`, so this reads the flag rather than defaulting
    either way — a mutating verb that guesses is what the shared convention forbids.
    """
    return bib_write.APPLY_FLAG in parsed.rest


def _corpus_keys(ctx: Context, parsed: bib_argv.Parsed, target: Path) -> frozenset[str]:
    """Return every key an edge may resolve into: the target's PLUS every sibling named.

    ⚑⚑ THE POPULATION IS STATED, NOT INFERRED. Globbing the target's directory would silently
    widen the validation set on a tree the writer does not own, and an edge that resolves only
    because an unrelated file sat beside it is a pass for the wrong reason.
    """
    keys = _keys(ctx, target)
    for other in parsed.corpus:
        path = Path(other)
        if path.resolve() != target.resolve():
            keys |= _keys(ctx, path)
    return keys


def _item_refusal(target: Path, wkey: str) -> str | None:
    """Return why an `item:` witness cannot resolve, or None when it can."""
    module = witness_resolves.witness_module(str(target))
    if module is None:
        return witness_resolves.missing_module(str(target), wkey)
    asked = witness_resolves.probe(module, wkey)
    if not asked.resolved:
        # ⚑ THE CAUSE TRAVELS: a hang-guard crossing must not print as "exits 2" (gate-G453).
        return witness_resolves.refusal(module, wkey, asked.cause)
    return None


def _witness_refusal(target: Path, check: str) -> str | None:
    """Return why a `check` cannot be written, or None when it may be.

    ⚑⚑ TWO ARMS, TWO QUESTIONS. An `item:` check names a witness that must RESOLVE — asked of
    the resolver, because a claim whose witness does not exist files as ordered-but-never-
    closable. A `refuses:`/`selftest:` check names a COMMAND whose exit code must already match
    the polarity its kind asserts, which no static reading of the text can establish.

    ⚑ EACH ARM FALLS THROUGH FOR A CHECK IT DOES NOT OWN. `item:`, `unwitnessed`, `standing`,
    `traces:` and a command check are all legitimate, so a guard refusing anything it did not
    recognise would break every entry filed under a kind it does not read.
    """
    wkey = bib_entry.witness_key(check)
    if wkey is not None:
        return _item_refusal(target, wkey)
    refusal: str | None = bib_check.refusal(check, str(corpus.ROOT))
    return refusal


def add(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Create a NEW entry from `name=value` operands."""
    split = bib_pairs.split(list(parsed.paths))
    if not split.usable or split.key is None:
        return (bib_pairs.USAGE,), bib_cli.REFUSED

    target = _target(parsed)
    refusal = bib_entry.validate(
        split.key,
        split.fields,
        target_keys=_keys(ctx, target),
        corpus_keys=_corpus_keys(ctx, parsed, target),
    )
    if refusal is not None:
        return (refusal.message,), refusal.code

    # ⚑⚑ THE CHECK PROBE, AND IT ASKS RATHER THAN READS. For an `item:` check this is the one
    # line Ⓑ24 exists for; for a command check it is the polarity arm gate-F92 named.
    blocked = _witness_refusal(target, split.fields.get("check", ""))
    if blocked is not None:
        return (blocked,), bib_cli.REFUSED

    old = _text(target)
    outcome = bib_write.apply_write(
        bib_write.Edit(
            verb="--add",
            label=split.key,
            target=target,
            old=old,
            new=bib_entry.append(old, split.key, split.fields),
            expect_key=split.key,
        ),
        ctx.bench,
        applying=_applying(parsed),
    )
    return outcome.lines, outcome.code


def set_one(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Edit ONE field of ONE existing entry."""
    if len(parsed.paths) < SET_OPERANDS:
        return (SET_USAGE,), bib_cli.REFUSED

    key, field = parsed.paths[0], parsed.paths[1]
    value = " ".join(parsed.paths[2:])
    target = _target(parsed)
    old = _text(target)

    edited = bib_edit.set_field(old, (key, field, value), ctx.read(target), ctx.grammar)
    if isinstance(edited, bib_edit.Refusal):
        return (edited.message,), edited.code

    outcome = bib_write.apply_write(
        bib_write.Edit(verb="--set", label=f"{key}.{field}", target=target, old=old, new=edited),
        ctx.bench,
        applying=_applying(parsed),
    )
    return outcome.lines, outcome.code


def add_field(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Add a field an EXISTING entry does not carry.

    ⚑⚑ THIS VERB EXISTS BECAUSE THE OTHER TWO LEFT A GAP NEITHER COULD REACH. `--set` refuses a
    field the entry lacks and `--add` refuses a key that exists, so an entry filed WITHOUT a field
    was fixable by neither — measured on a peer's live floor, where a corroboration missing `note`
    read back as `kind ? by ?` and the only routes left were hand-editing a peer's file or deleting
    and re-adding.
    """
    if len(parsed.paths) < SET_OPERANDS:
        return (ADDFIELD_USAGE,), bib_cli.REFUSED

    key, field = parsed.paths[0], parsed.paths[1]
    value = " ".join(parsed.paths[2:])
    target = _target(parsed)
    old = _text(target)

    widened = bib_edit.add_field(old, (key, field, value), ctx.read(target), ctx.grammar)
    if isinstance(widened, bib_edit.Refusal):
        return (widened.message,), widened.code

    outcome = bib_write.apply_write(
        bib_write.Edit(
            verb="--addfield", label=f"{key}.{field}", target=target, old=old, new=widened
        ),
        ctx.bench,
        applying=_applying(parsed),
    )
    return outcome.lines, outcome.code


DELETE_USAGE = (
    "usage: bibstruct.py --delete <key> --bib <bib> [--corpus <bib> …] --apply\n"
    "  removes ONE whole entry from the target bib. Refused while an entry in the\n"
    "  stated corpus has an edge into the key and no other bib there declares it.\n"
    "  Without --apply this prints the diff and writes nothing."
)

# The fields that carry an edge to another entry.
_EDGE_FIELDS = ("from", "rests-on")


def _dangling_after(ctx: Context, parsed: bib_argv.Parsed, target: Path, key: str) -> list[str]:
    """Return the entries whose edge into `key` would dangle once `target` no longer declares it.

    ⚑ THE POPULATION IS THE STATED CORPUS, as for every edge check here. A key still declared in a
    sibling bib (the duplicated case this verb was built for) leaves nothing dangling; a key
    declared nowhere else leaves every inbound edge pointing at nothing.
    """
    bibs = [target, *(Path(p) for p in parsed.corpus)]
    others = [bib for bib in bibs if bib.resolve() != target.resolve()]
    if any(key in _keys(ctx, bib) for bib in others):
        return []
    inbound: list[str] = []
    for bib in bibs:
        entries = ctx.read(bib) if bib.exists() else {}
        for other, fields in entries.items():
            targets = {t.strip() for f in _EDGE_FIELDS for t in fields.get(f, "").split(",")}
            if other != key and key in targets:
                inbound.append(f"{bib.name}:{other}")
    return inbound


def delete(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Remove ONE whole entry, refusing while doing so would leave an edge dangling."""
    if len(parsed.paths) != 1:
        return (DELETE_USAGE,), bib_cli.REFUSED

    key = parsed.paths[0]
    target = _target(parsed)
    dangling = _dangling_after(ctx, parsed, target, key)
    if dangling:
        why = (
            f"bibstruct --delete: {key} is the target of {len(dangling)} edge(s) and no other "
            f"bib in the corpus declares it: {', '.join(dangling)}. Repoint them first."
        )
        return (why,), bib_cli.REFUSED

    old = _text(target)
    removed = bib_edit.remove_entry(old, key, ctx.read(target), ctx.grammar)
    if isinstance(removed, bib_edit.Refusal):
        return (removed.message,), removed.code

    outcome = bib_write.apply_write(
        bib_write.Edit(
            verb="--delete", label=key, target=target, old=old, new=removed, gone_key=key
        ),
        ctx.bench,
        applying=_applying(parsed),
    )
    return outcome.lines, outcome.code


RENAME_USAGE = (
    "usage: bibstruct.py --rename <old> <new> --bib <bib> [--corpus <bib> …] --apply\n"
    "  renames ONE entry's key in the target bib and repoints every from/rests-on edge\n"
    "  naming it across the target and the stated corpus. Refused if <new> is taken.\n"
    "  Without --apply this prints the diffs and writes nothing."
)

# `--rename` takes exactly the old key and the new one.
_RENAME_OPERANDS = 2


def _repoint(
    text: str, edit: tuple[str, str], entries: dict[str, dict[str, str]], grammar: bib_edit.Grammar
) -> str | bib_edit.Refusal:
    """Return `text` with every edge naming `old` rewritten to `new`. `edit` is `(old, new)`.

    ⚑ A WHOLE COMMA-SEPARATED TOKEN, NEVER A SUBSTRING: an edge list `A5, A5-as` repointing `A5`
    must leave `A5-as` alone. `entries` is the file's entries keyed as they are NOW (after a header
    rename, under the new key), because `set_field` checks the key it edits.
    """
    old, new = edit
    for key, fields in entries.items():
        for field in _EDGE_FIELDS:
            tokens = [t.strip() for t in fields.get(field, "").split(",")]
            if old not in tokens:
                continue
            value = ", ".join(new if t == old else t for t in tokens)
            text_or_refusal = bib_edit.set_field(text, (key, field, value), entries, grammar)
            if isinstance(text_or_refusal, bib_edit.Refusal):
                return text_or_refusal
            text = text_or_refusal
    return text


def rename(ctx: Context, parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Rename ONE entry's key and repoint every inbound edge across the stated corpus.

    ⚑⚑ THE RE-KEY'S SUCCESSOR (the findings roster is the bibs now). One write per touched bib,
    each through the one protocol — so each is snapshotted, round-tripped and read back. The
    target's write declares BOTH arms: the new key must read back and the old must not.
    """
    if len(parsed.paths) != _RENAME_OPERANDS:
        return (RENAME_USAGE,), bib_cli.REFUSED
    old_key, new_key = parsed.paths[0], parsed.paths[1]
    target = _target(parsed)
    renamed = bib_edit.rename_entry(
        _text(target), (old_key, new_key), ctx.read(target), ctx.grammar
    )
    if isinstance(renamed, bib_edit.Refusal):
        return (renamed.message,), renamed.code
    others = [Path(p) for p in parsed.corpus if Path(p).resolve() != target.resolve()]
    lines: list[str] = []
    worst = bib_write.OK
    for bib in [target, *others]:
        is_target = bib.resolve() == target.resolve()
        before = _text(bib)
        entries = dict(ctx.read(bib)) if bib.exists() else {}
        if is_target:
            entries[new_key] = entries.pop(old_key)
        after = _repoint(renamed if is_target else before, (old_key, new_key), entries, ctx.grammar)
        if isinstance(after, bib_edit.Refusal):
            return (*lines, after.message), after.code
        outcome = bib_write.apply_write(
            bib_write.Edit(
                verb="--rename",
                label=f"{old_key} -> {new_key} in {bib.name}",
                target=bib,
                old=before,
                new=after,
                expect_key=new_key if is_target else None,
                gone_key=old_key if is_target else None,
            ),
            ctx.bench,
            applying=_applying(parsed),
        )
        lines.extend(outcome.lines)
        worst = max(worst, outcome.code)
    return tuple(lines), worst


def bind(ctx: Context) -> dict[str, Callable[[bib_argv.Parsed], bib_cli.Result]]:
    """Return the write-handler table over `ctx`.

    ⚑ THE TABLE IS A LOOKUP, AND SO IS ITS CONSTRUCTION. Each entry binds a module-level handler to
    the context — nothing here is a place logic can accumulate, which is what the complexity
    refusal was pointing at.
    """
    return {
        "--add": partial(add, ctx),
        "--set": partial(set_one, ctx),
        "--addfield": partial(add_field, ctx),
        "--delete": partial(delete, ctx),
        "--rename": partial(rename, ctx),
    }
