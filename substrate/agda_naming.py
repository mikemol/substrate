# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Path-to-module and module-to-path for the Agda tree, plus the name a source DECLARES.

⚑⚑⚑ THE SECOND UNIT OUT OF THE `agda_lex` PROMOTION, AND THE SEAM IS THE ORIGIN'S OWN. That
module is reached from 91 BARE import sites across 63 files with ZERO dotted ones
(`module_importers agda_lex`), so the tree's most-shared reader is unimportable from any
packaged consumer; `attr_reads agda_lex.*` reports 182 attribute reads over ~20 names. After
`mask_comments` (drained as `substrate.agda_mask`), the next cluster by consumption is
path-and-naming — `module_path`, `module_file`, `module_name_of`, `SUFFIX` — reached by four
pre-commit gates and every `tests/test_agda_lex_*` suite.

⚑⚑ THESE ARE THE PURE HALF, AND THE ORIGIN ALREADY SEPARATED THEM. `module_path`'s own
docstring says *"Pure: no cwd, no filesystem, no globals"*, and `agda_root_from` is documented
as deliberately apart because *"this is the one function that touches the filesystem and makes
an assumption about layout, so it is the one function a different deployment would replace"*.
That root-finder is therefore NOT drained here: lifting it would carry a layout assumption into
the package, which is exactly what its author kept out.

⚑ THE ROOT SPELLING MUST NOT CHANGE THE ANSWER — WITHIN ONE FRAME. `module_path` normalises
both operands, so `agda` and `agda/` agree and `/w/agda` against `/w/agda/…` resolves.

⚑⚑ WHAT IT DOES NOT DO IS MIX FRAMES, AND A CASE I WROTE ASSERTING OTHERWISE FAILED. An
absolute path against a RELATIVE root cannot be reconciled without consulting the cwd — and the
cwd is precisely the dependence this function exists to avoid. The origin reaches for `abspath`
there, so it answers differently depending on where it was invoked; that is a bound to name
rather than a behaviour to copy. A mixed pair falls through to the un-rebased name, which is
visibly wrong rather than quietly cwd-dependent.

⚑⚑ AND `module_name_of` READS THE HEADER, NOT THE PATH, WHICH IS A RECORDED DEFECT CLASS. The
two disagree mid-collapse and mid-move, and the HEADER is what Agda binds. The origin records
two ways the obvious regex fails: it is not anchored on a same-line `where` (a PARAMETERIZED
header spans lines, and all eight copies of `^module\s+(\S+)\s+where` in the tree miss it), and
an ASCII-only character class rejects most of this corpus, whose names carry mathematical
letters and subscripts. Both are cased.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

#: The extension every Agda source carries.
SUFFIX = ".agda"

# ⚑ THE HEADER PATTERN IS NEGATIVE, NOT AN ALLOW-LIST. It stops at whitespace, `{` or `(` —
# which is what admits a unicode name AND what lets a parameterized header match, since the
# parameters begin at one of those characters rather than at a `where` on the same line.
_HEADER = re.compile(r"^module[ \t]+([^\s{(]+)", re.MULTILINE)


def module_path(path: str, root: str) -> str:
    """Return the dotted module name for `path`, relative to `root`.

    `module_path("agda/Substrate/Foundation/Eq.agda", "agda")` is `Substrate.Foundation.Eq`.

    ⚑ PURE — no cwd, no filesystem, no globals. Both operands are normalised, so `agda` and
    `agda/` agree; a reader that let the spelling through would make every module name depend
    on where it was invoked.

    ⚑⚑ BOTH OPERANDS MUST SHARE A FRAME. An absolute path against a relative root is NOT
    reconciled — doing so needs the cwd, which is the dependence being avoided — so such a pair
    falls through un-rebased. That is visibly wrong at the call site rather than quietly
    cwd-dependent, and it is the one case a caller must get right.
    """
    got = PurePosixPath(path.replace("\\", "/"))
    base = PurePosixPath(root.replace("\\", "/"))
    rel = got.relative_to(base) if got == base or base in got.parents else got
    return str(rel).removesuffix(SUFFIX).replace("/", ".")


def module_file(mod: str, root: str) -> str:
    """Return the path under `root` for dotted module `mod` — the inverse of `module_path`."""
    return str(PurePosixPath(root) / (mod.replace(".", "/") + SUFFIX))


def module_name_of(src: str) -> str | None:
    """Return the module this SOURCE declares, from its own header, or None.

    ⚑⚑ FROM THE HEADER, NEVER THE PATH. The two disagree mid-collapse and mid-move, and the
    header is what Agda actually binds — so a reader taking the path answers a question about
    the filesystem when it was asked one about the language.

    ⚑ TAKES TEXT, NOT A PATH, so the caller controls I/O and comment masking. A function that
    opened the file would make every caller's caching and every test's fixture harder for no
    gain, and it is the reason this module needs no filesystem at all.

    ⚑ MASKED FIRST, because a commented-out header is not a declaration. The mask is the drained
    authority rather than a second stripper — the defect that once put fifteen copies of one
    stripper in the tree, nineteen importers inheriting the weakest.
    """
    from substrate import agda_mask  # noqa: PLC0415

    found = _HEADER.search(agda_mask.mask_comments(src))
    return found.group(1) if found else None
