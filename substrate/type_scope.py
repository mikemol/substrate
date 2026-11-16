# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""One file's mypy messages, split into its OWN and those its IMPORT CLOSURE creates.

⚑⚑ THE QUESTION A DRAIN TURNS ON, AND NO MODE ANSWERED IT. `type_gate` ignores its path
argument entirely and always censuses the promoted corpus; `type_census_summary --files`
attributes whole-corpus messages to files. Neither says whether a leaf's messages would
SURVIVE a move to a tree that imports nothing untyped -- which is the only question a drain
asks. `jea/metalanguage/sorted_stream.py` was drained on exactly this reasoning; before the
drain no tool could have said which of its messages would go with it.

⚑ THE MECHANISM IS A DIFFERENTIAL, NOT AN ATTRIBUTION. mypy reports the USE of an `Any`, not
its source, so no run can be asked "which import caused this message". What CAN be asked is
what changes when the closure is taken away: run the same file with `--follow-imports=normal`
(every import resolved from source) and with `--follow-imports=skip` (every import becomes
`Any`), and read the two multisets against each other.

- A message in BOTH arms is the file's OWN. Its presence does not depend on anything the
  closure supplies, so it survives a move.
- A message only under `normal` is CLOSURE-INDUCED: it fires because a followed import
  brought an untyped value in. This is the population a drain removes.
- A message only under `skip` is CLOSURE-SUPPRESSED: the closure's real types are what keep
  it from firing. It is an artefact of the differential, not debt -- and it is the arm a
  reader forgets exists, which is what would turn `induced` into a difference of totals.

⚑⚑⚑ WHICH import contributes a closure-induced message is INFERRED, NEVER MEASURED, and this
module marks that on its output. `record_migrate` logs six wrong attributions in a row on
precisely this shape -- *"the error names the DUMP, not the literal."* The leads printed
below the split are error CODES, which are measured; naming a suspect IMPORT would need a
claim mypy never makes, and would read as measured because it names real modules.

⚑ THE OBSERVATION IS ALREADY IN THIS REPO, FROM THE OTHER DIRECTION. `pyproject.toml`'s
`packages` note records paperkit converting three suites off `sys.path.insert`: 3 own
findings became 231, and 0 became 312, purely because naming a module made its edge
FOLLOWABLE. That is this differential with the arms swapped, measured before this tool
existed -- which is what makes the induced arm a real population rather than a hypothesis.

    type_scope.py <relpath>            # the split, and the inferred leads behind it
    type_scope.py <relpath> --own      # only the messages that survive a move
    type_scope.py <relpath> --closure  # only the closure-dependent messages, both arms
    type_scope.py --selftest           # the module's own cases
