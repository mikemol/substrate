# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Tell decomposition CHURN from genuinely-new debt in a ratchet's added keys.

⚑⚑⚑ THIS IS THE DRAIN'S PRECONDITION, AND WITHOUT IT A DRAIN CANNOT BANK ITS OWN PAYDOWN.
Decomposing a monolith is content-preserving but KEY-CHANGING: `X.agda` becomes
`X/Leaf.agda`, the old census key retires, and a byte-identical line mints a new one. A set
ratchet sees only "a key appeared" and refuses — and because it returns on `added` BEFORE
reaching its paydown branch, the churn also BLOCKS the real paydown from recording. So the
act of draining makes every gate over the drained file read as growth.

⚑⚑ IDENTITY ALONE IS NOT ENOUGH, and assuming it was is a false-absolution bug the origin
hit on its first live run. A key like `<file>::Substrate.Foundation.Eq::using` shares its
identity with hundreds of files, so pairing on identity alone would call a genuinely-new
violation churn because SOME unrelated file with that identity had moved. Pairing therefore
requires a PLAUSIBLE PATH MOVE as well — which is what `moved_from` decides.

⚑ THE HONEST LIMITATION, CARRIED FORWARD RATHER THAN QUIETLY DROPPED. If a name moves and a
genuinely-new violation of the SAME identity appears elsewhere in the same run, both
classify as churn. Two things bound it: churn is never auto-absolved, and a
one-old-to-many-new fan-out shows as a count asymmetry that `strict` reports as SUSPECT
rather than churn.

⚑ PROMOTED FROM `scripts/gate_preflight.py`, whose live path calls a reader that no longer
exists — so the tool crashes on any real invocation while its own suite passes, because the
cases exercise this pure half and never reach the read. That file carries hundreds of its
own findings and cannot be repaired in place; this is the half worth keeping.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from substrate import ratchet_key

_AGDA = ".agda"


@dataclass(frozen=True, slots=True)
class Verdict:
    """What a ratchet's added and paid keys mean once churn is separated out."""

    gate: str
    added: frozenset[str]
    paid: frozenset[str]
    churn: dict[str, tuple[str, ...]]
    genuinely_new: tuple[str, ...]
    suspect: dict[str, tuple[str, ...]]
    unpaired: frozenset[str]

    @property
    def queue(self) -> int:
        """How many added keys are real debt rather than a move."""
        return len(self.genuinely_new)

    @property
    def creditable(self) -> dict[str, str]:
        """The churn a RATCHET may actually credit: strict 1:1 pairs only.

        ⚑⚑⚑ THIS EXISTS BECAUSE THE TWO COUNTS READ AS A CONTRADICTION AND ARE NOT ONE.
        MEASURED on the ban gate: this module reported 198 churn keys while
        `ratchet_core.split_moves` credited 20 — and an operator seeing both concluded the
        classifier was wrong. Neither is. **They answer different questions.** `churn`
        answers *"is this the same violation at a new path"*, which is what a reader needs
        in order to understand a red gate. This answers *"may a paydown-only baseline
        absolve it"*, which is a strictly narrower thing.

        ⚑⚑ AND THE NARROWING IS A FAN-OUT, WHICH IS THE DOMINANT BAN SHAPE. One monolith
        splitting into seventeen leaves mints seventeen keys carrying one retired key's
        identity. At most ONE is that key relocated; the other sixteen are new violations
        that inherited a moved name. Crediting all seventeen on one retirement absolves
        sixteen pieces of real debt into a baseline that can never legitimately un-absolve
        them — so a fan-out is growth, exactly as `check_public_ratchet` already records.

        ⚑ REPORTED ALWAYS, NOT UNDER A FLAG. `strict` reclassifies a fan-out as SUSPECT and
        is opt-in, so the DEFAULT rendering showed 198 with nothing saying how much of it a
        gate could act on. A number an operator cannot act on, printed beside one they can,
        with no way to tell them apart, is the shape that made this look like a bug.

        ⚑⚑⚑ AND IT REPRODUCES `split_moves`' RULE RATHER THAN A STRICTER ONE — a first cut
        did NOT, and that disagreement was the same defect repeating one layer in.
        `split_moves` pairs on IDENTITY ALONE, one-to-one on both sides, with no path-shape
        test. Layering `moved_from` on top credited 0 of ban's 20 and 3 of sumtype's 2 —
        wrong in BOTH directions at once, which is what a second independent implementation
        of one predicate buys. The path test belongs to `churn`, a reader's question where a
        false pair costs one confusing line; the CREDIT question has an authority, and this
        defers to it rather than re-deriving it.
        """
        return {dst: src for src, dst in self.moves}

    @property
    def moves(self) -> frozenset[tuple[str, str]]:
        """The `(retired, added)` pairs a paydown-only baseline may absolve.

        ⚑ ONE-TO-ONE ON BOTH SIDES. A 1→N fan-out is growth wearing a move's clothes; an
        N→1 is a genuine paydown that must stay visible as one. Each credited move consumes
        exactly one removal, so the total can never rise through this path.
        """
        src_by = _group_by_identity(self.gate, self.paid)
        dst_by = _group_by_identity(self.gate, self.added)
        return frozenset(
            (src_by[ident][0], dsts[0])
            for ident, dsts in dst_by.items()
            if len(dsts) == 1 and len(src_by.get(ident, [])) == 1
        )


