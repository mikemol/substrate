# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Build the elaborated-type cache by driving `agda --interaction-json`.

Write a wrapper module importing every `Substrate.*` module, then feed agda one
`Cmd_load` plus two `Cmd_show_module_contents_toplevel` per module (AsIs, then
Normalised) and parse the JSON replies. `substrate.agda_type_cache` owns reading
what this writes; the split is the consumer's — `scratch/findings.py` uses the read
side alone and never runs agda.

⚑ THE WRAPPER USES PLAIN `import M`, NEVER `open import M public`, AND THE
DIFFERENCE IS LOAD-BEARING. A plain import typechecks each module transitively
without bringing its names into the wrapper's scope. Several Substrate modules
define the same name (`Fiber` appears in multiple cocycle files), so a public open
raises "Multiple definitions" and the whole batch fails.
`Cmd_show_module_contents_toplevel` still resolves fully-qualified names, so nothing
is lost by keeping the scope empty.

⚑⚑ THE WRAPPER GOES WHEREVER TMPDIR SAYS, NOT `/tmp`. The origin hardcoded
`/tmp/AgdaQueryAll.agda`; on this box `/tmp` is a small tmpfs shared with the editor
and the agent harness, and it has FILLED TWICE — after which children fail at spawn
with ENOSPC, reading as "the tool is broken" rather than "the volume is full"
(`worklist_engine.scratch_root` records that incident and owns the general form of
this choice).

⚑⚑⚑ AND THE AGDA BINARY IS RESOLVED, NOT NAMED. `subprocess.run(["agda", ...])`
leaves the interpreter's identity to `$PATH` at call time — the same
proxy-for-the-subject shape that makes a cached verdict unsound when the tool moves
underneath it. `resolve_agda` returns the absolute path actually selected, so a
caller can record WHICH binary produced a cache rather than only that one did.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

from substrate import json_reply
from substrate.agda_type_cache import AGDA_ROOT

if TYPE_CHECKING:
    from pathlib import Path

WRAPPER_NAME = "AgdaQueryAll"
AGDA_TIMEOUT_S = 600


class AgdaMissingError(RuntimeError):
    """Raised when no `agda` executable is on PATH."""


def resolve_agda() -> str:
    """Return the absolute path of the `agda` that would run, or raise.

    ⚑ RESOLVING IS NOT PINNING, and this does only the first. It fixes WHICH binary
    this process invokes and makes that path reportable; it says nothing about
    whether the binary matches the one that built an existing cache. Folding the
    binary's identity into the cache is the separate work that would close that gap.
    """
    found = shutil.which("agda")
    if found is None:
        msg = "no `agda` on PATH — cannot build the elaborated-type cache"
        raise AgdaMissingError(msg)
    return found


def wrapper_text(modules: list[tuple[str, Path]]) -> str:
    """Return the wrapper module that plain-imports every discovered module."""
    lines = [
        "{-# OPTIONS --safe --without-K #-}",
        f"module {WRAPPER_NAME} where",
        "",
    ]
    lines.extend(f"import {mod}" for mod, _ in modules)
    return "\n".join(lines) + "\n"


def batch_script(wrapper: Path, modules: list[tuple[str, Path]]) -> str:
    """Return the IOTCM batch: one load, then AsIs for every module, then Normalised.

    ⚑ ORDER IS THE ONLY KEY TYING A REPLY BACK TO ITS MODULE. Agda's replies carry
    no module name, so the parsed payloads match by POSITION — which is why both
    passes emit modules in one fixed order and why a caller must never reorder one
    pass alone.
    """
    wp = str(wrapper)
    inc = f'["-i", "{AGDA_ROOT}", "-i", "{wrapper.parent}"]'
    lines = [f'IOTCM "{wp}" None Direct (Cmd_load "{wp}" {inc})']
    for level in ("AsIs", "Normalised"):
        lines.extend(
            f'IOTCM "{wp}" None Direct (Cmd_show_module_contents_toplevel {level} "{mod}")'
            for mod, _ in modules
        )
    return "\n".join(lines) + "\n"


def parse_module_contents(output: str) -> tuple[list[list[object]], list[str]]:
    """Return the `ModuleContents` payloads in reply order, plus any error messages.

    ⚑ ERRORS COME BACK BESIDE THE PAYLOADS RATHER THAN RAISING, because a batch that
    reports errors can still have produced usable contents for the modules that did
    load — and a caller that cannot see both cannot tell a partial result from a
    total one.
    """
    payloads: list[list[object]] = []
    errors: list[str] = []
    for raw in output.splitlines():
        line = raw.replace("JSON> ", "").strip()
        if not line.startswith("{"):
            continue
        reply = json_reply.decode(line)
        if reply is None:
            continue
        info = json_reply.field(reply, "info")
        kind = json_reply.text_field(info, "kind")
        if kind == "ModuleContents":
            payloads.append(json_reply.list_field(info, "contents"))
        elif kind == "Error":
            error = json_reply.field(info, "error")
            errors.append(json_reply.text_field(error, "message"))
    return payloads, errors


def run_agda(wrapper: Path, batch: str) -> subprocess.CompletedProcess[str]:
    """Drive the resolved agda over the batch, capturing both streams."""
    return subprocess.run(  # noqa: S603
        [
            resolve_agda(),
            "--interaction-json",
            "-i",
            str(AGDA_ROOT),
            "-i",
            str(wrapper.parent),
        ],
        input=batch,
        capture_output=True,
        text=True,
        timeout=AGDA_TIMEOUT_S,
        check=False,
    )
