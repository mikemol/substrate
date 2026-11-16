# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve a luthen port BY NAME, on every call (W49, 2026-09-23; generalised W38c; W319).

A thin adapter over `substrate.luthen_resolver`, the one caller of luthen's resolver. It keeps the
names its importers use: `resolve(port, luthen) -> (host, port)`, `address(luthen)`,
`UnresolvedError`, `DEFAULT_LUTHEN`, and `run`, the process launcher both adapters inject (this is
the module the lint config sanctions a subprocess call in).
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from substrate import luthen_resolver as lr

if TYPE_CHECKING:
    from pathlib import Path

VMAGENT = "vmagent-http"
TIMEOUT_S = 10

#: ⚑⚑⚑ THE ONE SANCTIONED DEFAULT (W35). `resolve`/`address` refuse to default `luthen`
#: themselves; `vlogs_destination.destination()` has no CLI entry point to carry a `--luthen` flag.
#: A caller with a real entry point should take `--luthen` and default to THIS constant.
DEFAULT_LUTHEN: Path = lr.DEFAULT_LUTHEN


class UnresolvedError(lr.ResolverError):
    """luthen's resolver did not answer with a host and port."""


def run(argv: list[str], timeout_s: int = TIMEOUT_S) -> tuple[int, str]:
    """Run one command and return `(exit code, stdout)`; a launch failure is exit -1."""
    try:
        got = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        return -1, str(exc)
    return got.returncode, got.stdout


def resolve(port: str, luthen: Path) -> tuple[str, int]:
    """Return `(host, port)` for the named luthen port, or raise UnresolvedError with the reply.

    ⚑ `luthen` IS A REQUIRED PARAMETER, NOT A MODULE CONSTANT (W35, operator 2026-09-24).
    """
    try:
        got = lr.resolve(port, run, luthen)
    except lr.ResolverError as exc:
        raise UnresolvedError(str(exc)) from exc
    return got.host, got.port


def address(luthen: Path) -> tuple[str, int]:
    """Return `(host, port)` for vmagent-http, or raise UnresolvedError with the reply."""
    return resolve(VMAGENT, luthen)
