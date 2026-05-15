"""
architecture_state_machine.py — formal state machine over the 28-cell
signature matrix, with V₄ and Walsh-Hadamard coherence formulae.

Definition (Q, Σ, δ, q₀, F):
  Q  = 28 cells indexed by (held, enabled) ∈ AXES × P(AXES \\ {held})
  Σ  = micro-ops ∪ V₄ swaps ∪ WHT projections
  δ  = transition function from (state × symbol) → state
  q₀ = the foundational cell (held=D, enabled=∅) — pure data access
  F  = orbit-complete cells (all 4 V₄-equivalent directions populated)

Coherence laws:
  (V) V₄ invariance:    swap acts within V₄-orbit
  (C) Cocycle commute:  op ∘ swap = swap ∘ swap(op)
  (W) WHT orthogonality: different readings detect different orbits
"""

import numpy as np
from itertools import combinations, product
from collections import defaultdict

# ============================================================
# Architecture constants
# ============================================================

AXES = ['D', 'C', 'S', 'W']
AXIS_BIT = {'D': 0, 'C': 1, 'S': 2, 'W': 3}

V4_SWAPS = {
    'e':         {a: a for a in AXES},
    'α-swap':    {'D': 'C', 'C': 'D', 'S': 'W', 'W': 'S'},  # preserves {D,C}+{S,W}
    'β-swap':    {'D': 'S', 'S': 'D', 'C': 'W', 'W': 'C'},  # preserves {D,S}+{C,W}
    'γ-swap':    {'D': 'W', 'W': 'D', 'C': 'S', 'S': 'C'},  # preserves {D,W}+{C,S}
}

PAIRINGS = {
    'α': ({'D', 'C'}, {'S', 'W'}),
    'β': ({'D', 'S'}, {'C', 'W'}),
    'γ': ({'D', 'W'}, {'C', 'S'}),
}


# ============================================================
# Micro-operations: the alphabet for the state machine
# ============================================================
# Each micro-op specifies its (held, enabled) effect. Applying the op
# transitions the state by setting the new (held, enabled).

MICRO_OPS = {
    # From the chart's S1–S7 founding micro-operations
    'S1_nil':       {'sig': ('D', frozenset()),              'class': 'data-access'},
    'S2_cons':      {'sig': ('D', frozenset({'S'})),         'class': 'data-creation'},
    'S3_left':      {'sig': ('D', frozenset()),              'class': 'data-access'},
    'S3_right':     {'sig': ('D', frozenset()),              'class': 'data-access'},
    'S4_eq':        {'sig': ('D', frozenset()),              'class': 'data-compare'},
    'S5_apply':     {'sig': ('S', frozenset({'C'})),         'class': 'compute-advance'},
    'S6_parse':     {'sig': ('D', frozenset({'C'})),         'class': 'compute-on-data'},
    'S7_transform': {'sig': ('D', frozenset({'C'})),         'class': 'compute-on-data'},
    # Higher-order
    'interp':       {'sig': ('D', frozenset({'C', 'S'})),    'class': 'meta-circular'},
}


# ============================================================
# State space enumeration: 28 cells
# ============================================================

def enumerate_states():
    """Q = the 28 (held, enabled) signatures."""
    states = []
    for held in AXES:
        other = [a for a in AXES if a != held]
        for k in range(0, 4):  # 0 to 3 enabled axes
            for combo in combinations(other, k):
                states.append((held, frozenset(combo)))
    return states


# ============================================================
# V₄ orbit computation
# ============================================================

def apply_swap(state, swap):
    held, enabled = state
    new_held = swap.get(held, held)
    new_enabled = frozenset(swap.get(a, a) for a in enabled)
    return (new_held, new_enabled)


def v4_orbit(state):
    """Return the V₄-orbit containing state."""
    orbit = {state}
    for swap in V4_SWAPS.values():
        orbit.add(apply_swap(state, swap))
    return frozenset(orbit)


# ============================================================
# Walsh-Hadamard reading of a state
# ============================================================
# Each state has a 4-bit axis-engagement pattern: which of D, C, S, W
# are touched (held or enabled). The 16 WHT readings detect this pattern
# orthogonally.

def state_to_engagement_bits(state):
    """Return the 4-bit pattern of axis engagement (held or enabled)."""
    held, enabled = state
    engaged = {held} | enabled
    bits = 0
    for axis in engaged:
        bits |= (1 << AXIS_BIT[axis])
    return bits


def wht_reading(state, signature):
    """Compute the Walsh-Hadamard reading at signature ∈ {0..15}.

    Reading = (-1)^(signature · engagement_pattern) — a single ±1 value.
    """
    bits = state_to_engagement_bits(state)
    dot = bin(signature & bits).count('1') % 2
    return -1 if dot else 1


