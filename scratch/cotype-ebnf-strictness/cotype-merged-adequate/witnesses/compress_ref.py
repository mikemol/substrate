# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Reference implementations of the compression primitives name-dropped in the groundings.
Each is decomposed into its constituent steps. bzip2 = RLE->BWT->MTF->RLE2->Huffman; DEFLATE = LZ77->Huffman.
These are the 'how it works / how it breaks down' the conformance warrants pin. All round-trip (lossless)."""

# ---------- BWT: Burrows-Wheeler Transform (the heart of bzip2) ----------
# HOW IT WORKS: form all rotations of s+sentinel, sort them, take the last column. Clusters equal-context
# symbols into runs (which is WHY it precedes RLE). INVERTIBLE: the last column + the primary index recover s.
# This invertibility IS the canonical-form + residue law: BWT(s) is the canonical (sorted-rotation) form,
# the primary index is the residue that makes it lossless.
def bwt(s, sentinel="\x03"):
    s = s + sentinel
    rots = sorted(range(len(s)), key=lambda i: s[i:]+s[:i])  # sorted rotations (by suffix)
    last = "".join(s[(i-1) % len(s)] for i in rots)          # last column
    primary = rots.index(0)                                   # residue: where the original row landed
    return last, primary

def ibwt(last, primary, sentinel="\x03"):
    n = len(last)
    # LF-mapping: stable-sort the last column to get the first column's source order
    rank = sorted(range(n), key=lambda i: (last[i], i))
    out = []
    j = rank[primary]
    for _ in range(n):
        out.append(last[j]); j = rank[j]
    s = "".join(out)
    return s.rstrip(sentinel) if sentinel in s else s

# ---------- RLE: Run-Length Encoding ----------
# HOW IT WORKS: replace a run of k identical symbols with (symbol, k). Shrinks the runs BWT created.
def rle(s):
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append((s[i], j-i)); i = j
    return out
def unrle(pairs):
    return "".join(c*k for c,k in pairs)

# ---------- MTF: Move-To-Front ----------
# HOW IT WORKS: maintain a list of symbols; encode each as its current index, then move it to front.
# After BWT (runs of equal symbols) MTF produces many zeros -> highly skewed -> Huffman-friendly.
def mtf_encode(s, alphabet=None):
    table = sorted(set(s)) if alphabet is None else list(alphabet)
    out = []
    for c in s:
        idx = table.index(c); out.append(idx)
        table.pop(idx); table.insert(0, c)
    return out, (sorted(set(s)) if alphabet is None else list(alphabet))
def mtf_decode(idxs, table):
    table = list(table); out = []
    for idx in idxs:
        c = table[idx]; out.append(c)
        table.pop(idx); table.insert(0, c)
    return "".join(out)

# ---------- Huffman: optimal prefix code ----------
# HOW IT WORKS: build a min-heap of (freq,symbol) leaves, repeatedly merge the two least-frequent into a
# parent, assign 0/1 down the tree -> shorter codes for frequent symbols. Prefix-free => uniquely decodable.
import heapq
def huffman_codes(freqs):
    if len(freqs) == 1:                       # degenerate: single symbol -> 1-bit code
        return {next(iter(freqs)): "0"}
    heap = [[w, [(sym, "")]] for sym, w in freqs.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap); hi = heapq.heappop(heap)
        for pair in lo[1]: pair_code = pair
        lo[1] = [(s, "0"+c) for s,c in lo[1]]
        hi[1] = [(s, "1"+c) for s,c in hi[1]]
        heapq.heappush(heap, [lo[0]+hi[0], lo[1]+hi[1]])
    return {s:c for s,c in heap[0][1]}
def huffman_encode(s):
    from collections import Counter
    codes = huffman_codes(Counter(s))
    return "".join(codes[c] for c in s), codes
def huffman_decode(bits, codes):
    inv = {c:s for s,c in codes.items()}; out=[]; cur=""
    for b in bits:
        cur += b
        if cur in inv: out.append(inv[cur]); cur=""
    return "".join(out)

# ---------- bzip2 pipeline: RLE -> BWT -> MTF -> Huffman (the real stack, simplified) ----------
def bzip2_compress(s):
    b, primary = bwt(s)
    idxs, table = mtf_encode(b)
    # serialize mtf indices as symbols for Huffman
    sym = "".join(chr(i) for i in idxs)
    bits, codes = huffman_encode(sym)
    return {"bits": bits, "codes": codes, "primary": primary, "table": table, "n": len(sym)}
def bzip2_decompress(blob):
    sym = huffman_decode(blob["bits"], blob["codes"])
    idxs = [ord(c) for c in sym]
    b = mtf_decode(idxs, blob["table"])
    return ibwt(b, blob["primary"])

# ---------- LZ77: the dictionary half of DEFLATE ----------
# HOW IT WORKS: slide a window; emit (distance-back, length, next-literal) for the longest match found in
# the window, else (0,0,literal). DEFLATE then Huffman-codes these tokens. Captures repetition by reference.
def lz77_compress(s, window=4096, lookahead=15):
    i = 0; out = []
    while i < len(s):
        best_len, best_dist = 0, 0
        start = max(0, i-window)
        for j in range(start, i):
            l = 0
            while l < lookahead and i+l < len(s) and s[j+l] == s[i+l]: l += 1
            if l > best_len: best_len, best_dist = l, i-j
        nxt = s[i+best_len] if i+best_len < len(s) else ""
        out.append((best_dist, best_len, nxt)); i += best_len + 1
    return out
def lz77_decompress(tokens):
    out = []
    for dist, length, nxt in tokens:
        if dist > 0:
            start = len(out)-dist
            for k in range(length): out.append(out[start+k])
        if nxt: out.append(nxt)
    return "".join(out)

# ---------- DEFLATE: LZ77 -> Huffman (the gzip/zlib core, simplified) ----------
def deflate(s):
    tokens = lz77_compress(s)
    flat = "".join(f"{d},{l},{n}|" for d,l,n in tokens)   # serialize tokens
    bits, codes = huffman_encode(flat)
    return {"bits": bits, "codes": codes, "ntok": len(tokens)}
def inflate(blob):
    flat = huffman_decode(blob["bits"], blob["codes"])
    tokens = []
    for part in flat.split("|")[:-1]:
        d,l,n = part.split(",")
        tokens.append((int(d), int(l), n))
    return lz77_decompress(tokens)
