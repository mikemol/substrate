# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Read a generated makefile structurally: its targets, their prerequisites, its variables.

⚑⚑⚑ THE BUILD'S CENTRAL ARTIFACT HAD NO READER, AND THAT IS WHY A QUESTION WENT UNANSWERED.
`agda/Flat.mk` is generated, ~21k lines, and nothing in the toolkit parses it: `toolmodes --find
makefile` returns the generator and three tools that WRITE recipes, no reader. So *"is there a
target for this module"* had no owning tool — `Read` refuses the file on size, the structural
hook refuses `grep` on it, and `struct-tools` has no row for `.mk`. A missing mode is WORK.

⚑⚑ AND THE ANSWER MATTERS BECAUSE A COUNT CANNOT SUBSTITUTE FOR IT. The generator reports its
module total as the length of its own walk, so that figure reads identically whether a given
file is a target or not. Asking the makefile what it actually contains is the only reading that
distinguishes *"built"* from *"outside the enumeration root"* — the distinction that hid a
top-level module from three correlated instruments at once.

⚑ THIS PARSES A GENERATED SUBSET, AND SAYS SO. It handles the shapes this repo's generator
emits — `NAME := value`, `NAME ?= value`, `target: prereqs`, pattern rules, `.PHONY` — and
deliberately not the full GNU make grammar: no `include`, no conditionals, no function
expansion. A parser claiming more than it implements is worse than one that states its subset,
because the excess reads as coverage.

⚑⚑ A VARIABLE IS RETURNED UNEXPANDED. `AGDAI := $(patsubst %,$(BUILD)/%.agdai,…)` is a
DERIVATION, and expanding it here would mean re-implementing make's substitution — a second
authority for what the build computes, differing from the first exactly where it matters.
A caller that wants the expansion must ask make; a caller that wants to know what was WRITTEN
gets what was written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# `NAME := value` / `NAME ?= value` / `NAME = value` at column zero.
_ASSIGN = re.compile(r"^([A-Za-z_][\w.]*)\s*(:=|\?=|=)\s*(.*)$")

# `target [target …]: [prereq …]` at column zero. ⚑ THE `:=` CASE IS EXCLUDED by requiring the
# colon not be followed by `=`; without it every assignment parses as a target named for its
# variable, which is a plausible-looking rule set that is entirely wrong.
_RULE = re.compile(r"^([^\t#=][^:=]*):(?!=)\s*(.*)$")

# A recipe line — a tab, per make's own rule. Nothing else is a recipe, which is why the
# distinction is lexical rather than positional.
_RECIPE = "\t"


@dataclass(frozen=True, slots=True)
class Rule:
    """One target, what it depends on, and the recipe lines under it."""

    target: str
    prereqs: tuple[str, ...]
    recipe: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_pattern(self) -> bool:
        """Whether this is a pattern rule rather than a rule for one named target."""
        return "%" in self.target


@dataclass(frozen=True, slots=True)
class Makefile:
    """A parsed makefile: its variables, its rules, and what it declares phony."""

    variables: dict[str, str]
    rules: tuple[Rule, ...]
    phony: frozenset[str]

    def rules_for(self, target: str) -> tuple[Rule, ...]:
        """Return every rule whose target is exactly `target`.

        ⚑ EVERY RULE, NOT THE FIRST. make allows a target to accumulate prerequisites across
        several rules, and returning one would silently answer a different question than the
        one asked — what a target depends on is the UNION.
        """
        return tuple(r for r in self.rules if r.target == target)

    def targets_matching(self, needle: str) -> tuple[str, ...]:
        """Return the targets whose name contains `needle`, in file order.

        ⚑ A SUBSTRING SEARCH, AND IT REPORTS WHAT IT FOUND rather than deciding. A module named
        as a suffix of another would match both; the caller sees both and can tell.
        """
        return tuple(r.target for r in self.rules if needle in r.target)


def _split(text: str) -> list[str]:
    """Return logical lines, joining backslash continuations.

    ⚑ A CONTINUATION IS PART OF ITS LINE. A prerequisite list wrapped across lines would
    otherwise parse as a rule plus a fragment, and the fragment's leading token would read as
    a target — inventing rules that do not exist.
    """
    out: list[str] = []
    buf = ""
    for raw in text.split("\n"):
        if raw.endswith("\\"):
            buf += raw[:-1] + " "
            continue
        out.append(buf + raw)
        buf = ""
    if buf:
        out.append(buf)
    return out


def assignment(line: str) -> tuple[str, str] | None:
    """Return `(name, value)` when `line` assigns a variable, else None.

    ⚑ THE NARROWING HAPPENS HERE, ONCE. `Match.group` is untyped, so a caller using its result
    carries `Any` into every expression downstream — the same boundary discipline the dynamic
    call sites use, applied to the regex layer.
    """
    match = _ASSIGN.match(line)
    if match is None:
        return None
    return str(match.group(1)), str(match.group(3)).strip()


def rule_heads(line: str) -> tuple[list[str], tuple[str, ...]] | None:
    """Return `(targets, prereqs)` when `line` opens a rule, else None."""
    match = _RULE.match(line)
    if match is None:
        return None
    return str(match.group(1)).split(), tuple(str(match.group(2)).split())


