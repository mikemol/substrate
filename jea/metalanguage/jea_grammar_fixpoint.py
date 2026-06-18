#!/usr/bin/env python3
"""jea_grammar_fixpoint.py — grammar recognition AS the intern-fixpoint of decomposition.

This is the CONSOLIDATED result of the BNF/EBNF/ABNF arc, after three corrections (overbuild → compose
→ control-flow-dissolved). It supersedes the exploratory scratch (jea_sppf_chart.py / _seed.py /
_compose.py), which carried bespoke machinery the arc proved unnecessary. The finding, stated as code:

    THERE IS NO SEPARATE PARSER. Earley recognition is the intern-fixpoint of the term decomposition the
    core already runs. Concretely, on jea_pyalg's Intern + PyDivStr:
      * predict / scan / complete  = the three wedge/recon cases (decompose-expecting / consume-atom /
        rebuild-and-reintern) — NOT bespoke operations.
      * the chart                  = the TRACE's descent-grading. Position/span is RESIDUE carried on the
        interned node (the grading the core already keeps: "depth(trace) is the grade axis"), NOT an
        external chart[k] array (which the core warns is a forbidden digest).
      * the closure loop           = the FIXPOINT of intern's idempotence. intern appends only on a NEW
        key, so "the table grew this round" IS the progress signal — no `changed` flag.
      * acceptance                 = a structural READOUT (does the start-symbol-over-the-full-input node
        exist in the table?), not a returned flag.
      * the grammar readout        = stream_rhs: the BACKWARD read of the retained chain, streamed. (It
        is the trace_fold direction — "different reads of the SAME kept trace" — but trace_fold/trace()
        MATERIALIZE eagerly, so the streaming reader drives `wedge` directly in a loop instead; see
        stream_rhs. This is why trace_fold is NOT imported here.)

    This is the Σ-OBLIGATION spine at the parsing scale: predict/scan/complete = forward discharge
    (register obligations, compose witnesses); stream_rhs = the backward read of the same retained
    structure. ONE fold, two reads. Termination = the table reaches a fixed size (finite for a finite
    input + finitely many (rule,dot,span) consequences) — the per-instance well-foundedness witness the
    spine itself does not supply.

SHARED vs PACKED (the S and P of SPPF): NOT re-derived here — jea_zsppf already states it. Sorting/
deduping by the STRUCTURAL code (op, child-ids) gives SHARING (one node, many parents — exactly
Intern's hash-cons + fan-in). Deduping by the VALUE code gives PACKING (structurally-distinct,
value-equal terms collapse). Ambiguity-sharing here is the structural half = Intern's existing dedup;
the fan-in count is the sharing signal. So the earlier "is the ambiguity-sharing faithful?" question is
answered by the existing S/P characterization, not a new mechanism.

HONEST RESIDUE (conservation-of-difficulty): this re-scans all item-nodes each fixpoint round, so it is
O(items²)·rounds. The classic Earley chart[k] buckets are a legitimate INDEX over the trace-grading for
performance (an index over existing structure, not a parallel coordinate system) — reintroduce ONLY as
an index if a real corpus needs the speed. Correctness needs only the intern-fixpoint + the grading.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR, PyDivStr

# grammar = {nonterminal: [rhs, ...]}, rhs = [symbol, ...]; symbol is a nonterminal (a grammar key) or
# a terminal (matched against the input token's symbol). tokens are bare symbols or (symbol, lexeme).


def recognize(grammar: dict, tokens: list, start: str, intern: Intern | None = None) -> dict:
    """Recognition = intern derivable consequences to fixpoint; accept = a structural readout.
    No chart[k] array, no `changed` flag — the table's growth IS the fixpoint signal."""
    I = intern or Intern()
    toks = [(t if isinstance(t, tuple) else (t, t)) for t in tokens]
    syms = [s for s, _ in toks]
    n = len(toks)

    def item(lhs, rhs, dot, origin, end, kids):
        # a NORMAL interned node. The production+dot is the IDENTITY (in the KEY, op); the span
        # (origin,end) is the grading (role). kids = the consumed sub-result nodes (the retained chain).
        return I.intern(IR(kind="it", op=f"{lhs}|{'>'.join(rhs)}|{dot}",
                           role=f"{origin}:{end}", children=tuple(kids)))

    for rhs in grammar.get(start, []):
        item(start, rhs, 0, 0, 0, ())

    def items():
        return [i for i in range(I.size()) if I.nodes[i].kind == "it"]

    while True:                                                # FIXPOINT of intern's idempotence
        before = I.size()
        for it in items():
            nd = I.nodes[it]
            lhs, rhs_s, dot_s = nd.op.split("|")
            rhs = rhs_s.split(">") if rhs_s else []
            dot = int(dot_s); origin, end = map(int, nd.role.split(":"))
            if dot < len(rhs):
                nxt = rhs[dot]
                if nxt in grammar:                             # PREDICT (decompose-expecting)
                    for r in grammar[nxt]:
                        item(nxt, r, 0, end, end, ())
                elif end < n and syms[end] == nxt:             # SCAN (consume atom; lexeme retained)
                    leaf = I.intern(IR(kind="tok", op=nxt, children=(), payload=(toks[end][1],)))
                    item(lhs, rhs, dot + 1, origin, end + 1, nd.children + (leaf,))
            else:                                              # COMPLETE (rebuild + reintern)
                done = I.intern(IR(kind="parse", op=lhs, children=nd.children))
                for w in items():
                    wd = I.nodes[w]
                    wl, wrs, wds = wd.op.split("|")
                    wr = wrs.split(">") if wrs else []
                    wdot = int(wds); worigin, wend = map(int, wd.role.split(":"))
                    if wend == origin and wdot < len(wr) and wr[wdot] == lhs:
                        item(wl, wr, wdot + 1, worigin, end, wd.children + (done,))
        if I.size() == before:                                 # table stopped growing → fixpoint
            break

    roots = [i for i in items()
             if (lambda nd: nd.op.split("|")[0] == start
                 and int(nd.op.split("|")[2]) == len(nd.op.split("|")[1].split(">") if nd.op.split("|")[1] else [])
                 and nd.role == f"0:{n}")(I.nodes[i])]
    return {"accept": bool(roots), "roots": roots, "forest_size": I.size(), "intern": I}


