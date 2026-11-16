# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Move a witness to a new key IN PLACE — the operation the pairing census asks for and lacks.

⚑⚑⚑ THE CENSUS PRINTS AN INSTRUCTION NO MODE PERFORMS (gate-F99). `findings.py --pairing`
reports SPELLING PAIRS as *one finding, two spellings — RE-KEY, do not file twice*, and the only
write the ledger offers is `register`, which CREATES. Measured: registering the long spelling
closed the pair row, turned the short key into WITNESS-ONLY, and left TRUE DRIFT unchanged — the
census moved a row between drift classes while the total held, because the honest repair is a
RENAME and creation cannot express one. The probe was reverted from the index.

⚑⚑ AND THE PAIR IS NOT TWO FILINGS, WHICH IS WHY RENAMING IS RIGHT. The short key is the
WITNESS; the long key is the BIB ENTRY. `findings.py tmi-F6` answers with its note while
`findings.py tmi-F6-ground-truth-…` exits 2 — one witness, one entry, differing keys. So nothing
is duplicated and nothing should be deleted: the witness needs the entry's spelling.

⚑⚑⚑ THIS EDITS THE KEY TOKEN AND NOTHING ELSE, AND THAT IS THE WHOLE SAFETY ARGUMENT. A rewriter
that PARSED the roster and re-emitted it would keep only what its parser recognised — a peer
measured exactly that this week, silently destroying three prose comments between bib entries
while their parse guard passed because the result was still valid. The roster here is source text
carrying hand-written comments, `# noqa` directives and lambda bodies that no re-emitter of mine
should ever be trusted to reproduce. So the edit is a single anchored replacement over the raw
bytes: everything the module does not explicitly change is not merely preserved but never read.

⚑ THE ANCHOR IS THE FULL ENTRY PREFIX, NOT THE BARE KEY, and the distinction is load-bearing.
`tmi-F1` occurs inside `tmi-F10`'s key, inside note prose, and inside other witnesses' text; only
a newline plus the ledger's exact indent plus the quoted key plus `": "` identifies the definition
site. The count is asserted to be exactly one before any write, so an anchor that matched twice —
or zero times — refuses instead of guessing which.

⚑ AND THE KEY CHARSET IS INHERITED FROM THE READER, NOT CHOSEN HERE. `bibstruct` resolves a
`check=item:<key>` against the ledger with a regex requiring a DOUBLE-quoted key, and the ledger's
own `register` records the incident: `%r` emitted single quotes, so the first machine-registered
witness was the first one that regex could not see — it existed, answered correctly, and was
invisible to the one reader whose refusal it had to clear. A re-key emitting the wrong quoting
would reproduce that silently, on a witness that used to work.

⚑⚑ AND THE VERDICT IS A TRI-STATE RATHER THAN A BOOL, WHICH THE GATE NAMED FOR ME. A first cut
returned `ok: bool` and was refused at `FBT003` — a bare `False` at a call site. Reading that as
a style rule would have produced a keyword argument; reading it as a design signal produced the
right carrier, because this operation genuinely has three outcomes: it WROTE, it would write and
was not asked to (a dry run is not a failure), or it REFUSED. Collapsing the first two onto one
`True` is what made the bool feel adequate.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pathlib import Path

#: The indent the ledger writes its entries at — matched, never assumed by re-indenting.
INDENT = "    "

#: The charset a key may use. Inherited from the readers that parse the emitted source, not a
#: preference: the ledger's own `register` enforces the same set for the same reason.
KEY_OK = re.compile(r"^[A-Za-z0-9_-]+$")


class Outcome(Enum):
    """What a re-key attempt did — three states, because a dry run is not a failure."""

    WROTE = "wrote"
    WOULD = "would"
    REFUSED = "refused"


