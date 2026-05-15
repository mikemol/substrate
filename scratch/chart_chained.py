"""
chart_chained.py — M37: 4-axis chained operations.

The user's structural choice: use the 4th axis to chain another operation.
The chained op is "whatever is naturally witnessed by the triple being extended-on."

Formalization: for host (s, t, w), the chained op is (t, f, w), where f is the
fourth axis. This rule has three properties:

  1. The host's output on t becomes the chained's input on t (pass-through).
  2. The host's witness w is preserved as the chained's witness (shared validation).
  3. The chained's sink f is the previously-unused fourth axis (full engagement).

Structural payoff:
  The chain function (s,t,w) -> (t,f,w) is the Z_3 = A_4/V_4 quotient action.
  It preserves witness w and chirality (sign of permutation), and cycles
  through the 3 pairings (α -> β -> γ -> α).
  The 24 directed witnessed ops decompose into 8 3-cycles under chaining.
  Combined with V_4 (axis swaps) and Z_2 (inverse, source/sink swap), this
  realizes the full S_4 = V_4 ⋊ S_3 group action at the implementation level.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Tuple
from chart_full_v4 import ChartFullV4
from meta_protocol import WitnessedOp, AXES


# ============================================================
# How to extract the "axis-t value" from a host op's call
# ============================================================
# When chaining, the host produces something on its sink axis t.
# This value flows into the chained op as its first argument.
# The way to read "the t-axis output" depends on what t is and what
# the host op's calling convention is.

# Operations where the workspace_id is in args (not the return value):
W_SINK_OPS = {
    'store':                          0,  # store(slot_id, data_id) -- slot is arg[0]
    'validated_store':                1,  # validated_store(data, slot, pred) -- slot is arg[1]
    'compute_to_workspace_via_state': 1,
    'compute_to_workspace_via_data':  1,
    'state_to_workspace_via_compute': 1,
    'state_to_workspace_via_data':    1,
}


# ============================================================
# ChainedOp: a 4-axis operation = host + chained
# ============================================================

@dataclass
class ChainedOp:
    """A 4-axis chained operation: host (s, t, w) → chained (t, f, w)."""
    chart: ChartFullV4
    host: WitnessedOp
    chained: WitnessedOp

    def __post_init__(self):
        # Enforce chaining rule
        if self.chained.source != self.host.sink:
            raise ValueError(
                f"chained.source ({self.chained.source}) != host.sink ({self.host.sink})"
            )
        if self.chained.witness != self.host.witness:
            raise ValueError(
                f"chained.witness ({self.chained.witness}) != host.witness ({self.host.witness})"
            )

    @property
    def name(self) -> str:
        return f"chain[{self.host.name}>>{self.chained.name}]"

    @property
    def source(self) -> str:
        return self.host.source

    @property
    def passthrough(self) -> str:
        return self.host.sink  # = chained.source

    @property
    def witness(self) -> str:
        return self.host.witness  # = chained.witness

    @property
    def sink(self) -> str:
        return self.chained.sink

    @property
    def signature_4axis(self) -> Tuple[str, str, str, str]:
        """(source, passthrough, witness, sink) — all 4 axes labeled by role."""
        return (self.source, self.passthrough, self.witness, self.sink)

    @property
    def held_axis(self) -> str:
        """The 'held' axis in V_4 (held, enabled) framework is the witness."""
        return self.witness

    @property
    def chirality(self) -> str:
        return self.host.chirality  # chain preserves chirality

    def _extract_intermediate(self, host_args, host_result):
        """Extract the value-on-axis-t after host has run."""
        t = self.host.sink
        if t in ('D', 'C'):
            # Return value is the t-axis output
            return host_result
        if t == 'S':
            # State-sink: the latest history index
            return len(self.chart._history) - 1
        if t == 'W':
            # Workspace-sink: workspace_id is in host's args
            arg_idx = W_SINK_OPS.get(self.host.name)
            if arg_idx is None:
                raise ValueError(f"Unknown W-sink op for chaining: {self.host.name}")
            return host_args[arg_idx]
        raise ValueError(f"Unknown sink axis: {t}")

    def run(self, host_args: tuple, chained_extra_args: tuple = ()) -> int:
        """Execute the chain: run host, extract intermediate, run chained."""
        host_result = self.host.fn(*host_args)
        if host_result == self.chart.FAILURE:
            return self.chart.FAILURE
        intermediate = self._extract_intermediate(host_args, host_result)
        return self.chained.fn(intermediate, *chained_extra_args)


# ============================================================
# Build all 24 chains (one per host op)
# ============================================================

def build_all_chains(chart: ChartFullV4) -> List[ChainedOp]:
    """Generate the 24 chained 4-axis operations from the chained rule."""
    chains = []
    for host_op in chart.registry.all():
        s, t, w = host_op.source, host_op.sink, host_op.witness
        f = (set(AXES) - {s, t, w}).pop()
        chained_sig = (t, f, w)
        chained_ops = chart.registry.at_signature(*chained_sig)
        if not chained_ops:
            raise RuntimeError(f"No registered op at chained signature {chained_sig}")
        chains.append(ChainedOp(chart=chart, host=host_op, chained=chained_ops[0]))
    return chains


# ============================================================
# Z_3 cycle discovery
# ============================================================

def discover_z3_cycles(chart: ChartFullV4):
    """The chain function is a Z_3 generator. Find its 3-cycles."""
    def chain_of_signature(sig):
        s, t, w = sig
        f = (set(AXES) - {s, t, w}).pop()
        return (t, f, w)

    all_sigs = {(op.source, op.sink, op.witness) for op in chart.registry.all()}
    cycles = []
    seen = set()
    for sig in all_sigs:
        if sig in seen:
            continue
        cycle = [sig]
        nxt = chain_of_signature(sig)
        while nxt != sig:
            cycle.append(nxt)
            nxt = chain_of_signature(nxt)
        for s in cycle:
            seen.add(s)
        cycles.append(cycle)
    return cycles


# ============================================================
# ChartChained: chart with chains registered
# ============================================================

class ChartChained(ChartFullV4):
    """ChartFullV4 + 24 4-axis chained operations indexed by host."""

    def __init__(self):
        super().__init__()
        self.chains = build_all_chains(self)
        self.chains_by_host = {c.host.name: c for c in self.chains}

    def chain_for(self, host_name: str) -> ChainedOp:
        """Get the chained op for a given host."""
        return self.chains_by_host[host_name]

    def show_chain_structure(self) -> None:
        """Print the 8 Z_3-cycles of the chain action."""
        cycles = discover_z3_cycles(self)
        print("  Chain action decomposes 24 ops into 8 3-cycles (Z_3 = A_4/V_4):")
        print()
        for i, cycle in enumerate(cycles, 1):
            ops = [self.registry.at_signature(*s)[0] for s in cycle]
            witness = cycle[0][2]
            chirality = ops[0].chirality
            pairings = [op.pairing for op in ops]
            print(f"  Cycle {i}  [witness={witness}, chirality={chirality}, pairings: {'→'.join(pairings)}→{pairings[0]}]")
            print(f"    {' → '.join(op.name for op in ops)}")
        print()


def demo():
    print("=" * 78)
    print("  ChartChained — M37: 4-axis chained operations (Z_3 generator)")
    print("=" * 78)
    print()

    c = ChartChained()
    print(f"  3-axis operations registered: {len(c.registry)}")
    print(f"  4-axis chained operations:    {len(c.chains)} (one per host)")
    print()

    # ============================================================
    # Show one chain's structure
    # ============================================================
    print("=" * 78)
    print("  Anatomy of one chained operation")
    print("=" * 78)
    print()
    apply_chain = c.chain_for('apply')
    print(f"  Chain: {apply_chain.name}")
    print(f"    host:        {apply_chain.host.name} ({apply_chain.host.source}→{apply_chain.host.sink} w/ {apply_chain.host.witness})")
    print(f"    chained:     {apply_chain.chained.name} ({apply_chain.chained.source}→{apply_chain.chained.sink} w/ {apply_chain.chained.witness})")
    print(f"    4-axis sig:  {apply_chain.signature_4axis} = (source, passthrough, witness, sink)")
    print(f"    held axis:   {apply_chain.held_axis} (the V_4-quadradic cell)")
    print(f"    chirality:   {apply_chain.chirality} (preserved by chain)")

    # ============================================================
    # Z_3 cycle structure
    # ============================================================
    print()
    print("=" * 78)
    print("  Z_3-cycle decomposition of the chain action")
    print("=" * 78)
    print()
    c.show_chain_structure()

    # ============================================================
    # Run sample chains
    # ============================================================
    print("=" * 78)
    print("  Sample chains running end-to-end")
    print("=" * 78)
    print()

    # Chain 1: apply >> compute_to_workspace_via_state
    # input: data term, output: workspace slot id (storing the reduced compute)
    w0 = c.workspace_alloc()
    chain1 = c.chain_for('apply')
    expr = c.cons(c.I, c.TRUE)
    result = chain1.run(host_args=(expr,), chained_extra_args=(w0,))
    print(f"  apply >> compute_to_workspace_via_state(I TRUE, w0)")
    print(f"    chain returns: {c.show(result)}")
    print(f"    workspace[w0] = {c._workspace[w0]}")
    print(f"    [α-even chain: data reduces to compute result, then deposits to workspace]")

    # Chain 2: store >> workspace_to_compute_via_state
    # input: slot_id, data; output: compute result of evaluating workspace contents
    print()
    w1 = c.workspace_alloc()
    chain2 = c.chain_for('store')
    result = chain2.run(host_args=(w1, c.TRUE), chained_extra_args=())
    print(f"  store >> workspace_to_compute_via_state(w1, TRUE)")
    print(f"    chain returns: {c.show(result)}")
    print(f"    [γ-odd chain: store data → fire compute on stored value (deferred eval)]")

    # Chain 3: evolve_with_receipt >> state_to_compute_via_workspace
    # input: data, workspace; runs evolve, then replays the new history entry via compute
    print()
    w2 = c.workspace_alloc()
    w3 = c.workspace_alloc()
    chain3 = c.chain_for('evolve_with_receipt')
    result = chain3.run(host_args=(c.TRUE, w2), chained_extra_args=(w3,))
    print(f"  evolve_with_receipt >> state_to_compute_via_workspace(TRUE, w2, w3)")
    print(f"    chain returns: {c.show(result)}")
    print(f"    [β-even chain: state-evolve with receipt → replay history through compute]")


if __name__ == "__main__":
    demo()
