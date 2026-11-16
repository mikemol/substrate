# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A per-invocation fact, bound WRITE-ONCE, so a second resolution is an error rather than a race.

⚑⚑⚑ ONE MECHANISM, THREE VARIABLES — NOT THREE IMPLEMENTATIONS. `intent`, `snapshot state` and
`tenant` are the same shape: a fact about THE INVOCATION that was being passed as a PARAMETER, so
anyone could address it positionally and two different propositions ended up spelled identically.
Building a second copy of this for the tenant would be the derived-view duplication this repo keeps
paying for; the vocabulary differs, the machinery does not.

⚑⚑⚑ THE REFUSAL FIRES AT THE WRITE, NOT AT A READ, AND THAT IS THE WHOLE DESIGN. An earlier cut
compared a stated value against the ambient one AT EVERY CONSUMER: N checks, each forgettable, and
forgetting one is exactly the plausible-local-fix failure this is scaled against. A write-once
variable means **there is nothing to disagree with** — the second write fails where the write
happens, not at some downstream consumer that happened to remember to look.

⚑⚑ AND THAT IS WHAT THE TENANT CASE ACTUALLY NEEDED. The measured incident was not someone passing
a wrong flag: two functions in one report each resolved the store INDEPENDENTLY, one reading a
stale sqlite file and one reading live postgres, and the report mixed them. Neither routed through
a comparison, which is why refuse-on-disagreement would not have caught it. Write-once makes the
FIRST resolution the answer and the second an ERROR, with no cooperation required from either site.

⚑⚑ THE VALUE AND ITS ORIGIN ARE WRITTEN IN ONE ACT, BY ONE WRITER. That is what keeps the origin
from becoming a hand-maintained `source=` field: `set` is the only writer of either variable, so
they cannot drift, and the declaration site carries the scope while `contextvars` does the rest.

⚑ `vocab` IS CLOSED. An unrecognised value REFUSES rather than passing — an escape must be at least
as strict as the thing it bypasses, or a typo satisfies the contract silently.

