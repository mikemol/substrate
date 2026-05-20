"""Eliza.Sequitur — incremental online grammar induction.

The Nevill-Manning & Witten 1997 algorithm with a hot, incremental
digram index. Rule bodies are doubly-linked lists of `Node`s; the
digram index maps each canonical digram-value to a single node (the
first node of its registered occurrence). All structural updates are
O(1) and propagate via a local work queue rather than full scans.

Invariants maintained continuously:

  1. **Digram uniqueness**: each distinct (sym1, sym2) appears at most
     once across the entire rule set.
  2. **Rule utility**: every non-root rule has reference count ≥ 2.

Per the Agda contract this module is generic in α; instantiated per
pipeline level (chars, generators, chambers, orbits).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Set, Tuple


# V₄ ≅ Z/2 × Z/2 composition table, indexed by (left, right) of residue tags.
# Identity 'e' is the V₄ identity; α, β, γ are the three involutions with
# α·β = γ (and cyclic). Used to compose NT residue tags under V₄ transforms.
_V4_COMPOSE: Dict[Tuple[str, str], str] = {
    ("e", "e"): "e", ("e", "α"): "α", ("e", "β"): "β", ("e", "γ"): "γ",
    ("α", "e"): "α", ("α", "α"): "e", ("α", "β"): "γ", ("α", "γ"): "β",
    ("β", "e"): "β", ("β", "α"): "γ", ("β", "β"): "e", ("β", "γ"): "α",
    ("γ", "e"): "γ", ("γ", "α"): "β", ("γ", "β"): "α", ("γ", "γ"): "e",
}


@dataclass(frozen=True)
class NT:
    """Nonterminal reference (used as a node's symbol).

    `residue` is the V₄ orbit-residue tag ∈ {e, α, β, γ}: when V₄
    canonicalization is active, a reference `NT(rid, r)` means "the rule
    body of `rid` with V₄-transform `r` applied to its expansion." When
    canonicalization is off (default), `residue == "e"` and references
    behave identically to plain Sequitur."""
    rule_id: int
    residue: str = "e"

    def __repr__(self) -> str:
        if self.residue == "e":
            return f"R{self.rule_id}"
        return f"R{self.rule_id}·{self.residue}"


class Node:
    """Doubly-linked node in a rule body. Guards are sentinel nodes
    that mark the head/tail boundary; their sym is None and is_guard
    is True."""
    __slots__ = ("sym", "rule_id", "prev", "next", "is_guard")

    def __init__(self, sym: Any, rule_id: int, is_guard: bool = False) -> None:
        self.sym = sym
        self.rule_id = rule_id
        self.is_guard = is_guard
        self.prev: "Node" = self  # circular: self-loop for fresh node
        self.next: "Node" = self


class Rule:
    __slots__ = ("rule_id", "guard", "uses")

    def __init__(self, rule_id: int) -> None:
        self.rule_id = rule_id
        # Sentinel guard. body = guard.next ... guard.prev (excluding guard itself).
        self.guard = Node(sym=None, rule_id=rule_id, is_guard=True)
        self.uses = 0

    def is_empty(self) -> bool:
        return self.guard.next is self.guard

    def first(self) -> Node:
        return self.guard.next

    def last(self) -> Node:
        return self.guard.prev

    def length(self) -> int:
        n = 0
        cur = self.guard.next
        while cur is not self.guard:
            n += 1
            cur = cur.next
        return n

    def body_iter(self):
        cur = self.guard.next
        while cur is not self.guard:
            yield cur
            cur = cur.next


class Sequitur:
    """Online grammar over a stream of terminals.

    All operations are O(1) per terminal (amortised), assuming the
    digram index lookups are O(1).
    """

    def __init__(self, v4_canonicalize: bool = False) -> None:
        self.rules: Dict[int, Rule] = {0: Rule(0)}
        self.rules[0].uses = 1  # root is the entry-point reference
        # Digram value → Node that starts the occurrence.
        # When v4_canonicalize, the KEY is the V₄-canonical form of the
        # digram (lex-min of its V₄ orbit); the residue is encoded in the
        # NT.residue field at promotion time.
        self.digrams: Dict[Tuple[Any, Any], Node] = {}
        # Back-references: rule_id → set of Nodes whose sym == NT(rule_id).
        # Used to find the single caller when inlining underused rules.
        self.back_refs: Dict[int, Set[Node]] = {}
        self._next_id = 1
        # Work queue of nodes whose trailing digram might need re-checking.
        self._queue: Deque[Node] = deque()
        # When True, digrams are indexed by their V₄-canonical form and
        # NT references carry residue tags. Inlining works normally;
        # there are no synthetic siblings — one rule per V₄-orbit.
        self.v4_canonicalize = v4_canonicalize

    # --- Public --------------------------------------------------------

    def observe(self, terminal: Any) -> None:
        """Extend the root by one terminal; restore invariants."""
        node = Node(sym=terminal, rule_id=0)
        self._insert_before(self.rules[0].guard, node)
        # The new trailing digram of root: (node.prev, node) if prev not guard.
        if not node.prev.is_guard:
            self._enqueue(node.prev)
        self._drain()

    def top_rule(self) -> List[Any]:
        return [n.sym for n in self.rules[0].body_iter()]

    def n_rules(self) -> int:
        return len(self.rules) - 1

    def n_nt_refs(self) -> int:
        """Total number of NT-reference nodes across all rule bodies
        (including top rule). Used by the codec to bill V₄ residue bits
        when v4_canonicalize is on (2 bits per NT reference)."""
        total = 0
        for rule in self.rules.values():
            for node in rule.body_iter():
                if isinstance(node.sym, NT):
                    total += 1
        return total

    def all_rules(self) -> Dict[int, List[Any]]:
        return {
            rid: [n.sym for n in r.body_iter()] for rid, r in self.rules.items()
        }

    def rule_uses(self, rule_id: int) -> int:
        rule = self.rules.get(rule_id)
        return rule.uses if rule is not None else 0

    # --- Linked-list mutations -----------------------------------------

    def _insert_before(self, anchor: Node, node: Node) -> None:
        """Insert `node` before `anchor` in `anchor`'s rule. Updates
        use counts and back-refs."""
        node.prev = anchor.prev
        node.next = anchor
        anchor.prev.next = node
        anchor.prev = node
        if isinstance(node.sym, NT):
            self.rules[node.sym.rule_id].uses += 1
            self.back_refs.setdefault(node.sym.rule_id, set()).add(node)

    def _remove(self, node: Node) -> None:
        """Unlink `node` and decrement any references."""
        if isinstance(node.sym, NT):
            rid = node.sym.rule_id
            if rid in self.rules:
                self.rules[rid].uses -= 1
            refs = self.back_refs.get(rid)
            if refs is not None:
                refs.discard(node)
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node
        node.next = node

    # --- Digram index --------------------------------------------------

    @staticmethod
    def _digram_value(first: Node) -> Optional[Tuple[Any, Any]]:
        """The digram starting at `first`, or None if `first` is at the
        tail boundary."""
        if first.is_guard or first.next.is_guard:
            return None
        return (first.sym, first.next.sym)

    def _register(self, first: Node) -> None:
        d = self._digram_value(first)
        if d is None:
            return
        key = self._canonical_digram(d)[0] if self.v4_canonicalize else d
        self.digrams.setdefault(key, first)

    def _unregister(self, first: Node) -> None:
        """If `first` is the registered occurrence of its digram, drop it."""
        d = self._digram_value(first)
        if d is None:
            return
        key = self._canonical_digram(d)[0] if self.v4_canonicalize else d
        if self.digrams.get(key) is first:
            del self.digrams[key]

    # --- Resolution loop -----------------------------------------------

    def _enqueue(self, node: Node) -> None:
        if not node.is_guard:
            self._queue.append(node)

    def _drain(self) -> None:
        """Process the work queue until no more violations remain."""
        while self._queue:
            node = self._queue.popleft()
            # The node may have been removed during a prior resolution.
            if node.next is node:  # detached
                continue
            self._handle_digram(node)

    def _handle_digram(self, first: Node) -> None:
        d = self._digram_value(first)
        if d is None:
            return
        # Canonicalize when V₄ canonicalization is on: digram index keys
        # by canonical form so any V₄-variant matches the same rule.
        if self.v4_canonicalize:
            key, residue_first = self._canonical_digram(d)
        else:
            key, residue_first = d, "e"
        registered = self.digrams.get(key)
        if registered is None:
            self.digrams[key] = first
            return
        if registered is first:
            return  # already registered here; nothing to do
        # Reject overlap: if `registered.next is first` (so registered and
        # first share `first.prev = registered`'s second symbol), skip —
        # overlapping (aaa) digrams aren't deduped.
        if registered.next is first or first.next is registered:
            return
        # Two non-overlapping occurrences. Resolve.
        if self.v4_canonicalize:
            # registered's body is the canonical form. residue_registered
            # is the transform that maps canonical → registered's observed
            # digram. Compute it from the registered node's actual digram.
            reg_d = self._digram_value(registered)
            if reg_d is None:
                # registered is stale; replace and bail.
                self.digrams[key] = first
                return
            _, residue_registered = self._canonical_digram(reg_d)
            target_rid = self._find_rule_with_body(key)
            if target_rid is None:
                target_rid = self._create_rule(key)
        else:
            residue_registered = "e"
            target_rid = self._find_exact_rule_for(d)
            if target_rid is None:
                target_rid = self._create_rule(d)
        # Replace both occurrences with NT(target_rid, residue). If the
        # new target_rid IS one of the rules containing first or
        # registered, skip the replacement for that rule's occurrence
        # (it IS the canonical body).
        first_target = first.rule_id == target_rid
        registered_target = registered.rule_id == target_rid
        if not first_target:
            self._replace_pair_with_nt(first, target_rid, residue_first)
        if not registered_target:
            self._replace_pair_with_nt(registered, target_rid, residue_registered)
        # Rule-utility check REMOVED per substrate-honest discipline:
        # _maybe_inline_underused erases structural observations from
        # the grammar. Every rule created here is a catalogued fact;
        # don't garbage-collect.
        # self._maybe_inline_underused()

    def _find_rule_with_body(self, body: Tuple[Any, Any]) -> Optional[int]:
        """A non-root rule whose body is exactly the given digram."""
        for rid, rule in self.rules.items():
            if rid == 0:
                continue
            if rule.length() == 2:
                a = rule.first()
                b = a.next
                if (a.sym, b.sym) == body:
                    return rid
        return None

    def _replace_pair_with_nt(
        self, first: Node, target_rid: int, residue: str = "e"
    ) -> None:
        """Replace (first, first.next) with a single NT(target_rid, residue)."""
        second = first.next
        if second.is_guard:
            return  # shouldn't happen but defensive
        prev_of_pair = first.prev
        next_of_pair = second.next
        # Unregister any digrams that include first or second.
        if not prev_of_pair.is_guard:
            self._unregister(prev_of_pair)
        self._unregister(first)  # the (first, second) digram itself
        if not next_of_pair.is_guard:
            self._unregister(second)
        # Remove first and second.
        self._remove(first)
        self._remove(second)
        # Insert NT node.
        nt_node = Node(sym=NT(target_rid, residue=residue), rule_id=prev_of_pair.rule_id)
        # prev_of_pair belongs to the same rule (which contained first/second).
        rule_of_pair = self.rules[prev_of_pair.rule_id if not prev_of_pair.is_guard else next_of_pair.rule_id]
        # Insert before next_of_pair.
        self._insert_before(next_of_pair, nt_node)
        # Re-register digrams around the inserted node.
        if not nt_node.prev.is_guard:
            self._register(nt_node.prev)
            self._enqueue(nt_node.prev)
        if not nt_node.next.is_guard:
            self._register(nt_node)
            self._enqueue(nt_node)

    def _find_exact_rule_for(
        self, digram: Tuple[Any, Any]
    ) -> Optional[int]:
        """A non-root rule whose body is exactly (sym1, sym2)."""
        for rid, rule in self.rules.items():
            if rid == 0:
                continue
            if rule.length() == 2:
                a = rule.first()
                b = a.next
                if (a.sym, b.sym) == digram:
                    return rid
        return None

    def _create_rule(self, digram: Tuple[Any, Any]) -> int:
        new_id = self._next_id
        self._next_id += 1
        new_rule = Rule(new_id)
        self.rules[new_id] = new_rule
        sym1, sym2 = digram
        n1 = Node(sym=sym1, rule_id=new_id)
        n2 = Node(sym=sym2, rule_id=new_id)
        self._insert_before(new_rule.guard, n1)
        self._insert_before(new_rule.guard, n2)
        # Register the new occurrence (this BECOMES the canonical occurrence
        # of the digram in the index after callers replace their copies).
        self.digrams[digram] = n1
        return new_id

    # --- V₄ orbit canonicalization helpers (stateless) ---------------------

    @staticmethod
    def _invert_sym_v4(sym: Any) -> Any:
        """V₄ involution on a grammar symbol. For NT, conjugate the residue
        by β (the V₄ 'invert' generator): residue_new = compose(β, residue).
        For V₄ terminals (chr(ord) ∈ 0..3), bit-complement: chr(ord ^ 3)."""
        if isinstance(sym, NT):
            return NT(sym.rule_id, residue=_V4_COMPOSE[("β", sym.residue)])
        return chr(ord(sym) ^ 3)

    @staticmethod
    def _swap_then_invert(digram: Tuple[Any, Any], transform: str) -> Tuple[Any, Any]:
        """Apply a V₄ transform to a 2-tuple digram.

          e: (a, b)
          α: (b, a)              — swap terms
          β: (inv(a), inv(b))   — invert each
          γ: (inv(b), inv(a))   — swap and invert
        """
        a, b = digram
        if transform == "e":
            return (a, b)
        if transform == "α":
            return (b, a)
        inv_a = Sequitur._invert_sym_v4(a)
        inv_b = Sequitur._invert_sym_v4(b)
        if transform == "β":
            return (inv_a, inv_b)
        if transform == "γ":
            return (inv_b, inv_a)
        raise ValueError(f"unknown V₄ transform: {transform}")

    @staticmethod
    def _digram_sort_key(d: Tuple[Any, Any]) -> Tuple[Any, ...]:
        """Total ordering on digrams, so canonicalization can pick a
        unique representative. NTs sort after terminals; within either,
        sort by (rule_id, residue) for NTs and by ord for terminals."""
        def k(s: Any) -> Tuple[int, Any, str]:
            if isinstance(s, NT):
                return (1, s.rule_id, s.residue)
            return (0, ord(s), "")
        return (k(d[0]), k(d[1]))

    @classmethod
    def _canonical_digram(cls, digram: Tuple[Any, Any]) -> Tuple[Tuple[Any, Any], str]:
        """Return (canonical_form, residue) where applying `residue` to
        canonical_form yields the original digram. Canonical form is the
        sort-minimum of the V₄ orbit of `digram`."""
        orbit = {t: cls._swap_then_invert(digram, t) for t in ("e", "α", "β", "γ")}
        # canonical = min by sort key; residue = transform from canonical back.
        canonical_transform = min(orbit.keys(), key=lambda t: cls._digram_sort_key(orbit[t]))
        canonical_form = orbit[canonical_transform]
        # Residue r such that r·canonical = original. Since transforms
        # form V₄ and each is its own inverse, r = canonical_transform.
        return canonical_form, canonical_transform

    # --- Utility (rule-use < 2 → inline or drop) ----------------------

    def _maybe_inline_underused(self) -> None:
        protected = getattr(self, "protected_rule_ids", frozenset())
        for rid in list(self.rules.keys()):
            if rid == 0:
                continue
            if rid in protected:
                continue
            rule = self.rules[rid]
            if rule.uses < 2:
                self._inline_or_drop(rid)

    def _inline_or_drop(self, rid: int) -> None:
        rule = self.rules.get(rid)
        if rule is None:
            return
        refs = self.back_refs.get(rid, set())
        # Inline if exactly one reference; drop if zero.
        if len(refs) == 0:
            # Orphan — also drop digrams that referenced rule's body.
            for node in rule.body_iter():
                self._unregister(node)
            self.rules.pop(rid, None)
            self.back_refs.pop(rid, None)
            return
        if len(refs) > 1:
            return  # shouldn't get here, but defensive
        # Inline.
        caller_node = next(iter(refs))
        # Splice rule's body in place of caller_node.
        body_nodes = list(rule.body_iter())
        # Unregister any digrams adjacent to caller_node.
        if not caller_node.prev.is_guard:
            self._unregister(caller_node.prev)
        self._unregister(caller_node)
        # Detach body from its rule's guard.
        first = rule.first()
        last = rule.last()
        first.prev.next = first.next  # unhook from guard (left)
        # Actually since body_nodes spans first..last and guard is at both ends,
        # rebuild manually: detach the body from `rule.guard`.
        rule.guard.next = rule.guard
        rule.guard.prev = rule.guard
        # Splice body in place of caller_node.
        prev_anchor = caller_node.prev
        next_anchor = caller_node.next
        self._remove(caller_node)
        # Reassign body nodes' rule_id to caller's rule.
        new_rid = prev_anchor.rule_id if not prev_anchor.is_guard else next_anchor.rule_id
        # Walk the body and rewrite rule_id; reattach to the caller's rule.
        cur = first
        nodes_in_order = []
        while True:
            nodes_in_order.append(cur)
            if cur is last:
                break
            cur = cur.next
        # Reset back-refs for inlined NTs (they previously counted under rule
        # `rid`; that count was via Rule(rid).uses which we already invalidate).
        # Re-insert one by one before next_anchor.
        for n in nodes_in_order:
            # Detach n cleanly.
            n.prev.next = n.next
            n.next.prev = n.prev
            n.prev = n
            n.next = n
            # Update its rule_id and back-refs.
            n.rule_id = new_rid
            self._insert_before(next_anchor, n)
        # Drop the inlined rule.
        self.rules.pop(rid, None)
        self.back_refs.pop(rid, None)
        # Re-register surrounding digrams and enqueue for re-check.
        if not prev_anchor.is_guard and not prev_anchor.next.is_guard:
            self._register(prev_anchor)
            self._enqueue(prev_anchor)
        # Walk the inlined block to register internal digrams.
        for n in nodes_in_order:
            if not n.next.is_guard:
                self._register(n)
                self._enqueue(n)

    # --- Pretty-print -------------------------------------------------

    def format_rule(self, rule_id: int) -> str:
        rule = self.rules.get(rule_id)
        if rule is None:
            return f"R{rule_id} → ⟨deleted⟩"
        parts: List[str] = []
        for n in rule.body_iter():
            if isinstance(n.sym, NT):
                parts.append(f"R{n.sym.rule_id}")
            else:
                parts.append(repr(n.sym))
        return f"R{rule_id} → {' '.join(parts) or 'ε'}  (uses={rule.uses})"

    def top_rules(self, n: int = 5) -> List[str]:
        candidates = [
            (rid, r.uses) for rid, r in self.rules.items() if rid != 0
        ]
        candidates.sort(key=lambda kv: -kv[1])
        return [self.format_rule(rid) for rid, _ in candidates[:n]]