class Rekey(NamedTuple):
    """The outcome of one re-key attempt.

    ⚑ `text` IS THE NEW CONTENT ON A NON-REFUSAL AND `None` ON A REFUSAL, so a caller cannot
    write a result it did not get. A shape returning text beside an independent flag lets a
    caller ignore the flag, which is the branch nobody tests.
    """

    outcome: Outcome
    reason: str
    text: str | None


def _refuse(reason: str) -> Rekey:
    """Return a refusal carrying `reason` and no text."""
    return Rekey(Outcome.REFUSED, reason, None)


def anchor_for(key: str) -> str:
    """Return the exact source anchor that identifies `key`'s definition site.

    ⚑ THE LEADING NEWLINE AND THE INDENT ARE BOTH PART OF THE IDENTITY. Without them the anchor
    matches inside note prose and inside longer keys — `tmi-F1` is a substring of `tmi-F10` and
    of a dozen sentences — and a substring match on a rename is how the wrong definition gets
    edited while every surface stays green.
    """
    return f'\n{INDENT}"{key}": '


def rekey(src: str, old: str, new: str) -> Rekey:
    """Return the ledger source with `old`'s entry key replaced by `new`, or a refusal.

    ⚑⚑ EVERY REFUSAL IS A DISTINCT REASON, NEVER A BARE NO. This runs against a roster whose
    corruption is unrecoverable in the shape that matters — a half-renamed key leaves a witness
    that neither spelling reaches — so a caller must be able to say WHICH precondition failed.

    ⚑ THE NEW KEY MUST NOT ALREADY EXIST. Renaming onto a live key would collapse two witnesses
    into one entry position and silently drop whichever the replacement did not keep — the
    reassembling-writer loss, reached through a rename rather than a re-emit.
    """
    if not KEY_OK.match(old) or not KEY_OK.match(new):
        return _refuse("a key must be [A-Za-z0-9_-]: it is emitted as source and read back by "
                       "a regex in bibstruct's witness resolver")
    if old == new:
        return _refuse(f"{old!r} is already the key — nothing to move")

    found = anchor_for(old)
    seen = src.count(found)
    if seen != 1:
        # ⚑ ZERO AND MANY ARE DIFFERENT FAILURES AND THE MESSAGE SAYS WHICH. Zero means the key
        # is not a definition site here (a bib-only key, or a typo); many means the roster is
        # already malformed, and renaming one of several is the worst available outcome.
        what = "no definition site" if seen == 0 else f"{seen} definition sites"
        return _refuse(f"{old!r} has {what} in this roster — refusing to guess")
    if src.count(anchor_for(new)) != 0:
        return _refuse(f"{new!r} is already a witness key — a rename onto a live key would drop "
                       "one of the two")

    return Rekey(Outcome.WOULD, f"{old} -> {new}", src.replace(found, anchor_for(new), 1))


def rekey_file(path: Path, old: str, new: str, *, apply: bool = False) -> Rekey:
    """Re-key in `path`, writing only under `apply`.

    ⚑ THE WRITE IS ATOMIC VIA A TEMP FILE AND `replace`, matching the ledger's own discipline:
    a half-written roster is unimportable, which breaks every witness at once rather than the one
    being renamed.

    ⚑⚑ AND `apply` IS EXPLICIT WITH NO DEFAULT-WRITE. The house rule is that a mutating tool must
    not guess — default-dry silently does nothing when you meant to write, default-apply silently
    writes when you meant to look — and this one edits a file whose corruption is not locally
    recoverable.
    """
    try:
        src = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _refuse(f"cannot read {path}: {exc}")

    found = rekey(src, old, new)
    if found.outcome is Outcome.REFUSED or found.text is None:
        return found
    if not apply:
        return Rekey(Outcome.WOULD, f"would re-key {found.reason} (--apply to write)", found.text)

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(found.text, encoding="utf-8")
    tmp.replace(path)
    return Rekey(Outcome.WROTE, f"re-keyed {found.reason}", found.text)