⚑ WHAT THIS STILL DOES NOT PREVENT, STATED PLAINLY: a caller can reach the underlying `ContextVar`
or run in a context of its own making. Python has no unforgeable capability and this does not
pretend to be one. The property it DOES have is that the ACCIDENTAL second binding — the one a
locally-sound fix produces — fails loudly at the point of the write. Getting past it requires
naming a private attribute or copying a context, neither of which anyone reaches for while
"fixing" something.
"""

from __future__ import annotations

import contextvars
import sys
from typing import TYPE_CHECKING, Literal, NamedTuple, Self

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence


class MutationContractError(Exception):
    """The base of every refusal this module RAISES rather than exits on.

    ⚑⚑⚑ IT RAISES AND DOES NOT `sys.exit`, AND THE REASON IS NOT ABOUT THIS FRAME. This mechanism
    is reached as a LIBRARY from dozens of importing files, so `sys.exit` here would unwind the
    CALLER'S interpreter — and because `SystemExit` derives from `BaseException` it slips past
    every `except Exception` on the way out. **A refusal a caller cannot contain is not a refusal,
    it is a kill.**

    ⚑⚑ AND IT SITS OFF `Exception` DELIBERATELY — a family the broad advisory handlers scattered
    through the tree do not catch. A refusal swallowed by an `except Exception` prints as an
    advisory warning while the tool proceeds to write anyway, which is the failure mode a contract
    exists to prevent.
    """


class AmbientVocabError(MutationContractError):
    """An out-of-vocabulary value offered to `Ambient.set`.

    ⚑ IT IS NOT ALSO A `ValueError`, though it reads like one. `ValueError` derives from
    `Exception`, and Python resolves a handler by the MRO — so a dual base would be caught by the
    broad advisory handlers and re-open the hole the base class exists to close. **The kind is
    chosen by WHO MUST BE ABLE TO CATCH IT, not by what it resembles.**
    """


class AmbientConflictError(MutationContractError):
    """A SECOND write to a write-once ambient. Names the site that already bound it.

    ⚑ THE REFUSAL NAMES ITS SUCCESSORS. A refusal with no named successor is an invitation to
    invent one locally, which is the route-around this mechanism exists not to provoke.
    """

    def __init__(self, amb: Ambient, label: str, stated: str, ambient: str, origin: str) -> None:
        """Record which site bound the value, which tried to rebind it, and to what."""
        self.amb = amb
        self.label = label
        self.stated = stated
        self.ambient = ambient
        self.origin = origin
        super().__init__(str(self))

    def _matched(self) -> str:
        """Return the note for a second write of the SAME value — still a defect."""
        return (
            "  ⚑ The values MATCH, which is not a reprieve: two sites each believe they are "
            "the\n    one that decides. They agree today and nothing makes them agree "
            "tomorrow — that\n    is the shape that put two stores in one report.\n"
        )

    def _successors(self) -> str:
        """Return the ordered remedies, so the refusal does not invite a local invention."""
        kw = self.amb.kw
        return (
            f"  ⚑ Successors, in the order you should try them:\n"
            f"    1. READ IT, do not re-bind it: `{kw.upper()}.get()` returns the value this\n"
            f"       invocation already established. A callee almost never needs to write.\n"
            f"    2. BIND IT ONCE, AT ENTRY — where the operator's request is read, so every\n"
            f"       frame below inherits it and none has to assert anything.\n"
            f"    3. If this genuinely is a NEW invocation (a fixture, a nested run over a\n"
            f"       different target), give it a NEW CONTEXT rather than overwriting this "
            f"one:\n"
            f"           contextvars.copy_context().run(fn, ...)\n"
            f"       or, for a registered divergence, `{kw.upper()}.override(...)`."
        )

    def __str__(self) -> str:
        """Return the full refusal: what was bound, by whom, what was attempted, and what to do."""
        head = (
            f"⚑ {self.label}: {self.amb.kw} is ALREADY BOUND for this invocation "
            f"({self.ambient!r}) and is WRITE-ONCE."
        )
        body = (
            f"  bound:    {self.ambient!r}  by {self.origin}\n"
            f"  attempted:{self.stated!r}  at {self.label}\n"
        )
        body += self._matched() if self.stated == self.ambient else f"  {self.amb.two_readings}\n"
        return f"{head}\n{body}{self._successors()}"


class Divergence(NamedTuple):
    """What an override IS: the value it wants, why, and the label it is registered under.

    ⚑⚑ THIS SPLIT IS THE PER-FILE GATE READ AS A DESIGN SIGNAL RATHER THAN A LIMIT. A first cut
    took six flat parameters and was refused at `PLR0913`. The six are TWO KINDS — what this
    divergence is (here) and the POLICY it is judged against (`sanctioned`, plus where to announce
    it). Reading the refusal as a number to satisfy would have produced a parameter tuple; reading
    it as grain produces the split a caller actually wants, because the policy is fixed for a
    deployment while the divergence differs at every site.
    """

    value: str
    reason: str
    label: str


class Ambient:
    """A per-invocation context variable with write-once binding.

    ⚑ `set` IS THE SINGLE ENFORCEMENT POINT. Every route by which a wrong value could enter this
    invocation passes through it, so the check lives there and nowhere else. That is the property
    a distributed discipline could not have: a consumer that forgets to compare is not a hole,
    because there is nothing for it to compare — the value it reads is the only one ever bound.
    """

    def __init__(self, kw: str, vocab: Iterable[str], two_readings: str) -> None:
        """Declare an ambient named `kw`, closed over `vocab`, naming what it would conflate."""
        self.kw = kw
        self.vocab = tuple(vocab)
        self.two_readings = two_readings
        self._var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
            f"substrate_{kw}", default=None
        )
        self._origin: contextvars.ContextVar[str | None] = contextvars.ContextVar(
            f"substrate_{kw}_origin", default=None
        )

    def get(self) -> str | None:
        """Return the value bound for this invocation, or None when nothing bound one."""
        return self._var.get()

    def origin(self) -> str | None:
        """Return the label of the site that bound the value, or None when unbound."""
        return self._origin.get()

    def set(self, value: str, origin: str) -> None:
        """Bind value and origin in ONE act — WRITE-ONCE. A second write RAISES.

        ⚑⚑ AND THERE IS NO PUBLIC `reset`. A reset returns the variable to its prior value, which
        is legitimate for a scoped override and is ALSO a hole if anything may call it: write-once
        plus an unrestricted reset is write-many with extra steps. A new binding needs a NEW
        CONTEXT, not an undo — which is what `override` supplies.
        """
        if value not in self.vocab:
            spelled = " / ".join(repr(v) for v in self.vocab)
            msg = (
                f"⚑ {origin}: {self.kw}={value!r} is not one of {spelled}.\n"
                f"  An unrecognised value REFUSES rather than passing — the escape must be at "
                f"least as\n  strict as the contract it bypasses, or a typo satisfies it "
                f"silently."
            )
            raise AmbientVocabError(msg)
        cur = self._var.get()
        if cur is not None:
            raise AmbientConflictError(self, origin, value, cur, self._origin.get() or "<unknown>")
        self._var.set(value)
        self._origin.set(origin)

    def resolve(self, label: str, stated: str | None = None) -> str | None:
        """Return the invocation's value, binding `stated` if nothing is bound yet.

        ⚑⚑ A STATED VALUE THAT MATCHES THE ALREADY-BOUND ONE IS A NO-OP, NOT A REBIND. That is
        what lets a site which hardcodes its own intent keep working while the guarantee holds:
        under an agreeing invocation they agree and agreement passes silently, and under a
        DISAGREEING one the same site raises — which is the whole point.

        ⚑ THE DISAGREEING CASE ROUTES BACK THROUGH `set`, so the refusal text and the write-once
        semantics are stated once. Two spellings of one refusal is how the messages drift apart and
        the weaker one becomes the one people read.
        """
        ambient = self.get()
        if stated is None:
            return ambient
        if ambient is None:
            self.set(stated, f"stated at {label}")
            return stated
        if ambient != stated:
            self.set(stated, f"stated at {label}")
        return ambient

    def override(
        self,
        divergence: Divergence,
        sanctioned: Mapping[tuple[str, str], str],
        announce_to: Callable[[str], None] | None = None,
    ) -> Override:
        """Return a SCOPED, REASONED divergence — the deliberate override.

        ⚑⚑⚑ IT MUST EXIST, AND A DRY-RUN-THAT-WRITES IS THE CASE THAT PROVES IT. A tool that
        writes, re-checks and restores genuinely DISAGREES with a stated dry run — and the
        disagreement is CORRECT. Without an override the correct behaviour is unspellable, and the
        author deletes the guard instead.

        ⚑⚑ THE ROSTER IS AN ARGUMENT, NOT A MODULE GLOBAL — a change from the origin. A registry
        baked into this module makes the mechanism own a policy list belonging to whoever deploys
        it, which is the second-roster shape this repo keeps paying for. A caller supplies the
        registry it is willing to defend, and a gate can enumerate it.
        """
        return Override(self, divergence, sanctioned, announce_to)


class Override:
    """A registered, reasoned divergence that runs a callable in a FRESH context.

    ⚑ A SCOPE, NOT AN ASSIGNMENT. A bare re-`set` leaks the divergent value past the branch that
    meant it, so later readers see an override as if it were the operator's own statement.
    """

    def __init__(
        self,
        amb: Ambient,
        divergence: Divergence,
        sanctioned: Mapping[tuple[str, str], str],
        announce_to: Callable[[str], None] | None = None,
    ) -> None:
        """Validate the divergence at CONSTRUCTION, so an unusable override cannot be held."""
        if divergence.value not in amb.vocab:
            spelled = " / ".join(repr(v) for v in amb.vocab)
            msg = (
                f"{amb.kw}.override({divergence.value!r}): not one of {spelled}. An override "
                f"is at least as strict as the contract it diverges from."
            )
            raise ValueError(msg)
        if not divergence.reason or not divergence.reason.strip():
            msg = (
                f"{amb.kw}.override(...) requires a REASON. An override with no reason is "
                f"`--no-verify` — a bypass that leaves no trace of why."
            )
            raise ValueError(msg)
        if (amb.kw, divergence.label) not in sanctioned:
            raise ValueError(_unregistered(amb, divergence.label))
        self.amb = amb
        self.value = divergence.value
        self.reason = divergence.reason.strip()
        self.label = divergence.label
        self._out = announce_to

    def run(self, fn: Callable[[], object]) -> object:
        """Run `fn` in a FRESH CONTEXT where this ambient holds `value`.

        ⚑⚑⚑ A NEW CONTEXT, NOT AN ASSIGNMENT — which is what makes the override structurally
        costly to spell. The caller must hand over a CALLABLE and accept that the divergent binding
        cannot outlive it; nobody "fixing" a refusal reaches this by adding a keyword argument,
        which was the failure of the parameter form it replaces.

        ⚑⚑ `copy_context()` GIVES A GENUINELY FRESH BINDING, so write-once is satisfied honestly
        rather than bypassed: inside the copy the variable is unbound, this sets it once, and the
        outer context is UNTOUCHED — no reset, no undo, no hole. That is why there is no public
        `Ambient.reset`.
        """
        out = self._out or _to_stderr
        cur, org = self.amb.get(), self.amb.origin()
        if cur is not None and cur != self.value:
            out(
                f"   ⚑ {self.label}: {self.amb.kw} OVERRIDE {cur!r} → {self.value!r} "
                f"in a copied context (outer binding by {org} is unchanged)\n"
                f"     reason: {self.reason}"
            )

        def _inner() -> object:
            # ⚑⚑⚑ THIS WRITES THE VARIABLES DIRECTLY RATHER THAN THROUGH `set`, AND THE REASON IS
            # A DEFECT THE SUITE CAUGHT. `copy_context()` copies the VALUES, not merely the
            # variables — so inside the copy the ambient is STILL BOUND, and routing this through
            # the public write-once `set` made the override refuse ITSELF. The one sanctioned way
            # around write-once cannot itself be subject to write-once.
            #
            # ⚑⚑ SO THE PRIVATE WRITE IS THE MECHANISM, NOT A SHORTCUT PAST IT. What keeps this
            # honest is the CONTEXT BOUNDARY, not the setter: the binding cannot outlive `run`,
            # the outer context is untouched, and every path that reaches here has already passed
            # the vocabulary, reason and registration checks at construction.
            self.amb._var.set(self.value)  # noqa: SLF001 - see above; the boundary is the guard
            self.amb._origin.set(  # noqa: SLF001 - written in the same act as the value
                f"override at {self.label}: {self.reason}"
            )
            return fn()

        return contextvars.copy_context().run(_inner)

    def __exit__(self, *exc: object) -> Literal[False]:
        """Refuse the context-manager protocol — `__enter__` raises before this can run.

        ⚑ THE RETURN IS `Literal[False]`, NOT `bool`, and the checker was right to insist: an
        `__exit__` that MIGHT return True is one that might swallow the caller's exception, and a
        type saying "maybe" where the answer is always "no" understates what this promises.
        """
        return False

    def __enter__(self) -> Self:
        """Refuse `with`, naming the successor.

        ⚑ BOTH HALVES OF THE PROTOCOL ARE DEFINED SO THE REFUSAL IS THE ONE A READER SEES. With
        only `__enter__`, Python raises its own "does not support the context manager protocol"
        BEFORE calling anything here — a correct refusal with no named successor, which is the
        shape this module argues against everywhere else.

        ⚑⚑ AND `with` IS REFUSED ON THE MERITS, not for tidiness: a `with` block would have to
        mutate the CURRENT context and undo it afterwards — the write-then-reset hole write-once
        exists to close, wearing a context manager's clothes. A callable bounds the divergence by
        a CALL FRAME, which cannot be forgotten the way an unbalanced `__exit__` can.
        """
        msg = (
            f"{self.amb.kw}.override(...) is not a context manager, deliberately.\n"
            f"  A `with` block would mutate the CURRENT context and undo it afterwards — the\n"
            f"  write-then-reset hole that write-once exists to close.\n"
            f"  ⚑ Successor: pass the body as a CALLABLE, which runs it in a copied context:\n"
            f"      {self.amb.kw.upper()}.override(Divergence(...), sanctioned=…) \\\n"
            f"          .run(lambda: <the work>)"
        )
        raise TypeError(msg)


def _to_stderr(message: str) -> None:
    """Announce to stderr — the default sink when a caller names none."""
    print(message, file=sys.stderr)  # noqa: T201 - the announce sink itself


def _unregistered(amb: Ambient, label: str) -> str:
    """Return the refusal for an override nobody registered, naming its successors."""
    return (
        f"{amb.kw}.override(...) at label {label!r} is NOT REGISTERED.\n"
        f"  A divergence from the ambient {amb.kw} is a claim that this branch knows "
        f"something\n"
        f"  the invocation does not — which is true rarely, and is otherwise the defect this\n"
        f"  mechanism exists to catch.\n"
        f"  ⚑ Successors, in the order you should try them:\n"
        f"    1. DO NOT DIVERGE — let the ambient {amb.kw} stand. This is right almost "
        f"always;\n"
        f"       a local branch that 'knows better' than the invocation is the failing "
        f"shape.\n"
        f"    2. State it at the ENTRY point instead, so it IS the ambient value and nothing\n"
        f"       downstream has to disagree with anything.\n"
        f"    3. If the divergence is genuinely real — the tool's effect differs from the\n"
        f"       operator's request, as with a dry run that writes then restores — register "
        f"it\n"
        f"       in the caller's own roster under ({amb.kw!r}, {label!r}) with the reason.\n"
        f"       That edit is REVIEWABLE, which is the point of the friction."
    )


#: ⚑ THE TWO READINGS THIS VARIABLE CONFLATES, named in the refusal so a reader sees WHY the two
#: values differ rather than only THAT they do.
INTENT = Ambient(
    "intent",
    ("apply", "dry-run"),
    "These are two different propositions spelled the same way — 'what the operator asked for'\n"
    "  and 'what this branch actually does'.",
)

#: ⚑⚑⚑ THE VARIABLE WHOSE FAILURE IS INVISIBLE. A wrong intent either writes or refuses —
#: observable either way. A wrong TENANT returns PLAUSIBLE ROWS NOBODY CAN DISTINGUISH, which is
#: how one report came to read two different stores without anything saying so.
TENANT = Ambient(
    "tenant",
    ("live", "sandbox"),
    "A read against the wrong tenant returns plausible rows nobody can distinguish; two\n"
    "  independent resolutions in one process is how one report read two stores.",
)

#: Whether this invocation has already taken its snapshot — the third instance of one mechanism.
SNAPSHOT = Ambient(
    "snapshot",
    ("taken", "skipped"),
    "'a snapshot exists for this run' and 'this run needs no snapshot' are different\n"
    "  claims, and a tool that conflates them writes unprotected while reporting safety.",
)

#: Every ambient this module declares, so a caller enumerates rather than restating them.
#: ⚑ NAMED HERE ONCE. A roster written beside the things it names is the duplication that drifts
#: the first time one of them is added, so a consumer asking "which ambients exist" reads this.
DECLARED: Sequence[Ambient] = (INTENT, TENANT, SNAPSHOT)