def parse(text: str) -> Makefile:
    """Parse makefile `text` into variables, rules and phony targets."""
    variables: dict[str, str] = {}
    rules: list[Rule] = []
    phony: set[str] = set()
    recipe: list[str] = []
    pending: list[Rule] = []

    def flush() -> None:
        """Attach the accumulated recipe to the rules it belongs to."""
        if pending:
            rules.extend(Rule(r.target, r.prereqs, tuple(recipe)) for r in pending)
        pending.clear()
        recipe.clear()

    for line in _split(text):
        if line.startswith(_RECIPE):
            if pending:
                recipe.append(line[1:])
            continue
        flush()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        assign = assignment(line)
        if assign is not None:
            variables[assign[0]] = assign[1]
            continue
        heads = rule_heads(line)
        if heads is None:
            continue
        targets, prereqs = heads
        if targets == [".PHONY"]:
            phony.update(prereqs)
            continue
        pending.extend(Rule(t, prereqs) for t in targets)
    flush()
    return Makefile(variables=variables, rules=tuple(rules), phony=frozenset(phony))


def read(path: Path) -> Makefile:
    """Parse the makefile at `path`."""
    return parse(path.read_text(encoding="utf-8", errors="replace"))


def modules(mk: Makefile) -> tuple[str, ...]:
    """Return the modules the makefile's `MODULES` variable declares.

    ⚑ THE DECLARED LIST, NOT THE RULE SET. `MODULES` is what the generator WROTE; the compile
    rules are what it EMITTED from that list. They should agree, and asking them separately is
    what makes a disagreement visible instead of assumed away.
    """
    return tuple(mk.variables.get("MODULES", "").split())


def has_target(mk: Makefile, name: str) -> bool:
    """Report whether `name` is an explicit (non-pattern) target.

    ⚑ PATTERN RULES ARE EXCLUDED DELIBERATELY. `$(BUILD)/%.ingested` would match almost any
    query, so counting it would answer "yes" for a module that has no rule of its own — the
    false positive that makes a build reader useless for the one question it exists to answer.
    """
    return any(r.target == name and not r.is_pattern for r in mk.rules)


USAGE = """\
make_rules.py — structural reader for the GENERATED makefiles (`.mk`).

  make_rules.py --summary <file>         rules, variables, phony, declared modules
  make_rules.py --modules <file>         what MODULES declares, one per line
  make_rules.py --target <file> <name>   the rules for one target, with prerequisites
  make_rules.py --grep <file> <needle>   targets whose NAME contains <needle>
  make_rules.py --var <file> <name>      one variable's value, UNEXPANDED
  make_rules.py --selftest               the cases

⚑ A VARIABLE IS RETURNED AS WRITTEN. `$(patsubst …)` is a DERIVATION; expanding it here
  would re-implement make's substitution as a second authority. Ask make for the value,
  ask this for the text.

⚑ PARSES THE GENERATED SUBSET — assignments, rules, pattern rules, `.PHONY`, backslash
  continuations. NOT `include`, conditionals, or function expansion. A parser claiming
  more than it implements reads as coverage.

⚑ `agda/Makefile` HAS NO SUFFIX, so the structural-query gate does not route to this tool
  for it — this reader parses it fine, the routing misses it. See the struct-tools skill.
"""


def summary(mk: Makefile, _arg: str) -> str:
    """Render the shape of one parsed makefile."""
    patterns = len([r for r in mk.rules if r.is_pattern])
    return (
        f"rules {len(mk.rules)} ({patterns} pattern) · "
        f"variables {len(mk.variables)} · phony {len(mk.phony)}\n"
        f"MODULES declares {len(modules(mk))}\n"
    )


def module_list(mk: Makefile, _arg: str) -> str:
    """Render the declared module list, one per line."""
    return "".join(f"{m}\n" for m in modules(mk))


def variable(mk: Makefile, arg: str) -> str:
    """Render one variable's value, exactly as written."""
    return f"{mk.variables.get(arg, '')}\n"


def matching(mk: Makefile, arg: str) -> str:
    """Render the targets whose name contains `arg`, with a count."""
    hits = mk.targets_matching(arg)
    return "".join(f"{t}\n" for t in hits) + f"{len(hits)} target(s) matching {arg!r}\n"


def target(mk: Makefile, arg: str) -> str:
    """Render one target's rules and recipes.

    ⚑ AN ABSENT TARGET SAYS SO. Rendering nothing would read identically to a target with
    no prerequisites, which is exactly the distinction this reader exists for.
    """
    found = mk.rules_for(arg)
    if not found:
        return f"no explicit target {arg!r} in this makefile\n"
    out = ""
    for rule in found:
        out += f"{rule.target}: {' '.join(rule.prereqs)}\n"
        out += "".join(f"\t{line}\n" for line in rule.recipe)
    return out


# ⚑⚑ A DISPATCH TABLE, NOT A CHAIN OF BRANCHES — and `PLR0911` is what said so, twice. It
# fired on a combined render-and-route function, then again after splitting rendering out,
# because the split was along the wrong seam: five modes in one function is a MAP that had
# not been named. Each mode is now a function with one job, and the routing is data.
MODES = {
    "--summary": summary,
    "--modules": module_list,
    "--var": variable,
    "--grep": matching,
    "--target": target,
}


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code."""
    import sys  # noqa: PLC0415 — kept local so importing this module costs nothing
    from pathlib import Path as _Path  # noqa: PLC0415

    if "--selftest" in argv:
        from substrate import make_rules_selftest  # noqa: PLC0415

        return 0 if make_rules_selftest.selftest() else 1

    rest = [a for a in argv[1:] if not a.startswith("--")]
    flags = [a for a in argv[1:] if a.startswith("--")]
    mode = MODES.get(flags[0]) if flags else None
    if mode is None or not rest:
        sys.stdout.write(USAGE)
        return 2

    sys.stdout.write(mode(read(_Path(rest[0])), rest[1] if len(rest) > 1 else ""))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
