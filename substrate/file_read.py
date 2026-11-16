# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a file as one of THREE outcomes, never two — present, absent, or broken.

⚑⚑⚑ THE DISTINCTION THREE CALL SITES LOST. A read that answers only *did I get text* collapses
*the file is not there* with *the file is there and I could not read it*, and those want different
responses: an absence is often expected and a broken read is always a defect. Sites that caught
`OSError` and moved on were counting a directory-as-document, a permission failure and a genuine
absence as one thing.

⚑⚑ AND `BROKEN` IS NOT A SUBTYPE OF `ABSENT`, WHICH IS THE WHOLE POINT. `IsADirectoryError` is an
`OSError`, so a caller guarding `except OSError` swallows it exactly as it swallows a missing file
— the seam exists so a caller CAN ask which fired, not so it must. A reader that only ever needs
*is there text* keeps working unchanged.

⚑ THE READ IS BYTES-FIRST WITH A STRICT DECODE. Raw bytes come back and the codec is chosen by the
caller rather than by the environment, and decoding is strict — a bad byte raises instead of
yielding replacement characters that a regex would happily scan and under-count. A silently mangled
document is worse than a refused one, because only the second is visible.

⚑⚑ THIS IS THE PACKAGED HALF OF AN UNPACKAGED SEAM. `scratch/vfs.py` owns a read, a write, a git
revision source and a glob listing; `swap_readiness` classifies it as resolving only through a
`sys.path` insert, so every packaged module wanting the three-valued read inherited that. The READ,
the WRITE and the LISTING are lifted; the revision source reads through `Source` below.

⚑⚑⚑ AND A READ CARRIES WHERE IT READ FROM, BECAUSE THE SAME PATH ANSWERS DIFFERENTLY PER SOURCE.
`ABSENT` means *not in the working tree* or *not in that commit*, and those are different facts a
caller acts on differently — one is an ordinary state, the other says a file was added since. The
origin put the source on the result for exactly this reason, and it is on the result rather than
paired beside it because a `Result` gets RETURNED: any function handing one onward drops a pairing
its caller then cannot reconstruct.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import NamedTuple, Protocol, runtime_checkable

#: The codec every document in this corpus is written in. Named so a caller reading a differently
#: encoded file states that rather than discovering it as mojibake.
ENCODING = "utf-8"


@runtime_checkable
class Source(Protocol):
    """Where a read came from — the working tree, or a named git revision.

    ⚑ A PROTOCOL RATHER THAN A BASE CLASS, so this module states what it NEEDS of a source (a
    printable name) without owning the revision machinery, which needs `pygit2` and belongs to the
    reader that has it. A module that must import a git library to describe an ordinary filesystem
    read has taken on a dependency its own callers do not want.
    """

    def __str__(self) -> str:
        """Return the human name of this source, as it should appear in a report."""


class Presence(StrEnum):
    """What a read found — three outcomes, deliberately not two.

    ⚑ A `StrEnum`, so a member compares equal to its own name and a report can print it directly.
    The origin hand-rolled that behaviour for callers mid-migration; a new module has none, so the
    standard type does the job and cannot drift from it.
    """

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    BROKEN = "BROKEN"

    @property
    def is_defect(self) -> bool:
        """Report whether this outcome is something to fix rather than something to expect.

        ⚑ ABSENT IS NOT A DEFECT. A census over a glob finds missing files routinely, and a reader
        that treated absence as breakage would report the shape of the query as damage to the tree.
        """
        return self is Presence.BROKEN


class Result(NamedTuple):
    """One read: what was found, the bytes if any, and the error if the read broke.

    ⚑⚑ `bool(result)` IS PRESENT-NESS AND NOTHING ELSE. That is what lets a caller write
    `if result:` without deciding between the other two, while `presence` stays available for one
    that cares. Making it truthy on BROKEN would put the collapse back.

    ⚑ `source` DEFAULTS TO `None`, MEANING THE WORKING TREE. The default is what keeps every
    existing construction site valid and keeps the ordinary read free of git vocabulary — a caller
    reading a file on disk should not have to name a source to say it meant the obvious one.
    """

    presence: Presence
    path: Path
    data: bytes | None = None
    error: Exception | None = None
    source: Source | None = None

    def __bool__(self) -> bool:
        """Report whether the read found readable content."""
        return self.presence is Presence.PRESENT

    def text(self, encoding: str = ENCODING) -> str:
        """Return the decoded text, raising when the read did not find any.

        ⚑ STRICT BY DEFAULT. A replacement character is a silent edit to a document, and every
        reader downstream would scan it as content.
        """
        if self.data is None:
            return self.require().decode(encoding)
        return self.data.decode(encoding)

    def require(self) -> bytes:
        """Return the bytes, or raise the reason there are none.

        ⚑⚑ THE TWO FAILURE ARMS RAISE DIFFERENT THINGS AND THAT IS DELIBERATE. An absence raises
        `FileNotFoundError`, so a caller's existing `except FileNotFoundError` keeps working; a
        broken read re-raises THE ORIGINAL ERROR, so the reason survives rather than being
        translated into a generic one.
        """
        if self.data is not None:
            return self.data
        if self.error is not None:
            raise self.error
        msg = f"{self.path} is absent{self.at()}"
        raise FileNotFoundError(msg)

    def at(self) -> str:
        """Return the ` at <source>` clause, empty for an ordinary working-tree read."""
        return "" if self.source is None else f" at {self.source}"

    def why(self) -> str:
        """Return a one-line account naming the path, the source, and what the read found.

        ⚑ THE SOURCE IS IN THE LINE BECAUSE AN ABSENCE IS AMBIGUOUS WITHOUT IT. `x.py: ABSENT`
        read against a revision says the file did not exist at that commit, which is a different
        fact from its being missing now, and a reader cannot tell which from the message alone.
        """
        if self.presence is Presence.PRESENT:
            size = len(self.data) if self.data is not None else 0
            return f"{self.path}{self.at()}: PRESENT, {size} byte(s)"
        if self.presence is Presence.ABSENT:
            return f"{self.path}{self.at()}: ABSENT"
        return f"{self.path}{self.at()}: BROKEN — {self.error}"


def read(path: Path | str) -> Result:
    """Return the three-valued read of `path`, never raising for absence or breakage.

    ⚑ NOT RAISING IS THE CONTRACT. A caller wanting an exception calls `require` or `text`; a
    caller taking a census over many paths needs each outcome as a VALUE, because one raised
    exception in the middle of a walk loses every row after it.
    """
    where = Path(path)
    try:
        return Result(Presence.PRESENT, where, data=where.read_bytes())
    except FileNotFoundError:
        return Result(Presence.ABSENT, where)
    except OSError as exc:
        return Result(Presence.BROKEN, where, error=exc)


def text(path: Path | str, encoding: str = ENCODING) -> str | None:
    """Return the decoded text, `None` when absent, RAISING when broken.

    ⚑⚑ ABSENT BECOMES `None` AND BROKEN STILL RAISES, which is the asymmetry a caller usually
    wants: a missing optional document is an ordinary branch, while an unreadable one is a defect
    that must not be mistaken for the same branch.
    """
    got = read(path)
    if got.presence is Presence.BROKEN:
        got.require()
    return got.text(encoding) if got else None
