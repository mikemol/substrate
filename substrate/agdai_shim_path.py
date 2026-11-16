# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the compiled `.agdai` decoder lives, resolved against the REAL checkout when one is named.

⚑ THE DECODER IS HOST STATE. `jea/metalanguage/agdai_shim` is a compiled, gitignored build output
(built from `agdai_shim.hs`), so it exists only in the real checkout. Inside the commit hook's
snapshot every core read as undecodable (`2409 of 2409`, W337) because the lookup was relative to
the importing file. The hook already names the real checkout in `MIKEMOL_REAL_ROOT` for the
interpreter; this applies the same routing to this one lookup.

The environment is a PARAMETER, supplied by the caller, never read from a module-level constant.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

REAL_ROOT_VAR = "MIKEMOL_REAL_ROOT"
_RELATIVE = Path("jea") / "metalanguage" / "agdai_shim"


def shim_path(here: Path, env: Mapping[str, str]) -> Path:
    """Return the decoder path: under the real checkout when `env` names one, else beside `here`.

    `here` is the directory of the module that used to resolve it. An empty value counts as unset,
    so an exported-but-blank variable cannot redirect the lookup to the current directory.
    """
    real = env.get(REAL_ROOT_VAR, "")
    if real:
        return Path(real) / _RELATIVE
    return here / "agdai_shim"
