# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Write a file atomically in a stated encoding, or refuse because the caller asked for a preview.

⚑⚑⚑ THIS SITS UNDER THE EXISTING GUARDS, NEVER BESIDE THEM. It is a CODEC-AND-ATOMICITY seam and
nothing else: it does not snapshot, does not decide mutation intent, and does not invalidate a
cache — because those layers exist already. A writer that re-implemented any of them would be a
fifth spelling of the snapshot, which is the very defect this repo records against itself. The
layering is `tool --apply` → snapshot guard → the caller's one write path → this.

⚑⚑ THE ENCODING IS THE POINT, AND THE BUG IS MEASURED. A fixture using a bare `open(path, "w")`
took the LOCALE default and mangled mathematical and Agda glyphs — costing four wrong cause
hypotheses against a function that was correct. The same note records that the tool doing the
repair read and wrote with bare `open()` too, so the defect sat on BOTH halves of the seam: a
read-only lift would have left the write half standing.

⚑ ATOMIC BY CONSTRUCTION. The bytes go to a sibling temp and then `os.replace`, so an interrupted
write leaves the ORIGINAL rather than a truncated file. `open(p, "w")` truncates BEFORE it writes,
which means a crash mid-write destroys the source — over a tree whose only other copy may be an
uncommitted working-tree edit.

⚑⚑⚑ AND THE DRY-RUN IS A VALUE THE CALLER HOLDS, NOT A MODULE GLOBAL. The origin honoured a
module-level `DRY_RUN` flag, so whether a write happened depended on ambient state no signature
mentioned — the same shape as a root derived from a source file's own location, which this arc's
operator ruling rejected. Here the mode is a parameter: a preview REFUSES and says so, and a reader
of the call can see which it is without knowing what some other module set.

⚑⚑ THE REFUSAL IS NOT A REGEX-PLEASER. A bare `intent = "apply"` assignment would satisfy a census
looking for the literal while doing nothing — code written to move a number, the false-green this
repo's ratchet comments record repeatedly. So the mode is checked WITH AN EFFECT: it is the point
where a preview is honoured, and a byte-level writer that ignored the operator's `--dry-run` would
be the hole under every gate above it.

⚑ AND THE TYPE GUARD THE ORIGIN CARRIED IS GONE BECAUSE THE TYPES MAKE IT UNREACHABLE. It raised a
`TypeError` for anything that was neither `str` nor `bytes`; under a checked signature mypy proves
that branch dead. A runtime check the type system already enforces is a check nothing can exercise,
and keeping it would mean shipping a line no case could ever reach.
"""

from __future__ import annotations

import os
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple

#: The codec every write uses. Named rather than defaulted, because the locale default is what
#: mangled a document once already.
ENCODING = "utf-8"

#: The suffix a pending write occupies while it is being filled.
TEMP_SUFFIX = ".write-tmp"


class Mode(StrEnum):
    """Whether a caller means to change the tree or to preview the change.

    ⚑ TWO NAMED MODES RATHER THAN A BOOLEAN, because `write(path, data, True)` at a call site says
    nothing about which way round the flag runs — and this is the parameter that decides whether
    the tree changes.
    """

    APPLY = "apply"
    PREVIEW = "preview"


class RefusedError(RuntimeError):
    """Raised when a write was attempted under `Mode.PREVIEW`.

    ⚑ A DISTINCT TYPE, so a caller running many writes can tell *the operator asked for a preview*
    from *the filesystem refused me*. Collapsing them into `OSError` would make a dry run
    indistinguishable from a permissions failure.
    """


class Written(NamedTuple):
    """What a write did, or would have done under a preview."""

    path: Path
    written: bool
    size: int

    def why(self) -> str:
        """Return a one-line account naming the path and what happened."""
        did = "wrote" if self.written else "would write"
        return f"{did} {self.size} byte(s) to {self.path}"


def encode(data: str | bytes, encoding: str = ENCODING) -> bytes:
    """Return `data` as bytes in the stated codec.

    ⚑ THE CODEC IS A PARAMETER RATHER THAN THE ENVIRONMENT'S. That is the whole defect this seam
    exists for: a locale-default encode is a different function on a different machine, and the
    document it mangles reads as plausible everywhere the locale happens to match.
    """
    return data.encode(encoding) if isinstance(data, str) else bytes(data)


def write(
    path: Path | str,
    data: str | bytes,
    mode: Mode = Mode.APPLY,
    encoding: str = ENCODING,
    *,
    mkdirs: bool = False,
) -> Written:
    """Write `data` to `path` atomically, or REFUSE when the caller asked for a preview.

    ⚑⚑ A PREVIEW RAISES RATHER THAN RETURNING QUIETLY. A caller that wanted the size without the
    write calls `preview`; a caller that reached HERE under a preview has a bug, and returning a
    plausible `Written` would let it report a dry run as a completed edit.

    ⚑ AND THE TEMP FILE IS REMOVED ON EVERY FAILURE PATH, including an interrupt — otherwise a
    cancelled run leaves a sibling that the next glob counts as a document.
    """
    where = Path(path)
    payload = encode(data, encoding)

    if mode is not Mode.APPLY:
        msg = (
            f"refused: the caller asked for {mode}, so this seam will not write to {where}. "
            f"Pass Mode.APPLY to apply."
        )
        raise RefusedError(msg)

    if mkdirs:
        where.parent.mkdir(parents=True, exist_ok=True)

    tmp = where.with_name(f"{where.name}{TEMP_SUFFIX}.{os.getpid()}")
    try:
        with tmp.open("wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        tmp.replace(where)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return Written(where, written=True, size=len(payload))


def preview(path: Path | str, data: str | bytes, encoding: str = ENCODING) -> Written:
    """Return what a write WOULD do, touching nothing.

    ⚑ THE SIZE IS COMPUTED THE SAME WAY THE WRITE COMPUTES IT, through `encode`, so a preview
    cannot report a length the real write would disagree with — which is the only thing that makes
    a dry run evidence about the write rather than about the preview.
    """
    return Written(Path(path), written=False, size=len(encode(data, encoding)))
