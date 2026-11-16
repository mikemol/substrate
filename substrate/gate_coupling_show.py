# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Print the git-coupling census over the pre-commit hook.

The CLI over `substrate.gate_coupling`. Split for the reason its siblings are: the reader
is importable by a caller that has already decided what to ask, and the dispatch is a
separate job with its own failure modes.

⚑ THE QUESTION IT ANSWERS IS A MIGRATION PRECONDITION. A build system has no git, so a
gate coupled to git cannot become a build target — and until this existed the partition
had to be read by eye off the hook, which is the judgement-in-the-turn shape the standing
rule refuses.
"""

from __future__ import annotations

import sys

from substrate import gate_coupling

_USAGE = """\
usage: gate_coupling_show.py [--triggers]

Report which pre-commit hook lines are coupled to git, and how.

  --triggers   print only the staged-path regexes the conditional gates key on

⚑ THIS READS THE HOOK, NOT THE GATES. A gate whose own body shells out to git is
  invisible here — a fact about the reader, not an absence.
"""


def main(argv: list[str]) -> int:
    """Print the coupling census, or the trigger patterns alone."""
    if "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0
    unknown = [a for a in argv if a != "--triggers"]
    if unknown:
        sys.stderr.write(f"gate_coupling_show: unrecognised argument(s): {' '.join(unknown)}\n")
        sys.stderr.write(_USAGE)
        return 2
    if "--triggers" in argv:
        pats = gate_coupling.triggers()
        for pat in pats:
            sys.stdout.write(pat + "\n")
        sys.stdout.write(f"{len(pats)} staged-path trigger(s)\n")
        return 0
    sys.stdout.write(gate_coupling.render() + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
