# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.make_rules` — the structural makefile reader.

⚑⚑⚑ THE ASSIGNMENT-VERSUS-RULE CASE IS LOAD-BEARING. `MODULES := a b c` contains a colon, so a
naive rule regex parses it as a target named `MODULES` with prerequisites `= a b c` — a
plausible-looking rule set that is entirely wrong, and one no count would catch because the
totals stay sensible. Both spellings are pinned in both directions.

⚑⚑ AND THE PATTERN-RULE EXCLUSION IS THE OTHER HALF. `$(BUILD)/%.ingested` matches almost any
query, so a reader counting it would answer "yes, there is a target" for a module that has no
rule of its own — the false positive that makes a build reader useless for the one question it
was built to answer.

⚑ THE LIVE CASE ASSERTS A CONTRAST, NOT A COUNT. A module that IS built and one that is not,
named side by side: a total over `Flat.mk` would be red the next time anyone adds a module,
while the contrast is exactly the reading the tool exists to provide.
"""

from __future__ import annotations

from substrate import corpus, make_rules

_SAMPLE = """\
# a comment
MODULES := Substrate.A Substrate.B
AGDA ?= agda
BUILD := _build/x/agda

.PHONY: all m/Substrate.A

all: $(BUILD)/Substrate/A.agdai

$(BUILD)/Substrate/A.agdai: $(AGDA_ROOT)/Substrate/A.agda
\t@mkdir -p $(@D)
\t@$(AGDA) $<
m/Substrate.A: $(BUILD)/Substrate/A.agdai

$(BUILD)/%.ingested: $(BUILD)/%.agdai
\t@touch $@
"""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    mk = make_rules.parse(_SAMPLE)

    # ── assignments are variables, NOT rules ────────────────────────────────
    # ⚑ THE COLON IN `:=` IS THE TRAP. Parsed as a rule, this yields a target named MODULES.
    check(
        "a `:=` assignment is a variable",
        passed=mk.variables.get("MODULES") == "Substrate.A Substrate.B",
    )
    check("and is NOT parsed as a target", passed=not make_rules.has_target(mk, "MODULES"))
    check("a `?=` assignment is a variable too", passed=mk.variables.get("AGDA") == "agda")

    # ── rules and their prerequisites ───────────────────────────────────────
    check(
        "a real-file rule is found", passed=make_rules.has_target(mk, "$(BUILD)/Substrate/A.agdai")
    )
    rules = mk.rules_for("m/Substrate.A")
    check(
        "an alias rule carries its prerequisite",
        passed=len(rules) == 1 and rules[0].prereqs == ("$(BUILD)/Substrate/A.agdai",),
    )

    # ── recipes attach to the rule above them ───────────────────────────────
    compiled = mk.rules_for("$(BUILD)/Substrate/A.agdai")
    check(
        "a rule's recipe lines are captured",
        passed=len(compiled) == 1 and len(compiled[0].recipe) == 2,
    )  # noqa: PLR2004
    # ⚑ A RECIPE IS A TAB, per make's own rule — lexical, not positional.
    check(
        "and the leading tab is stripped",
        passed=bool(compiled) and compiled[0].recipe[0].startswith("@mkdir"),
    )

    # ── .PHONY is a declaration, not a rule ─────────────────────────────────
    check("phony targets are collected", passed=mk.phony == {"all", "m/Substrate.A"})
    check("and .PHONY itself is not a target", passed=not make_rules.has_target(mk, ".PHONY"))

    # ── PATTERN RULES ARE NOT EXPLICIT TARGETS ──────────────────────────────
    # ⚑ THE FALSE-POSITIVE GUARD. A pattern would otherwise answer "built" for anything.
    patterns = [r for r in mk.rules if r.is_pattern]
    check("a pattern rule is recognised as a pattern", passed=len(patterns) == 1)
    check(
        "and does not count as an explicit target",
        passed=not make_rules.has_target(mk, "$(BUILD)/%.ingested"),
    )

    # ── the declared module list ────────────────────────────────────────────
    check(
        "MODULES parses into its members",
        passed=make_rules.modules(mk) == ("Substrate.A", "Substrate.B"),
    )

    # ── continuations join their line ───────────────────────────────────────
    # ⚑ Without this a wrapped prerequisite list invents a rule from its own tail.
    wrapped = make_rules.parse("t: a \\\n  b c\n")
    check(
        "a backslash continuation joins the rule",
        passed=wrapped.rules_for("t")[0].prereqs == ("a", "b", "c"),
    )

    # ── the live artifact: the question that had no owning tool ─────────────
    flat = corpus.ROOT / "agda" / "Flat.mk"
    if not flat.exists():
        check("Flat.mk is present to read", passed=False)
        return out
    live = make_rules.read(flat)
    mods = make_rules.modules(live)
    check("the generated makefile parses into many rules", passed=len(live.rules) > len(mods))
    # ⚑⚑ THE CONTRAST, NAMED. A module under the enumeration root is declared; the tree's
    # top-level module — outside that root — is not, and no target produces its interface.
    check("a module under the enumeration root is declared", passed="Substrate.Cocycle" in mods)
    check("the tree's top-level module is NOT declared", passed="Substrate" not in mods)
    check(
        "and no target builds its interface", passed=live.targets_matching("Substrate.agdai") == ()
    )

    # ── the CLI renderers, one case each ─────────────────────────────────────
    # ⚑⚑ THESE HAD NO CASES AND THE COVERAGE CENSUS COULD NOT SAY SO. It read only a `_selftest`
    # function, this suite spells its cases `_cases`, so every mode here reported as uncovered
    # for the wrong reason — and once that was fixed, four of the five were genuinely uncovered.
    # A renderer is where a reader's answer becomes the operator's, so an untested one is a
    # correct measurement rendered wrong.
    check(
        "--summary reports the rule and module counts",
        passed="MODULES declares" in make_rules.summary(live, ""),
    )
    check(
        "--var returns a variable UNEXPANDED",
        passed="$(" in make_rules.variable(live, "MODULES")
        or make_rules.variable(live, "MODULES").strip() != "",
    )
    check(
        "--grep names the targets it matched and counts them",
        passed="target(s) matching" in make_rules.matching(live, "Cocycle"),
    )
    # ⚑ AN ABSENT TARGET MUST SAY SO. Rendering nothing reads identically to a target with no
    # prerequisites, which is the one distinction this mode exists to draw.
    check(
        "--target on an absent target says so rather than rendering empty",
        passed="no explicit target" in make_rules.target(live, "Substrate.agdai"),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
