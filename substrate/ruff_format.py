# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Format Python source text exactly as `ruff format` would, by running ruff (W39).

⚑⚑ A GENERATOR MUST EMIT WHAT THE FORMATTER WOULD, OR ITS CHECK CAN NEVER PASS. The operator's
rule is that every `.py` in every repo is `ruff format`-clean (2026-09-25), and the bulk pass
reformatted the generated `jea/metalanguage/query_sql_postgres.py` with everything else. Its
generator (`sql_cache.render`) still emitted the old single-line layout, so the byte round-trip
`query_defs --check` relies on failed on the first entry: a green file, a red gate.

⚑ RUFF IS RUN, NOT IMITATED. Its layout rules (quote style, magic trailing commas, when a
container explodes) are ruff's to change; a hand re-derivation would pass today and drift on
the next ruff release, silently, in the one direction the gate cannot see. The project's own
config applies because ruff is started in the project and told the file's real name.

⚑ A FAILURE RAISES. A formatter that returned its input unchanged on error would hand the
caller unformatted text that LOOKS processed — exactly the defect this module exists to close.
"""

from __future__ import annotations

import subprocess
import sys

# How long one format may take before it is treated as a failure.
TIMEOUT_S = 60


class FormatError(RuntimeError):
    """ruff did not format the source."""


def format_source(text: str, filename: str) -> str:
    """Return `text` as `ruff format` would write it to `filename`, or raise FormatError."""
    try:
        done = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--stdin-filename", filename, "-"],
            input=text,
            capture_output=True,
            text=True,
            check=False,
            timeout=TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        msg = f"ruff format could not run on {filename}: {exc}"
        raise FormatError(msg) from exc
    if done.returncode != 0:
        msg = f"ruff format refused {filename} (exit {done.returncode}): {done.stderr.strip()}"
        raise FormatError(msg)
    return done.stdout
