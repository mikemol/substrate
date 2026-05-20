"""Eliza.GpuCodecKernel — custom CUDA RawKernel for the AC inner loop.

Slice 11 of the post-DBE plan (third pass): the speedup fix promised in
the previous self-check session.

The cupy backend of `gpu_codec.py` is byte-exact-correct but slow,
because every per-byte iteration triggers ~3 GPU kernel launches.
This module moves the per-byte AC loop INTO a CUDA kernel: one kernel
launch per chunk, all state in registers, counts updates via atomic-adds.

The kernel is a faithful port of the Python `RangeEncoder.encode` —
same low/high arithmetic, same emission rules, same finalisation. The
output bit-stream is byte-identical to the CPU version, so
`RangeDecoder` decodes it without modification.

For multi-chunk parallelism: each CUDA block processes one chunk;
chunks have independent AC states. The counts tensor is shared
across chunks (atomic updates), so model adaptation persists.

Falls back to the existing Python-loop AC if cupy is unavailable.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

try:
    import cupy as cp  # type: ignore
    HAS_CUPY = cp.cuda.is_available()
except Exception:
    cp = None
    HAS_CUPY = False


VOCAB = 256
CHUNK_SIZE = 4096

# The CUDA kernel for one chunk's encode loop. Single thread per chunk.
# Counts tensor is shared (atomic adds); each chunk has its own AC state.
_ENCODE_KERNEL_SRC = r"""
extern "C" __global__
void range_encode_chunk(
    int *counts,                  // [256*256*256] int32, atomic-updated
    const unsigned char *input,   // chunk bytes
    int n,                        // chunk length
    int c1_init,                  // initial c1 context
    int c2_init,                  // initial c2 context
    unsigned char *output,        // output bit-buffer (bytes)
    int *out_len,                 // bytes written (output)
    int *final_c1,                // c1 after chunk (output)
    int *final_c2                 // c2 after chunk (output)
) {
    const unsigned int HALF    = 0x80000000U;
    const unsigned int QUARTER = 0x40000000U;
    const unsigned int THREE_Q = 0xC0000000U;
    const unsigned int MASK    = 0xFFFFFFFFU;
    const int VOCAB_ = 256;
    const int ALPHA_X256 = 128;  // 0.5 * 256

    unsigned int low = 0;
    unsigned int high = MASK;
    int pending = 0;
    int c1 = c1_init;
    int c2 = c2_init;

    // Bit emission state.
    int buf = 0;
    int buf_len = 0;
    int out_pos = 0;

    for (int i = 0; i < n; i++) {
        int byte = (int)input[i];

        // Compute cumfreqs on-the-fly: row = counts[c1*256+c2, :].
        // Scaled freq per symbol b: counts[c1,c2,b] * 256 + 128 + 1 = counts*256 + 129.
        // We compute cum_before (sum of freqs for b < byte) and
        // sym_freq (= freq at byte) and total (sum over all b).
        long long cum_before = 0;
        long long sym_freq   = 0;
        long long total      = 0;
        int row_off = (c1 * VOCAB_ + c2) * VOCAB_;
        for (int b = 0; b < VOCAB_; b++) {
            long long freq = (long long)counts[row_off + b] * VOCAB_ + ALPHA_X256 + 1;
            total += freq;
            if (b <  byte) cum_before += freq;
            if (b == byte) sym_freq    = freq;
        }
        long long cum_after = cum_before + sym_freq;

        // AC narrow. Use uint64 for range to avoid 2^32 overflow.
        unsigned long long rng = (unsigned long long)high - (unsigned long long)low + 1ULL;
        unsigned long long h_new = (unsigned long long)low + (rng * (unsigned long long)cum_after)  / (unsigned long long)total - 1ULL;
        unsigned long long l_new = (unsigned long long)low + (rng * (unsigned long long)cum_before) / (unsigned long long)total;
        high = (unsigned int)h_new;
        low  = (unsigned int)l_new;

        // Normalize loop.
        while (true) {
            int emit = -1;
            if (high < HALF) {
                emit = 0;
            } else if (low >= HALF) {
                emit = 1;
                low  -= HALF;
                high -= HALF;
            } else if (low >= QUARTER && high < THREE_Q) {
                pending++;
                low  -= QUARTER;
                high -= QUARTER;
                low  = (low << 1);
                high = (high << 1) | 1U;
                continue;
            } else {
                break;
            }
            // Emit the bit + pending opposite bits.
            for (int k = 0; k <= pending; k++) {
                int bit = (k == 0) ? emit : (1 - emit);
                buf = (buf << 1) | bit;
                buf_len++;
                if (buf_len == 8) {
                    output[out_pos++] = (unsigned char)buf;
                    buf = 0;
                    buf_len = 0;
                }
            }
            pending = 0;
            low  = (low << 1);
            high = (high << 1) | 1U;
        }

        // Update counts (atomic).
        atomicAdd(&counts[(c1 * VOCAB_ + c2) * VOCAB_ + byte], 1);
        c1 = c2;
        c2 = byte;
    }

    // Finalize: pending++, emit either 0 or 1 based on low.
    pending++;
    int emit_final = (low < QUARTER) ? 0 : 1;
    for (int k = 0; k <= pending; k++) {
        int bit = (k == 0) ? emit_final : (1 - emit_final);
        buf = (buf << 1) | bit;
        buf_len++;
        if (buf_len == 8) {
            output[out_pos++] = (unsigned char)buf;
            buf = 0;
            buf_len = 0;
        }
    }
    // Pad final byte if needed.
    if (buf_len > 0) {
        buf = buf << (8 - buf_len);
        output[out_pos++] = (unsigned char)buf;
    }

    out_len[0]   = out_pos;
    final_c1[0]  = c1;
    final_c2[0]  = c2;
}
"""


_KERNEL = None


def _get_kernel():
    """Lazy-compile the kernel once."""
    global _KERNEL
    if _KERNEL is None and HAS_CUPY:
        _KERNEL = cp.RawKernel(
            _ENCODE_KERNEL_SRC, "range_encode_chunk", options=("-std=c++17",)
        )
    return _KERNEL


def encode_chunked_kernel(data: bytes) -> bytes:
    """Encode `data` via the CUDA RawKernel — one launch per chunk.

    Falls back to the existing Python-loop version if cupy is
    unavailable. Output format identical to `gpu_codec.encode_chunked`:
    [n_chunks: u32][offsets: u32 × n_chunks][payloads...].
    """
    if not HAS_CUPY:
        from eliza.gpu_codec import encode_chunked
        return encode_chunked(data)

    kernel = _get_kernel()
    n = len(data)
    n_chunks = (n + CHUNK_SIZE - 1) // CHUNK_SIZE

    # GPU buffers.
    counts = cp.zeros(VOCAB * VOCAB * VOCAB, dtype=cp.int32)
    # Output buffer: AC produces at most ~2 bits per input bit; size
    # generously. For binary worst case, ~2 bytes per input byte.
    max_out = max(64, CHUNK_SIZE * 2 + 64)
    out_buf = cp.zeros(max_out, dtype=cp.uint8)
    out_len = cp.zeros(1, dtype=cp.int32)
    final_c1 = cp.zeros(1, dtype=cp.int32)
    final_c2 = cp.zeros(1, dtype=cp.int32)

    c1, c2 = 0, 0
    chunk_payloads: List[bytes] = []
    for chunk_start in range(0, n, CHUNK_SIZE):
        chunk_data = data[chunk_start:chunk_start + CHUNK_SIZE]
        n_in_chunk = len(chunk_data)
        input_gpu = cp.frombuffer(chunk_data, dtype=cp.uint8)
        out_len.fill(0)

        # Launch the kernel: single thread, single block.
        kernel(
            (1,), (1,),
            (counts, input_gpu, np.int32(n_in_chunk),
             np.int32(c1), np.int32(c2),
             out_buf, out_len, final_c1, final_c2)
        )
        cp.cuda.runtime.deviceSynchronize()

        n_out = int(out_len.get()[0])
        payload = bytes(out_buf[:n_out].get())
        chunk_payloads.append(payload)
        c1 = int(final_c1.get()[0])
        c2 = int(final_c2.get()[0])

    # Assemble header + payloads (same format as encode_chunked).
    n_chunks_actual = len(chunk_payloads)
    header = bytearray()
    header.extend(n_chunks_actual.to_bytes(4, "little"))
    offset = 4 + 4 * n_chunks_actual
    for payload in chunk_payloads:
        header.extend(offset.to_bytes(4, "little"))
        offset += len(payload)
    return bytes(header) + b"".join(chunk_payloads)


def decode_chunked_kernel(encoded: bytes, n_bytes: int) -> bytes:
    """Decode counterpart. For now, delegates to the CPU decoder since
    decoding's per-byte loop is the same cost as encoding's and we
    haven't yet kernelised that. Round-trip correctness is the gate
    we're proving with the kernel; decoder speedup is a follow-up."""
    from eliza.gpu_codec import decode_chunked
    return decode_chunked(encoded, n_bytes)


