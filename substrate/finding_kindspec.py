#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Parse a `--register` KIND argument into a builder plus its arguments, or a refusal.

⚑⚑⚑ THE SIXTH DRAIN UNIT, AND IT IS THE HALF OF `register` THAT IS PURE. `register` does two
things: it PARSES a kind string, and it SPLICES source text into the roster. The second is
coupled to the file by nature; the first touches nothing — no filesystem, no roster, no
`__file__` — and is where every refusal a filer actually reads lives. Separating them is what
lets the menu be cased without writing to a 7,054-line file the gate refuses.

⚑⚑⚑ THE REFUSAL MENU IS THE MOST LOAD-BEARING TEXT IN THE LEDGER, AND IT ONCE OMITTED THE TWO
FALSIFIABLE KINDS. That omission is the measured reason `standing` became the default: at the
moment it was found, the census read 150 of 163 witnesses `standing`, against 8 `unwitnessed`,
3 `mode:` and 2 `selftest:`. The docstring named `selftest:` and the usage line named it; THIS
refusal did not, so an agent that guessed wrong was told the menu was *"standing, unwitnessed,
mode:"* and picked the one that always passes. **A tool's self-description at the point of
refusal outranks its docstring, because the refusal is what arrives at the moment of need.**

⚑⚑ SO THE ORDER IS DELIBERATE AND IS PART OF THE CONTRACT. The falsifiable kinds come FIRST
and `standing` is listed WITH the condition under which it is legitimate, so choosing it is a
choice rather than the residue of a short menu.

⚑ AND THE ONE-SHELL-WORD HAZARD IS CASED BECAUSE IT SHIPPED. `KIND` is a single argv element,
so `selftest:scripts/cgroup-scope selftest` puts only `scripts/cgroup-scope` in the kind and
silently donates the subcommand to the NOTE. The witness then ran the tool BARE, which printed
usage and exited 2 — caught only because the verdict contradicted the finding it was filed to
hold. A command that parses to nothing is refused, and the refusal names both fixes.
"""

from __future__ import annotations

from dataclasses import dataclass

# The two kinds that carry no command and therefore no polarity.
BARE: tuple[str, ...] = ("standing", "unwitnessed")

# ⚑ A KEY IS EMITTED AS SOURCE AND READ BACK BY A REGEX IN BIBSTRUCT'S RESOLVER, so its
#   alphabet is part of the contract rather than a style preference.
KEY_CHARS = "-_"


@dataclass(frozen=True, slots=True)
class Spec:
    """One parsed kind: which builder to emit, and the arguments it takes.

    ⚑ `cmd` IS EMPTY FOR A BARE KIND, and that is how a caller knows there is no polarity to
    probe — rather than by re-testing the kind name at each site.
    """

    builder: str
    cmd: tuple[str, ...]
    tool: str
    flag: str

    @property
    def probed(self) -> bool:
        """Whether this kind runs a command whose polarity can be checked at filing time."""
        return bool(self.cmd) or self.builder == "_mode_undocumented"


def _split_command(raw: str) -> list[str]:
    """Split a command that may be space- or comma-separated.

    ⚑ COMMAS ARE ACCEPTED BECAUSE THE SHELL EATS SPACES. An unquoted space ends the KIND argv
    element, so a filer who forgets the quotes needs a spelling that survives — and being told
    to quote it only helps the filer who reads the refusal, not the one who already typed it.
    """
    parts = raw.split(",") if "," in raw else raw.split()
    return [word for word in parts if word]


def _menu(kind: str) -> str:
    """Return the four-kind menu, which is the only kind documentation most filers read."""
    return (f"unknown kind {kind!r}. FOUR KINDS, and the kind picks the EXIT CODE — prefer a "
            "FALSIFIABLE one:\n"
            "  selftest:<command>   holds when the command exits 0 — a mechanism WORKS. "
            "Quote it.\n"
            "  refuses:<command>    holds when the command exits NON-ZERO — an installed "
            "REFUSAL is still installed. Quote it. Use this for any 'the repair landed' "
            "finding whose repair is a refusal; `standing` cannot notice a revert.\n"
            "  mode:TOOL:FLAG       holds while the flag is DOCUMENTED (roster-vs-dispatch, "
            "via toolmodes --divergence). NOT a test that anything works.\n"
            "  unwitnessed          reports 2. The honest kind for a judgement or a lesson "
            "no command can distinguish true from false.\n"
            "  standing             holds at 0 unconditionally. LEGITIMATE ONLY for a "
            "measured FACT about how something behaves, never for a claim that a repair "
            "landed — its witness asserts the finding is still RECORDED, and no change to "
            "the code can flip it.")


def parse(kind: str) -> tuple[Spec | None, str]:
    """Return `(spec, "")` for a well-formed kind, or `(None, refusal)`.

    ⚑ THE REFUSAL IS RETURNED, NEVER RAISED. A tool whose main job is refusing must be able to
    assert on its own refusals — the origin's `main` raised `SystemExit` from inside a branch
    and its suite aborted at the first refusal, leaving later cases as dead text under a score
    that read as full coverage.
    """
    if kind.startswith("mode:"):
        parts = kind.split(":")
        if len(parts) != 3 or not parts[1] or not parts[2]:  # noqa: PLR2004 — TOOL:FLAG is 3
            return None, ("mode kind must be mode:TOOL:FLAG, e.g. "
                          "mode:fix_notinscope.py:--summary")
        return Spec("_mode_undocumented", (), parts[1], parts[2]), ""
    for verb in ("selftest", "refuses"):
        if not kind.startswith(verb + ":"):
            continue
        cmd = _split_command(kind.split(":", 1)[1])
        if not cmd:
            return None, (f"{verb} kind must be {verb}:<command>, e.g. "
                          f'"{verb}:scripts/cgroup-scope selftest" (QUOTE it — an unquoted '
                          "space ends the KIND argument and the rest becomes the note), or "
                          "pass it comma-separated")
        return Spec(f"_{verb}", tuple(cmd), "", ""), ""
    if kind in BARE:
        return Spec(f"_{kind}", (), "", ""), ""
    return None, _menu(kind)


def bad_key(key: str) -> str:
    """Return a refusal if `key` cannot survive the round trip, else the empty string.

    ⚑⚑ THE ALPHABET IS A CONTRACT WITH A READER IN ANOTHER TOOL. The key is emitted as source
    and `bibstruct --add` resolves `check=item:<key>` against it with a regex; a character
    outside the slug alphabet makes a witness that exists, works, and is INVISIBLE to the one
    reader whose refusal it has to clear.
    """
    if not key:
        return "a key is required — it names the finding in both the roster and the bib"
    if not all(c.isalnum() or c in KEY_CHARS for c in key):
        return (f"key {key!r} must be [A-Za-z0-9-_] — it is emitted as source and read back "
                "by a regex in bibstruct's witness resolver")
    return ""