def moved_from(old_path: str, new_path: str) -> bool:
    """Report whether `new_path` is a plausible destination for `old_path`.

    The decomposition shapes this exists for are path-LOCAL:

        X.agda      → X/Leaf.agda    a monolith split into its own directory
        Dir/X.agda  → Dir/Y.agda     a leaf renamed within its directory

    ⚑ ANYTHING ELSE IS NOT A MOVE THIS CAN EVIDENCE, so it is not churn. Widening the
    predicate to "some file with this identity moved" is precisely the false absolution
    the origin measured: a shared identity would launder every new violation carrying it.
    """
    if old_path == new_path:
        return False
    stem = old_path.removesuffix(_AGDA)
    if new_path.startswith(stem + "/"):
        return True
    return str(Path(old_path).parent) == str(Path(new_path).parent)


def _same_identity(gate: str, key: str, ident: tuple[str, ...]) -> bool:
    """Report whether `key` carries `ident`, treating a malformed key as no match."""
    try:
        return ratchet_key.identity(gate, key) == ident
    except ratchet_key.MalformedKeyError:
        return False


def _group_by_identity(
    gate: str,
    keys: frozenset[str],
) -> dict[tuple[str, ...], list[str]]:
    """Group whole KEYS by identity — the grouping a move pairing needs.

    ⚑ ITS SIBLING GROUPS PATHS, AND THE DIFFERENCE IS THE WHOLE POINT. `_paid_by_identity`
    keeps paths because `churn` asks whether a path move is plausible; a move CREDIT names
    the retired key itself, so nothing may be discarded on the way.

    ⚑ A MALFORMED KEY IS SKIPPED, NOT RAISED — it can pair with nothing, and a baseline
    predating a schema change must not abort the classification.
    """
    out: dict[tuple[str, ...], list[str]] = {}
    for key in keys:
        try:
            ident = ratchet_key.identity(gate, key)
        except ratchet_key.MalformedKeyError:
            continue
        out.setdefault(ident, []).append(key)
    return out


def _paid_by_identity(gate: str, paid: set[str]) -> dict[tuple[str, ...], list[str]]:
    """Group the paid keys' paths by identity.

    ⚑ A MALFORMED BASELINE KEY IS SKIPPED, NOT RAISED. It cannot pair anything, and a
    baseline predating a schema change should not stop the whole classification.
    """
    out: dict[tuple[str, ...], list[str]] = {}
    for key in paid:
        try:
            ident = ratchet_key.identity(gate, key)
        except ratchet_key.MalformedKeyError:
            continue
        out.setdefault(ident, []).append(ratchet_key.path_of(gate, key))
    return out


def classify(
    gate: str,
    base: set[str],
    cur: set[str],
    *,
    strict: bool = False,
) -> Verdict:
    """Partition `cur - base` into churn and genuinely-new. Pure; no I/O.

    ⚑ AN UNPARSEABLE ADDED KEY IS NEVER SILENTLY ABSOLVED. It cannot be paired, so it
    counts as genuinely new — the safe direction, since the alternative is calling real
    debt a move on the strength of a key nobody could read.
    """
    added, paid = cur - base, base - cur
    by_ident = _paid_by_identity(gate, paid)

    churn: dict[str, tuple[str, ...]] = {}
    genuinely_new: list[str] = []
    suspect: dict[str, tuple[str, ...]] = {}
    consumed: set[str] = set()

    for key in sorted(added):
        try:
            new_path, ident = ratchet_key.parse(gate, key)
        except ratchet_key.MalformedKeyError:
            genuinely_new.append(key)
            continue
        olds = tuple(p for p in by_ident.get(ident, ()) if moved_from(p, new_path))
        if not olds:
            genuinely_new.append(key)
            continue
        # ⚑ A 1-OLD → N-NEW FAN-OUT MEANS AT MOST ONE OF THE N IS THE MOVE, and the rest
        # are new violations wearing a moved name. Under `strict` that asymmetry is
        # SUSPECT rather than churn, because absolving all N on one move is the shape
        # this tool exists to refuse.
        rivals = sum(
            1
            for other in added
            if other != key
            and _same_identity(gate, other, ident)
            and any(moved_from(p, ratchet_key.path_of(gate, other)) for p in olds)
        )
        if strict and rivals >= len(olds):
            suspect[key] = olds
        else:
            churn[key] = olds
            consumed.update(ratchet_key.rekey(gate, key, p) for p in olds)

    return Verdict(
        gate=gate,
        added=frozenset(added),
        paid=frozenset(paid),
        churn=churn,
        genuinely_new=tuple(genuinely_new),
        suspect=suspect,
        unpaired=frozenset(paid - consumed),
    )