"""

from __future__ import annotations

import subprocess
import sys
from collections import Counter
from dataclasses import dataclass

from substrate import corpus, mypy_census

# Exit code for a split that could not be taken -- `gate_main`'s spelling, deliberately.
_CANNOT_MEASURE = 2

# The separator `mypy_census` builds its keys from: `<code>::<relpath>`.
_SEP = "::"

# How much of a message to show in a listing.
_EXCERPT = 88

# How many rows a listing shows before it names its own remainder.
_TOP = 12

_MODES = ("--own", "--closure")

# ⚑ THE TWO ARMS OF THE DIFFERENTIAL, NAMED ONCE. `normal` follows every import and types it
# from source; `skip` replaces each imported module with `Any` without reading it. These are
# mypy's own spellings and are not ours to paraphrase.
_FOLLOW_NORMAL = "--follow-imports=normal"
_FOLLOW_SKIP = "--follow-imports=skip"

# ⚑⚑ THE SHAPES THIS DIFFERENTIAL CANNOT SEE -- the `attr_reads.unresolved` pattern, and the
# `walk_scope` second boundary with it: the first line is what the READING cannot decide, the
# last three are what the two RUNS never reached. A zero in any arm is a fact about the
# differential until a reader has checked their own file against these.
_CASCADE = (
    "cross-file-cascade -- only the NAMED file's messages are read, so a message that this "
    "file's own untyped surface induces in an IMPORTER is not counted against it here"
)
_MASKING = (
    "skip-arm-masking -- under `skip` an `Any` receiver silences codes that would fire on a "
    "real type, so CLOSURE-SUPPRESSED can hold a message the file would own after a drain"
)
_THIRD_PARTY = (
    "third-party-invariance -- `--ignore-missing-imports` types an absent package as `Any` "
    "in BOTH arms, so an untyped THIRD-PARTY dependency cancels out and is never reached"
)
_UNFOLLOWED = (
    "unfollowed-first-party -- an import mypy cannot resolve from source is `Any` in both "
    "arms too; the differential never reaches it, and it reads as though the file owned it"
)

_BLIND: tuple[str, ...] = (_CASCADE, _MASKING, _THIRD_PARTY, _UNFOLLOWED)


@dataclass(frozen=True, slots=True)
class Split:
    """One file's messages, partitioned by whether its import closure is load-bearing.

    ⚑ THE THREE ARMS ARE NOT DERIVABLE FROM EACH OTHER and each answers a different question.
    `own` is what survives a drain; `induced` is what a drain removes; `suppressed` is what
    the closure currently PREVENTS. Reporting `induced` as `normal_total - len(own)` would
    silently fold the third arm into the second, which is the collapse-to-a-scalar this repo
    keeps paying for -- so all three are held.
    """

    target: str
    own: tuple[str, ...]
    induced: tuple[str, ...]
    suppressed: tuple[str, ...]

    @property
    def normal_total(self) -> int:
        """How many messages the file carries with its closure resolved -- the live count."""
        return len(self.own) + len(self.induced)


def messages_for(rows: dict[str, list[str]], target: str) -> tuple[str, ...]:
    """Return `<code>: <message>` for every census row keyed to `target`.

    ⚑ CODE-QUALIFIED, BECAUSE THE TEXT ALONE IS NOT AN IDENTITY. `Expression has type "Any"`
    is emitted under `misc` tens of thousands of times across this tree; unqualified, one
    arm's text would match another arm's different finding and the diff would report a
    cancellation that never happened.
    """
    out: list[str] = []
    for key, msgs in rows.items():
        code, _, relpath = key.partition(_SEP)
        if relpath == target:
            out.extend(f"{code}: {m}" for m in msgs)
    return tuple(sorted(out))


def one_file_census(target: str, follow: str) -> dict[str, list[str]] | None:
    """Census `target` alone under one `--follow-imports` arm. None when mypy could not run.

    ⚑ IT TAKES ITS FLAGS FROM `mypy_census.FLAGS` RATHER THAN RESPELLING THEM. The gate's
    predicate and this one must differ in exactly one place -- the follow arm -- and a second
    flag list here would be a second authority that drifts silently, which is
    `census-keyed-on-one-spelling` at the flag list. It does not call `type_errors` itself
    because that function's flags are policy, and a `follow=` parameter there would let any
    caller change the GATE's predicate.

    ⚑ NONE RATHER THAN `{}` ON A FAILED RUN, for the reason `type_errors` carries the
    `UNRUNNABLE` sentinel: a caller that folds "could not run" into "no messages" would report
    a file whose closure did not resolve as one whose messages are all its own.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", *mypy_census.FLAGS, follow, "--", target],
            cwd=str(corpus.ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode not in (0, 1) or "No module named mypy" in (proc.stderr or ""):
        return None
    return mypy_census.parse(proc.stdout or "")


def split_of(normal: dict[str, list[str]], skip: dict[str, list[str]], target: str) -> Split:
    """Partition `target`'s messages by differencing the two `--follow-imports` arms.

    ⚑⚑ A MULTISET DIFFERENCE, NOT A SET ONE, AND THE COUNT IS THE WHOLE FINDING. A file with
    675 identical `misc` messages under one arm and 700 under the other has 25 induced; a set
    difference reports zero, because the text is the same and the SET is unchanged. On this
    corpus one code carries most of the messages and a handful of texts carry most of that
    code, so a set diff would report almost every file as entirely self-owned.
    """
    live = Counter(messages_for(normal, target))
    bare = Counter(messages_for(skip, target))
    return Split(
        target=target,
        own=tuple(sorted((live & bare).elements())),
        induced=tuple(sorted((live - bare).elements())),
        suppressed=tuple(sorted((bare - live).elements())),
    )


def unresolved() -> tuple[str, ...]:
    """Return the shapes this differential cannot see, so no arm's zero reads as an absence.

    ⚑⚑ THE HALF THAT MAKES A ZERO HONEST, and a function rather than a printed caveat because
    `attr_reads.unresolved` established that a reader given a count and no boundary treats the
    count as the population. Each line names a MECHANISM a reader can check their own file
    against, not a general disclaimer.
    """
    return _BLIND


def rows_for(label: str, msgs: tuple[str, ...], top: int) -> list[str]:
    """Render up to `top` messages under one arm's label, naming any remainder.

    ⚑ THE REMAINDER LINE IS NOT DECORATION, for `type_census_summary.listing`'s reason: a
    truncated arm with no residue row reads as the whole arm, and a reader cannot tell whether
    what is hidden is one more message or nine hundred.
    """
    out = [f"  {label:<10} {m[:_EXCERPT]}" for m in msgs[:top]]
    if len(msgs) > top:
        out.append(f"  {label:<10} ... {len(msgs) - top} more")
    return out


def leads(split: Split) -> tuple[str, ...]:
    """Return the inferred leads for `split`'s closure-induced messages, ranked by volume.

    ⚑⚑ IT RANKS CODES, NOT IMPORTS, AND THAT IS THE HONEST FORM. Ranking the file's imports
    would need a claim mypy never makes -- which import an `Any` came from -- and such a
    ranking reads as measured precisely because it names real modules. The error CODES of the
    induced arm ARE measured, and they are the actual lead: `no-untyped-call` names a call
    into an unannotated callee, `no-untyped-def` an unannotated definition, `misc` with
    `Expression has type "Any"` a value that arrived already typed as `Any`. The reader takes
    the code to their own import list; the tool does not guess on their behalf.
    """
    by_code: Counter[str] = Counter(m.partition(":")[0] for m in split.induced)
    return tuple(f"{code}  {n} induced message(s)" for code, n in by_code.most_common(_TOP))


def headline(split: Split) -> str:
    """Return the one line that names all three arms, so none can stand in for the debt."""
    return (
        f"{split.target}: {split.normal_total} message(s) with the closure resolved"
        f" -- {len(split.own)} OWN, {len(split.induced)} CLOSURE-INDUCED,"
        f" {len(split.suppressed)} closure-SUPPRESSED"
    )


def honesty() -> list[str]:
    """Return the lines separating what the differential establishes from what it infers.

    ⚑ A FUNCTION RATHER THAN A STRING IN THE RENDERER, so every mode carries it by
    construction. A per-mode caveat is one a future mode forgets.
    """
    established = (
        "  ESTABLISHED: each arm's membership -- a multiset difference of two "
        "mypy runs over this one file, identical but for --follow-imports."
    )
    inferred = (
        "  INFERRED:    every lead below. mypy reports the USE of an `Any`, never "
        "its source, so no message here is attributed to a NAMED import."
    )
    return [established, inferred]


def render(split: Split, mode: str) -> str:
    """Render the split, marking what is established and what is inferred."""
    if mode == "--own":
        body = rows_for("OWN", split.own, len(split.own))
    elif mode == "--closure":
        body = rows_for("INDUCED", split.induced, len(split.induced)) + rows_for(
            "SUPPRESSED", split.suppressed, len(split.suppressed)
        )
    else:
        body = rows_for("OWN", split.own, _TOP) + rows_for("INDUCED", split.induced, _TOP)
    lines = [*body, headline(split), *honesty()]
    lines.extend(f"     lead (INFERRED)  {lead}" for lead in leads(split))
    lines.append(
        f"   {len(unresolved())} shape(s) this differential CANNOT see -- a zero in"
        f" any arm above is not yet an absence:"
    )
    lines.extend(f"     {b}" for b in unresolved())
    return "\n".join(lines) + "\n"


def refusal(target: str, arm: str) -> str:
    """Return the refusal for a split that could not be taken, naming the arm that failed."""
    return (
        f"type-scope: CANNOT MEASURE {target} -- refusing rather than reporting an "
        f"empty split.\n  reason: the {arm} arm produced no census; mypy is not "
        f"installed for this interpreter, or it refused this path.\n"
        f"  try:  uv run --with mypy python3 -m substrate.type_scope {target}\n"
    )


def scope(target: str, mode: str) -> int:
    """Take both arms for `target` and render the split, or refuse with the reason."""
    normal = one_file_census(target, _FOLLOW_NORMAL)
    skip = one_file_census(target, _FOLLOW_SKIP)
    if normal is None or skip is None:
        sys.stderr.write(refusal(target, _FOLLOW_NORMAL if normal is None else _FOLLOW_SKIP))
        return _CANNOT_MEASURE
    sys.stdout.write(render(split_of(normal, skip, target), mode))
    return 0


# The case fixtures' expected arm sizes, named so no comparison below is a bare literal.
_AGREED_OWN = 3
_ONE = 1
_LIVE_WITH_INDUCED = 4


def main(argv: list[str]) -> int:
    """Split one named file's messages.

    ⚑⚑ `--selftest` IS DISPATCHED FROM THE `__main__` GUARD, NOT FROM HERE. A branch inside this
    function returns, and `return` is invalid at module level — so `module_trim` could not re-home
    the cases while their dispatch lived in a function body (gate-G327). Rewriting the branch to
    `sys.exit` was refused for a better reason: a reachable `SystemExit` takes the exit decision
    from anything that imports this module (gate-G329). Moving the dispatch into the guard, where
    the block never runs on import, is the repair that costs neither property.
    """
    operands = [a for a in argv if not a.startswith("-")]
    unknown = [a for a in argv if a.startswith("-") and a not in (*_MODES, "--selftest")]
    # ⚑⚑ THE PATH OPERAND IS HONOURED OR REFUSED, NEVER DISCARDED. `module_size` silently
    # returned the whole-corpus census for a path operand -- a true line for the wrong
    # reason, which is worse than an error, and it scoped two dispatch waves wrongly. There
    # is deliberately no no-operand form here: this tool has nothing to say about a corpus,
    # so an absent operand is a refusal rather than a default.
    if unknown or len(operands) != 1:
        sys.stderr.write(
            f"usage: type_scope.py <relpath> [{' | '.join(_MODES)}]\n"
            f"       type_scope.py --selftest\n"
        )
        return _CANNOT_MEASURE
    target = operands[0]
    if not (corpus.ROOT / target).is_file():
        sys.stderr.write(f"type-scope: no such file under the corpus root: {target}\n")
        return _CANNOT_MEASURE
    mode = next((a for a in argv if a in _MODES), "")
    return scope(target, mode)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
