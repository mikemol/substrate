"""
verify_unified_address.py — tests for M38 unified codeword structure.

Verifies:
  - Encoding is injective (24 distinct codewords)
  - Encode/decode round-trip preserves the operation
  - Each parity bit extracts the correct structural property
  - Bit-level group actions correspond to algebraic ones
  - Multi-scale parity is internally consistent
  - Hamming distance properties hold (inverse pairs at distance 1)
  - S_3 = Z_3 ⋊ Z_2 chirality-orientation structure verified
"""

from chart_chained import ChartChained
from unified_address import (
    UnifiedCodeword, encode_op, decode_to_signature,
    AXIS_TO_LABEL, V4_XOR_MASK, PAIRING_TO_BITS,
    z3_next_pairing, verify_parity_coherence,
)


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.records = []

    def run(self, name, fn):
        try:
            result = fn()
            if result is True:
                self.passed += 1
                self.records.append(('✓', name))
            else:
                self.failed += 1
                self.records.append(('✗', f"{name}: {result}"))
        except Exception as e:
            self.failed += 1
            self.records.append(('✗', f"{name}: {type(e).__name__}: {e}"))

    def summary(self):
        for marker, line in self.records:
            print(f"  {marker} {line}")
        print()
        total = self.passed + self.failed
        verdict = '✓✓✓' if self.failed == 0 else f'({self.failed} failures)'
        print(f"  {self.passed}/{total} pass  {verdict}")


# ============================================================
# Injectivity & round-trip
# ============================================================

def test_encoding_is_injective():
    c = ChartChained()
    codes = [encode_op(op).code for op in c.registry.all()]
    if len(set(codes)) != 24:
        return f"only {len(set(codes))} unique codewords (expected 24)"
    return True


def test_encode_decode_round_trip():
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        decoded = decode_to_signature(cw, c.registry)
        if decoded is None or decoded.name != op.name:
            return f"{op.name} round-trip failed"
    return True


def test_valid_codewords_avoid_pairing_11():
    """Valid codewords have pairing bits ∈ {00, 01, 10}, not 11."""
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        if cw.pairing_bits == 0b11:
            return f"{op.name} has invalid pairing bits 11"
        if not cw.is_valid:
            return f"{op.name} not marked valid"
    return True


# ============================================================
# Parity bit correspondence
# ============================================================

def test_chirality_bit_matches_sign():
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        expected = 1 if op.chirality == 'odd' else 0
        if cw.chirality_bit != expected:
            return f"{op.name}: chirality bit mismatch"
    return True


def test_witness_bits_match_axis_label():
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        if cw.witness_bits != AXIS_TO_LABEL[op.witness]:
            return f"{op.name}: witness bits don't match axis label"
    return True


def test_pairing_bits_match_pairing():
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        if cw.pairing_bits != PAIRING_TO_BITS[op.pairing]:
            return f"{op.name}: pairing bits don't match"
    return True


# ============================================================
# Group actions at the bit level
# ============================================================

def test_inverse_flips_chirality_bit_only():
    """Inverse pairs should differ in exactly bit 4 (chirality) and nothing else."""
    c = ChartChained()
    for op in c.registry.all():
        inv_sig = op.invert_signature()
        inv_ops = c.registry.at_signature(*inv_sig)
        if inv_ops:
            inv_op = inv_ops[0]
            cw_a = encode_op(op)
            cw_b = encode_op(inv_op)
            xor = cw_a.code ^ cw_b.code
            if xor != 0b10000:  # Only bit 4
                return f"{op.name} ↔ {inv_op.name}: XOR = {xor:05b}, expected 10000"
    return True


def test_inverse_hamming_distance_is_1():
    c = ChartChained()
    for op in c.registry.all():
        inv_sig = op.invert_signature()
        inv_ops = c.registry.at_signature(*inv_sig)
        if inv_ops:
            cw_a = encode_op(op)
            cw_b = encode_op(inv_ops[0])
            if cw_a.hamming_distance(cw_b) != 1:
                return f"{op.name}: distance not 1"
    return True


def test_chain_action_via_codeword():
    """The codeword's chain() method should produce the chained op's codeword."""
    c = ChartChained()
    for chain in c.chains:
        host_cw = encode_op(chain.host)
        chained_cw = encode_op(chain.chained)
        derived = host_cw.chain()
        if derived.code != chained_cw.code:
            return f"{chain.host.name}: codeword chain mismatch"
    return True


def test_z3_orientation_depends_on_chirality():
    """Even chirality: forward Z_3. Odd: reversed Z_3."""
    forward = {'α': 'β', 'β': 'γ', 'γ': 'α'}
    reversed_ = {'α': 'γ', 'γ': 'β', 'β': 'α'}
    for p in ('α', 'β', 'γ'):
        if z3_next_pairing(p, 'even') != forward[p]:
            return f"even chirality not forward at {p}"
        if z3_next_pairing(p, 'odd') != reversed_[p]:
            return f"odd chirality not reversed at {p}"
    return True


def test_chain_period_3_at_codeword_level():
    """Applying chain() three times returns the original codeword."""
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        cw3 = cw.chain().chain().chain()
        if cw3.code != cw.code:
            return f"{op.name}: chain^3 != identity"
    return True


def test_chain_preserves_chirality_and_witness_bits():
    """Chain only modifies pairing bits (2-3), leaving chirality and witness bits unchanged."""
    c = ChartChained()
    for op in c.registry.all():
        cw = encode_op(op)
        cw_next = cw.chain()
        if cw.chirality_bit != cw_next.chirality_bit:
            return f"{op.name}: chain changed chirality"
        if cw.witness_bits != cw_next.witness_bits:
            return f"{op.name}: chain changed witness"
    return True


# ============================================================
# Coherence with the chart's registry
# ============================================================

def test_parity_coherence_all_passes():
    c = ChartChained()
    results, _ = verify_parity_coherence(c)
    failures = [k for k, v in results.items() if not v]
    if failures:
        return f"failures: {failures}"
    return True


# ============================================================
# Run
# ============================================================

def main():
    print("=" * 78)
    print("  verify_unified_address.py — M38 unified Hamming-coded address space")
    print("=" * 78)

    runner = TestRunner()

    print("\n[injectivity & round-trip]")
    runner.run('encoding_is_injective', test_encoding_is_injective)
    runner.run('encode_decode_round_trip', test_encode_decode_round_trip)
    runner.run('valid_codewords_avoid_pairing_11', test_valid_codewords_avoid_pairing_11)

    print("\n[parity bit correspondence]")
    runner.run('chirality_bit_matches_sign', test_chirality_bit_matches_sign)
    runner.run('witness_bits_match_axis_label', test_witness_bits_match_axis_label)
    runner.run('pairing_bits_match_pairing', test_pairing_bits_match_pairing)

    print("\n[group actions at bit level]")
    runner.run('inverse_flips_chirality_bit_only', test_inverse_flips_chirality_bit_only)
    runner.run('inverse_hamming_distance_is_1', test_inverse_hamming_distance_is_1)
    runner.run('chain_action_via_codeword', test_chain_action_via_codeword)
    runner.run('z3_orientation_depends_on_chirality', test_z3_orientation_depends_on_chirality)
    runner.run('chain_period_3_at_codeword_level', test_chain_period_3_at_codeword_level)
    runner.run('chain_preserves_chirality_and_witness_bits', test_chain_preserves_chirality_and_witness_bits)

    print("\n[coherence]")
    runner.run('parity_coherence_all_passes', test_parity_coherence_all_passes)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