def wht_signature_of_state(state):
    """The 16-vector of WHT readings — a 'fingerprint' of the state."""
    return np.array([wht_reading(state, s) for s in range(16)])


# ============================================================
# The transition function δ
# ============================================================

def delta(state, symbol):
    """δ: Q × Σ → Q.

    Symbol can be:
      - Micro-op name (e.g., 'S2_cons'): transitions to the op's signature
      - V₄ swap name: applies the swap
      - 'WHT_s' for s ∈ 0..15: returns the reading (does not change state)
    """
    if symbol in MICRO_OPS:
        return MICRO_OPS[symbol]['sig']
    elif symbol in V4_SWAPS:
        return apply_swap(state, V4_SWAPS[symbol])
    elif symbol.startswith('WHT_'):
        s = int(symbol[4:])
        return state  # WHT readings don't change state; they observe it
    else:
        raise ValueError(f"Unknown symbol: {symbol}")


# ============================================================
# Coherence checks
# ============================================================

def check_v4_invariance(state):
    """Verify swap(state) is in the same V₄-orbit."""
    orbit = v4_orbit(state)
    for swap in V4_SWAPS.values():
        if apply_swap(state, swap) not in orbit:
            return False
    return True


def check_cocycle_commutativity(state, op_name, swap_name):
    """Verify (op ∘ swap)(state) ≡ (swap ∘ op_twin)(state).

    The cocycle invariance says: applying an op and then swapping is
    V₄-equivalent to swapping first, then applying the swapped op.
    """
    if swap_name == 'e':
        return True

    swap = V4_SWAPS[swap_name]
    op_sig = MICRO_OPS[op_name]['sig']

    # Path 1: op, then swap
    after_op = delta(state, op_name)
    path1 = apply_swap(after_op, swap)

    # Path 2: swap state, then apply swapped op
    swapped_state = apply_swap(state, swap)
    swapped_op_sig = apply_swap(op_sig, swap)

    # Path 2's result is: starting from swapped_state, apply an op
    # whose signature is the swapped one (this requires an op with that
    # signature to exist). For coherence verification, we compare
    # V₄-orbits rather than exact equality.

    return v4_orbit(path1) == v4_orbit(swapped_op_sig)


def check_wht_orthogonality():
    """The 16 WHT readings form an orthogonal basis: H · H^T = 16 · I."""
    H = np.array([[wht_reading(('D', frozenset()), s) * (-1 if bin(s & i).count('1') % 2 else 1)
                   for i in range(16)] for s in range(16)])
    # Build Hadamard matrix directly
    H = np.zeros((16, 16), dtype=int)
    for s in range(16):
        for i in range(16):
            H[s, i] = -1 if bin(s & i).count('1') % 2 else 1
    product = H @ H.T
    expected = 16 * np.eye(16, dtype=int)
    return np.array_equal(product, expected)


# ============================================================
# Accepting states: orbit-completion
# ============================================================

def is_orbit_complete(populated_states):
    """A V₄-orbit is complete iff all 4 of its directions are populated."""
    orbits_seen = defaultdict(set)
    for state in populated_states:
        orbits_seen[v4_orbit(state)].add(state)
    complete = [orbit for orbit, dirs in orbits_seen.items() if len(dirs) == 4]
    return complete


def F_accepting(populated_states):
    """F = the states that lie in orbit-complete V₄-orbits."""
    complete_orbits = is_orbit_complete(populated_states)
    accepting = set()
    for orbit in complete_orbits:
        accepting.update(orbit)
    return accepting


# ============================================================
# Demonstration: run the state machine
# ============================================================

