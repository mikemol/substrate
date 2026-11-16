#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the kind parser, and pin that the REFUSAL MENU still names the falsifiable kinds.

⚑⚑⚑ THE MENU IS CASED BECAUSE ITS OMISSION IS MEASURED, NOT HYPOTHETICAL. The refusal once
listed only `standing`, `unwitnessed` and `mode:`, and the census at that moment read 150 of
163 witnesses `standing`. An agent that guessed a kind wrong was handed a menu missing both
falsifiable options and picked the one that always passes. So the cases assert every kind is
NAMED and that `standing` is named WITH its condition — a menu that lists it bare is the
defect restored.

⚑⚑ AND THE ORDER IS ASSERTED, NOT JUST THE MEMBERSHIP. Listing `standing` first would satisfy
a presence check while restoring the failure mode: the default becomes the residue of reading
order. The case compares indices, which is the same lesson gate-G52 taught about a sample
placed under the wrong count.

⚑ THE ONE-SHELL-WORD HAZARD SHIPPED ONCE AND IS CASED IN BOTH SPELLINGS — a quoted command and
a comma-separated one must parse identically, because being told to quote it only helps the
filer who reads the refusal, not the one who already typed it.
"""

from __future__ import annotations

import sys

from substrate import finding_kindspec

Case = tuple[str, bool]


def _menu_cases() -> list[Case]:
    """Return the cases pinning that the refusal names every kind, in the right order."""
    spec, refusal = finding_kindspec.parse("nonsense-kind")
    return [
        ("an unknown kind is refused", spec is None),
        # ⚑ EVERY KIND NAMED. The measured defect was an INCOMPLETE menu, not a missing one.
        ("...and the menu names selftest", "selftest:<command>" in refusal),
        ("...and refuses", "refuses:<command>" in refusal),
        ("...and mode", "mode:TOOL:FLAG" in refusal),
        ("...and unwitnessed", "unwitnessed" in refusal),
        ("...and standing", "standing" in refusal),
        # ⚑⚑ ORDER, NOT JUST MEMBERSHIP. `standing` last, with its condition attached, is what
        #   makes choosing it a decision rather than the residue of a short list.
        ("the falsifiable kinds are listed BEFORE standing",
         refusal.index("selftest:<command>") < refusal.index("  standing")),
        ("...and standing carries the condition that makes it legitimate",
         "LEGITIMATE ONLY" in refusal and "measured FACT" in refusal),
        # ⚑ AND THE REASON refuses: EXISTS IS STATED, since that is the kind a filer reaches
        #   for least and needs most — `standing` cannot notice a revert.
        ("...and refuses names why standing cannot replace it",
         "cannot notice a revert" in refusal),
    ]


def _command_cases() -> list[Case]:
    """Return the cases pinning both command spellings and the empty-command refusal."""
    quoted, _ = finding_kindspec.parse("selftest:python3 -m substrate.finding_kinds_selftest")
    commas, _ = finding_kindspec.parse("selftest:python3,-m,substrate.finding_kinds_selftest")
    refusing, _ = finding_kindspec.parse("refuses:python3 tool.py --bad")
    empty_spec, empty_refusal = finding_kindspec.parse("selftest:")
    return [
        ("a quoted command parses to its words",
         quoted is not None and quoted.cmd[0] == "python3"),
        # ⚑ BOTH SPELLINGS MUST AGREE, or the fallback for an unquoted filer is a second
        #   behaviour rather than a second spelling.
        ("a comma-separated command parses identically",
         quoted is not None and commas is not None and quoted.cmd == commas.cmd),
        ("selftest picks the selftest builder",
         quoted is not None and quoted.builder == "_selftest"),
        ("refuses picks the refuses builder",
         refusing is not None and refusing.builder == "_refuses"),
        # ⚑ THE MEASURED HAZARD: an unquoted space donates the command to the note, leaving
        #   the kind bare — which ran a tool with no arguments and exited 2 on its usage.
        ("an empty command is REFUSED rather than registered bare", empty_spec is None),
        ("...and the refusal names the quoting fix", "QUOTE it" in empty_refusal),
        ("...and names the comma fallback too", "comma-separated" in empty_refusal),
    ]


def _mode_cases() -> list[Case]:
    """Return the cases pinning the three-part mode kind."""
    good, _ = finding_kindspec.parse("mode:fix_notinscope.py:--summary")
    short, short_why = finding_kindspec.parse("mode:onlytool")
    hollow, _ = finding_kindspec.parse("mode:tool:")
    return [
        ("a well-formed mode kind parses", good is not None),
        ("...carrying its tool", good is not None and good.tool == "fix_notinscope.py"),
        ("...and its flag", good is not None and good.flag == "--summary"),
        ("a two-part mode kind is refused", short is None),
        ("...and the refusal shows the required shape", "mode:TOOL:FLAG" in short_why),
        # ⚑ AN EMPTY HALF IS AS BROKEN AS A MISSING ONE, and only checking the part count
        #   would let `mode:tool:` through to build a witness probing an empty flag.
        ("a mode kind with an empty flag is refused", hollow is None),
    ]


def _bare_cases() -> list[Case]:
    """Return the cases pinning the two kinds that carry no command."""
    standing, _ = finding_kindspec.parse("standing")
    unwitnessed, _ = finding_kindspec.parse("unwitnessed")
    probed, _ = finding_kindspec.parse("refuses:python3 tool.py")
    moded, _ = finding_kindspec.parse("mode:tool.py:--flag")
    return [
        ("standing parses to its builder",
         standing is not None and standing.builder == "_standing"),
        ("unwitnessed parses to its builder",
         unwitnessed is not None and unwitnessed.builder == "_unwitnessed"),
        # ⚑ THE `probed` PREDICATE EXISTS SO A CALLER NEVER RE-TESTS THE KIND NAME. Spelling
        #   that rule at each site is how one site ends up disagreeing with the others.
        ("a bare kind reports it carries no polarity to probe",
         standing is not None and not standing.probed),
        ("a command kind reports that it does", probed is not None and probed.probed),
        # ⚑ AND `mode:` IS PROBED DESPITE CARRYING NO COMMAND — its reader runs toolmodes, so a
        #   predicate keyed only on `cmd` would silently exempt the kind gate-G63 just armed.
        ("a mode kind is probed too, though it carries no argv",
         moded is not None and moded.probed and not moded.cmd),
    ]


def _key_cases() -> list[Case]:
    """Return the cases pinning the key alphabet, which is a contract with another tool."""
    return [
        ("an ordinary slug key is accepted",
         finding_kindspec.bad_key("gate-G63-the-mode-polarity-arm-is-built") == ""),
        ("an underscore is accepted", finding_kindspec.bad_key("tmi_F6") == ""),
        ("an empty key is refused", finding_kindspec.bad_key("") != ""),
        # ⚑ THE ALPHABET IS NOT STYLE. A key outside it makes a witness that exists, works,
        #   and is INVISIBLE to bibstruct's resolver regex — the refusal it must clear.
        ("a key with a colon is refused", finding_kindspec.bad_key("gate:G1") != ""),
        ("a key with a space is refused", finding_kindspec.bad_key("gate G1") != ""),
        ("...and the refusal says why the alphabet matters",
         "bibstruct" in finding_kindspec.bad_key("gate G1")),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (_menu_cases() + _command_cases() + _mode_cases()
             + _bare_cases() + _key_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_kindspec: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
