# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""THE declaration shape for a CLI mode — promoted into the package, typed.

⚑⚑ THE STANDARD, AND WHY IT IS ONE (operator, 2026-08-23: *"that farm.py-inspired model is THE
INTENDED, SHOULD-BE-STANDARDIZED shape"*). A tool's modes were declared five different ways — a
module docstring, an argparse `options:` block, a `_MODES` tuple of `(flag, gloss)` pairs, a usage
string printed from inside `__main__`, and this. Five shapes means five things a reader must know to
ask *"what modes does this tool have"*, and `toolmodes` had to learn all five before it could
answer. **Consistency IS the deliverable**; the extra fields are what make consistency worth having.

⚑ THE MODEL IS `Arm(key, file, find, replace, expect, why)` FROM GCALCULUS `farm.py`, and its
load-bearing property is that **the declared field is one a discriminator can CHECK**. An `Arm`
names the message its mutation must provoke, so an Arm that stops biting is VACUOUS and detectably
so. A `Mode` declares that its branch consumes `scan()` and therefore owes an incomplete-scan
report — and `check_mode_contracts.py` (pre-commit gate, Phase A) runs the discriminator. A mode
claiming a contract it does not honour is a GATE FAILURE, not a code-review note.

⚑⚑⚑ PROMOTED FROM `scripts/climode.py`, AND THE PROMOTION IS THE POINT RATHER THAN A RELOCATION.
Its original home records living in `scripts/` because the four rosters awaiting conversion were in
`jea/metalanguage/` and importing from `scratch/` there would add a runtime coupling. That reasoning
was about `scratch/`; it does not license a module the whole corpus depends on being unreachable by
a normal import. MEASURED: `module_importers climode` reports **14 bare sites beside 0 dotted**, and
its own reader flags the consequence — *"a bare site names this module by its leaf alone, so it
resolves only under a `sys.path` insert and FAILS for an adopter importing the installed wheel."*
So every consumer pays with path surgery, and the declaration authority is the one module that
cannot be reached the way the repo's own rules require.

⚑⚑ AND THE STANDING RULE IS WHAT FORCED THE FIX RATHER THAN ANOTHER INSERT (operator: *"NOO. No
sys.path modification"*, and then *"drain the thing that's blocking you"*). A fifteenth
`sys.path.insert` would have been consistent with the other fourteen and would have deepened the
defect by one. **The blocker was the packaging, so the packaging is what moved.**

⚑ WHAT THIS MODULE DELIBERATELY DOES NOT DO. It does not parse argv, dispatch, or print usage. A
declaration that also executed would be satisfied by its own execution — the same reason
`Mode.scans` is declared rather than inferred. Tools keep their own dispatch; what they share is
the SHAPE of the claim they make about it.
"""

from __future__ import annotations

from dataclasses import dataclass

# The key a POSITIONAL invocation is filed under. ⚑ KEYED APART FROM THE FLAGS so it is never
# compared against argv as though it were one — a roster that stored it as a flag would try to
# match a bare operand spelling against a `-`-prefixed token and silently never fire.
POSITIONAL = "(positional)"


@dataclass(frozen=True, slots=True)
class Mode:
    """One CLI mode's argument shape AND the reporting contracts it owes.

    Fields, and which are checkable by what:

      operand  the token the flag itself consumes (None = nullary). DERIVABLE from the dispatch,
               and `pycodemod --declare-modes` derives it — the one field a migration can fill in
               mechanically.
      paths    the mode also takes a trailing path population.
      opts     the modifier flags THIS mode accepts, so a modifier is owned by one mode rather
               than being globally true.
      scans    the verdict rests on a corpus `scan()`, so the branch MUST report what it could not
               read. Checked by `scan_contract`.
      writes   WHICH ARTIFACT KINDS this mode mutates — a tuple of keys from the `struct-tools`
               artifact table (`.py`, `.md`, `.bib`, `.agda`, `store`, …), empty for a pure read.
               Checked against the `--apply`/`--dry-run` refusal convention.
      why      the `Arm.why` field, in the reader's words.

    ⚑⚑ `scans` AND `writes` ARE DECLARED, NEVER INFERRED, AND THAT IS THE WHOLE DESIGN. A contract
    read out of the body would be satisfied BY the body by construction: it could never fail, so it
    could never find anything. The derivers can only report the spellings they already know, which
    is exactly what made them incomplete — a flag absent from a declaration is absent VISIBLY, and
    the gate says so.

    ⚑ WHAT A MISSING DECLARATION COSTS, MEASURED. The entry point resolves operand arity from the
    roster, so an undeclared mode makes the arg-stripper guess: `--key --archive f.py` CRASHED
    because `--key`'s operand was bound as a tarball path. The other direction is worse — a
    DECLARED-but-never-dispatched row is a promise the CLI does not keep and still feeds arity
    resolution.

    ⚑⚑ A BOOLEAN CANNOT SAY WHAT `writes` SAYS, AND THE DIFFERENCE IS THE WHOLE POINT (operator,
    2026-08-23: *"it matters WHAT you're mutating; a tool might read two things and only mutate one
    of them."*). `toolmodes --sync` reads every tool's output and writes ONE markdown block;
    `sppf_db --project-core` reads `.agdai` and writes the STORE. `mutates=True` collapses both into
    one undifferentiated bit — unrankable. And the kinds are not invented here: they are keys of the
    artifact→tool table that `hook_structural_query.routes()` already parses, so a mode declaring it
    writes `.md` inside a tool that claims no `.md` artifact is a DETECTABLE LIE.
    """

    operand: str | None = None
    paths: bool = False
    opts: tuple[str, ...] = ()
    scans: bool = False
    writes: tuple[str, ...] = ()
    why: str = ""

    @property
    def mutates(self) -> bool:
        """Whether this mode writes anything at all. DERIVED from `writes`, never stored.

        ⚑ THE BOOLEAN IS A PROJECTION OF THE TARGET SET, NOT A PEER FIELD. Storing both would be
        two spellings of one fact that can disagree — `census-keyed-on-one-spelling`. Ask `writes`
        for WHAT; ask this for WHETHER, and they cannot drift.
        """
        return bool(self.writes)


def split_flag(spelling: str) -> tuple[str, str | None]:
    """Split `"--sample REL [N]"` into `("--sample", "REL [N]")`; `"--census"` into `(…, None)`.

    ⚑⚑ THE TUPLE ROSTERS ENCODE ARITY IN THE FLAG STRING, AND A NAIVE LIFT DROPS IT. `_MODES`
    entries are written `("--core PATH", "…")` — the operand is real, declared, and carried in
    PROSE inside the key. A `{flag: Mode(why=gloss)}` comprehension would produce a roster whose
    keys are `"--core PATH"` (matching no argv token) and whose arity is silently `None`. That is a
    MIGRATION THAT LOSES A FIELD THE OLD SHAPE HAPPENED TO CARRY — worse than the defect it fixes,
    because the new shape then reads as authoritative about arity it never learned.

    ⚑ SO THE PROSE IS PARSED, NOT DISCARDED. Everything after the first space is the operand
    spelling, kept VERBATIM (`"REL [N]"`, `"{--dry-run|--apply}"`) rather than normalised to a
    name — the spelling is what a reader needs, and inventing a canonical form here would be a
    second authority over what the dispatch already accepts.
    """
    spelling = spelling.strip()
    if " " not in spelling:
        return spelling, None
    flag, operand = spelling.split(" ", 1)
    return flag, operand.strip() or None


def from_pairs(pairs: list[tuple[str, str]]) -> dict[str, Mode]:
    """Lift a `[(spelling, gloss)]` tuple-roster into `{flag: Mode}`.

    ⚑ THE MIGRATION PATH FOR THE FOUR TUPLE ROSTERS, AND IT IS DELIBERATELY LOSSY UPWARD. A
    `(spelling, gloss)` pair carries two of `Mode`'s six fields — `operand` (via `split_flag`) and
    `why` — so this fills those and leaves the rest at their defaults. Those defaults are CLAIMS
    the gate will hold the tool to: `scans=False` says *"this mode's verdict does not rest on a
    scan"*, `writes=()` says *"this mode mutates nothing"*, and if either is wrong the
    discriminator says so.

    ⚑ SO THIS IS A STARTING POINT, NOT A CONVERSION. A roster lifted through here and never
    revisited has traded five shapes for one — which is the point, and consistency is the
    deliverable — but has not yet declared anything the old shape could not. The gate is what turns
    the second half from optional into owed.
    """
    out: dict[str, Mode] = {}
    for raw, gloss in pairs:
        spelling = raw.strip()
        # ⚑ A NON-FLAG ENTRY IS THE POSITIONAL INVOCATION — keyed apart so it is never compared
        # against argv as if it were a flag. See `POSITIONAL`.
        if not spelling.startswith("-"):
            out[POSITIONAL] = Mode(operand=spelling, paths=True, why=gloss)
            continue
        flag, operand = split_flag(spelling)
        out[flag] = Mode(operand=operand, why=gloss)
    return out