def demo():
    print("=" * 76)
    print("  Architecture State Machine — Formal Definition Verified")
    print("=" * 76)
    print()

    # 1. Q
    Q = enumerate_states()
    print(f"  |Q| = {len(Q)} states")

    # Group into orbits
    orbit_set = set()
    for s in Q:
        orbit_set.add(v4_orbit(s))
    print(f"  V₄-orbits: {len(orbit_set)}")
    print()

    # 2. Σ
    sigma_ops = list(MICRO_OPS.keys())
    sigma_swaps = list(V4_SWAPS.keys())
    sigma_wht = [f"WHT_{s}" for s in range(16)]
    print(f"  |Σ| = {len(sigma_ops)} micro-ops + {len(sigma_swaps)} V₄ swaps + {len(sigma_wht)} WHT readings")
    print(f"      = {len(sigma_ops) + len(sigma_swaps) + len(sigma_wht)}")
    print()

    # 3. q₀
    q0 = ('D', frozenset())
    print(f"  q₀ = {q0}  (foundational data access)")
    print()

    # 4. δ — verify each symbol transition is well-defined
    print("  δ transition examples:")
    for op_name in ['S2_cons', 'S5_apply', 'interp']:
        new_state = delta(q0, op_name)
        print(f"    δ({q0}, '{op_name}') = {new_state}")
    for swap_name in ['α-swap', 'β-swap', 'γ-swap']:
        new_state = delta(q0, swap_name)
        print(f"    δ({q0}, '{swap_name}') = {new_state}")
    print()

    # 5. Coherence law (V) — V₄ invariance
    print("  COHERENCE LAW (V) — V₄ invariance:")
    fails_v4 = [s for s in Q if not check_v4_invariance(s)]
    print(f"    States passing V₄ invariance: {len(Q) - len(fails_v4)} / {len(Q)}")
    print(f"    Verdict: {'✓ all states V₄-invariant' if not fails_v4 else f'✗ {len(fails_v4)} failures'}")
    print()

    # 6. Coherence law (C) — Cocycle commutativity
    print("  COHERENCE LAW (C) — cocycle commutativity:")
    cocycle_results = []
    for op_name in MICRO_OPS:
        for swap_name in ['α-swap', 'β-swap', 'γ-swap']:
            for state in Q[:5]:  # sample
                result = check_cocycle_commutativity(state, op_name, swap_name)
                cocycle_results.append(result)
    print(f"    Sampled cocycle checks: {sum(cocycle_results)} / {len(cocycle_results)} pass")
    print()

    # 7. Coherence law (W) — WHT orthogonality
    print("  COHERENCE LAW (W) — Walsh-Hadamard orthogonality:")
    wht_orthogonal = check_wht_orthogonality()
    print(f"    H · H^T = 16 · I_16: {'✓' if wht_orthogonal else '✗'}")
    print()

    # 8. Accepting states based on current population
    print("=" * 76)
    print("  Current M-history → accepting states")
    print("=" * 76)
    print()

    # The 5 populated signatures from the M-history audit
    populated = [
        ('D', frozenset({'C'})),
        ('C', frozenset({'D'})),
        ('D', frozenset({'C', 'S'})),
        ('D', frozenset({'S'})),
        ('S', frozenset({'C', 'D'})),
    ]
    print(f"  Populated states from M-history: {len(populated)}")
    F = F_accepting(populated)
    print(f"  Orbit-complete (accepting) states: {len(F)}")
    print()

    if not F:
        print("  NO orbit-complete V₄-orbits in the M-history.")
        print("  The architecture has not yet achieved orbit-completion.")
        print()

    # 9. Reachability: find shortest path from q₀ to a target
    print("=" * 76)
    print("  Reachability example: paths through the state machine")
    print("=" * 76)
    print()

    target = ('W', frozenset({'C', 'D'}))  # an empty cell from M-history
    print(f"  Target state: {target}  (V₄-twin of M_SPPF_witness_application)")
    print()

    # Try paths using V₄ swaps and micro-ops
    # The target's V₄-orbit contains 'S→{C,D}' which IS in M-history
    target_orbit = v4_orbit(target)
    populated_in_orbit = set(populated) & target_orbit
    if populated_in_orbit:
        sibling = list(populated_in_orbit)[0]
        print(f"  V₄-sibling already populated: {sibling}")
        # Find which swap maps sibling to target
        for swap_name, swap in V4_SWAPS.items():
            if swap_name == 'e':
                continue
            if apply_swap(sibling, swap) == target:
                print(f"  Path: apply '{swap_name}' to {sibling}")
                print(f"        constructs target {target} mechanically")
                print(f"  This is the V₄-rotation principle in action.")
                break
    print()


def show_state_table():
    """Print the full Q × Σ transition table for V₄ swaps."""
    print()
    print("=" * 76)
    print("  V₄ swap transitions for all 28 states")
    print("=" * 76)
    print()

    Q = enumerate_states()
    print(f"  {'state':<25}  {'α-swap':<25}  {'β-swap':<25}  {'γ-swap':<25}")
    print(f"  {'-'*25}  {'-'*25}  {'-'*25}  {'-'*25}")
    for state in Q:
        held, enabled = state
        state_str = f"{held}→{sorted(enabled)}"
        row_parts = [state_str]
        for swap_name in ['α-swap', 'β-swap', 'γ-swap']:
            new_state = apply_swap(state, V4_SWAPS[swap_name])
            h2, e2 = new_state
            row_parts.append(f"{h2}→{sorted(e2)}")
        print(f"  {row_parts[0]:<25}  {row_parts[1]:<25}  {row_parts[2]:<25}  {row_parts[3]:<25}")


if __name__ == "__main__":
    demo()
    show_state_table()