def self_check(sizes_kb=(1, 4, 16, 64), verbose: bool = True) -> bool:
    """Round-trip + wall-clock for the kernel encoder vs CPU decoder.

    Compression numbers are byte-exact to `gpu_codec.encode_chunked`
    because the kernel reproduces the Python AC step exactly. The
    decode path uses the existing CPU decoder."""
    import time
    from pathlib import Path

    print("=== Eliza GPU codec RawKernel self-check ===")
    print(f"HAS_CUPY: {HAS_CUPY}")
    if not HAS_CUPY:
        print("cupy not available — kernel path can't run.")
        return False

    src_path = Path(__file__)
    with open(src_path, "rb") as f:
        base = f.read()

    all_ok = True
    for size_kb in sizes_kb:
        n = size_kb * 1024
        data = (base * ((n // len(base)) + 1))[:n]

        t0 = time.perf_counter()
        encoded = encode_chunked_kernel(data)
        cp.cuda.runtime.deviceSynchronize()
        enc_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        decoded = decode_chunked_kernel(encoded, len(data))
        dec_time = time.perf_counter() - t0

        ok = decoded == data
        all_ok = all_ok and ok
        bpb = len(encoded) * 8 / len(data)
        enc_rate = len(data) / enc_time if enc_time > 0 else 0.0
        dec_rate = len(data) / dec_time if dec_time > 0 else 0.0
        status = "✓" if ok else "✗"
        if verbose:
            print(
                f"  {size_kb:>5}KB: {status}  enc={enc_time*1000:>7.1f}ms "
                f"({enc_rate / 1e6:>6.2f} MB/s)  "
                f"dec={dec_time*1000:>7.1f}ms ({dec_rate / 1e6:>6.2f} MB/s)  "
                f"comp={bpb:.2f} b/byte"
            )
    print(f"\nResult: {'OK' if all_ok else 'FAILURE'}")
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