def stream_rhs(I: Intern, parse_node: int):
    """The rhs as a STREAM (generator), O(1) state: loop the single-step primitive `wedge`, yielding each
    component as it is produced — the EEA back-substitution read, where the grammar IS the Bézout chain
    and you dump it as you walk it. Does NOT use trace()/trace_fold() (both eagerly materialize: trace
    builds the whole nested Trace, trace_fold accumulates to the base before composing). A 50GiB SPPF
    emits in CONSTANT memory because nothing beyond the current wedge step is ever held.

    (The spine, corrected: 'retain all intermediates' is a property of the FOREST — the interned shared
    structure persists — NOT of the readout. The forest keeps everything; the read of it keeps nothing.)"""
    D = PyDivStr(I)
    cur = parse_node
    while True:
        w = D.wedge(cur)
        if w is None:
            return
        nb = I.nodes[w.base]
        yield nb.payload[0] if (nb.kind == "tok" and nb.payload) else nb.op
        if w.rem == -1:
            return
        cur = w.rem


# ── SPPF → ABNF / EBNF readout (the unparse direction; STREAMING — a member of the project/emit family) ──
# Emit each rule straight to `out` as it is reached; never materialize a grammar dict (that dict was the
# 50GiB-fatal re-materialization). EBNF↔ABNF is a CARRIER-RENAME: same chain, different surface tokens.
# `rules` is an iterable of (lhs, alternation) where alternation is an iterable of parse-node ids (one
# per concatenation) whose rhs streams via stream_rhs — so the whole emit is O(1)-state over the forest.
_DIALECT = {
    "abnf": {"def": "=",   "alt": " / ", "term": lambda s: f'"{s}"'},
    "ebnf": {"def": "::=", "alt": " | ", "term": lambda s: f'"{s}"'},
}


def emit_abnf_stream(I: Intern, rules, is_nonterminal, dialect="abnf", out=None):
    """STREAMING SPPF→ABNF/EBNF. `rules`: iterable of (lhs, [concat_parse_node, ...]); each concat's rhs
    streams via stream_rhs. Writes each rule to `out` as reached (default: yields lines). O(1) state."""
    import sys as _sys
    d = _DIALECT[dialect]
    sink = (out.write if out is not None else None)
    def sym(s): return s if is_nonterminal(s) else d["term"](s)
    for lhs, concats in rules:
        parts = []
        for c in concats:
            seq = list(stream_rhs(I, c)) if not isinstance(c, (list, tuple)) else list(c)
            parts.append(" ".join(sym(s) for s in seq) if seq else '""')
        line = f"{lhs} {d['def']} {d['alt'].join(parts)}"
        if sink: sink(line + "\n")
        else: yield line


def emit_grammar(grammar: dict, dialect: str = "abnf") -> str:
    """Convenience wrapper for a SMALL in-memory grammar dict (tests/fragments). For large/streamed
    forests use emit_abnf_stream (O(1) state). EBNF↔ABNF = carrier-rename. HONEST LIMIT: terminal-vs-
    nonterminal is 'is it a grammar key', so a FRAGMENT with undefined nonterminal refs can't distinguish
    them (quotes them as terminals); unambiguous for a COMPLETE grammar."""
    d = _DIALECT[dialect]
    def sym(s): return s if s in grammar else d["term"](s)
    return "\n".join(
        f"{lhs} {d['def']} " + d["alt"].join(
            " ".join(sym(s) for s in conc) if conc else '""' for conc in alts)
        for lhs, alts in grammar.items())


if __name__ == "__main__":
    print("=== jea_grammar_fixpoint: recognition AS the intern-fixpoint of decomposition ===\n")
    print("S->A B on 'a b' :", recognize({"S": [["A", "B"]], "A": [["a"]], "B": [["b"]]},
                                          ["a", "b"], "S")["accept"])
    G = {"S": [["a", "S", "b"], []]}
    for t in (["a", "b"], ["a", "a", "b", "b"], ["a", "a", "b"], []):
        print(f"a^n b^n on {''.join(t) or 'ε':5}:", recognize(G, t, "S")["accept"],
              " (no chart[k], no changed flag — intern-fixpoint + a readout)")
    r = recognize({"E": [["E", "+", "E"], ["x"]]}, ["x", "+", "x", "+", "x"], "E")
    I = r["intern"]; xid = I.table.get(("tok", "", "x", "", ()))
    print(f"E->E+E|x ambiguous: accept={r['accept']}  'x' fan-in={I.fanin[xid]} "
          f"(SHARING = structural dedup; PACKING = value dedup — see jea_zsppf, not re-derived)")

    print("\n--- SPPF → ABNF / EBNF readout (the unparse direction; EBNF↔ABNF a carrier-rename) ---")
    Gx = {"S": [["a", "S", "b"], ["a", "b"]], "word": [["NAME"], ["STRING"]]}
    print(emit_grammar(Gx, "abnf"))
    print("  --- same grammar, EBNF carrier-rename ---")
    print(emit_grammar(Gx, "ebnf"))
