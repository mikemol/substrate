# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Parse `bibstruct`'s argv: the mode, the write target, the corpus, and the operands.

⚑⚑⚑ EVERY RULE HERE IS A RECORDED DEFECT, AND THE FILE IT COMES FROM CARRIES THE SCARS IN ITS
COMMENTS. This is argv OWNERSHIP — which token belongs to which flag — and the origin paid for it
four times: a trailing bib path appended into the previous field's VALUE, `--bib` accepted by a
read mode and silently dropped from the read set (reporting a peer's clean corpus as broken),
`--corpus` consuming greedily past the next flag so that `--bib`'s operand was eaten and the write
fell through to the DEFAULT bib, and a write verb reaching the guard but not the recogniser
because two rosters named the same set independently.

⚑⚑ THE COMMON SHAPE IS A SILENT MISDIRECTION, NOT AN ERROR. In each case the tool ran, produced a
plausible answer, and answered about the wrong thing — a false dangling report, a diff against a
file the author never named, a mode refused by a message listing only its siblings. **That is why
every rule below REFUSES rather than repairing**: a stray positional is named, not eaten.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the
per-file gate refuses every write to it, so its parse is rebuilt here whole and the origin is left
alone until it can be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from substrate import bib_modes

# The verbs that WRITE and the verbs that READ — DERIVED FROM THE ROSTER, never restated.
# ⚑⚑ THIS WAS A LITERAL TUPLE UNDER A COMMENT CLAIMING "ONE ROSTER", and the claim was false: the
# roster is `bib_modes.MODES`, and this was a second spelling of it. Measured when `--delete`
# landed there: the parser read it as a READ mode, refused `--bib`, and printed the mode as
# `None` beside a message naming only the three verbs it knew — the same defect the comment said
# it ended, one verb later. A read mode's corpus is positional, which is why the write-target flags
# are refused on them.
WRITE_MODES: tuple[str, ...] = bib_modes.WRITE_MODES
READ_MODES: tuple[str, ...] = bib_modes.READ_MODES

# The modes that take a target bib as a FLAG rather than a trailing positional.
TARGET_FLAG = "--bib"
CORPUS_FLAG = "--corpus"


@dataclass(frozen=True, slots=True)
class Refusal:
    """A parse that will not proceed, and what the caller should do instead."""

    message: str
    code: int = 2


@dataclass(frozen=True, slots=True)
class Parsed:
    """A parse that will proceed: the mode, its target, its corpus and its operands."""

    mode: str | None
    target: str | None = None
    corpus: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    rest: tuple[str, ...] = field(default_factory=tuple)

    @property
    def writes(self) -> bool:
        """Whether this mode mutates a bib."""
        return self.mode in WRITE_MODES


def known_modes() -> tuple[str, ...]:
    """Return every mode this CLI dispatches, read and write."""
    return (*READ_MODES, *WRITE_MODES, "--selftest")


def operands_after(flag: str, argv: list[str]) -> tuple[str, ...]:
    """Return the operands following `flag`, stopping at the next `-`-prefixed token.

    ⚑⚑ THE BOUNDARY IS THE NEXT FLAG, AND GREEDY CONSUMPTION MADE THIS ORDER-DEPENDENT. Filtering
    flags out while scanning PAST them let `--corpus a.bib --bib target.bib` swallow `target.bib`
    as a corpus member and leave `--bib` with nothing — measured as two failed invocations where
    putting `--corpus` last was the only working order, with the usage text saying nothing.

    ⚑ AND THE SILENT HALF IS WORSE THAN THE ERROR: with the target's operand eaten, the write
    falls through to the DEFAULT bib, so a write aimed at a peer's file reports a clean diff
    against one the author never named.
    """
    if flag not in argv:
        return ()
    out: list[str] = []
    for token in argv[argv.index(flag) + 1 :]:
        if token.startswith("-"):
            break
        out.append(token)
    return tuple(out)


def _target(argv: list[str], mode: str | None) -> tuple[str | None, Refusal | None]:
    """Resolve the `--bib` write target, or say why it cannot be used."""
    if TARGET_FLAG not in argv:
        return None, None

    at = argv.index(TARGET_FLAG) + 1
    if at >= len(argv) or argv[at].startswith("-"):
        return None, Refusal(f"bibstruct.py {TARGET_FLAG} needs a path")

    # ⚑⚑⚑ A READ MODE ACCEPTING THE WRITE TARGET SILENTLY MISREAD THE CORPUS. It takes exactly
    # one path and is removed from the read set, so `--orphans --bib a.bib b.bib …` read every
    # file but the named one and reported FALSE DANGLING EDGES for every premise defined there.
    # A peer measured exactly that against their own corpus and reasonably read it as a merge
    # defect — the tool was right and the invocation was wrong, which is the worst combination.
    if mode not in WRITE_MODES:
        return None, Refusal(
            f"bibstruct.py: {TARGET_FLAG} is the WRITE target ({'/'.join(WRITE_MODES)}) and "
            f"takes ONE path;\n  {mode} reads every bib given POSITIONALLY. Passing "
            f"{TARGET_FLAG} to a read mode would DROP it from the read set and report false "
            f"dangling edges for anything it defines.\n    bibstruct.py {mode} <bib> [<bib> …]"
        )
    return argv[at], None


def _corpus(argv: list[str], mode: str | None) -> tuple[tuple[str, ...], Refusal | None]:
    """Resolve `--corpus`, the sibling bibs a write's edge check may resolve into."""
    if CORPUS_FLAG not in argv:
        return (), None

    # ⚑ REFUSED ON A READ for the same reason the target flag is: a read takes its corpus
    # positionally, so accepting it here would create a second spelling of one thing.
    if mode not in WRITE_MODES:
        return (), Refusal(
            f"bibstruct.py: {CORPUS_FLAG} names sibling bibs for a WRITE's edge check "
            f"({'/'.join(WRITE_MODES)});\n  {mode} reads its corpus POSITIONALLY — pass the "
            f"bibs directly:\n    bibstruct.py {mode} <bib> [<bib> …]"
        )

    found = operands_after(CORPUS_FLAG, argv)
    if not found:
        return (), Refusal(f"usage: bibstruct.py {mode} … {CORPUS_FLAG} <bib> [<bib> …]")
    return found, None


def parse(argv: list[str]) -> Parsed | Refusal:
    """Return what to run, or a refusal naming the remedy.

    ⚑ A STRAY POSITIONAL IS A REFUSAL, NOT A SILENT SUFFIX. The origin's pair-loop appended any
    extra `=`-free token to the PREVIOUS field's value, so the natural `--add <key> f=v other.bib`
    wrote a filesystem path INTO the entry. Naming the operand beats eating it.
    """
    mode = next((a for a in argv if a in known_modes()), None)

    target, refusal = _target(argv, mode)
    if refusal is not None:
        return refusal

    corpus, refusal = _corpus(argv, mode)
    if refusal is not None:
        return refusal

    paths = [a for a in argv if not a.startswith("-")]
    paths = [p for p in paths if p != target and p not in corpus]

    if mode in ("--add", "--set") and target is None:
        stray = [p for p in paths if p.endswith(".bib")]
        if stray:
            return Refusal(
                f"bibstruct.py {mode}: {stray[0]!r} looks like a target bib, but {mode} takes it "
                f"as `{TARGET_FLAG} <path>` — a trailing positional here would be swallowed into "
                f"the previous field's value."
            )

    # ⚑⚑⚑ A WRITE MODE NAMING NO TARGET SILENTLY DEFAULTED, AND THE MIRROR REFUSAL ALREADY
    # EXISTED. `_target` refuses a READ mode given `--bib` in full; a WRITE mode given nothing
    # fell through with `target=None` and a default applied downstream. Measured by summit against
    # their own floor: the reader answered `24 of 24` over a path the writer then reported as
    # `no entry <key> (have 0)`. Reproduced here as `have 67` — SAME COMMAND, DIFFERENT CWD, so
    # the number is the size of whatever corpus the default resolved to, and the caller cannot
    # tell an empty file from a wrong default.
    #
    # ⚑⚑ THE COMMENT FIFTEEN LINES ABOVE ALREADY RECORDED THE CONSEQUENCE — a write that "fell
    # through to the DEFAULT bib, so a write aimed at a peer's file diffed cleanly against one the
    # author never named." That was repaired for ONE cause (greedy `--corpus`) and left open for
    # the general one. A defect fixed at its trigger rather than its class comes back.
    if mode in WRITE_MODES and target is None:
        return Refusal(
            f"bibstruct.py {mode}: names no {TARGET_FLAG}, so the write would go to the DEFAULT "
            f"corpus rather than a file you named.\n  A refusal reporting `have <n>` would be "
            f"counting THAT corpus, not yours — which reads as a fact about your file.\n"
            f"    bibstruct.py {mode} <key> … {TARGET_FLAG} <path>"
        )

    # ⚑⚑⚑ `rest` CARRIES THE MODIFIER FLAGS, AND IT WAS DECLARED-BUT-NEVER-POPULATED UNTIL THE
    # FIRST CONSUMER NEEDED IT. `Parsed.rest` existed as a field from the start and `parse` never
    # filled it, so it read as an empty tuple forever — which meant `--apply` was INVISIBLE and
    # every write silently took the dry-run branch. A field nothing fills is the built-then-
    # orphaned shape inside a dataclass, and the only thing that found it was a suite asserting a
    # write actually landed.
    #
    # ⚑ THE MODE IS EXCLUDED because it is not a modifier: `parsed.mode` already carries it, and
    # leaving it here would let a caller test membership in two places and get two answers.
    rest = tuple(a for a in argv if a.startswith("-") and a != mode)
    return Parsed(mode=mode, target=target, corpus=corpus, paths=tuple(paths), rest=rest)
